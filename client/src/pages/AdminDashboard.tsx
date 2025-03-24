/**
 * AdminDashboard.tsx
 * 
 * This component serves as a simple admin interface to view the database contents.
 * It allows viewing users, journeys, and messages with real-time updates.
 * The dashboard is organized in tabs for easy navigation between different data types.
 */

import { useState } from 'react';
import axios from 'axios';
import { User, Journey, Message } from '@/api/models';
import { useQuery, useQueryClient } from '@tanstack/react-query';

// API fetching functions
const fetchUsers = async (): Promise<User[]> => {
  const response = await axios.get('http://localhost:8000/users');
  return response.data;
};

const fetchJourneys = async (): Promise<Journey[]> => {
  const response = await axios.get('http://localhost:8000/journeys');
  return response.data;
};

const fetchMessages = async (journeyId?: number): Promise<Message[]> => {
  const url = journeyId 
    ? `http://localhost:8000/messages/${journeyId}` 
    : 'http://localhost:8000/messages/all';
  const response = await axios.get(url);
  return response.data;
};

// API mutation functions
const deleteUser = async (userId: number): Promise<void> => {
  await axios.delete(`http://localhost:8000/users/${userId}`);
};

/**
 * AdminDashboard is a component that displays database contents
 * and updates in real-time to show changes as they occur.
 */
