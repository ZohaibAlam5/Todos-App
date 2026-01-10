'use client';

import React from 'react';
import Link from 'next/link';
import ThemeToggle from '@/components/ThemeToggle';

export default function HomePage() {
  return (
    // Outer Background
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gray-50 dark:bg-gray-950 transition-colors duration-500 p-4">
      
      {/* --- Ambient Background Glow --- */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/10 dark:bg-indigo-500/10 rounded-full blur-[128px] animate-pulse" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 dark:bg-purple-500/10 rounded-full blur-[128px] animate-pulse delay-1000" />

      {/* --- Main Container Wrapper --- */}
      {/* RESPONSIVE UPDATES:
          1. max-w-md: Default for mobile (phones).
          2. md:max-w-xl: On Tablets (iPad Mini/Pro), increases width to 36rem (approx 576px).
          3. w-full: Ensures it takes available space up to the max-width.
      */}
      <div className="relative z-10 w-full max-w-md md:max-w-xl transition-all duration-300">

        {/* === LAYER 1: THE STRONG GLOW (Behind) === */}
        <div className="absolute -inset-7.5 rounded-[5rem] blur-3xl opacity-60 dark:opacity-100 -z-10 overflow-hidden transition-opacity duration-500">
             <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[200%] aspect-square animate-[spin_3s_linear_infinite] bg-[conic-gradient(from_90deg_at_50%_50%,#6366f1_0%,#a855f7_50%,#ec4899_100%)]" />
        </div>

        {/* === LAYER 2: THE SHARP BORDER STRIP (Middle) === */}
        <div className="relative rounded-[3rem] overflow-hidden p-0.5 shadow-2xl z-10">
            
            {/* Spinning Square Gradient */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[200%] aspect-square animate-[spin_3s_linear_infinite] bg-[conic-gradient(from_90deg_at_50%_50%,#6366f1_0%,#a855f7_50%,#ec4899_100%)] -z-10" />

            {/* === LAYER 3: THE CONTENT (Top) === */}
            {/* RESPONSIVE PADDING:
                - p-8: Mobile padding.
                - md:p-14: Increased padding for iPads to make use of the wider container.
            */}
            <div className="relative h-full w-full bg-white dark:bg-gray-950 rounded-[calc(3rem-2px)] p-8 md:p-14 overflow-hidden backdrop-blur-xl border border-gray-100 dark:border-gray-800/50 transition-colors duration-500">
            
              {/* Internal shine (Dark mode only) */}
              <div className="absolute inset-0 bg-linear-to-br from-white/20 to-transparent dark:from-white/5 dark:to-transparent pointer-events-none mix-blend-overlay opacity-0 dark:opacity-100 transition-opacity duration-500" />

              {/* Theme Toggle */}
              <div className="absolute top-6 right-6 z-20">
                <ThemeToggle />
              </div>

              <div className="relative z-10 flex flex-col items-center text-center mt-4">
                {/* Typography */}
                <h1 className="text-5xl md:text-7xl font-black tracking-tighter mb-4 md:mb-6">
                  <span className="bg-linear-to-r from-indigo-600 via-purple-600 to-pink-600 dark:from-indigo-400 dark:via-purple-400 dark:to-pink-400 bg-clip-text text-transparent drop-shadow-sm pr-1">
                    TaskFlow
                  </span>
                </h1>
                
                <p className="text-lg md:text-xl font-medium text-gray-600 dark:text-gray-300/80 mb-10 md:mb-12 max-w-md leading-relaxed transition-colors duration-500">
                  Streamline your reality. <br /> Manage tasks efficiently.
                </p>

                {/* Action Buttons */}
                <div className="w-full flex flex-col gap-4">
                  <Link
                    href="/login"
                    className="group relative w-full flex justify-center items-center py-4 md:py-5 px-6 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-lg md:text-xl rounded-full transition-all duration-300 shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_30px_rgba(79,70,229,0.5)] hover:scale-[1.02]"
                  >
                    Login
                    <svg className="w-5 h-5 md:w-6 md:h-6 ml-2 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path></svg>
                  </Link>

                  <Link
                    href="/register"
                    className="group w-full flex justify-center items-center py-4 md:py-5 px-6 bg-gray-50 dark:bg-white/5 text-gray-800 dark:text-white border-2 border-gray-200 dark:border-gray-700/50 font-bold text-lg md:text-xl rounded-full hover:bg-gray-100 dark:hover:bg-white/10 transition-all duration-300 hover:scale-[1.02]"
                  >
                    Register
                  </Link>
                </div>
              </div>
            </div>
        </div>
      </div>
      
    </div>
  );
}