'use client';

import React from 'react';
import { Message, ToolCallInfo } from '@/types';
import { Terminal, CheckCircle2, ListTodo, Plus, Trash2, Edit2 } from 'lucide-react';

interface ChatMessageProps {
  message: Message;
  isLatest?: boolean;
}

export default function ChatMessage({ message, isLatest = false }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={`
        flex w-full mb-4 animate-in fade-in slide-in-from-bottom-2 duration-300
        ${isUser ? 'justify-end' : 'justify-start'}
      `}
    >
      <div
        className={`
          max-w-[85%] sm:max-w-[80%] px-5 py-3.5 rounded-2xl shadow-sm relative overflow-hidden
          ${isUser
            ? 'bg-linear-to-br from-indigo-600 to-purple-600 text-white rounded-br-none'
            : 'bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border border-gray-100 dark:border-gray-700 text-gray-800 dark:text-gray-100 rounded-bl-none'
          }
        `}
      >
        {/* Shine effect for user messages */}
        {isUser && (
           <div className="absolute inset-0 bg-white/10 opacity-0 hover:opacity-100 transition-opacity pointer-events-none" />
        )}

        {/* Message content */}
        <div className="whitespace-pre-wrap wrap-break-word text-sm md:text-base leading-relaxed">
          {message.content}
        </div>

        {/* Tool calls display */}
        {!isUser && message.tool_calls && message.tool_calls.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200/50 dark:border-gray-700/50">
            <div className="text-[10px] uppercase tracking-wider font-semibold text-gray-400 dark:text-gray-500 mb-2">
              Actions Taken
            </div>
            <div className="space-y-2">
              {message.tool_calls.map((toolCall, index) => (
                <ToolCallBadge key={index} toolCall={toolCall} />
              ))}
            </div>
          </div>
        )}

        {/* Timestamp */}
        <div
          className={`
            text-[10px] mt-1.5 text-right opacity-70
            ${isUser ? 'text-indigo-100' : 'text-gray-400'}
          `}
        >
          {formatTime(message.created_at)}
        </div>
      </div>
    </div>
  );
}

// --- TOOL BADGE SUB-COMPONENT ---

interface ToolCallBadgeProps {
  toolCall: ToolCallInfo;
}

function ToolCallBadge({ toolCall }: ToolCallBadgeProps) {
  // Mapping tool names to Icons
  const getToolIcon = (name: string) => {
    if (name.includes('add')) return <Plus className="w-3 h-3" />;
    if (name.includes('list')) return <ListTodo className="w-3 h-3" />;
    if (name.includes('complete')) return <CheckCircle2 className="w-3 h-3" />;
    if (name.includes('delete')) return <Trash2 className="w-3 h-3" />;
    if (name.includes('update')) return <Edit2 className="w-3 h-3" />;
    return <Terminal className="w-3 h-3" />;
  };

  const displayName = toolCall.tool_name.replace(/_/g, ' ');

  return (
    <div className="flex items-center gap-2 text-xs bg-gray-50 dark:bg-gray-900/50 p-1.5 rounded-lg border border-gray-100 dark:border-gray-700/50">
      <span
        className={`
          p-1 rounded-md flex items-center justify-center
          bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400
        `}
      >
        {getToolIcon(toolCall.tool_name)}
      </span>
      <span className="text-gray-600 dark:text-gray-300 capitalize font-medium flex-1">
        {displayName}
      </span>
      {toolCall.result !== undefined && toolCall.result !== null && (
        <span className="text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 px-1.5 py-0.5 rounded text-[10px] font-bold">
          DONE
        </span>
      )}
    </div>
  );
}

function formatTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return 'Just now';
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}