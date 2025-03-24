/**
 * SessionStartForm.tsx
 * 
 * This component provides a form for users to start a new session.
 * It demonstrates how to use the TanStack Query hooks to interact with the API.
 */

import { useState, useEffect } from 'react';
import { useStartSession } from '@/api';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { User } from '@/api/models';

/**
 * SessionStartFormProps
 * @property {Function} onSessionStarted - Callback function that receives the session data when a session is started
 */
interface SessionStartFormProps {
  onSessionStarted: (sessionData: { userId: number; journeyId: number }) => void;
}

/**
 * A form component for starting a new session.
 * Demonstrates how to use mutation hooks from TanStack Query.
 * 
 * @param onSessionStarted - Callback that runs after successfully starting a session
 */
export function SessionStartForm({ onSessionStarted }: SessionStartFormProps) {
  // Form state
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [formMode, setFormMode] = useState<'new' | 'existing'>('new');
  
  // Fetch existing users
  const { data: users = [], isLoading: loadingUsers } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await axios.get<User[]>('http://localhost:8000/users');
      return response.data;
    }
  });
  
  // Use the mutation hook
  const { mutate, isPending, isError, error } = useStartSession({
    onSuccess: (data) => {
      // Call the callback with the user ID and journey ID
      onSessionStarted({
        userId: data.user_id,
        journeyId: data.journey_id
      });
    }
  });
  
  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formMode === 'existing' && selectedUserId) {
      // Use existing user
      mutate({
        user_id: selectedUserId
      });
    } else {
      // Create new user
      mutate({
        first_name: firstName,
        last_name: lastName,
      });
    }
  };
  
  // Clear form fields when switching modes
  useEffect(() => {
    if (formMode === 'new') {
      setSelectedUserId(null);
    } else {
      setFirstName('');
      setLastName('');
    }
  }, [formMode]);
  
  return (
    <div className="max-w-md mx-auto p-6 bg-white dark:bg-slate-800 rounded-lg shadow-md ">
      <h2 className="text-2xl font-bold mb-6 text-center text-gray-800 dark:text-white">
        Start Your Renovation Journey
      </h2>
      
      {/* Toggle between new and existing user */}
      <div className="flex justify-center mb-6">
        <div className="flex p-1 bg-gray-100 dark:bg-slate-700 rounded-md">
          <button
            type="button"
            className={`px-4 py-2 rounded-md ${
              formMode === 'new'
                ? 'bg-blue-500 text-white'
                : 'bg-transparent text-gray-700 dark:text-gray-300'
            }`}
            onClick={() => setFormMode('new')}
          >
            New User
          </button>
          <button
            type="button"
            className={`px-4 py-2 rounded-md ${
              formMode === 'existing'
                ? 'bg-blue-500 text-white'
                : 'bg-transparent text-gray-700 dark:text-gray-300'
            }`}
            onClick={() => setFormMode('existing')}
          >
            Existing User
          </button>
        </div>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {formMode === 'new' ? (
          <>
            <div>
              <label 
                htmlFor="firstName"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
              >
                First Name
              </label>
              <input
                id="firstName"
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your first name"
              />
            </div>
            
            <div>
              <label 
                htmlFor="lastName"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
              >
                Last Name
              </label>
              <input
                id="lastName"
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your last name"
              />
            </div>
          </>
        ) : (
          <div>
            <label 
              htmlFor="existingUser"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Select Existing User
            </label>
            <select
              id="existingUser"
              value={selectedUserId || ''}
              onChange={(e) => setSelectedUserId(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={loadingUsers}
            >
              <option value="">Select a user</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>
                  ID: {user.id} - {user.first_name || ''} {user.last_name || ''}
                </option>
              ))}
            </select>
            {loadingUsers && (
              <p className="text-sm text-gray-500 mt-1">Loading users...</p>
            )}
            {users.length === 0 && !loadingUsers && (
              <p className="text-sm text-red-500 mt-1">No existing users found. Please create a new user.</p>
            )}
          </div>
        )}
        
        {isError && (
          <div className="text-red-500 text-sm">
            Error: {error.message || 'Failed to start session'}
          </div>
        )}
        
        <button
          type="submit"
          disabled={isPending || (formMode === 'existing' && !selectedUserId)}
          className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isPending 
            ? 'Starting...' 
            : formMode === 'new' 
              ? 'Start New Journey' 
              : 'Continue Journey'
          }
        </button>
      </form>
    </div>
  );
} 