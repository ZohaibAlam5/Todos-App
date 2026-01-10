'use client';

import React from 'react';
import AuthForm from '@/components/AuthForm';
import ThemeToggle from '@/components/ThemeToggle';

export default function RegisterPage() {
  return (
    // Added: bg-gray-50 dark:bg-gray-950
    <div className="relative min-h-screen w-full bg-gray-50 dark:bg-gray-950 transition-colors duration-500">
      {/* Theme Toggle:
          Positioned absolutely to float on top of the AuthForm background.
          z-50 ensures it stays above the complex background elements.
      */}
      <div className="absolute top-4 right-4 z-50">
        <ThemeToggle />
      </div>

      {/* The AuthForm handles the full page layout, split design, and specific "Register" logic internally based on the mode prop */}
      <AuthForm mode="register" />
    </div>
  );
}