// Frontend authentication service

export interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

class AuthService {
  private baseUrl: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  async register(email: string, password: string): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      // Removed console.error here
      throw new Error(errorData.detail || 'Registration failed');
    }

    const data = await response.json();
    return data;
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    // Removed console.log("Attempting login...")

    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        email: email,
        username: email,
        password: password
      }),
    });

    if (!response.ok) {
      let errorMessage = 'Login failed';
      let errorBody;

      try {
        errorBody = await response.json();
        // Removed console.error('❌ Login Error Body...')
        
        // Handle validation errors specifically
        if (errorBody.detail) {
          if (Array.isArray(errorBody.detail)) {
             // Extract Pydantic validation error
             errorMessage = errorBody.detail.map((e: any) => `${e.msg}`).join(', ');
          } else {
             errorMessage = errorBody.detail;
          }
        }
      } catch (e) {
        // Removed console.error('❌ Could not parse...')
        // Silently fall back to generic error
      }

      // We still THROW the error so the UI knows to show the red alert box,
      // but we removed the console logs that clutter your developer tools.
      throw new Error(errorMessage);
    }

    const data = await response.json();
    // Removed console.log("Success...")

    return {
      user: data.user,
      access_token: data.access_token,
      token_type: data.token_type
    };
  }

  async logout(): Promise<void> {
    localStorage.removeItem('token');
  }

  // --- NEW: FORGOT PASSWORD METHODS ---

  async requestPasswordReset(email: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to send reset code');
    }
  }

  async resetPassword(email: string, code: string, newPassword: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email,
        code,
        new_password: newPassword
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to reset password');
    }
  }

  async getCurrentUser(): Promise<User | null> {
    const token = this.getToken();
    if (!token) return null;

    try {
      const response = await fetch(`${this.baseUrl}/auth/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          this.logout();
        }
        return null;
      }

      const userData = await response.json();
      return {
        id: userData.id,
        email: userData.email,
        created_at: userData.created_at || userData.createdAt, 
        updated_at: userData.updated_at || userData.updatedAt
      };
    } catch (error) {
      // Removed console.error
      this.logout();
      return null;
    }
  }

  setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token);
    }
  }

  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token');
    }
    return null;
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

export const authService = new AuthService();