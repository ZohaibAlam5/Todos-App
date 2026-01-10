'use client';

import React from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import { Sun, Moon } from 'lucide-react'; // Assuming you have lucide-react installed

const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={`
        relative p-2.5 rounded-full transition-all duration-300 ease-in-out
        focus:outline-none focus:ring-2 focus:ring-indigo-500/50
        
        /* Light Mode Styles: Glassy White */
        bg-white/80 border border-gray-200 shadow-sm hover:shadow-md hover:bg-white
        text-amber-500
        
        /* Dark Mode Styles: Glassy Dark */
        dark:bg-gray-800/50 dark:border-gray-700/50 dark:text-indigo-400
        dark:hover:bg-gray-800 dark:hover:text-indigo-300
      `}
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      <div className="relative w-5 h-5">
        {/* Sun Icon (Shows in Light Mode) */}
        <span 
          className={`absolute inset-0 transform transition-transform duration-500 ${
            theme === 'dark' ? 'rotate-90 opacity-0 scale-50' : 'rotate-0 opacity-100 scale-100'
          }`}
        >
           <Sun className="w-5 h-5 fill-current" />
        </span>

        {/* Moon Icon (Shows in Dark Mode) */}
        <span 
          className={`absolute inset-0 transform transition-transform duration-500 ${
            theme === 'light' ? '-rotate-90 opacity-0 scale-50' : 'rotate-0 opacity-100 scale-100'
          }`}
        >
          <Moon className="w-5 h-5 fill-current" />
        </span>
      </div>
    </button>
  );
};

export default ThemeToggle;