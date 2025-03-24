/**
 * Conversation.tsx
 * 
 * This component displays the conversation between the user and the assistant.
 * It fetches existing messages and allows the user to send new messages.
 * The component demonstrates how to use TanStack Query for data fetching and mutations.
 */

import { useState, useRef, useEffect } from 'react';
import { useGetMessages, useSendMessage, Message as MessageType, JourneyStateResponse } from '@/api';
import { useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/api/hooks';

/**
 * ConversationProps
 * @property {number} userId - The ID of the current user
 * @property {number} journeyId - The ID of the current journey
 * @property {function} onJourneyStateUpdate - Optional callback when journey state is updated
 */
interface ConversationProps {
  userId: number;
  journeyId: number;
  onJourneyStateUpdate?: (state: JourneyStateResponse) => void;
}

/**
 * MessageProps
 * @property {MessageType} message - The message to display
 */
interface MessageProps {
  message: MessageType;
}

/**
 * Renders a single message in the conversation.
 * Styles differ based on whether the message is from the user or the assistant.
 * 
 * @param message - The message to display
 */
const Message = ({ message }: MessageProps) => {
  const isUser = message.speaker === 'user';
  
  return (
    <div
      className={`mb-4 ${
        isUser ? 'text-right' : 'text-left'
      }`}
    >
      <div
        className={`inline-block px-4 py-2 rounded-lg max-w-[80%] ${
          isUser
            ? 'bg-blue-500 text-white rounded-br-none'
            : 'bg-gray-200 dark:bg-slate-700 text-gray-800 dark:text-white rounded-bl-none'
        }`}
      >
        <p className="text-sm">{message.content}</p>
      </div>
      <div className="text-xs text-gray-500 mt-1">
        {new Date(message.timestamp).toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        })}
      </div>
    </div>
  );
};

/**
 * Conversation component displays messages and allows sending new ones.
 * Uses React Query for data fetching and mutations.
 * 
 * @param userId - ID of the current user
 * @param journeyId - ID of the current journey
 * @param onJourneyStateUpdate - Optional callback when journey state is updated
 */
