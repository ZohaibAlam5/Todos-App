'use client';

import React, { useState, useEffect } from 'react';
import TodoList from '@/components/TodoList';
import { useAuth } from '@/components/AuthContext';
import ThemeToggle from '@/components/ThemeToggle';
import { useRouter } from 'next/navigation';
import { LogOut, User, AlertCircle } from 'lucide-react';
import Image from 'next/image';

export default function DashboardPage() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  // NEW: State to toggle full email view on mobile
  const [isEmailExpanded, setIsEmailExpanded] = useState(false);
  const [showAuthMessage, setShowAuthMessage] = useState(false);

  // Check authentication status on component mount
  useEffect(() => {
    if (!loading) {
      if (!user) {
        // Show authentication message for 3 seconds, then redirect
        setShowAuthMessage(true);
        const timer = setTimeout(() => {
          setShowAuthMessage(false);
          router.push('/login');
        }, 3000);

        return () => clearTimeout(timer);
      }
    }
  }, [user, loading, router]);

  // Add CSS for the progress animation
  useEffect(() => {
    const style = document.createElement('style');
    style.innerHTML = `
      @keyframes progress {
        0% { width: 0%; }
        100% { width: 100%; }
      }
      .animate-progress {
        animation: progress 3s linear forwards;
      }
    `;
    document.head.appendChild(style);

    return () => {
      document.head.removeChild(style);
    };
  }, []);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  // Show loading state while checking auth
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Show auth message if user is not authenticated
  if (showAuthMessage) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex flex-col items-center text-center">
            <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mb-4">
              <AlertCircle className="w-8 h-8 text-red-600 dark:text-red-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Authentication Required</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              You are not signed in. Redirecting to login page...
            </p>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div className="bg-red-500 h-2 rounded-full animate-progress"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Don't render anything if user is not authenticated and message is shown
  if (!user && !showAuthMessage) {
    return null;
  }

  return (
    // Outer Container: Dynamic Background
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors duration-500 relative overflow-hidden flex flex-col">
      
      {/* --- Ambient Background Glow --- */}
      <div className="absolute top-0 left-0 w-75 sm:w-125 h-75 sm:h-125 bg-indigo-500/20 dark:bg-indigo-500/10 rounded-full blur-[80px] sm:blur-[100px] animate-pulse pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-75 sm:w-125 h-75 sm:h-125 bg-purple-500/20 dark:bg-purple-500/10 rounded-full blur-[80px] sm:blur-[100px] animate-pulse delay-1000 pointer-events-none" />

      {/* --- Header / Navigation --- */}
      <div className="container mx-auto px-4 pt-4 sm:pt-6 pb-2 sm:pb-4 relative z-20">
        {/* Responsive Header: Stacks on mobile (flex-col), Row on Desktop (md:flex-row) */}
        <header className="bg-white/70 dark:bg-gray-900/60 backdrop-blur-xl border border-white/20 dark:border-white/10 rounded-4xl shadow-lg px-4 sm:px-6 py-3 flex flex-col sm:flex-row justify-between items-center gap-4 transition-all duration-300">
          
          {/* Logo Section */}
          <div className="flex items-center gap-2">
            <div className="relative h-8 w-8"> {/* Set width/height here */}
              <Image 
                src="/logo.png" 
                alt="TaskFlow Logo" 
                fill 
                className="object-contain" // Keeps aspect ratio correct
              />
            </div>
            <h1 className="text-xl font-bold bg-linear-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
              TaskFlow
            </h1>
          </div>

          {/* User & Actions */}
          <div className="flex items-center gap-2 sm:gap-4 w-full sm:w-auto justify-between sm:justify-end">
            
            {/* User Email Pill (UPDATED) */}
            <div 
              onClick={() => setIsEmailExpanded(!isEmailExpanded)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-100/50 dark:bg-gray-800/50 border border-gray-200/50 dark:border-gray-700/50 text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-300 transition-all duration-300 cursor-pointer sm:cursor-default 
                ${isEmailExpanded ? 'max-w-full' : 'max-w-30'} sm:max-w-none`}
              title="Click to expand"
            >
              <User className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
              <span className={isEmailExpanded ? '' : 'truncate'}>
                {user?.email}
              </span>
            </div>

            <div className="h-6 w-px bg-gray-300 dark:bg-gray-700 mx-1 hidden sm:block" />

            <div className="flex items-center gap-2">
              <ThemeToggle />

              <button
                onClick={handleLogout}
                className="group flex items-center gap-2 px-3 sm:px-4 py-2 bg-linear-to-r from-red-500 to-pink-600 hover:from-red-400 hover:to-pink-500 text-white rounded-full text-xs sm:text-sm font-bold shadow-md transition-all hover:scale-105 hover:shadow-lg"
              >
                <span className="hidden sm:inline">Logout</span>
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </header>
      </div>

      {/* --- Main Content --- */}
      <main className="container mx-auto px-4 py-4 sm:py-6 grow relative z-10">
        <div className="w-full max-w-5xl mx-auto">
            {/* Glowing Border Container */}
            <div className="relative rounded-4xl sm:rounded-[2.5rem] overflow-hidden p-px shadow-2xl transition-all duration-300">
                <div className="absolute inset-0 bg-linear-to-r from-indigo-500/30 via-purple-500/30 to-pink-500/30 blur-xl opacity-80 dark:opacity-40" />
                
                {/* Main Card Content */}
                <div className="relative bg-white/60 dark:bg-gray-900/60 backdrop-blur-2xl rounded-4xl sm:rounded-[2.5rem] border border-white/40 dark:border-gray-800/50 p-4 sm:p-8 min-h-125 sm:min-h-150">
                    <TodoList />
                </div>
            </div>
        </div>
      </main>

      {/* --- Footer --- */}
      <footer className="relative z-10 mt-auto py-6">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm text-gray-500 dark:text-gray-500 font-medium">
            © 2026 TaskFlow. Streamlining your reality.
          </p>
        </div>
      </footer>
    </div>
  );
}