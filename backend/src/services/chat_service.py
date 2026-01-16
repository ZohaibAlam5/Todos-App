from typing import List, Optional, Any, Dict
from sqlmodel import Session, select
from datetime import datetime
import json
import asyncio
import os

# Disable OpenAI Agents SDK tracing before importing (prevents 401 errors with non-OpenAI providers)
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "true"

from agents import Agent, Runner, function_tool, RunResult, set_default_openai_client
from openai import AsyncOpenAI

# Try to import OpenAIChatCompletionsModel for custom model provider
try:
    from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
    HAS_CHAT_COMPLETIONS_MODEL = True
except ImportError:
    HAS_CHAT_COMPLETIONS_MODEL = False
    print("[WARNING] OpenAIChatCompletionsModel not available, using default model handling")

# Try to disable tracing programmatically (may not exist in all versions)
try:
    from agents import set_tracing_disabled
    set_tracing_disabled(True)
except ImportError:
    pass  # Tracing disabled via environment variable

from src.models.conversation import Conversation, ConversationRead
from src.models.message import Message, MessageRole, MessageRead, ToolCallInfo
from src.services.task_service import TaskService
from src.config import GEMINI_API_KEY, GEMINI_BASE_URL, GEMINI_MODEL


# Agent instructions for the Todo Assistant
AGENT_INSTRUCTIONS = """You are a helpful Todo Assistant that helps users manage their tasks through natural language conversation.

CAPABILITIES:
- Create new tasks with titles, descriptions, priorities (High/Medium/Low), and tags
- List all tasks or filter by completion status, priority, or tags
- Mark tasks as complete
- Update task details (title, description, priority, tags)
- Delete tasks (with user confirmation)

GUIDELINES:
1. Be conversational and helpful. Acknowledge what the user wants before taking action.
2. When creating tasks, if the title is unclear or too vague (e.g., just "add something"), ask for clarification about what the task should be.
3. For listing tasks, format the output in a readable way showing title, status, and priority.
4. When the user mentions a task by partial name, find the best match. If multiple tasks match, ask which one they mean.
5. ALWAYS ask for confirmation before deleting tasks. Never delete without explicit user approval.
6. If a task operation fails, explain what went wrong and suggest alternatives.
7. When no tasks exist, suggest creating one.
8. Be concise but friendly in your responses.

IMPORTANT:
- You can only manage tasks for the current authenticated user.
- Always be helpful and guide users on how to use the task management features.
- If a request is ambiguous, ask clarifying questions before taking action.
- For task creation, a valid title should be descriptive enough to understand what needs to be done.
"""


class ProcessMessageResult:
    """Result of processing a chat message through the AI agent."""
    def __init__(
        self,
        response_text: str,
        tool_calls: Optional[List[ToolCallInfo]] = None,
        conversation_id: str = "",
    ):
        self.response_text = response_text
        self.tool_calls = tool_calls or []
        self.conversation_id = conversation_id


