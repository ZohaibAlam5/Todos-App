'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, AlertCircle } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

export default function ChatInput({
  onSend,
  disabled = false,
  placeholder = 'Type a message...',
  maxLength = 2000,
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [charCount, setCharCount] = useState(0);
  const [hasInteracted, setHasInteracted] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Only auto-resize after user has started typing
  useEffect(() => {
    if (textareaRef.current && hasInteracted) {
      // Reset height to auto to get accurate scrollHeight
      textareaRef.current.style.height = 'auto';
      // Calculate new height, capped at 120px
      const newHeight = Math.min(textareaRef.current.scrollHeight, 120);
      textareaRef.current.style.height = `${newHeight}px`;
    }
  }, [message, hasInteracted]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedMessage = message.trim();
    if (!trimmedMessage || disabled) return;
    onSend(trimmedMessage);
    setMessage('');
    setCharCount(0);
    setHasInteracted(false);
    if (textareaRef.current) textareaRef.current.style.height = '44px';
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    if (value.length <= maxLength) {
      if (!hasInteracted) setHasInteracted(true);
      setMessage(value);
      setCharCount(value.length);
    }
  };

  const isOverLimit = charCount >= maxLength * 0.9;
  const isEmpty = message.trim().length === 0;

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2 w-full">
      {/* FIX 1: Changed items-end to items-center for vertical centering */}
      <div className="relative flex items-center gap-3 p-2 bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700 rounded-3xl transition-colors focus-within:border-indigo-400 dark:focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-500/20">
        
        <textarea
          ref={textareaRef}
          value={message}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className="w-full pl-4 py-2.5 bg-transparent border-none outline-none text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:ring-0 focus:outline-none resize-none text-sm md:text-base scrollbar-hide leading-normal"
          style={{ height: '44px', maxHeight: '120px', overflow: hasInteracted && message ? 'auto' : 'hidden' }}
        />

        {/* Character Count */}
        {charCount > 0 && (
           <div className={`absolute right-16 bottom-3 text-[10px] font-medium transition-colors ${isOverLimit ? 'text-red-500' : 'text-gray-400'}`}>
             {charCount}/{maxLength}
           </div>
        )}

        {/* Send Button */}
        <button
          type="submit"
          disabled={disabled || isEmpty}
          className={`
            p-3 rounded-full shrink-0 transition-all duration-200 flex items-center justify-center
            ${disabled || isEmpty
              ? 'bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
              : 'bg-linear-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/30 hover:scale-105 active:scale-95'
            }
          `}
        >
          {disabled ? (
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </div>

      {isEmpty && message.length > 0 && (
        <div className="flex items-center gap-1 text-xs text-red-500 px-2 animate-pulse">
          <AlertCircle className="w-3 h-3" />
          <span>Message cannot be empty</span>
        </div>
      )}
    </form>
  );
}