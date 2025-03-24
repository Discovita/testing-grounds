/**
 * hooks.ts
 * 
 * This file contains React Query hooks for the State Machine Demo API.
 * These hooks provide a convenient way to interact with the API in React components.
 * They handle caching, loading states, errors, and data mutations.
 */

import { 
  useQuery, 
  useMutation, 
  useQueryClient,
  UseQueryOptions,
  UseMutationOptions 
} from '@tanstack/react-query';
import { userApi, sessionApi, journeyApi, messageApi } from './api';
import {
  User,
  Journey,
  Message,
  SessionResponse,
  JourneyStateResponse,
  ProcessMessageResponse,
  ChatResponse
} from './models';

// Query keys for caching
export const queryKeys = {
  users: {
    all: ['users'] as const,
    detail: (id: number) => [...queryKeys.users.all, id] as const,
  },
  sessions: {
    user: (id: number) => ['sessions', id] as const,
  },
  journeys: {
    all: ['journeys'] as const,
    detail: (id: number) => [...queryKeys.journeys.all, id] as const,
    active: (userId: number) => [...queryKeys.journeys.all, 'active', userId] as const,
    state: (userId: number) => [...queryKeys.journeys.all, 'state', userId] as const,
  },
  messages: {
    byJourney: (journeyId: number) => ['messages', journeyId] as const,
  },
};

/**
 * User Hooks
 * Hooks for interacting with user-related API endpoints
 */

// Hook for creating a new user
export const useCreateUser = (
  options?: UseMutationOptions<
    User,
    Error,
    { first_name?: string; last_name?: string }
  >
) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: userApi.createUser,
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.users.detail(data.id), data);
      queryClient.invalidateQueries({ queryKey: queryKeys.users.all });
    },
    ...options,
  });
};

// Hook for getting user details
export const useGetUser = (
  userId: number,
  options?: Omit<UseQueryOptions<User>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: queryKeys.users.detail(userId),
    queryFn: () => userApi.getUser(userId),
    ...options,
  });
};

// Hook for updating user details
export const useUpdateUser = (
  userId: number,
  options?: UseMutationOptions<
    User,
    Error,
    { first_name?: string; last_name?: string }
  >
) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data) => userApi.updateUser(userId, data),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.users.detail(userId), data);
    },
    ...options,
  });
};

/**
 * Session Hooks
 * Hooks for session management
 */

// Hook for starting a new session
export const useStartSession = (
  options?: UseMutationOptions<
    SessionResponse,
    Error,
    { user_id?: number; first_name?: string; last_name?: string }
  >
) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: sessionApi.startSession,
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.sessions.user(data.user_id), data);
      queryClient.setQueryData(queryKeys.journeys.detail(data.journey_id), {
        id: data.journey_id,
        user_id: data.user_id,
        current_milestone: data.current_milestone,
        status: data.status,
      });
    },
    ...options,
  });
};

// Hook for resuming an existing session
export const useResumeSession = (
  userId: number,
  options?: Omit<UseQueryOptions<SessionResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: queryKeys.sessions.user(userId),
    queryFn: () => sessionApi.resumeSession(userId),
    // Data from this query is handled in component level
    ...options,
  });
};

/**
 * Journey Hooks
 * Hooks for interacting with journey-related API endpoints
 */

// Hook for creating a new journey
export const useCreateJourney = (
  options?: UseMutationOptions<Journey, Error, number>
) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: journeyApi.createJourney,
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.journeys.detail(data.id), data);
      queryClient.invalidateQueries({ queryKey: queryKeys.journeys.active(data.user_id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.journeys.all });
    },
    ...options,
  });
};

// Hook for getting journey details
export const useGetJourney = (
  journeyId: number,
  options?: Omit<UseQueryOptions<Journey>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: queryKeys.journeys.detail(journeyId),
    queryFn: () => journeyApi.getJourney(journeyId),
    ...options,
  });
};

// Hook for updating journey details
export const useUpdateJourney = (
  journeyId: number,
  options?: UseMutationOptions<Journey, Error, Partial<Journey>>
) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data) => journeyApi.updateJourney(journeyId, data),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.journeys.detail(journeyId), data);
      queryClient.invalidateQueries({ queryKey: queryKeys.journeys.active(data.user_id) });
    },
    ...options,
  });
};