class ChatService:
    """Service for conversation and message management."""

    def __init__(self, db: Session):
        self.db = db

    def create_conversation(self, user_id: str, title: Optional[str] = None) -> Conversation:
        """Create a new conversation for a user."""
        conversation = Conversation(
            user_id=user_id,
            title=title,
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """Get a conversation by ID, ensuring it belongs to the user."""
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        return self.db.exec(statement).first()

    def get_or_create_conversation(
        self, user_id: str, conversation_id: Optional[str] = None
    ) -> Conversation:
        """Get existing conversation or create a new one."""
        if conversation_id:
            conversation = self.get_conversation(conversation_id, user_id)
            if conversation:
                return conversation

        # Create new conversation
        return self.create_conversation(user_id)

    def add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        tool_calls: Optional[List[ToolCallInfo]] = None,
    ) -> Message:
        """Add a message to a conversation."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=json.dumps([tc.model_dump() for tc in tool_calls]) if tool_calls else None,
        )
        self.db.add(message)

        # Update conversation's updated_at timestamp
        conversation = self.db.exec(
            select(Conversation).where(Conversation.id == conversation_id)
        ).first()
        if conversation:
            conversation.updated_at = datetime.utcnow()

            # Auto-generate title from first user message if no title exists
            if not conversation.title and role == MessageRole.user:
                conversation.title = self._generate_title(content)

            self.db.add(conversation)

        self.db.commit()
        self.db.refresh(message)
        return message

    def _generate_title(self, first_message: str) -> str:
        """Generate a conversation title from the first user message."""
        # Take first 50 chars, truncate at last complete word
        max_length = 50
        if len(first_message) <= max_length:
            return first_message.strip()

        truncated = first_message[:max_length]
        last_space = truncated.rfind(" ")
        if last_space > 20:  # Only truncate at word if reasonable length remains
            truncated = truncated[:last_space]

        return truncated.strip() + "..."

    def get_messages(
        self,
        conversation_id: str,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[MessageRead]:
        """Get messages for a conversation with pagination."""
        # First verify the conversation belongs to the user
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return []

        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        messages = self.db.exec(statement).all()

        return [self._message_to_read(msg) for msg in messages]

    def get_recent_messages(
        self, conversation_id: str, user_id: str, count: int = 20
    ) -> List[MessageRead]:
        """Get the most recent messages for context (ordered oldest to newest)."""
        # First verify the conversation belongs to the user
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return []

        # Get the most recent messages, ordered by created_at desc, then reverse
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(count)
        )
        messages = list(self.db.exec(statement).all())
        messages.reverse()  # Now oldest to newest

        return [self._message_to_read(msg) for msg in messages]

    def get_user_conversations(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> List[ConversationRead]:
        """Get all conversations for a user, ordered by most recent activity."""
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        conversations = self.db.exec(statement).all()

        return [
            ConversationRead(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
            )
            for conv in conversations
        ]

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation and all its messages."""
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False

        # Delete all messages in the conversation first
        messages = self.db.exec(
            select(Message).where(Message.conversation_id == conversation_id)
        ).all()
        for message in messages:
            self.db.delete(message)

        # Delete the conversation
        self.db.delete(conversation)
        self.db.commit()
        return True

    def _message_to_read(self, message: Message) -> MessageRead:
        """Convert Message model to MessageRead schema."""
        tool_calls = None
        if message.tool_calls:
            try:
                tool_calls_data = json.loads(message.tool_calls)
                tool_calls = [ToolCallInfo(**tc) for tc in tool_calls_data]
            except (json.JSONDecodeError, TypeError):
                tool_calls = None

        return MessageRead(
            id=message.id,
            role=message.role,
            content=message.content,
            tool_calls=tool_calls,
            created_at=message.created_at,
        )

    def _create_tools_for_user(self, user_id: str) -> List:
        """Create function tools bound to the current user context."""
        task_service = TaskService(self.db)

        @function_tool
        def add_task(
            title: str,
            description: Optional[str] = None,
            priority: str = "Medium",
            tags: Optional[List[str]] = None,
        ) -> Dict[str, Any]:
            """
            Create a new task for the user.

            Args:
                title: The title of the task (required, should be descriptive)
                description: Optional detailed description of the task
                priority: Task priority - must be "High", "Medium", or "Low" (default: Medium)
                tags: Optional list of tags to categorize the task

            Returns:
                Dict with success status, task_id, title, and message
            """
            try:
                task = task_service.create_task(
                    user_id=user_id,
                    title=title,
                    description=description,
                    priority=priority,
                    tags=tags,
                )
                return {
                    "success": True,
                    "task_id": task.id,
                    "title": task.title,
                    "priority": task.priority,
                    "message": f"Task '{title}' created successfully with {priority} priority."
                }
            except ValueError as e:
                return {
                    "success": False,
                    "task_id": None,
                    "title": title,
                    "message": str(e)
                }
            except Exception as e:
                return {
                    "success": False,
                    "task_id": None,
                    "title": title,
                    "message": f"Failed to create task: {str(e)}"
                }

        @function_tool
        def list_tasks(
            completed: Optional[bool] = None,
            priority: Optional[str] = None,
            tags: Optional[List[str]] = None,
        ) -> Dict[str, Any]:
            """
            List all tasks for the user with optional filters.

            Args:
                completed: Filter by completion status (True for completed, False for incomplete, None for all)
                priority: Filter by priority level ("High", "Medium", or "Low")
                tags: Filter by tags (tasks must have all specified tags)

            Returns:
                Dict with success status, list of tasks, count, and message
            """
            try:
                tasks = task_service.get_tasks(
                    user_id=user_id,
                    completed=completed,
                    priority=priority,
                    tags=tags,
                )
                tasks_list = [
                    {
                        "id": t.id,
                        "title": t.title,
                        "completed": t.completed,
                        "priority": t.priority,
                        "tags": t.tags if t.tags else [],
                    }
                    for t in tasks
                ]
                return {
                    "success": True,
                    "tasks": tasks_list,
                    "count": len(tasks_list),
                    "message": f"Found {len(tasks_list)} task(s)."
                }
            except Exception as e:
                return {
                    "success": False,
                    "tasks": [],
                    "count": 0,
                    "message": f"Failed to list tasks: {str(e)}"
                }

        @function_tool
        def complete_task(task_identifier: str) -> Dict[str, Any]:
            """
            Mark a task as complete.

            Args:
                task_identifier: The task ID (number) or partial title to match

            Returns:
                Dict with success status, task_id if found, and message
            """
            try:
                # Try to parse as ID first
                task_id = None
                try:
                    task_id = int(task_identifier)
                except ValueError:
                    pass

                if task_id:
                    # Find by ID
                    result = task_service.update_task(
                        user_id=user_id,
                        task_id=task_id,
                        completed=True,
                    )
                    if result:
                        return {
                            "success": True,
                            "task_id": result.id,
                            "message": f"Task '{result.title}' marked as complete."
                        }
                    else:
                        return {
                            "success": False,
                            "task_id": None,
                            "message": f"Task with ID {task_id} not found."
                        }
                else:
                    # Find by title match
                    task = task_service.find_task_by_title(user_id, task_identifier)
                    if task:
                        result = task_service.update_task(
                            user_id=user_id,
                            task_id=task.id,
                            completed=True,
                        )
                        return {
                            "success": True,
                            "task_id": task.id,
                            "message": f"Task '{task.title}' marked as complete."
                        }
                    else:
                        return {
                            "success": False,
                            "task_id": None,
                            "message": f"No task found matching '{task_identifier}'."
                        }
            except Exception as e:
                return {
                    "success": False,
                    "task_id": None,
                    "message": f"Failed to complete task: {str(e)}"
                }

        @function_tool
        def update_task(
            task_identifier: str,
            title: Optional[str] = None,
            description: Optional[str] = None,
            priority: Optional[str] = None,
            tags: Optional[List[str]] = None,
        ) -> Dict[str, Any]:
            """
            Update an existing task.

            Args:
                task_identifier: The task ID (number) or partial title to match
                title: New title for the task (optional)
                description: New description for the task (optional)
                priority: New priority - "High", "Medium", or "Low" (optional)
                tags: New list of tags - replaces existing tags (optional)

            Returns:
                Dict with success status, task_id if found, and message
            """
            try:
                # Try to parse as ID first
                task_id = None
                try:
                    task_id = int(task_identifier)
                except ValueError:
                    pass

                target_task = None
                if task_id:
                    target_task = task_service.get_task_by_id(user_id, task_id)
                else:
                    target_task_raw = task_service.find_task_by_title(user_id, task_identifier)
                    if target_task_raw:
                        target_task = task_service.get_task_by_id(user_id, target_task_raw.id)

                if not target_task:
                    return {
                        "success": False,
                        "task_id": None,
                        "message": f"No task found matching '{task_identifier}'."
                    }

                result = task_service.update_task(
                    user_id=user_id,
                    task_id=target_task.id,
                    title=title,
                    description=description,
                    priority=priority,
                    tags=tags,
                )

                if result:
                    changes = []
                    if title:
                        changes.append(f"title to '{title}'")
                    if priority:
                        changes.append(f"priority to {priority}")
                    if tags is not None:
                        changes.append(f"tags to {tags}")
                    if description:
                        changes.append("description updated")

                    return {
                        "success": True,
                        "task_id": result.id,
                        "message": f"Task updated: {', '.join(changes) if changes else 'no changes made'}."
                    }
                else:
                    return {
                        "success": False,
                        "task_id": None,
                        "message": "Failed to update task."
                    }
            except ValueError as e:
                return {
                    "success": False,
                    "task_id": None,
                    "message": str(e)
                }
            except Exception as e:
                return {
                    "success": False,
                    "task_id": None,
                    "message": f"Failed to update task: {str(e)}"
                }

        @function_tool
        def delete_task(task_identifier: str, confirmed: bool = False) -> Dict[str, Any]:
            """
            Delete a task. Requires confirmation.

            IMPORTANT: Always ask the user to confirm deletion before calling this.
            Only call with confirmed=True after the user explicitly says yes.

            Args:
                task_identifier: The task ID (number) or partial title to match
                confirmed: Must be True to actually delete. If False, returns confirmation request.

            Returns:
                Dict with success status and message
            """
            if not confirmed:
                return {
                    "success": False,
                    "requires_confirmation": True,
                    "message": "Please confirm you want to delete this task. Say 'yes' or 'confirm' to proceed."
                }

            try:
                # Try to parse as ID first
                task_id = None
                try:
                    task_id = int(task_identifier)
                except ValueError:
                    pass

                target_task = None
                if task_id:
                    target_task = task_service.get_task_by_id(user_id, task_id)
                else:
                    target_task_raw = task_service.find_task_by_title(user_id, task_identifier)
                    if target_task_raw:
                        target_task = task_service.get_task_by_id(user_id, target_task_raw.id)

                if not target_task:
                    return {
                        "success": False,
                        "message": f"No task found matching '{task_identifier}'."
                    }

                task_title = target_task.title
                deleted = task_service.delete_task(user_id, target_task.id)

                if deleted:
                    return {
                        "success": True,
                        "message": f"Task '{task_title}' has been deleted."
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to delete task."
                    }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Failed to delete task: {str(e)}"
                }

        return [add_task, list_tasks, complete_task, update_task, delete_task]

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
    ) -> ProcessMessageResult:
        """
        Process a user message through the AI agent.

        Args:
            user_id: The authenticated user's ID
            message: The user's message text
            conversation_id: Optional existing conversation ID

        Returns:
            ProcessMessageResult with response text and tool calls
        """
        # Ensure GEMINI_API_KEY is set
        if not GEMINI_API_KEY:
            return ProcessMessageResult(
                response_text="I'm sorry, but the AI service is not configured. Please contact support.",
                tool_calls=[],
                conversation_id=conversation_id or "",
            )

        # Configure OpenAI Agents SDK to use Gemini's OpenAI-compatible endpoint
        gemini_client = AsyncOpenAI(
            api_key=GEMINI_API_KEY,
            base_url=GEMINI_BASE_URL,
        )

        # Set as default client for the agents SDK
        set_default_openai_client(gemini_client)

        # Create model - use chat completions wrapper if available
        if HAS_CHAT_COMPLETIONS_MODEL:
            gemini_model = OpenAIChatCompletionsModel(
                model=GEMINI_MODEL,
                openai_client=gemini_client,
            )
        else:
            # Fallback: just use model name string (relies on default client)
            gemini_model = GEMINI_MODEL

        # Get or create conversation
        conversation = self.get_or_create_conversation(user_id, conversation_id)

        # Store user message
        self.add_message(
            conversation_id=conversation.id,
            role=MessageRole.user,
            content=message,
        )

        # Get recent conversation history for context
        recent_messages = self.get_recent_messages(conversation.id, user_id, count=20)

        # Build conversation history for the agent
        history = []
        for msg in recent_messages[:-1]:  # Exclude the message we just added
            history.append({
                "role": msg.role.value,
                "content": msg.content,
            })

        # Create tools bound to this user's context
        tools = self._create_tools_for_user(user_id)

        # Create the agent with Gemini model (using chat completions wrapper)
        agent = Agent(
            name="Todo Assistant",
            instructions=AGENT_INSTRUCTIONS,
            tools=tools,
            model=gemini_model,  # Use Gemini model via OpenAI-compatible chat completions
        )

        try:
            # Run the agent with the message
            print(f"[DEBUG] Running agent with model: {GEMINI_MODEL}")
            print(f"[DEBUG] Base URL: {GEMINI_BASE_URL}")
            print(f"[DEBUG] Using OpenAIChatCompletionsModel: {HAS_CHAT_COMPLETIONS_MODEL}")
            print(f"[DEBUG] Model type: {type(gemini_model)}")

            # Quick test: verify the Gemini client works directly
            try:
                test_response = await gemini_client.chat.completions.create(
                    model=GEMINI_MODEL,
                    messages=[{"role": "user", "content": "Say 'test ok' in 2 words"}],
                    max_tokens=10
                )
                print(f"[DEBUG] Direct Gemini test successful: {test_response.choices[0].message.content}")
            except Exception as test_err:
                print(f"[DEBUG] Direct Gemini test FAILED: {test_err}")

            result: RunResult = await Runner.run(
                agent,
                message,
                context={"conversation_history": history},
            )

            # Extract the response
            response_text = result.final_output or "I processed your request."

            # Extract tool calls from the result
            tool_calls = []
            if hasattr(result, 'new_items') and result.new_items:
                for item in result.new_items:
                    if hasattr(item, 'call') and hasattr(item, 'output'):
                        tool_call_info = ToolCallInfo(
                            tool_name=item.call.name if hasattr(item.call, 'name') else str(item.call),
                            arguments=item.call.arguments if hasattr(item.call, 'arguments') else {},
                            result=item.output if isinstance(item.output, dict) else {"result": str(item.output)},
                        )
                        tool_calls.append(tool_call_info)

            # Store assistant response
            self.add_message(
                conversation_id=conversation.id,
                role=MessageRole.assistant,
                content=response_text,
                tool_calls=tool_calls if tool_calls else None,
            )

            return ProcessMessageResult(
                response_text=response_text,
                tool_calls=tool_calls,
                conversation_id=conversation.id,
            )

        except Exception as e:
            # Log detailed error for debugging
            import traceback
            print(f"[ERROR] Agent execution failed: {str(e)}")
            print(f"[ERROR] Full traceback:\n{traceback.format_exc()}")

            error_message = f"I encountered an error processing your request. Please try again or use the traditional task interface. Error: {str(e)}"

            # Store error response
            self.add_message(
                conversation_id=conversation.id,
                role=MessageRole.assistant,
                content=error_message,
            )

            return ProcessMessageResult(
                response_text=error_message,
                tool_calls=[],
                conversation_id=conversation.id,
            )
