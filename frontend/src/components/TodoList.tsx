'use client';

import React, { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { Task, TaskCreateRequest, TaskUpdateRequest } from '@/types';
import { taskService } from '@/services/task';
import { useAuth } from '@/components/AuthContext';
import { 
  Plus, Search, Filter, SortAsc, Calendar, 
  CheckCircle, Circle, Trash2, Edit2, X, Tag, AlertCircle, Loader2, ChevronDown, Sparkles, Check
} from 'lucide-react';

// --- 1. ANIMATED CUSTOM DROPDOWN ---
interface CustomDropdownProps {
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
  icon?: React.ElementType;
  className?: string;
  buttonClassName?: string;
}

const CustomDropdown: React.FC<CustomDropdownProps> = ({ value, onChange, options, icon: Icon, className, buttonClassName }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selectedLabel = options.find(opt => opt.value === value)?.label || value;

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full flex items-center justify-between gap-3 px-4 py-3 
        bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 
        rounded-xl text-sm md:text-base text-gray-700 dark:text-gray-200 font-medium 
        hover:border-indigo-500 dark:hover:border-indigo-500 transition-all shadow-sm group whitespace-nowrap
        ${buttonClassName || ''}
        `}
      >
        <div className="flex items-center gap-2 flex-1 overflow-hidden">
             {Icon && <Icon className="w-4 h-4 text-gray-400 group-hover:text-indigo-500 transition-colors shrink-0" />}
             <span className="truncate">{selectedLabel}</span>
        </div>
        <ChevronDown 
          className={`w-4 h-4 text-gray-400 transition-transform duration-300 ease-out ${isOpen ? 'rotate-180' : 'rotate-0'}`} 
        />
      </button>

      {/* Animated Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-2 z-50 
          bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl 
          border border-gray-100 dark:border-gray-700 
          rounded-xl shadow-2xl overflow-hidden 
          origin-top animate-dropdown-open"
          style={{ animation: 'dropdown-open 0.2s ease-out forwards' }}
        >
          <div className="py-1 max-h-60 overflow-y-auto custom-scrollbar">
            {options.map((option) => (
              <button
                type="button"
                key={option.value}
                onClick={() => {
                  onChange(option.value);
                  setIsOpen(false);
                }}
                className={`w-full flex items-center justify-start relative px-4 py-3 text-sm transition-all duration-200
                  ${option.value === value 
                    ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 font-semibold pl-6' 
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:pl-6'
                  }`}
              >
                {option.label}
                {option.value === value && (
                  <span className="absolute right-4 top-1/2 -translate-y-1/2">
                    <Check className="w-4 h-4" />
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// --- MAIN COMPONENT ---

interface TodoListProps {
  onTaskUpdated?: () => void;
}

const TodoList: React.FC<TodoListProps> = ({ onTaskUpdated }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState<'High' | 'Medium' | 'Low'>('Medium');
  const [newTaskTags, setNewTaskTags] = useState('');
  
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [editPriority, setEditPriority] = useState<'High' | 'Medium' | 'Low'>('Medium');
  const [editTags, setEditTags] = useState('');
  
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'completed'>('all');
  const [filterPriority, setFilterPriority] = useState<'all' | 'High' | 'Medium' | 'Low'>('all');
  const [sortBy, setSortBy] = useState<'created_at' | 'priority' | 'title'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  
  const [showAddForm, setShowAddForm] = useState(false);
  const [isFormClosing, setIsFormClosing] = useState(false);
  
  const [isProcessing, setIsProcessing] = useState(false); 
  const [deleteModal, setDeleteModal] = useState<{isOpen: boolean, taskId: number | null}>({
    isOpen: false,
    taskId: null
  });

  const { user } = useAuth();

  useEffect(() => {
    setMounted(true);
    fetchTasks();
  }, [user]);

  useEffect(() => {
    if (onTaskUpdated) onTaskUpdated();
  }, [tasks, onTaskUpdated]);

  const fetchTasks = async () => {
    const token = localStorage.getItem('token');
    if (!user || !token) {
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      const response = await taskService.getTasks();
      if (response.success && response.data) setTasks(response.data);
      else setError(response.error || 'Failed to fetch tasks');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error fetching tasks');
    } finally {
      setLoading(false);
    }
  };

  // --- HELPER: Close form smoothly ---
  const handleCloseForm = () => {
    setIsFormClosing(true);
    // Wait for animation to finish (500ms) before removing from DOM
    setTimeout(() => {
        setShowAddForm(false);
        setEditingTask(null);
        setIsFormClosing(false);
    }, 500); 
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;
    const tags = newTaskTags.split(',').map(tag => tag.trim()).filter(tag => tag);
    setIsProcessing(true);
    try {
      const response = await taskService.createTask({
        title: newTaskTitle, description: newTaskDescription, priority: newTaskPriority, tags: tags,
      });
      if (response.success && response.data) {
        setTasks([response.data, ...tasks]);
        setNewTaskTitle(''); setNewTaskDescription(''); setNewTaskPriority('Medium'); setNewTaskTags(''); 
        handleCloseForm();
        setError(null);
      } else setError(response.error || 'Failed to create task');
    } catch (err) { setError(err instanceof Error ? err.message : 'An error occurred'); } finally { setIsProcessing(false); }
  };

  const handleUpdateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTask) return;
    const tags = editTags.split(',').map(tag => tag.trim()).filter(tag => tag);
    setIsProcessing(true);
    try {
      const response = await taskService.updateTask(editingTask.id, {
        title: editTitle, description: editDescription, priority: editPriority, tags: tags,
      });
      if (response.success && response.data) {
        setTasks(tasks.map(task => task.id === editingTask.id ? response.data! : task));
        handleCloseForm();
        setError(null);
      } else setError(response.error || 'Failed to update task');
    } catch (err) { setError(err instanceof Error ? err.message : 'An error occurred'); } finally { setIsProcessing(false); }
  };

  const handleDeleteClick = (id: number) => setDeleteModal({ isOpen: true, taskId: id });

  const confirmDeleteTask = async () => {
    if (!deleteModal.taskId) return;
    const id = deleteModal.taskId;
    setDeleteModal({ isOpen: false, taskId: null });
    setIsProcessing(true);
    try {
      const response = await taskService.deleteTask(id);
      if (response.success) setTasks(tasks.filter(task => task.id !== id));
      else setError(response.error || 'Failed to delete task');
    } catch (err) { setError(err instanceof Error ? err.message : 'An error occurred'); } finally { setIsProcessing(false); }
  };

  const handleToggleCompletion = async (id: number) => {
    setIsProcessing(true);
    try {
      const response = await taskService.toggleTaskCompletion(id);
      if (response.success && response.data) setTasks(tasks.map(task => task.id === id ? response.data! : task));
    } catch (err) { setError(err instanceof Error ? err.message : 'An error occurred'); } finally { setIsProcessing(false); }
  };

  const startEditing = (task: Task) => {
    if (showAddForm || editingTask) {
        // Instant switch if already open
    } else {
        // Animation triggers on mount
    }
    setEditingTask(task); 
    setEditTitle(task.title); 
    setEditDescription(task.description || ''); 
    setEditPriority(task.priority); 
    setEditTags(task.tags.join(', ')); 
    setShowAddForm(false); 
  };

  const filteredTasks = tasks.filter(task => {
      const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) || (task.description && task.description.toLowerCase().includes(searchTerm.toLowerCase()));
      const matchesStatus = filterStatus === 'all' || (filterStatus === 'active' && !task.completed) || (filterStatus === 'completed' && task.completed);
      const matchesPriority = filterPriority === 'all' || task.priority === filterPriority;
      return matchesSearch && matchesStatus && matchesPriority;
    }).sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'title': comparison = a.title.localeCompare(b.title); break;
        case 'priority': 
          const pOrder = { 'High': 3, 'Medium': 2, 'Low': 1 };
          comparison = pOrder[b.priority] - pOrder[a.priority]; break;
        case 'created_at': comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime(); break;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

  if (loading && tasks.length === 0) return (<div className="flex justify-center items-center h-64"><Loader2 className="animate-spin h-10 w-10 text-indigo-500" /></div>);

  const InputClasses = "w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors text-base";

  return (
    <div className="w-full relative">
      
      {/* --- CSS ANIMATIONS --- */}
      <style jsx global>{`
        @keyframes form-enter {
          from { 
            opacity: 0; 
            transform: translateY(-20px) scale(0.98); 
          }
          to { 
            opacity: 1; 
            transform: translateY(0) scale(1); 
          }
        }
        
        /* UPDATED: Collapse height, margin, padding, and border to 0 */
        @keyframes form-exit {
          0% { 
            opacity: 1; 
            transform: translateY(0) scale(1);
            max-height: 800px;
            margin-bottom: 2rem;
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
            border-width: 1px;
          }
          100% { 
            opacity: 0; 
            transform: translateY(-20px) scale(0.98); 
            max-height: 0;
            margin-bottom: 0;
            padding-top: 0;
            padding-bottom: 0;
            border-width: 0;
          }
        }

        @keyframes dropdown-open {
          from { opacity: 0; transform: scaleY(0.95); }
          to { opacity: 1; transform: scaleY(1); }
        }
        
        .animate-form-enter {
          animation: form-enter 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        .animate-form-exit {
          animation: form-exit 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        .animate-dropdown-open {
          animation: dropdown-open 0.2s ease-out forwards;
        }
      `}</style>

      {/* --- POPUPS --- */}
      {mounted && isProcessing && createPortal(
         <div className="fixed inset-0 z-9999 flex flex-col items-center justify-center bg-gray-50/50 dark:bg-gray-950/50 backdrop-blur-sm transition-all duration-300">
           <div className="relative p-8 rounded-3xl bg-white/40 dark:bg-gray-900/40 backdrop-blur-xl border border-white/20 dark:border-white/10 shadow-2xl flex flex-col items-center gap-6 animate-in zoom-in-95 duration-200">
             <div className="relative w-16 h-16 flex items-center justify-center">
                <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-indigo-500 border-r-purple-500 animate-[spin_1.5s_linear_infinite]" />
                <div className="absolute inset-2 rounded-full border-2 border-transparent border-t-purple-500 border-l-indigo-500 animate-[spin_2s_linear_infinite_reverse]" />
                <Sparkles className="w-6 h-6 text-indigo-600 dark:text-indigo-400 animate-pulse" />
             </div>
             <div className="text-center">
               <h3 className="text-xl font-bold bg-clip-text text-transparent bg-linear-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400">Processing Request</h3>
               <p className="text-sm text-gray-500 dark:text-gray-400">Syncing with server...</p>
             </div>
           </div>
         </div>, document.body 
      )}

      {mounted && deleteModal.isOpen && createPortal(
        <div className="fixed inset-0 z-9999 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-gray-900/60 backdrop-blur-sm transition-opacity" onClick={() => setDeleteModal({isOpen: false, taskId: null})}/>
          <div className="relative w-full max-w-md bg-white dark:bg-gray-900 rounded-3xl shadow-2xl border border-gray-200 dark:border-gray-800 p-8 animate-in zoom-in-95 duration-200">
             <div className="flex flex-col items-center text-center">
               <div className="w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mb-6">
                 <Trash2 className="w-8 h-8 text-red-600 dark:text-red-500" />
               </div>
               <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Delete Task?</h3>
               <p className="text-gray-500 dark:text-gray-400 mb-8">Are you sure you want to remove this task? <br/> This action cannot be undone.</p>
               <div className="flex gap-4 w-full">
                 <button onClick={() => setDeleteModal({isOpen: false, taskId: null})} className="flex-1 px-6 py-3 rounded-xl font-bold text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">Cancel</button>
                 <button onClick={confirmDeleteTask} className="flex-1 px-6 py-3 rounded-xl font-bold text-white bg-linear-to-r from-red-600 to-pink-600 hover:from-red-500 hover:to-pink-500 shadow-lg shadow-red-500/30 transition-all hover:scale-[1.02]">Delete</button>
               </div>
             </div>
          </div>
        </div>, document.body 
      )}

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 px-4 py-3 rounded-xl mb-6 flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}

      {/* --- CONTROLS BAR --- */}
      <div className="mb-8 p-6 bg-white/50 dark:bg-gray-800/40 backdrop-blur-md border border-white/50 dark:border-gray-700/50 rounded-2xl shadow-sm">
        
        <div className="flex flex-col lg:flex-row gap-5 items-start lg:items-center">
          
          {/* Group 1: Add Button & Search */}
          <div className="flex flex-col sm:flex-row gap-4 w-full lg:w-auto lg:flex-1">
            
            <button
              onClick={() => {
                if (showAddForm) {
                    handleCloseForm();
                } else {
                    setShowAddForm(true);
                    setEditingTask(null);
                }
              }}
              className={`group flex items-center justify-center gap-2 px-5 py-3 font-bold rounded-xl transition-all shadow-md shrink-0 text-sm md:text-base
                ${showAddForm 
                  ? 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-200 hover:bg-gray-300' 
                  : 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-indigo-500/30'}`}
            >
              {showAddForm ? <X className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
              <span className="whitespace-nowrap">{showAddForm ? 'Cancel' : 'New Task'}</span>
            </button>

            <div className="relative w-full flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search tasks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-11 pr-4 py-3 text-base bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm transition-all"
              />
            </div>
          </div>

          {/* Group 2: Filters */}
          <div className="flex flex-wrap gap-3 w-full lg:w-auto shrink-0">
             
             <CustomDropdown 
                value={filterStatus}
                onChange={(val) => setFilterStatus(val as any)}
                options={[
                  { value: 'all', label: 'All Status' },
                  { value: 'active', label: 'Active' },
                  { value: 'completed', label: 'Completed' },
                ]}
                className="flex-1 sm:flex-none sm:w-auto min-w-35"
             />

             <CustomDropdown 
                value={filterPriority}
                onChange={(val) => setFilterPriority(val as any)}
                options={[
                  { value: 'all', label: 'All Priorities' },
                  { value: 'High', label: 'High' },
                  { value: 'Medium', label: 'Medium' },
                  { value: 'Low', label: 'Low' },
                ]}
                className="flex-1 sm:flex-none sm:w-auto min-w-35"
             />

             <div className="h-12 w-px bg-gray-300 dark:bg-gray-700 mx-1 hidden lg:block"></div>

             <CustomDropdown 
                value={`${sortBy}-${sortOrder}`}
                onChange={(val) => {
                  const [field, order] = val.split('-') as [any, any];
                  setSortBy(field);
                  setSortOrder(order);
                }}
                options={[
                  { value: 'created_at-desc', label: 'Newest First' },
                  { value: 'created_at-asc', label: 'Oldest First' },
                  { value: 'priority-desc', label: 'Priority (High)' },
                  { value: 'title-asc', label: 'Title (A-Z)' },
                ]}
                className="flex-1 sm:flex-none w-full sm:w-auto min-w-40"
             />
          </div>
        </div>
      </div>

      {/* --- CREATE / EDIT FORM (ANIMATED) --- */}
      {/* We check showAddForm OR editingTask OR isFormClosing to keep it in DOM during exit animation */}
      {(showAddForm || editingTask || isFormClosing) && (
        <div 
          className={`
            p-6 md:p-8 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-xl 
            ${isFormClosing ? 'animate-form-exit overflow-hidden' : 'animate-form-enter mb-8'}
          `}
        >
          
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              {editingTask ? <Edit2 className="w-5 h-5 text-indigo-500" /> : <Plus className="w-5 h-5 text-indigo-500" />}
              {editingTask ? 'Edit Task' : 'Create New Task'}
            </h3>
            <button onClick={handleCloseForm} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
              <X className="w-6 h-6" />
            </button>
          </div>

          <form onSubmit={editingTask ? handleUpdateTask : handleCreateTask}>
            <div className="space-y-5">
              <div>
                <input type="text" placeholder="Task Title" value={editingTask ? editTitle : newTaskTitle} onChange={(e) => editingTask ? setEditTitle(e.target.value) : setNewTaskTitle(e.target.value)} className={InputClasses} required />
              </div>
              
              <div>
                <textarea placeholder="Description (Optional)" value={editingTask ? editDescription : newTaskDescription} onChange={(e) => editingTask ? setEditDescription(e.target.value) : setNewTaskDescription(e.target.value)} className={InputClasses} rows={3} />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5 relative">
                {/* Priority Dropdown */}
                <div className="flex flex-col gap-1.5 relative z-20">
                   <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Priority</label>
                   <CustomDropdown 
                     value={editingTask ? editPriority : newTaskPriority} 
                     onChange={(val) => editingTask ? setEditPriority(val as any) : setNewTaskPriority(val as any)} 
                     options={[
                       { value: 'High', label: 'High Priority' },
                       { value: 'Medium', label: 'Medium Priority' },
                       { value: 'Low', label: 'Low Priority' }
                     ]}
                     className="w-full"
                     buttonClassName="bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 py-3"
                   />
                </div>

                <div className="flex flex-col gap-1.5 relative z-10">
                  <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Tags</label>
                  <input type="text" placeholder="Comma separated (e.g. Work, Urgent)" value={editingTask ? editTags : newTaskTags} onChange={(e) => editingTask ? setEditTags(e.target.value) : setNewTaskTags(e.target.value)} className={InputClasses} />
                </div>
              </div>

              <div className="pt-4 flex gap-3 justify-end">
                <button type="button" onClick={handleCloseForm} className="px-5 py-3 rounded-xl font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">Cancel</button>
                <button type="submit" className="px-8 py-3 bg-linear-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold rounded-xl shadow-lg shadow-indigo-500/30 transition-all hover:scale-[1.02]">{editingTask ? 'Save Changes' : 'Create Task'}</button>
              </div>
            </div>
          </form>
        </div>
      )}

      {/* --- TASK LIST RENDER --- */}
      <div className="space-y-4">
        {filteredTasks.length === 0 ? (
          <div className="text-center py-16 bg-white/30 dark:bg-gray-800/20 rounded-2xl border border-dashed border-gray-300 dark:border-gray-700">
            <div className="inline-block p-4 rounded-full bg-gray-100 dark:bg-gray-800 mb-4">
              <Calendar className="w-10 h-10 text-gray-400 dark:text-gray-500" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">No tasks found</h3>
            <p className="text-gray-500 dark:text-gray-400 mt-1">Try adjusting your filters or add a new task.</p>
          </div>
        ) : (
          filteredTasks.map(task => (
            <div key={task.id} className={`group flex flex-col sm:flex-row items-start sm:items-center justify-between p-5 rounded-2xl transition-all duration-300 border ${task.completed ? 'bg-gray-50/80 dark:bg-gray-900/40 border-gray-200 dark:border-gray-800' : 'bg-white dark:bg-gray-800/40 border-white/50 dark:border-gray-700/50 hover:shadow-lg hover:border-indigo-300 dark:hover:border-indigo-500/50'}`}>
              <div className="flex items-start gap-4 flex-1 w-full">
                <button onClick={() => handleToggleCompletion(task.id)} className={`mt-1 shrink-0 transition-colors duration-300 ${task.completed ? 'text-green-500' : 'text-gray-300 dark:text-gray-500 hover:text-indigo-500'}`}>
                  {task.completed ? <CheckCircle className="w-6 h-6 fill-current/10" /> : <Circle className="w-6 h-6" />}
                </button>
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <h3 className={`text-lg font-semibold truncate transition-all duration-300 ${task.completed ? 'text-gray-400 dark:text-gray-600 line-through' : 'text-gray-800 dark:text-white'}`}>{task.title}</h3>
                    <span className={`px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded-full border ${task.priority === 'High' ? 'bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-300 dark:border-red-800' : task.priority === 'Medium' ? 'bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-300 dark:border-yellow-800' : 'bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-300 dark:border-green-800'}`}>{task.priority}</span>
                  </div>
                  {task.description && <p className={`text-sm mb-2 line-clamp-2 ${task.completed ? 'text-gray-400 dark:text-gray-600' : 'text-gray-600 dark:text-gray-400'}`}>{task.description}</p>}
                  <div className="flex flex-wrap items-center gap-3 text-xs text-gray-400 dark:text-gray-500">
                    <span className="flex items-center gap-1 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded-md"><Calendar className="w-3 h-3" />{new Date(task.created_at).toLocaleDateString()}</span>
                    {task.tags && task.tags.length > 0 && <div className="flex items-center gap-2">{task.tags.map((tag, idx) => (<span key={idx} className="flex items-center gap-1 text-indigo-500 dark:text-indigo-400"><Tag className="w-3 h-3" /> {tag}</span>))}</div>}
                  </div>
                </div>
              </div>
              <div className="flex gap-1 mt-4 sm:mt-0 sm:ml-4 w-full sm:w-auto justify-end">
                <button onClick={() => startEditing(task)} className="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 dark:hover:text-indigo-400 rounded-lg transition-colors"><Edit2 className="w-4 h-4" /></button>
                <button onClick={() => handleDeleteClick(task.id)} className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 dark:hover:text-red-400 rounded-lg transition-colors"><Trash2 className="w-4 h-4" /></button>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="mt-8 grid grid-cols-3 gap-4">
        <div className="p-4 bg-white/50 dark:bg-gray-800/40 rounded-2xl border border-white/50 dark:border-gray-700/50 text-center backdrop-blur-sm"><div className="text-2xl font-bold text-gray-800 dark:text-white">{tasks.length}</div><div className="text-xs text-gray-500 uppercase tracking-wider">Total</div></div>
        <div className="p-4 bg-white/50 dark:bg-gray-800/40 rounded-2xl border border-white/50 dark:border-gray-700/50 text-center backdrop-blur-sm"><div className="text-2xl font-bold text-green-500">{tasks.filter(t => t.completed).length}</div><div className="text-xs text-gray-500 uppercase tracking-wider">Done</div></div>
        <div className="p-4 bg-white/50 dark:bg-gray-800/40 rounded-2xl border border-white/50 dark:border-gray-700/50 text-center backdrop-blur-sm"><div className="text-2xl font-bold text-indigo-500">{tasks.filter(t => !t.completed).length}</div><div className="text-xs text-gray-500 uppercase tracking-wider">Pending</div></div>
      </div>
    </div>
  );
};

export default TodoList;