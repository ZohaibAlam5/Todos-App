"""
TaskFlow MCP Server
A standalone MCP (Model Context Protocol) tool server for AI agents.
Provides task management tools that can be used by external AI clients.
"""

import os
from datetime import datetime
from typing import Optional, List
from contextlib import asynccontextmanager
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import httpx

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
MCP_PORT = int(os.getenv("MCP_PORT", "8001"))


# Pydantic models for tool schemas
class ToolSchema(BaseModel):
    name: str
    description: str
    parameters: dict


class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: dict
    auth_token: Optional[str] = None


class ToolCallResponse(BaseModel):
    success: bool
    result: dict
    error: Optional[str] = None


# Available tools
TOOLS = [
    ToolSchema(
        name="add_task",
        description="Create a new task for the user",
        parameters={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "The title of the task (required)"},
                "description": {"type": "string", "description": "Optional detailed description"},
                "priority": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"], "default": "MEDIUM"},
            },
            "required": ["title"]
        }
    ),
    ToolSchema(
        name="list_tasks",
        description="List all tasks for the user with optional filters",
        parameters={
            "type": "object",
            "properties": {
                "completed": {"type": "boolean", "description": "Filter by completion status"},
            },
            "required": []
        }
    ),
    ToolSchema(
        name="complete_task",
        description="Mark a task as complete",
        parameters={
            "type": "object",
            "properties": {
                "task_identifier": {"type": "string", "description": "Task ID or partial title"},
            },
            "required": ["task_identifier"]
        }
    ),
    ToolSchema(
        name="update_task",
        description="Update an existing task",
        parameters={
            "type": "object",
            "properties": {
                "task_identifier": {"type": "string", "description": "Task ID or partial title"},
                "title": {"type": "string", "description": "New title"},
                "description": {"type": "string", "description": "New description"},
                "priority": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
            },
            "required": ["task_identifier"]
        }
    ),
    ToolSchema(
        name="delete_task",
        description="Delete a task (requires confirmation)",
        parameters={
            "type": "object",
            "properties": {
                "task_identifier": {"type": "string", "description": "Task ID or partial title"},
                "confirmed": {"type": "boolean", "default": False},
            },
            "required": ["task_identifier"]
        }
    ),
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print(f"MCP Server starting on port {MCP_PORT}...")
    print(f"Backend URL: {BACKEND_URL}")
    yield
    print("MCP Server shutting down...")


app = FastAPI(
    title="TaskFlow MCP Server",
    description="MCP tool server for TaskFlow task management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "service": "TaskFlow MCP Server",
        "version": "1.0.0",
        "tools_available": len(TOOLS)
    }


@app.get("/health")
def health_check(full: Optional[str] = None):
    """
    Health check endpoint for Kubernetes probes.

    - GET /health: Basic liveness check
    - GET /health?full=1: Full readiness check with backend connectivity
    """
    response = {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    if full == "1":
        checks = {}
        try:
            # Check backend connectivity
            with httpx.Client(timeout=5.0) as client:
                backend_response = client.get(f"{BACKEND_URL}/health")
                if backend_response.status_code == 200:
                    checks["backend"] = "connected"
                else:
                    checks["backend"] = "unhealthy"
                    response["status"] = "unhealthy"
        except Exception:
            checks["backend"] = "unreachable"
            response["status"] = "unhealthy"

        response["checks"] = checks

        if response["status"] == "unhealthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=response
            )

    return response


@app.get("/tools")
def list_tools() -> List[ToolSchema]:
    """List all available tools."""
    return TOOLS


@app.get("/tools/{tool_name}")
def get_tool(tool_name: str) -> ToolSchema:
    """Get a specific tool schema by name."""
    for tool in TOOLS:
        if tool.name == tool_name:
            return tool
    raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")


@app.post("/tools/call")
async def call_tool(request: ToolCallRequest) -> ToolCallResponse:
    """
    Execute a tool call by proxying to the backend API.

    This endpoint allows AI agents to call task management tools.
    Authentication token must be provided for authenticated operations.
    """
    tool_name = request.tool_name
    arguments = request.arguments
    auth_token = request.auth_token

    # Validate tool exists
    tool_exists = any(t.name == tool_name for t in TOOLS)
    if not tool_exists:
        return ToolCallResponse(
            success=False,
            result={},
            error=f"Tool '{tool_name}' not found"
        )

    # Build headers
    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if tool_name == "add_task":
                response = await client.post(
                    f"{BACKEND_URL}/tasks",
                    json=arguments,
                    headers=headers
                )
            elif tool_name == "list_tasks":
                params = {}
                if arguments.get("completed") is not None:
                    params["completed"] = str(arguments["completed"]).lower()
                response = await client.get(
                    f"{BACKEND_URL}/tasks",
                    params=params,
                    headers=headers
                )
            elif tool_name == "complete_task":
                task_id = arguments.get("task_identifier")
                response = await client.put(
                    f"{BACKEND_URL}/tasks/{task_id}",
                    json={"completed": True},
                    headers=headers
                )
            elif tool_name == "update_task":
                task_id = arguments.pop("task_identifier", None)
                response = await client.put(
                    f"{BACKEND_URL}/tasks/{task_id}",
                    json=arguments,
                    headers=headers
                )
            elif tool_name == "delete_task":
                task_id = arguments.get("task_identifier")
                confirmed = arguments.get("confirmed", False)
                if not confirmed:
                    return ToolCallResponse(
                        success=False,
                        result={"requires_confirmation": True},
                        error="Deletion requires confirmation. Set confirmed=true to proceed."
                    )
                response = await client.delete(
                    f"{BACKEND_URL}/tasks/{task_id}",
                    headers=headers
                )
            else:
                return ToolCallResponse(
                    success=False,
                    result={},
                    error=f"Tool '{tool_name}' not implemented"
                )

            if response.status_code >= 400:
                return ToolCallResponse(
                    success=False,
                    result=response.json() if response.content else {},
                    error=f"Backend returned status {response.status_code}"
                )

            return ToolCallResponse(
                success=True,
                result=response.json() if response.content else {"message": "Success"}
            )

    except httpx.TimeoutException:
        return ToolCallResponse(
            success=False,
            result={},
            error="Backend request timed out"
        )
    except Exception as e:
        return ToolCallResponse(
            success=False,
            result={},
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=MCP_PORT)
