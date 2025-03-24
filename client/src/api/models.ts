/**
 * models.ts
 * 
 * This file contains TypeScript interfaces for the State Machine Demo API.
 * These interfaces represent the data structures returned by the API.
 * They are used throughout the application for type safety and autocomplete support.
 */

// User model
export interface User {
  id: number;
  first_name: string | null;
  last_name: string | null;
  created_at: string;
}

// Journey model representing a renovation planning journey
export interface Journey {
  id: number;
  user_id: number;
  current_milestone: number;
  status: 'in_progress' | 'completed' | 'abandoned';
  
  // Milestone 1: Project Basics
  room: string | null; // kitchen, bathroom, bedroom, living room, basement
  renovation_purpose: string | null; // aesthetic, functional, repair, expand space, modernize
  
  // Milestone 2: Budget and Timeline
  budget_range: string | null; // low, medium, high
  timeline: string | null; // weeks, months
  
  // Milestone 3: Style Preferences and Plan
  style_preference: string | null; // modern, traditional, rustic, minimalist, contemporary
  priority_feature: string | null; // increased storage, natural lighting, open space, energy efficiency, smart home features
  
  // Milestone completion tracking
  milestone1_completed: boolean;
  milestone2_completed: boolean;
  milestone3_completed: boolean;
  milestone1_completed_at: string | null;
  milestone2_completed_at: string | null;
  milestone3_completed_at: string | null;
  
  created_at: string;
  updated_at: string;
}

// Message model for conversation messages
export interface Message {
  id: number;
  user_id: number;
  journey_id: number;
  speaker: 'user' | 'assistant';
  content: string;
  current_milestone: number;
  timestamp: string;
}

// User attribute model
export interface UserAttribute {
  id: number;
  user_id: number;
  attribute_key: string;
  attribute_value: string;
  source_message_id: number;
  created_at: string;
}

// Session response model
export interface SessionResponse {
  user_id: number;
  journey_id: number;
  current_milestone: number;
  status: string;
  recent_messages: Message[];
}

// Journey state response model
export interface JourneyStateResponse {
  milestone: number;
  completed_checkpoints: string[];
  status: 'in_progress' | 'completed' | 'abandoned';
}

// Process message response model
export interface ProcessMessageResponse {
  journey: Journey;
  system_response: string;
}

// Chat response model for sending messages
export interface ChatResponse {
  message: Message;
  journey_state: JourneyStateResponse;
}

// Checkpoint values for milestone 1
export type RoomType = 'kitchen' | 'bathroom' | 'bedroom' | 'living room' | 'basement';
export type RenovationPurpose = 'aesthetic' | 'functional' | 'repair' | 'expand space' | 'modernize';

// Checkpoint values for milestone 2
export type BudgetRange = 'low' | 'medium' | 'high';
export type Timeline = 'weeks' | 'months';

// Checkpoint values for milestone 3
export type StylePreference = 'modern' | 'traditional' | 'rustic' | 'minimalist' | 'contemporary';
export type PriorityFeature = 'increased storage' | 'natural lighting' | 'open space' | 'energy efficiency' | 'smart home features'; 