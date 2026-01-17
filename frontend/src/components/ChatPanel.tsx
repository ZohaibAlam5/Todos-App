'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { Message, ChatResponse, Conversation } from '@/types';
import { chatService } from '@/services/chat';
import ChatInput from './ChatInput';
import ChatMessage from './ChatMessage';
import { MessageSquare, X, RefreshCw, Plus, History, Sparkles, ChevronDown, Trash2, AlertTriangle } from 'lucide-react';

interface ChatPanelProps {
  onTaskUpdate?: () => void;
}

export default function ChatPanel({ onTaskUpdate }: ChatPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isVisible, setIsVisible] = useState(false); // Controls DOM presence
  const [isAnimating, setIsAnimating] = useState(false); // Controls animation state
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [showConversationList, setShowConversationList] = useState(false);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const [deleteModal, setDeleteModal] = useState<{ isOpen: boolean; convId: string | null }>({
    isOpen: false,
    convId: null,
  });
  const [isDeleting, setIsDeleting] = useState(false);
  const [mounted, setMounted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Handle open/close animation states
  useEffect(() => {
    if (isOpen) {
      setIsVisible(true);
      // Small delay to ensure DOM is ready before animation starts
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          setIsAnimating(true);
        });
      });
    } else {
      setIsAnimating(false);
      // Wait for close animation to finish before hiding
      const timer = setTimeout(() => {
        setIsVisible(false);
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  const scrollToBottom = useCallback(() => {
    setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  }, []);

  useEffect(() => {
    if (isOpen) scrollToBottom();
  }, [messages, isOpen, scrollToBottom]);

  const loadConversations = useCallback(async () => {
    setLoadingConversations(true);
    try {
      const response = await chatService.getConversations(10);
      if (response.success && response.data) setConversations(response.data);
    } catch (err) { console.error(err); } 
    finally { setLoadingConversations(false); }
  }, []);

  useEffect(() => {
    if (isOpen) loadConversations();
  }, [isOpen, loadConversations]);

  const loadConversation = async (convId: string) => {
    setIsLoading(true);
    setShowConversationList(false);
    try {
      const response = await chatService.getConversation(convId);
      if (response.success && response.data) {
        setConversationId(convId);
        setMessages(response.data.messages || []);
      } else setError(response.error || 'Failed to load');
    } catch (err) { setError(err instanceof Error ? err.message : 'Error'); } 
    finally { setIsLoading(false); }
  };

  const handleSendMessage = async (messageText: string) => {
    setError(null);
    setIsLoading(true);
    const tempUserMessage: Message = {
      id: Date.now(),
      conversation_id: conversationId || 'temp',
      role: 'user',
      content: messageText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMessage]);

    try {
      const response = await chatService.sendMessage(messageText, conversationId);
      if (response.success && response.data) {
        const chatResponse: ChatResponse = response.data;
        if (!conversationId) setConversationId(chatResponse.conversation_id);
        
        setMessages(prev => prev.map(msg => msg.id === tempUserMessage.id ? { ...msg, conversation_id: chatResponse.conversation_id } : msg));
        
        const assistantMessage: Message = { ...chatResponse.message, tool_calls: chatResponse.tool_calls };
        setMessages(prev => [...prev, assistantMessage]);

        // Always refresh task list after chat response - the chatbot may have created/modified/deleted tasks
        // This is more reliable than checking tool_calls which may not always be populated correctly
        onTaskUpdate?.();

        if (!conversationId) loadConversations();
      } else {
        setMessages(prev => prev.filter(msg => msg.id !== tempUserMessage.id));
        setError(response.error || 'Failed to send');
      }
    } catch (err) {
      setMessages(prev => prev.filter(msg => msg.id !== tempUserMessage.id));
      setError(err instanceof Error ? err.message : 'Error');
    } finally { setIsLoading(false); }
  };

  const handleNewConversation = () => {
    setMessages([]);
    setConversationId(undefined);
    setError(null);
    setShowConversationList(false);
  };

  const handleDeleteClick = (e: React.MouseEvent, convId: string) => {
    e.stopPropagation(); // Prevent loading the conversation when clicking delete
    setDeleteModal({ isOpen: true, convId });
  };

  const confirmDeleteConversation = async () => {
    if (!deleteModal.convId) return;
    const convId = deleteModal.convId;
    setIsDeleting(true);

    try {
      const response = await chatService.deleteConversation(convId);
      if (response.success) {
        // Remove from local state
        setConversations(prev => prev.filter(c => c.id !== convId));
        // If we deleted the current conversation, clear it
        if (conversationId === convId) {
          setMessages([]);
          setConversationId(undefined);
        }
        setDeleteModal({ isOpen: false, convId: null });
      } else {
        setError(response.error || 'Failed to delete');
        setDeleteModal({ isOpen: false, convId: null });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error deleting');
      setDeleteModal({ isOpen: false, convId: null });
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          fixed z-60 bottom-4 right-4 md:bottom-8 md:right-8
          w-14 h-14 md:w-16 md:h-16 rounded-full
          bg-linear-to-r from-indigo-600 to-purple-600
          text-white shadow-xl shadow-indigo-500/40
          flex items-center justify-center
          transition-all duration-300 ease-out
          hover:scale-110 active:scale-95
          ${isOpen ? 'scale-0 opacity-0 pointer-events-none' : 'scale-100 opacity-100'}
        `}
        aria-label="Open AI Assistant"
      >
        <Sparkles className="w-6 h-6 md:w-8 md:h-8" />
      </button>

      {/* Chat Panel */}
      {isVisible && (
      <div
        className={`
          fixed z-50 flex flex-col overflow-hidden

          /* Position & Size */
          inset-3 rounded-3xl
          sm:inset-4
          md:inset-auto md:bottom-8 md:right-8
          md:w-105 md:h-150 md:max-h-[calc(100vh-5rem)]
          lg:w-112.5 lg:h-162.5

          /* Styling */
          bg-white/95 dark:bg-gray-900/95
          backdrop-blur-xl
          border border-gray-200/50 dark:border-gray-700/50
          shadow-2xl shadow-black/20 dark:shadow-black/40
        `}
        style={{
          transformOrigin: 'calc(100% - 2rem) calc(100% - 2rem)',
          transform: isAnimating ? 'scale(1)' : 'scale(0)',
          opacity: isAnimating ? 1 : 0,
          transition: 'transform 0.35s cubic-bezier(0.32, 0.72, 0, 1), opacity 0.25s ease-out',
        }}
      >
        <div className="flex-none px-4 py-4 md:py-5 border-b border-gray-100 dark:border-gray-800 bg-white/50 dark:bg-gray-900/50 backdrop-blur-md flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-xl bg-linear-to-br from-indigo-500 to-purple-600`}>
                <MessageSquare className="w-5 h-5 text-white" />
            </div>
            <div>
                <h3 className="font-bold text-gray-900 dark:text-white leading-tight">TaskFlow AI</h3>
                <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                    <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">Online</span>
                </div>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <button onClick={() => setShowConversationList(!showConversationList)} className="p-2 text-gray-500 hover:text-indigo-600 dark:text-gray-400 dark:hover:text-indigo-400 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors" title="History">
                <History className="w-5 h-5" />
            </button>
            <button onClick={handleNewConversation} className="p-2 text-gray-500 hover:text-indigo-600 dark:text-gray-400 dark:hover:text-indigo-400 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors" title="New Chat">
                <Plus className="w-5 h-5" />
            </button>
            <button onClick={() => setIsOpen(false)} className="p-2 text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                <ChevronDown className="w-6 h-6 md:hidden" /> 
                <X className="w-5 h-5 hidden md:block" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-hidden relative flex flex-col bg-gray-50/50 dark:bg-[#0b0f19]/50">
            {showConversationList && (
                <div className="absolute inset-0 z-20 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm animate-in fade-in slide-in-from-top-2 overflow-y-auto">
                    <div className="p-4 space-y-2">
                        <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 px-2">Recent Chats</h4>
                        {loadingConversations ? (
                            <div className="flex justify-center p-8"><RefreshCw className="w-6 h-6 animate-spin text-indigo-500" /></div>
                        ) : conversations.length === 0 ? (
                            <div className="text-center p-8 text-gray-500">No history found.</div>
                        ) : (
                            conversations.map(conv => (
                                <div key={conv.id} className={`relative group p-3 rounded-xl transition-all border ${conversationId === conv.id ? 'bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-800' : 'bg-white dark:bg-gray-800 border-gray-100 dark:border-gray-700 hover:border-indigo-300'}`}>
                                    <button onClick={() => loadConversation(conv.id)} className="w-full text-left pr-8">
                                        <div className="font-medium text-gray-800 dark:text-gray-200 truncate">{conv.title || 'Untitled Conversation'}</div>
                                        <div className="text-xs text-gray-400 mt-1">{formatConversationDate(conv.updated_at)}</div>
                                    </button>
                                    <button
                                        onClick={(e) => handleDeleteClick(e, conv.id)}
                                        className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 opacity-100 lg:opacity-0 lg:group-hover:opacity-100 transition-all"
                                        title="Delete conversation"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}

            <div className="flex-1 overflow-y-auto p-4 md:p-5 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-700">
                {messages.length === 0 ? (
                    // FIX 2: Removed opacity-60 and used stronger text colors for readability
                    <div className="h-full flex flex-col items-center justify-center text-center p-6">
                        <div className="w-16 h-16 bg-linear-to-br from-indigo-100 to-purple-100 dark:from-indigo-900/30 dark:to-purple-900/30 rounded-3xl flex items-center justify-center mb-4">
                            <Sparkles className="w-8 h-8 text-indigo-500" />
                        </div>
                        <h4 className="text-lg font-bold text-gray-800 dark:text-white mb-2">How can I help?</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400 max-w-50">Ask me to create tasks, organize your day, or summarize your list.</p>
                    </div>
                ) : (
                    messages.map((msg, idx) => (
                        <ChatMessage key={msg.id} message={msg} isLatest={idx === messages.length - 1} />
                    ))
                )}
                {isLoading && (
                    <div className="flex justify-start mb-4 animate-in fade-in">
                        <div className="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 px-4 py-3 rounded-2xl rounded-bl-none flex items-center gap-2 shadow-sm">
                            <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce" />
                            <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce delay-75" />
                            <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce delay-150" />
                        </div>
                    </div>
                )}
                {error && (
                    <div className="p-3 mb-4 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm flex justify-between items-center border border-red-100 dark:border-red-800">
                        <span>{error}</span>
                        <button onClick={() => setError(null)} className="hover:underline font-medium">Dismiss</button>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>
        </div>

        <div className="flex-none p-4 bg-white dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800">
            <ChatInput onSend={handleSendMessage} disabled={isLoading} />
            <div className="text-center mt-2">
                <p className="text-[10px] text-gray-400 dark:text-gray-600">AI can make mistakes. Review generated actions.</p>
            </div>
        </div>
      </div>
      )}

      {/* Delete Confirmation Modal */}
      {mounted && deleteModal.isOpen && createPortal(
        <div className="fixed inset-0 z-9999 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-gray-900/60 backdrop-blur-sm transition-opacity"
            onClick={() => !isDeleting && setDeleteModal({ isOpen: false, convId: null })}
          />
          {/* Modal */}
          <div className="relative w-full max-w-md bg-white dark:bg-gray-900 rounded-3xl shadow-2xl border border-gray-200 dark:border-gray-800 p-8 animate-in zoom-in-95 duration-200">
            <div className="flex flex-col items-center text-center">
              <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 ${isDeleting ? 'bg-indigo-100 dark:bg-indigo-900/30' : 'bg-red-100 dark:bg-red-900/30'}`}>
                {isDeleting ? (
                  <div className="w-8 h-8 border-3 border-indigo-200 dark:border-indigo-800 border-t-indigo-600 dark:border-t-indigo-400 rounded-full animate-spin" />
                ) : (
                  <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400" />
                )}
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                {isDeleting ? 'Deleting...' : 'Delete Conversation?'}
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-8">
                {isDeleting ? (
                  'Please wait while we delete this conversation.'
                ) : (
                  <>Are you sure you want to delete this conversation?<br />This action cannot be undone.</>
                )}
              </p>
              <div className="flex gap-4 w-full">
                <button
                  onClick={() => setDeleteModal({ isOpen: false, convId: null })}
                  disabled={isDeleting}
                  className={`flex-1 px-6 py-3 rounded-xl font-bold transition-colors ${
                    isDeleting
                      ? 'text-gray-400 bg-gray-100 dark:bg-gray-800 cursor-not-allowed'
                      : 'text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                >
                  Cancel
                </button>
                <button
                  onClick={confirmDeleteConversation}
                  disabled={isDeleting}
                  className={`flex-1 px-6 py-3 rounded-xl font-bold text-white transition-all flex items-center justify-center gap-2 ${
                    isDeleting
                      ? 'bg-gray-400 dark:bg-gray-600 cursor-not-allowed'
                      : 'bg-linear-to-r from-red-600 to-pink-600 hover:from-red-500 hover:to-pink-500 shadow-lg shadow-red-500/30 hover:scale-[1.02]'
                  }`}
                >
                  {isDeleting ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Deleting
                    </>
                  ) : (
                    'Delete'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>,
        document.body
      )}
    </>
  );
}

function formatConversationDate(dateString: string): string {
  // Backend stores UTC time - ensure proper parsing by adding 'Z' if missing
  const utcDateString = dateString.endsWith('Z') ? dateString : dateString + 'Z';
  const date = new Date(utcDateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}