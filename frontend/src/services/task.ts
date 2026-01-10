// Task service for the Todo application
import { Task, TaskCreateRequest, TaskUpdateRequest, ApiResponse } from '@/types';

class TaskService {
  private baseUrl: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('token');
    console.log('Token retrieved from localStorage:', token); // Debug log
    if (!token || token === 'undefined') {
      throw new Error('No authentication token found or token is invalid');
    }
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
  }

  async getTasks(): Promise<ApiResponse<Task[]>> {
    try {
      const response = await fetch(`${this.baseUrl}/tasks`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        const errorText = await response.text(); // Get raw text in case JSON parsing fails
        try {
          const errorData = JSON.parse(errorText);
          throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        } catch (e) {
          throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
      }

      const tasks = await response.json();
      return { data: tasks, success: true };
    } catch (error) {
      console.error('Error fetching tasks:', error);
      return { error: error instanceof Error ? error.message : 'Unknown error', success: false };
    }
  }

  async createTask(taskData: TaskCreateRequest): Promise<ApiResponse<Task>> {
    try {
      const response = await fetch(`${this.baseUrl}/tasks`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(taskData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create task');
      }

      const task = await response.json();
      return { data: task, success: true };
    } catch (error) {
      return { error: error instanceof Error ? error.message : 'Unknown error', success: false };
    }
  }

  async updateTask(id: number, taskData: TaskUpdateRequest): Promise<ApiResponse<Task>> {
    try {
      const response = await fetch(`${this.baseUrl}/tasks/${id}`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(taskData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update task');
      }

      const task = await response.json();
      return { data: task, success: true };
    } catch (error) {
      return { error: error instanceof Error ? error.message : 'Unknown error', success: false };
    }
  }

  async deleteTask(id: number): Promise<ApiResponse<boolean>> {
    try {
      const response = await fetch(`${this.baseUrl}/tasks/${id}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete task');
      }

      return { data: true, success: true };
    } catch (error) {
      return { error: error instanceof Error ? error.message : 'Unknown error', success: false };
    }
  }

  async toggleTaskCompletion(id: number): Promise<ApiResponse<Task>> {
    try {
      // First get the current task to get its current completion status
      const currentTaskResponse = await this.getTask(id);
      if (!currentTaskResponse.success || !currentTaskResponse.data) {
        throw new Error('Failed to fetch current task');
      }

      const currentTask = currentTaskResponse.data;
      const updatedTask = await this.updateTask(id, {
        completed: !currentTask.completed,
      });

      return updatedTask;
    } catch (error) {
      return { error: error instanceof Error ? error.message : 'Unknown error', success: false };
    }
  }

  private async getTask(id: number): Promise<ApiResponse<Task>> {
    try {
      const response = await fetch(`${this.baseUrl}/tasks/${id}`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch task');
      }

      const task = await response.json();
      return { data: task, success: true };
    } catch (error) {
      return { error: error instanceof Error ? error.message : 'Unknown error', success: false };
    }
  }
}

export const taskService = new TaskService();