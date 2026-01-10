// Shared types for the Todo application

export interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'High' | 'Medium' | 'Low';
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface TaskCreateRequest {
  title: string;
  description?: string;
  priority?: 'High' | 'Medium' | 'Low';
  tags?: string[];
}

export interface TaskUpdateRequest {
  title?: string;
  description?: string;
  priority?: 'High' | 'Medium' | 'Low';
  tags?: string[];
  completed?: boolean;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  token_type: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  success: boolean;
}