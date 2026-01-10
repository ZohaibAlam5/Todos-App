"use client"
import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authService, User } from '@/services/auth';
import { Loader2, Sparkles } from 'lucide-react';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (email: string, password: string) => Promise<void>;
  isAuthenticated: () => boolean;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        if (currentUser) {
          setUser(currentUser);
        }
      } catch (error) {
        console.error('Error checking auth status:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      console.log('Attempting login with email:', email);
      const response = await authService.login(email, password);
      console.log('Login response:', response);

      // Validate the response and token before storing
      if (!response.access_token) {
        throw new Error('Login response does not contain a valid access token');
      }

      // Store the token first
      authService.setToken(response.access_token);
      console.log('Token stored in localStorage:', localStorage.getItem('token')); // Debug log

      // Then refresh the user to ensure state is properly updated
      await refreshUser();
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (email: string, password: string) => {
    try {
      console.log('Attempting registration with email:', email);
      const response = await authService.register(email, password);
      console.log('Registration response:', response);

      // Validate the response and token before storing
      if (!response.access_token) {
        throw new Error('Registration response does not contain a valid access token');
      }

      // Store the token first
      authService.setToken(response.access_token);
      console.log('Token stored in localStorage:', localStorage.getItem('token')); // Debug log

      // Then refresh the user to ensure state is properly updated
      await refreshUser();
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      if (currentUser) {
        setUser(currentUser);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Error refreshing user:', error);
      setUser(null);
    }
  };

  const isAuthenticated = () => {
    return authService.isAuthenticated();
  };

  const value = {
    user,
    loading,
    login,
    logout,
    register,
    isAuthenticated,
    refreshUser
  };

  // --- FUTURISTIC GLOBAL LOADING SCREEN ---
  if (loading) {
    return (
      // FIX APPLIED HERE:
      // 1. Removed 'transition-colors duration-500' to prevent the white flash animation.
      // 2. Fixed 'z-9999' to 'z-[9999]' (Tailwind arbitrary value syntax).
      <div className="fixed inset-0 z-9999 flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-950 overflow-hidden">
        
        {/* Ambient Glows */}
        {/* Fixed w-125 to w-[500px] as 125 isn't a default Tailwind spacing unit */}
        <div className="absolute top-1/4 left-1/4 w-125 h-125 bg-indigo-500/20 dark:bg-indigo-500/10 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-125 h-125 bg-purple-500/20 dark:bg-purple-500/10 rounded-full blur-[120px] animate-pulse delay-1000" />

        {/* Central Loader Module */}
        <div className="relative z-10 flex flex-col items-center">
          
          {/* Glass Card Container */}
          <div className="relative p-8 rounded-3xl bg-white/30 dark:bg-gray-900/30 backdrop-blur-2xl border border-white/20 dark:border-white/10 shadow-2xl flex flex-col items-center gap-6">
            
            {/* Spinning Rings */}
            <div className="relative w-20 h-20 flex items-center justify-center">
               {/* Outer Ring */}
               <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-indigo-500 border-r-purple-500 animate-[spin_1.5s_linear_infinite]" />
               {/* Inner Ring */}
               <div className="absolute inset-2 rounded-full border-2 border-transparent border-t-purple-500 border-l-indigo-500 animate-[spin_2s_linear_infinite_reverse]" />
               
               {/* Center Icon */}
               <Sparkles className="w-8 h-8 text-indigo-600 dark:text-indigo-400 animate-pulse" />
            </div>

            {/* Loading Text */}
            <div className="text-center space-y-2">
              <h2 className="text-xl font-bold bg-clip-text text-transparent bg-linear-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400">
                TaskFlow
              </h2>
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <Loader2 className="w-3 h-3 animate-spin" />
                <span>Initializing System...</span>
              </div>
            </div>

          </div>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};