'use client';

import React from 'react';
import AuthForm from '@/components/AuthForm';
import ThemeToggle from '@/components/ThemeToggle';

export default function LoginPage() {
  return (
    // Added: bg-gray-50 dark:bg-gray-950 (Using gray-950 to match the deep dark theme)
    <div className="relative min-h-screen w-full bg-gray-50 dark:bg-gray-950 transition-colors duration-500">
      {/* Theme Toggle:
        Positioned absolutely to float on top of the AuthForm background.
        z-50 ensures it stays above the complex background elements.
      */}
      <div className="absolute top-4 right-4 z-50">
        <ThemeToggle />
      </div>

      {/* The AuthForm now handles the entire layout (Background, Split Card, Branding)
        so we just render it directly here.
      */}
      <AuthForm mode="login" />
    </div>
  );
}