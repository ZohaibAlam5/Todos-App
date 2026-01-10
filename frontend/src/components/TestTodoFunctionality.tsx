'use client';

import React, { useState, useEffect } from 'react';
import { taskService } from '@/services/task';
import { Task } from '@/types';

const TestTodoFunctionality: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await taskService.getTasks();
      if (response.success && response.data) {
        setTasks(response.data);
      } else {
        setError(response.error || 'Failed to fetch tasks');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading tasks...</div>;
  }

  if (error) {
    return <div className="text-center py-8 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4">Test Todo Functionality</h2>
      <div className="space-y-4">
        {tasks.length === 0 ? (
          <p className="text-gray-500">No tasks found. Try creating some tasks!</p>
        ) : (
          tasks.map(task => (
            <div key={task.id} className="p-4 border rounded-lg">
              <h3 className="font-semibold">{task.title}</h3>
              <p className="text-sm text-gray-600">{task.description}</p>
              <div className="mt-2 flex items-center justify-between">
                <span className={`px-2 py-1 rounded text-xs ${
                  task.completed
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {task.completed ? 'Completed' : 'Pending'}
                </span>
                <span className={`px-2 py-1 rounded text-xs ${
                  task.priority === 'High'
                    ? 'bg-red-100 text-red-800'
                    : task.priority === 'Medium'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-green-100 text-green-800'
                }`}>
                  {task.priority}
                </span>
              </div>
              {task.tags && task.tags.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {task.tags.map((tag, index) => (
                    <span key={index} className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default TestTodoFunctionality;