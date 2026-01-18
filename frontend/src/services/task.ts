// Task service for the Todo application
import { Task, TaskCreateRequest, TaskUpdateRequest, ApiResponse } from '@/types';

class TaskService {
  private baseUrl: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Normalize priority from backend (uppercase) to frontend format (title case)
  private normalizePriority(priority: string): 'High' | 'Medium' | 'Low' {
    const priorityMap: Record<string, 'High' | 'Medium' | 'Low'> = {
      'HIGH': 'High',
      'MEDIUM': 'Medium',
      'LOW': 'Low',
      'High': 'High',
      'Medium': 'Medium',
      'Low': 'Low'
    };
    return priorityMap[priority] || 'Medium';
  }

  // Convert priority from frontend format (title case) to backend format (uppercase)
  private toBackendPriority(priority: string): string {
    const priorityMap: Record<string, string> = {
      'High': 'HIGH',
      'Medium': 'MEDIUM',
      'Low': 'LOW',
      'HIGH': 'HIGH',
      'MEDIUM': 'MEDIUM',
      'LOW': 'LOW'
    };
    return priorityMap[priority] || 'MEDIUM';
  }

  // Transform task to normalize priority
  private normalizeTask(task: Task): Task {
    return {
      ...task,
      priority: this.normalizePriority(task.priority)
    };
  }

  // Transform request data to use backend priority format
  private toBackendTaskData(taskData: TaskCreateRequest | TaskUpdateRequest): TaskCreateRequest | TaskUpdateRequest {
    if (taskData.priority) {
      return { ...taskData, priority: this.toBackendPriority(taskData.priority) as 'High' | 'Medium' | 'Low' };
    }
    return taskData;
  }

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
      // Normalize priorities for all tasks
      const normalizedTasks = tasks.map((task: Task) => this.normalizeTask(task));
      return { data: normalizedTasks, success: true };
    } catch (error) {
      console.error('Error fetching tasks:', error);
      return { error: error instanceof Error ? error.message : 'Unknown error', success: false };
    }
  }

  async createTask(taskData: TaskCreateRequest): Promise<ApiResponse<Task>> {
    try {
      const backendData = this.toBackendTaskData(taskData);
      const response = await fetch(`${this.baseUrl}/tasks`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(backendData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create task');
      }

      const task = await response.json();
      return { data: this.normalizeTask(task), success: true };
    } catch (error) {
      return { error: error instanceof Error ? error.message : 'Unknown error', success: false };
    }
  }

  async updateTask(id: number, taskData: TaskUpdateRequest): Promise<ApiResponse<Task>> {
    try {
      const backendData = this.toBackendTaskData(taskData);
      const response = await fetch(`${this.baseUrl}/tasks/${id}`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(backendData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update task');
      }

      const task = await response.json();
      return { data: this.normalizeTask(task), success: true };
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
      return { data: this.normalizeTask(task), success: true };
    } catch (error) {
      return { error: error instanceof Error ? error.message : 'Unknown error', success: false };
    }
  }
}

export const taskService = new TaskService();