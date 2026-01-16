// Chat service for the AI Chatbot feature
import {
  ChatRequest,
  ChatResponse,
  Conversation,
  Message,
  ApiResponse
} from '@/types';

class ChatService {
  private baseUrl: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('token');
    if (!token || token === 'undefined') {
      throw new Error('No authentication token found or token is invalid');
    }
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
  }

  async sendMessage(
    message: string,
    conversationId?: string
  ): Promise<ApiResponse<ChatResponse>> {
    try {
      const request: ChatRequest = {
        message,
        conversation_id: conversationId,
      };

      const response = await fetch(`${this.baseUrl}/api/chat`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send message');
      }

      const chatResponse = await response.json();
      return { data: chatResponse, success: true };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Unknown error',
        success: false
      };
    }
  }

  async getConversations(
    limit: number = 20,
    offset: number = 0
  ): Promise<ApiResponse<Conversation[]>> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/chat/conversations?limit=${limit}&offset=${offset}`,
        {
          method: 'GET',
          headers: this.getAuthHeaders(),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch conversations');
      }

      const conversations = await response.json();
      return { data: conversations, success: true };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Unknown error',
        success: false
      };
    }
  }

  async getConversation(
    conversationId: string
  ): Promise<ApiResponse<Conversation & { messages: Message[] }>> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/chat/conversations/${conversationId}`,
        {
          method: 'GET',
          headers: this.getAuthHeaders(),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch conversation');
      }

      const conversation = await response.json();
      return { data: conversation, success: true };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Unknown error',
        success: false
      };
    }
  }

  async deleteConversation(conversationId: string): Promise<ApiResponse<void>> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/chat/conversations/${conversationId}`,
        {
          method: 'DELETE',
          headers: this.getAuthHeaders(),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete conversation');
      }

      return { success: true };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Unknown error',
        success: false
      };
    }
  }
}

export const chatService = new ChatService();