export function Conversation({ userId, journeyId, onJourneyStateUpdate }: ConversationProps) {
  // State for the message input
  const [messageText, setMessageText] = useState('');
  
  // State for optimistic UI updates
  const [optimisticMessages, setOptimisticMessages] = useState<MessageType[]>([]);
  
  // Ref for auto-scrolling
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Get query client for cache updates
  const queryClient = useQueryClient();
  
  // Fetch messages for the journey
  const { 
    data: messages,
    isLoading,
    isError,
    error,
    refetch
  } = useGetMessages(journeyId);
  
  // Clear optimistic messages when new data is loaded
  useEffect(() => {
    if (messages && messages.length > 0) {
      setOptimisticMessages([]);
    }
  }, [messages]);
  
  // Refetch messages when component mounts or journey changes
  useEffect(() => {
    // Immediately refetch messages when the component mounts or journey changes
    refetch();
    
    // Set up periodic refreshing every 30 seconds
    const intervalId = setInterval(() => {
      refetch();
    }, 30000);
    
    // Clean up interval on unmount
    return () => clearInterval(intervalId);
  }, [journeyId, refetch]);
  
  // Mutation for sending messages with the new API
  const { 
    mutate: sendMessage,
    isPending: isSending
  } = useSendMessage({
    onSuccess: (response) => {
      // Create a proper message object from the response
      const assistantMessage: MessageType = {
        id: response.message.id || Date.now(), // Use the ID from the server or generate one
        user_id: response.message.user_id,
        journey_id: response.message.journey_id,
        speaker: 'assistant',
        content: response.message.content,
        timestamp: response.message.timestamp || new Date().toISOString(),
        current_milestone: response.message.current_milestone
      };
      
      // Add to optimistic messages for immediate display
      // Instead of clearing previous optimistic messages, we append to them
      setOptimisticMessages(prev => [...prev, assistantMessage]);
      
      // Directly update the cache with new messages
      queryClient.setQueryData(
        queryKeys.messages.byJourney(response.message.journey_id),
        (oldData: MessageType[] | undefined) => {
          // If we have existing data, add our new messages without removing old ones
          if (oldData) {
            return [...oldData, assistantMessage];
          }
          // If no existing data, start with this message
          return [assistantMessage];
        }
      );
      
      // Call the callback with the updated journey state
      if (onJourneyStateUpdate) {
        onJourneyStateUpdate(response.journey_state);
      }
      
      // Log detailed response in development environment
      if (process.env.NODE_ENV === 'development') {
        console.group('Message Response');
        console.log('Response text:', response.message.content);
        console.log('Journey state:', response.journey_state);
        console.groupEnd();
      }
    }
  });
  
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, optimisticMessages]);
  
  // Handle sending a new message
  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!messageText.trim() || isSending) return;
    
    // Create optimistic user message for immediate UI update
    const optimisticUserMessage: MessageType = {
      id: Date.now(), // Temporary ID
      journey_id: journeyId,
      user_id: userId,
      speaker: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
      current_milestone: messages?.[messages.length - 1]?.current_milestone || 1 // Use the milestone from existing messages or default to 1
    };
    
    // Add to optimistic messages
    setOptimisticMessages(prev => [...prev, optimisticUserMessage]);
    
    // Update the cache with the user message immediately
    queryClient.setQueryData(
      queryKeys.messages.byJourney(journeyId),
      (oldData: MessageType[] | undefined) => {
        if (oldData) {
          return [...oldData, optimisticUserMessage];
        }
        return [optimisticUserMessage];
      }
    );
    
    // Send the actual message
    sendMessage({
      user_id: userId,
      journey_id: journeyId,
      content: messageText,
    });
    
    // Clear the input
    setMessageText('');
  };
  
  // Create a function to get unique messages by ID
  const getUniqueMessages = (messages: MessageType[]): MessageType[] => {
    const uniqueMap = new Map<number, MessageType>();
    
    messages.forEach(message => {
      uniqueMap.set(message.id, message);
    });
    
    return Array.from(uniqueMap.values());
  };
  
  // Combine fetched messages with optimistic ones, ensuring order and uniqueness
  const allMessages = getUniqueMessages([
    ...(messages || []),
    ...optimisticMessages
  ]).sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  
  return (
    <div className="_Conversation flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4">
        {isLoading && !allMessages.length ? (
          <div className="flex justify-center items-center h-full">
            <p className="text-gray-500">Loading messages...</p>
          </div>
        ) : isError ? (
          <div className="text-red-500 text-center">
            <p>Error: {error.message || 'Failed to load messages'}</p>
            <button 
              onClick={() => refetch()} 
              className="mt-2 bg-blue-500 hover:bg-blue-600 text-white py-1 px-3 rounded-md text-sm"
            >
              Try Again
            </button>
          </div>
        ) : allMessages.length > 0 ? (
          <div>
            {allMessages.map((message) => (
              <Message key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </div>
        ) : (
          <div className="flex justify-center items-center h-full">
            <p className="text-gray-500">
              No messages yet. Start the conversation!
            </p>
          </div>
        )}
      </div>
      
      {/* Message input */}
      <div className="border-t p-4 bg-white dark:bg-slate-800">
        <form onSubmit={handleSendMessage} className="flex">
          <input
            type="text"
            value={messageText}
            onChange={(e) => setMessageText(e.target.value)}
            disabled={isSending}
            placeholder="Type your message..."
            className="flex-1 border border-gray-300 rounded-l-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isSending || !messageText.trim()}
            className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-r-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSending ? 'Sending...' : 'Send'}
          </button>
        </form>
        
        {/* Show sending indicator when a message is being sent */}
        {isSending && (
          <div className="mt-2 text-xs text-gray-500 flex items-center">
            <svg className="animate-spin -ml-1 mr-2 h-3 w-3 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing with Sentinel...
          </div>
        )}
      </div>
    </div>
  );
} 