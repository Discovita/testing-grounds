/**
 * api.ts
 *
 * This file contains API service functions grouped by entity.
 * These functions handle the actual HTTP requests to the backend API.
 * They are used by the React Query hooks to fetch and mutate data.
 */

import apiClient from "./apiClient";
import {
  User,
  Journey,
  Message,
  SessionResponse,
  JourneyStateResponse,
  ProcessMessageResponse,
  ChatResponse,
} from "./models";

/**
 * User API functions
 * These functions handle all user-related API requests.
 */
export const userApi = {
  // Create a new user
  createUser: async (data: {
    first_name?: string;
    last_name?: string;
  }): Promise<User> => {
    console.log("[api.createUser]");
    const response = await apiClient.post<User>("/users", data);
    return response.data;
  },

  // Get user details
  getUser: async (userId: number): Promise<User> => {
    console.log("[api.getUser]");
    const response = await apiClient.get<User>(`/users/${userId}`);
    return response.data;
  },

  // Update user details
  updateUser: async (
    userId: number,
    data: { first_name?: string; last_name?: string }
  ): Promise<User> => {
    console.log("[api.updateUser]");
    const response = await apiClient.put<User>(`/users/${userId}`, data);
    return response.data;
  },
};

/**
 * Session API functions
 * These functions handle session management for users.
 */
export const sessionApi = {
  // Start a new session or resume an existing one
  startSession: async (data: {
    user_id?: number;
    first_name?: string;
    last_name?: string;
  }): Promise<SessionResponse> => {
    console.log("[api.startSession]");
    const response = await apiClient.post<SessionResponse>("/sessions", data);
    return response.data;
  },

  // Resume an existing session
  resumeSession: async (userId: number): Promise<SessionResponse> => {
    console.log("[api.resumeSession]");
    const response = await apiClient.get<SessionResponse>(
      `/sessions/${userId}`
    );
    return response.data;
  },
};

/**
 * Journey API functions
 * These functions handle all journey-related API requests.
 */
export const journeyApi = {
  // Create a new journey for a user
  createJourney: async (userId: number): Promise<Journey> => {
    console.log("[api.createJourney]");
    const response = await apiClient.post<Journey>("/journeys", {
      user_id: userId,
    });
    return response.data;
  },

  // Get journey details
  getJourney: async (journeyId: number): Promise<Journey> => {
    console.log("[api.getJourney]");
    const response = await apiClient.get<Journey>(`/journeys/${journeyId}`);
    return response.data;
  },

  // Update journey details
  updateJourney: async (
    journeyId: number,
    data: Partial<Journey>
  ): Promise<Journey> => {
    console.log("[api.updateJourney]");
    const response = await apiClient.put<Journey>(
      `/journeys/${journeyId}`,
      data
    );
    return response.data;
  },

  // Get the active journey for a user
  getActiveJourney: async (userId: number): Promise<Journey> => {
    console.log("[api.getActiveJourney]");
    const response = await apiClient.get<Journey>(`/journeys/active/${userId}`);
    return response.data;
  },

  // Save a checkpoint value for a journey
  saveCheckpoint: async (
    journeyId: number,
    checkpoint: string,
    value: string
  ): Promise<{ message: string }> => {
    console.log("[api.saveCheckpoint]");
    const response = await apiClient.post<{ message: string }>(
      `/journeys/${journeyId}/checkpoints/${checkpoint}`,
      { value }
    );
    return response.data;
  },

  // Advance to the next milestone
  advanceMilestone: async (journeyId: number): Promise<{ message: string }> => {
    console.log("[api.advanceMilestone]");
    const response = await apiClient.post<{ message: string }>(
      `/journeys/${journeyId}/advance`,
      {}
    );
    return response.data;
  },

  // Mark a journey as complete
  completeJourney: async (journeyId: number): Promise<{ message: string }> => {
    console.log("[api.completeJourney]");
    const response = await apiClient.post<{ message: string }>(
      `/journeys/${journeyId}/complete`,
      {}
    );
    return response.data;
  },

  // Get the current state of a user's journey for the LLM
  getJourneyState: async (userId: number): Promise<JourneyStateResponse> => {
    console.log("[api.getJourneyState]");
    const response = await apiClient.get<JourneyStateResponse>(
      `/journeys/state/${userId}`
    );
    return response.data;
  },
};

/**
 * Message API functions
 * These functions handle all message-related API requests.
 */
export const messageApi = {
  // Save a new message
  saveMessage: async (data: {
    user_id: number;
    journey_id: number;
    speaker: "user" | "assistant";
    content: string;
    current_milestone: number;
  }): Promise<Message> => {
    console.log("[api.saveMessage]");
    const response = await apiClient.post<Message>("/messages", data);
    return response.data;
  },

  // Get messages for a journey
  getMessages: async (
    journeyId: number,
    options: { limit?: number; offset?: number } = {}
  ): Promise<Message[]> => {
    console.log("[api.getMessages]");
    const { limit = 50, offset = 0 } = options;
    const response = await apiClient.get<Message[]>(
      `/messages/${journeyId}?limit=${limit}&offset=${offset}`
    );
    return response.data;
  },

  // Process a user message and get a response with updated journey state
  sendMessage: async (data: {
    user_id: number;
    journey_id: number;
    content: string;
  }): Promise<ChatResponse> => {
    console.log("[api.sendMessage]");
    const response = await apiClient.post<ChatResponse>("/messages/", data);
    return response.data;
  },

  // Legacy process message endpoint
  processMessage: async (data: {
    user_id: number;
    journey_id: number;
    content: string;
  }): Promise<ProcessMessageResponse> => {
    console.log("[api.processMessage]");
    const response = await apiClient.post<ProcessMessageResponse>(
      "/messages/process",
      data
    );
    return response.data;
  },
};