// Hook for getting the active journey for a user
export const useGetActiveJourney = (
  userId: number,
  options?: Omit<UseQueryOptions<Journey>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: queryKeys.journeys.active(userId),
    queryFn: () => journeyApi.getActiveJourney(userId),
    ...options,
  });
};

// Hook for saving a checkpoint value
export const useSaveCheckpoint = (
  options?: UseMutationOptions<
    { message: string },
    Error,
    { journeyId: number; checkpoint: string; value: string }
  >
) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ journeyId, checkpoint, value }) => 
      journeyApi.saveCheckpoint(journeyId, checkpoint, value),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.journeys.detail(variables.journeyId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.journeys.state(variables.journeyId) });
    },
    ...options,
  });
};

// Hook for advancing to the next milestone
export const useAdvanceMilestone = (
  options?: UseMutationOptions<
    { message: string },
    Error,
    number
  >
) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: journeyApi.advanceMilestone,
    onSuccess: (_, journeyId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.journeys.detail(journeyId) });
      // We can't know the user ID here, so we need to invalidate all journeys
      queryClient.invalidateQueries({ queryKey: queryKeys.journeys.all });
    },
    ...options,
  });
};

// Hook for completing a journey
export const useCompleteJourney = (
  options?: UseMutationOptions<
    { message: string },
    Error,
    number
  >
) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: journeyApi.completeJourney,
    onSuccess: (_, journeyId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.journeys.detail(journeyId) });
      // We can't know the user ID here, so we need to invalidate all journeys
      queryClient.invalidateQueries({ queryKey: queryKeys.journeys.all });
    },
    ...options,
  });
};

// Hook for getting the journey state
export const useGetJourneyState = (
  userId: number,
  options?: Omit<UseQueryOptions<JourneyStateResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: queryKeys.journeys.state(userId),
    queryFn: () => journeyApi.getJourneyState(userId),
    ...options,
  });
};

/**
 * Message Hooks
 * Hooks for interacting with message-related API endpoints
 */

// Hook for saving a new message
export const useSaveMessage = (
  options?: UseMutationOptions<
    Message,
    Error,
    {
      user_id: number;
      journey_id: number;
      speaker: 'user' | 'assistant';
      content: string;
      current_milestone: number;
    }
  >
) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: messageApi.saveMessage,
    onSuccess: (data) => {
      // Update the messages list by adding the new message
      queryClient.setQueryData<Message[]>(
        queryKeys.messages.byJourney(data.journey_id),
        (old) => old ? [...old, data] : [data]
      );
    },
    ...options,
  });
};

// Hook for getting messages for a journey
export const useGetMessages = (
  journeyId: number,
  options?: {
    limit?: number;
    offset?: number;
    queryOptions?: Omit<UseQueryOptions<Message[]>, 'queryKey' | 'queryFn'>;
  }
) => {
  const { limit, offset, queryOptions } = options || {};
  
  return useQuery({
    queryKey: [...queryKeys.messages.byJourney(journeyId), { limit, offset }],
    queryFn: () => messageApi.getMessages(journeyId, { limit, offset }),
    ...queryOptions,
  });
};

// Hook for processing a message with the legacy API (DEPRECATED)
export const useProcessMessage = (
  options?: UseMutationOptions<
    ProcessMessageResponse,
    Error,
    {
      user_id: number;
      journey_id: number;
      content: string;
    }
  >
) => {
  console.warn(
    "useProcessMessage is deprecated and will be removed in a future version. " +
    "Use useSendMessage instead for improved journey state tracking."
  );
  
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: messageApi.processMessage,
    onSuccess: (data, variables) => {
      // Update messages cache
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.messages.byJourney(variables.journey_id) 
      });
      
      // Update journey cache
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.journeys.detail(variables.journey_id) 
      });
    },
    ...options,
  });
};

// Hook for sending a message and processing the response with updated journey state
export const useSendMessage = (
  options?: UseMutationOptions<
    ChatResponse,
    Error,
    {
      user_id: number;
      journey_id: number;
      content: string;
    }
  >
) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: messageApi.sendMessage,
    onSuccess: (data, variables) => {
      // Update messages cache
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.messages.byJourney(variables.journey_id) 
      });
      
      // Update journey state cache
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.journeys.detail(variables.journey_id) 
      });
      
      // Update journey state cache
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.journeys.state(variables.user_id) 
      });
    },
    ...options,
  });
}; 