export default function AdminDashboard() {
  // State for active tab
  const [activeTab, setActiveTab] = useState<'users' | 'journeys' | 'messages'>('users');
  
  // Selected items for detailed view
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [selectedJourneyId, setSelectedJourneyId] = useState<number | null>(null);
  
  // Filter for messages by user ID
  const [messageUserFilter, setMessageUserFilter] = useState<number | null>(null);
  
  // Get access to the query client
  const queryClient = useQueryClient();
  
  // TanStack Query for users
  const { 
    data: users = [], 
    isLoading: usersLoading,
    error: usersError
  } = useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 25000, // Consider data stale after 25 seconds
  });
  
  // TanStack Query for journeys
  const {
    data: journeys = [],
    isLoading: journeysLoading,
    error: journeysError
  } = useQuery({
    queryKey: ['journeys'],
    queryFn: fetchJourneys,
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 25000, // Consider data stale after 25 seconds
  });
  
  // TanStack Query for messages
  const {
    data: messages = [],
    isLoading: messagesLoading,
    error: messagesError
  } = useQuery({
    queryKey: ['messages', selectedJourneyId],
    queryFn: () => fetchMessages(selectedJourneyId || undefined),
    refetchInterval: selectedJourneyId ? 15000 : 30000, // Refetch more frequently if a journey is selected
    staleTime: 10000, // Consider data stale after 10 seconds
  });
  
  // Filter messages by user ID if a filter is applied
  const filteredMessages = messageUserFilter 
    ? messages.filter(message => message.user_id === messageUserFilter)
    : messages;
  
  /**
   * Handle tab switching
   */
  const handleTabChange = (tab: 'users' | 'journeys' | 'messages') => {
    setActiveTab(tab);
  };
  
  /**
   * Get user name by ID
   */
  const getUserNameById = (userId: number) => {
    const user = users.find(u => u.id === userId);
    if (!user) return 'Unknown User';
    return `${user.first_name || ''} ${user.last_name || ''}`.trim() || `User ${userId}`;
  };
  
  /**
   * Format date to a readable format
   */
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };
  
  // Loading and error states for UI
  const loading = {
    users: usersLoading,
    journeys: journeysLoading,
    messages: messagesLoading
  };
  
  const error = {
    users: usersError ? 'Failed to load users' : '',
    journeys: journeysError ? 'Failed to load journeys' : '',
    messages: messagesError ? 'Failed to load messages' : ''
  };
  
  /**
   * Handle user deletion
   */
  const handleDeleteUser = async (userId: number) => {
    if (confirm(`Are you sure you want to delete user ${userId}? This will also delete all associated journeys and messages.`)) {
      try {
        await deleteUser(userId);
        // Invalidate relevant queries to refresh data
        queryClient.invalidateQueries({ queryKey: ['users'] });
        queryClient.invalidateQueries({ queryKey: ['journeys'] });
        queryClient.invalidateQueries({ queryKey: ['messages'] });
        alert('User deleted successfully');
      } catch (error) {
        console.error('Error deleting user:', error);
        alert('Failed to delete user');
      }
    }
  };
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-center">Database Admin Dashboard</h1>
      
      {/* Tabs */}
      <div className="flex border-b mb-6">
        <button 
          className={`px-4 py-2 ${activeTab === 'users' ? 'border-b-2 border-blue-500 font-medium' : 'text-gray-500'}`}
          onClick={() => handleTabChange('users')}
        >
          Users
        </button>
        <button 
          className={`px-4 py-2 ${activeTab === 'journeys' ? 'border-b-2 border-blue-500 font-medium' : 'text-gray-500'}`}
          onClick={() => handleTabChange('journeys')}
        >
          Journeys
        </button>
        <button 
          className={`px-4 py-2 ${activeTab === 'messages' ? 'border-b-2 border-blue-500 font-medium' : 'text-gray-500'}`}
          onClick={() => handleTabChange('messages')}
        >
          Messages
        </button>
      </div>
      
      {/* Users Tab Content */}
      {activeTab === 'users' && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Users</h2>
          {loading.users ? (
            <p className="text-center">Loading users...</p>
          ) : error.users ? (
            <p className="text-red-500 text-center">{error.users}</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white dark:bg-slate-800 rounded-lg overflow-hidden shadow">
                <thead className="bg-gray-100 dark:bg-slate-700">
                  <tr>
                    <th className="px-4 py-2 text-left">ID</th>
                    <th className="px-4 py-2 text-left">First Name</th>
                    <th className="px-4 py-2 text-left">Last Name</th>
                    <th className="px-4 py-2 text-left">Created At</th>
                    <th className="px-4 py-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className="border-t dark:border-slate-600">
                      <td className="px-4 py-2">{user.id}</td>
                      <td className="px-4 py-2">{user.first_name || '-'}</td>
                      <td className="px-4 py-2">{user.last_name || '-'}</td>
                      <td className="px-4 py-2">{formatDate(user.created_at)}</td>
                      <td className="px-4 py-2">
                        <button 
                          onClick={() => setSelectedUserId(user.id)}
                          className="text-blue-500 hover:underline mr-3"
                        >
                          View Journeys
                        </button>
                        <button 
                          onClick={() => handleDeleteUser(user.id)}
                          className="text-red-500 hover:underline"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                  {users.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-4 py-2 text-center text-gray-500">
                        No users found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
          
          {/* Selected User's Journeys */}
          {selectedUserId && (
            <div className="mt-8">
              <h3 className="text-lg font-medium mb-4">
                Journeys for {getUserNameById(selectedUserId)}
                <button 
                  onClick={() => setSelectedUserId(null)}
                  className="ml-2 text-sm text-blue-500 hover:underline"
                >
                  Clear
                </button>
              </h3>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white dark:bg-slate-800 rounded-lg overflow-hidden shadow">
                  <thead className="bg-gray-100 dark:bg-slate-700">
                    <tr>
                      <th className="px-4 py-2 text-left">ID</th>
                      <th className="px-4 py-2 text-left">Status</th>
                      <th className="px-4 py-2 text-left">Milestone</th>
                      <th className="px-4 py-2 text-left">Created At</th>
                      <th className="px-4 py-2 text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {journeys
                      .filter(journey => journey.user_id === selectedUserId)
                      .map((journey) => (
                        <tr key={journey.id} className="border-t dark:border-slate-600">
                          <td className="px-4 py-2">{journey.id}</td>
                          <td className="px-4 py-2">
                            <span className={`px-2 py-1 rounded text-xs ${
                              journey.status === 'completed' 
                                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' 
                                : journey.status === 'abandoned'
                                ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                                : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
                            }`}>
                              {journey.status}
                            </span>
                          </td>
                          <td className="px-4 py-2">{journey.current_milestone}</td>
                          <td className="px-4 py-2">{formatDate(journey.created_at)}</td>
                          <td className="px-4 py-2">
                            <button 
                              onClick={() => {
                                setSelectedJourneyId(journey.id);
                                setActiveTab('messages');
                              }}
                              className="text-blue-500 hover:underline"
                            >
                              View Messages
                            </button>
                          </td>
                        </tr>
                      ))}
                    {journeys.filter(journey => journey.user_id === selectedUserId).length === 0 && (
                      <tr>
                        <td colSpan={5} className="px-4 py-2 text-center text-gray-500">
                          No journeys found for this user
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Journeys Tab Content */}
      {activeTab === 'journeys' && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Journeys</h2>
          {loading.journeys ? (
            <p className="text-center">Loading journeys...</p>
          ) : error.journeys ? (
            <p className="text-red-500 text-center">{error.journeys}</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white dark:bg-slate-800 rounded-lg overflow-hidden shadow">
                <thead className="bg-gray-100 dark:bg-slate-700">
                  <tr>
                    <th className="px-4 py-2 text-left">ID</th>
                    <th className="px-4 py-2 text-left">User</th>
                    <th className="px-4 py-2 text-left">Status</th>
                    <th className="px-4 py-2 text-left">Milestone</th>
                    <th className="px-4 py-2 text-left">Room</th>
                    <th className="px-4 py-2 text-left">Purpose</th>
                    <th className="px-4 py-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {journeys.map((journey) => (
                    <tr key={journey.id} className="border-t dark:border-slate-600">
                      <td className="px-4 py-2">{journey.id}</td>
                      <td className="px-4 py-2">{getUserNameById(journey.user_id)}</td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-1 rounded text-xs ${
                          journey.status === 'completed' 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' 
                            : journey.status === 'abandoned'
                            ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                            : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
                        }`}>
                          {journey.status}
                        </span>
                      </td>
                      <td className="px-4 py-2">{journey.current_milestone}</td>
                      <td className="px-4 py-2">{journey.room || '-'}</td>
                      <td className="px-4 py-2">{journey.renovation_purpose || '-'}</td>
                      <td className="px-4 py-2">
                        <button 
                          onClick={() => {
                            setSelectedJourneyId(journey.id);
                            setActiveTab('messages');
                          }}
                          className="text-blue-500 hover:underline"
                        >
                          View Messages
                        </button>
                      </td>
                    </tr>
                  ))}
                  {journeys.length === 0 && (
                    <tr>
                      <td colSpan={7} className="px-4 py-2 text-center text-gray-500">
                        No journeys found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
      
      {/* Messages Tab Content */}
      {activeTab === 'messages' && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">
              {selectedJourneyId 
                ? `Messages for Journey #${selectedJourneyId}` 
                : 'All Messages'}
            </h2>
            
            {selectedJourneyId && (
              <button 
                onClick={() => setSelectedJourneyId(null)}
                className="text-blue-500 hover:underline"
              >
                View All Messages
              </button>
            )}
          </div>
          
          {/* User filter for messages */}
          <div className="mb-4 flex items-center">
            <label htmlFor="userFilter" className="mr-2">Filter by User ID:</label>
            <select 
              id="userFilter"
              className="border p-2 rounded dark:bg-slate-700 dark:border-slate-600"
              value={messageUserFilter || ""}
              onChange={(e) => {
                const value = e.target.value;
                setMessageUserFilter(value ? parseInt(value) : null);
              }}
            >
              <option value="">All Users</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>
                  {user.id} - {getUserNameById(user.id)}
                </option>
              ))}
            </select>
            
            {messageUserFilter && (
              <button 
                onClick={() => setMessageUserFilter(null)}
                className="ml-2 text-blue-500 hover:underline"
              >
                Clear Filter
              </button>
            )}
          </div>
          
          {loading.messages ? (
            <p className="text-center">Loading messages...</p>
          ) : error.messages ? (
            <p className="text-red-500 text-center">{error.messages}</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white dark:bg-slate-800 rounded-lg overflow-hidden shadow">
                <thead className="bg-gray-100 dark:bg-slate-700">
                  <tr>
                    <th className="px-4 py-2 text-left">ID</th>
                    <th className="px-4 py-2 text-left">Journey</th>
                    <th className="px-4 py-2 text-left">User</th>
                    <th className="px-4 py-2 text-left">Speaker</th>
                    <th className="px-4 py-2 text-left">Milestone</th>
                    <th className="px-4 py-2 text-left">Content</th>
                    <th className="px-4 py-2 text-left">Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredMessages.map((message) => (
                    <tr key={message.id} className="border-t dark:border-slate-600">
                      <td className="px-4 py-2">{message.id}</td>
                      <td className="px-4 py-2">{message.journey_id}</td>
                      <td className="px-4 py-2">{getUserNameById(message.user_id)}</td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-1 rounded text-xs ${
                          message.speaker === 'user'
                            ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300'
                            : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                        }`}>
                          {message.speaker}
                        </span>
                      </td>
                      <td className="px-4 py-2">{message.current_milestone}</td>
                      <td className="px-4 py-2 max-w-md truncate">{message.content}</td>
                      <td className="px-4 py-2">{message.timestamp ? formatDate(message.timestamp) : '-'}</td>
                    </tr>
                  ))}
                  {filteredMessages.length === 0 && (
                    <tr>
                      <td colSpan={7} className="px-4 py-2 text-center text-gray-500">
                        {messageUserFilter ? `No messages found for user ID ${messageUserFilter}` : 'No messages found'}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
      
      {/* Refresh Button */}
      <div className="mt-6 flex justify-center">
        <button
          onClick={() => {
            if (activeTab === 'users') {
              // Use the query client to invalidate and refetch users data
              queryClient.invalidateQueries({ queryKey: ['users'] });
            } else if (activeTab === 'journeys') {
              // Use the query client to invalidate and refetch journeys data
              queryClient.invalidateQueries({ queryKey: ['journeys'] });
            } else if (activeTab === 'messages') {
              // Use the query client to invalidate and refetch messages data
              queryClient.invalidateQueries({ queryKey: ['messages', selectedJourneyId] });
            }
          }}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Refresh Data
        </button>
      </div>
    </div>
  );
} 