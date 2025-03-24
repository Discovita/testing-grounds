# State Machine Demo API Documentation

## Overview

The State Machine Demo API provides functionality for guiding users through a renovation planning journey using a state machine approach. The API implements a conversation flow that progresses through different milestones, extracting and persisting information at each stage.

## Core Concepts

### Journey State Machine

The application implements a state machine to guide users through a conversation flow for planning a home renovation. Each journey consists of:

- **Milestones**: Major stages of the renovation planning process (3 total)
- **Checkpoints**: Specific pieces of information collected within each milestone
- **State Transitions**: Rules for advancing from one milestone to the next

### Milestones

1. **Project Basics** - Collects fundamental information about the renovation project:
   - Which room is being renovated
   - Primary purpose of the renovation (aesthetic, functional, repair)

2. **Budget and Timeline** - Establishes constraints for the project:
   - Approximate budget range (low, medium, high)
   - Timeline expectations (weeks, months)

3. **Style Preferences and Plan** - Captures design preferences:
   - General style preference (modern, traditional, etc.)
   - Priority features for the renovation

### State Progression

A journey progresses through these stages based on the information collected:

1. The user provides information through conversation
2. The system extracts and saves checkpoint data
3. When all checkpoints in a milestone are complete, the milestone is marked as completed
4. The system can advance to the next milestone when the current one is complete
5. When all milestones are complete, the journey is marked as completed

## Authentication

The API currently uses simple token authentication for development purposes. Authentication is not strictly enforced in the demo implementation, but production implementations would require proper authentication.

## Base URL

```
http://localhost:8000
```

## Models

### User

Represents a person interacting with the system.

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| first_name | string | User's first name (optional) |
| last_name | string | User's last name (optional) |
| created_at | datetime | When the user was created |

### Journey

Represents a renovation planning journey for a user.

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| user_id | integer | ID of the user this journey belongs to |
| current_milestone | integer | Current milestone (1-3) |
| status | string | Journey status: "in_progress", "completed", or "abandoned" |
| room | string | Which room is being renovated (Milestone 1) |
| renovation_purpose | string | Purpose of renovation (Milestone 1) |
| budget_range | string | Budget range: "low", "medium", "high" (Milestone 2) |
| timeline | string | Timeframe: "weeks", "months" (Milestone 2) |
| style_preference | string | Style preference (Milestone 3) |
| priority_feature | string | Priority feature (Milestone 3) |
| milestone1_completed | boolean | Whether Milestone 1 is complete |
| milestone2_completed | boolean | Whether Milestone 2 is complete | 
| milestone3_completed | boolean | Whether Milestone 3 is complete |
| milestone1_completed_at | datetime | When Milestone 1 was completed |
| milestone2_completed_at | datetime | When Milestone 2 was completed |
| milestone3_completed_at | datetime | When Milestone 3 was completed |
| created_at | datetime | When the journey was created |
| updated_at | datetime | When the journey was last updated |

### Message

Represents a single message in the conversation.

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| user_id | integer | ID of the user this message belongs to |
| journey_id | integer | ID of the journey this message belongs to |
| speaker | string | Who sent the message: "user" or "assistant" |
| content | string | The message content |
| current_milestone | integer | Which milestone was active when the message was sent |
| timestamp | datetime | When the message was sent |

### UserAttribute

Represents extracted information about a user.

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| user_id | integer | ID of the user |
| attribute_key | string | Type of information (e.g., "has_children") |
| attribute_value | string | Value of the information |
| source_message_id | integer | ID of the message where this information was extracted |
| created_at | datetime | When the attribute was created |

## API Endpoints

### Health Check

#### GET /health

Check if the API is running.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "api": "State Machine Demo API"
}
```

### User Management

#### POST /users

Create a new user.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2023-06-15T12:30:45.123456"
}
```

#### GET /users/{user_id}

Get user details.

**Path Parameters:**
- `user_id` (integer): ID of the user to retrieve

**Response:**
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2023-06-15T12:30:45.123456"
}
```

#### PUT /users/{user_id}

Update user details.

**Path Parameters:**
- `user_id` (integer): ID of the user to update

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Smith"
}
```

**Response:**
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Smith",
  "created_at": "2023-06-15T12:30:45.123456"
}
```

### Session Management

#### POST /sessions

Start a new session or resume an existing one.

**Request Body:**
```json
{
  "user_id": 1,
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "user_id": 1,
  "journey_id": 1,
  "current_milestone": 1,
  "status": "in_progress",
  "recent_messages": [
    {
      "id": 1,
      "user_id": 1,
      "journey_id": 1,
      "speaker": "assistant",
      "content": "Welcome to the renovation planner. Which room are you planning to renovate?",
      "current_milestone": 1,
      "timestamp": "2023-06-15T12:30:45.123456"
    }
  ]
}
```

#### GET /sessions/{user_id}

Resume an existing session.

**Path Parameters:**
- `user_id` (integer): ID of the user

**Response:**
```json
{
  "user_id": 1,
  "journey_id": 1,
  "current_milestone": 1,
  "status": "in_progress",
  "recent_messages": [
    {
      "id": 1,
      "user_id": 1,
      "journey_id": 1,
      "speaker": "assistant",
      "content": "Welcome to the renovation planner. Which room are you planning to renovate?",
      "current_milestone": 1,
      "timestamp": "2023-06-15T12:30:45.123456"
    }
  ]
}
```

### Journey Management

#### POST /journeys

Create a new journey for a user.

**Request Body:**
```json
{
  "user_id": 1
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "current_milestone": 1,
  "status": "in_progress",
  "room": null,
  "renovation_purpose": null,
  "budget_range": null,
  "timeline": null,
  "style_preference": null,
  "priority_feature": null,
  "milestone1_completed": false,
  "milestone2_completed": false,
  "milestone3_completed": false,
  "milestone1_completed_at": null,
  "milestone2_completed_at": null,
  "milestone3_completed_at": null,
  "created_at": "2023-06-15T12:30:45.123456",
  "updated_at": "2023-06-15T12:30:45.123456"
}
```

#### GET /journeys/{journey_id}

Get journey details.

**Path Parameters:**
- `journey_id` (integer): ID of the journey to retrieve

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "current_milestone": 1,
  "status": "in_progress",
  "room": "kitchen",
  "renovation_purpose": "functional",
  "budget_range": null,
  "timeline": null,
  "style_preference": null,
  "priority_feature": null,
  "milestone1_completed": false,
  "milestone2_completed": false,
  "milestone3_completed": false,
  "milestone1_completed_at": null,
  "milestone2_completed_at": null,
  "milestone3_completed_at": null,
  "created_at": "2023-06-15T12:30:45.123456",
  "updated_at": "2023-06-15T12:30:45.123456"
}
```

#### PUT /journeys/{journey_id}

Update journey details.

**Path Parameters:**
- `journey_id` (integer): ID of the journey to update

**Request Body:**
```json
{
  "room": "kitchen",
  "renovation_purpose": "functional"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "current_milestone": 1,
  "status": "in_progress",
  "room": "kitchen",
  "renovation_purpose": "functional",
  "budget_range": null,
  "timeline": null,
  "style_preference": null,
  "priority_feature": null,
  "milestone1_completed": false,
  "milestone2_completed": false,
  "milestone3_completed": false,
  "milestone1_completed_at": null,
  "milestone2_completed_at": null,
  "milestone3_completed_at": null,
  "created_at": "2023-06-15T12:30:45.123456",
  "updated_at": "2023-06-15T12:30:45.123456"
}
```

#### GET /journeys/active/{user_id}

Get the active journey for a user.

**Path Parameters:**
- `user_id` (integer): ID of the user

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "current_milestone": 1,
  "status": "in_progress",
  "room": "kitchen",
  "renovation_purpose": "functional",
  "budget_range": null,
  "timeline": null,
  "style_preference": null,
  "priority_feature": null,
  "milestone1_completed": false,
  "milestone2_completed": false,
  "milestone3_completed": false,
  "milestone1_completed_at": null,
  "milestone2_completed_at": null,
  "milestone3_completed_at": null,
  "created_at": "2023-06-15T12:30:45.123456",
  "updated_at": "2023-06-15T12:30:45.123456"
}
```

#### POST /journeys/{journey_id}/checkpoints/{checkpoint_name}

Save a checkpoint value for a journey.

**Path Parameters:**
- `journey_id` (integer): ID of the journey
- `checkpoint_name` (string): Name of the checkpoint (one of: "room", "renovation_purpose", "budget_range", "timeline", "style_preference", "priority_feature")

**Request Body:**
```json
{
  "value": "kitchen"
}
```

**Response:**
```json
{
  "message": "Saved checkpoint room with value kitchen"
}
```

#### POST /journeys/{journey_id}/advance

Advance to the next milestone.

**Path Parameters:**
- `journey_id` (integer): ID of the journey

**Response:**
```json
{
  "message": "Advanced to milestone 2"
}
```

#### POST /journeys/{journey_id}/complete

Mark a journey as complete.

**Path Parameters:**
- `journey_id` (integer): ID of the journey

**Response:**
```json
{
  "message": "Journey completed successfully"
}
```

#### GET /journeys/state/{user_id}

Get the current state of a user's journey for the LLM.

**Path Parameters:**
- `user_id` (integer): ID of the user

**Response:**
```json
{
  "has_journey": true,
  "milestone": 1,
  "completed_checkpoints": ["room", "renovation_purpose"],
  "milestone_completed": true
}
```

### Message Management

#### POST /messages

Save a new message.

**Request Body:**
```json
{
  "user_id": 1,
  "journey_id": 1,
  "speaker": "user",
  "content": "I want to renovate my kitchen",
  "current_milestone": 1
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "journey_id": 1,
  "speaker": "user",
  "content": "I want to renovate my kitchen",
  "current_milestone": 1,
  "timestamp": "2023-06-15T12:30:45.123456"
}
```

#### GET /messages/{journey_id}

Get messages for a journey.

**Path Parameters:**
- `journey_id` (integer): ID of the journey

**Query Parameters:**
- `limit` (integer, optional): Maximum number of messages to return (default: 50)
- `offset` (integer, optional): Number of messages to skip (default: 0)

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "journey_id": 1,
    "speaker": "assistant",
    "content": "Welcome to the renovation planner. Which room are you planning to renovate?",
    "current_milestone": 1,
    "timestamp": "2023-06-15T12:30:45.123456"
  },
  {
    "id": 2,
    "user_id": 1,
    "journey_id": 1,
    "speaker": "user",
    "content": "I want to renovate my kitchen",
    "current_milestone": 1,
    "timestamp": "2023-06-15T12:31:15.123456"
  }
]
```

#### POST /messages/process

Process a user message and update journey state.

**Request Body:**
```json
{
  "user_id": 1,
  "journey_id": 1,
  "content": "I want to renovate my kitchen to make it more functional"
}
```

**Response:**
```json
{
  "journey": {
    "id": 1,
    "user_id": 1,
    "current_milestone": 1,
    "status": "in_progress",
    "room": "kitchen",
    "renovation_purpose": "functional",
    "budget_range": null,
    "timeline": null,
    "style_preference": null,
    "priority_feature": null,
    "milestone1_completed": true,
    "milestone2_completed": false,
    "milestone3_completed": false,
    "milestone1_completed_at": "2023-06-15T12:31:45.123456",
    "milestone2_completed_at": null,
    "milestone3_completed_at": null,
    "created_at": "2023-06-15T12:30:45.123456",
    "updated_at": "2023-06-15T12:31:45.123456"
  },
  "system_response": "Great! We've established that you want to renovate your kitchen for functional purposes. Let's move on to budget and timeline considerations. What kind of budget do you have in mind? (low, medium, high)"
}
```

## Chatbot Integration

The chatbot integration in the State Machine Demo is designed to guide users through a series of milestones in their home renovation journey, using a state machine to track progress and personalize the conversation.

### Chat Processing Flow

1. **User sends a message**
   - The message is saved to the database
   - Recent messages are retrieved for context

2. **Sentinel Analysis**
   - The `Sentinel` analyzes recent messages to extract specific information
   - If relevant information is found, the journey state is updated
   - The sentinel focuses on one checkpoint at a time based on current journey state
   - Uses a faster LLM model (GPT-3.5-turbo) for efficient processing

3. **Dynamic Prompt Selection**
   - Based on the updated journey state, the system selects the most appropriate prompt template
   - The selection considers current milestone, completed checkpoints, and journey status
   - Specialized prompts handle different scenarios (e.g., when only room is known but not purpose)
   - Prompts include contextual information about what is already known about the user's journey

4. **Response Generation**
   - The selected prompt is used to create the system message for the LLM
   - Full conversation history (last 10 messages) is included for context
   - The LLM generates a response tailored to the current journey state
   - The response is saved to the database and returned to the user

### Sentinel System

The Sentinel system is a lightweight analyzer that efficiently extracts specific information from user messages without introducing significant latency.

#### Key Features

- **Focused Analysis**: Only looks for answers to the current checkpoint question
- **Minimal Context**: Uses only the last 5 messages for faster processing
- **Targeted Extraction**: Extracts only information relevant to the current milestone
- **Efficient Model**: Uses a faster LLM model to minimize latency
- **Conservative Approach**: Only updates journey state when confident

#### Implementation

The Sentinel is implemented as a separate class that:

1. Determines the active checkpoint question based on journey state
2. Builds a focused prompt for the LLM
3. Calls the LLM with specific checkpoint extraction functions
4. Updates the journey state if relevant information is found
5. Checks if milestone completion criteria are met

#### Extensibility

The Sentinel system can be extended to:

- Extract complex information beyond simple keywords
- Handle multiple checkpoints in parallel
- Implement more sophisticated completion criteria
- Support additional journey types beyond renovation

### Prompt Switching System

The prompt switching system dynamically selects the most appropriate prompt template based on the current journey state, creating a more personalized and focused conversation experience.

#### Prompt Categories

The system includes specialized prompts for different scenarios:

- **Milestone Introduction**: Introduces each milestone and its goals
- **Partial Completion**: Focuses on remaining checkpoints (e.g., "room known but purpose unknown")
- **Milestone Transition**: Summarizes completed milestones and introduces the next
- **Journey Completion**: Summarizes the entire journey when complete

#### Template Selection Logic

The prompt selection logic follows these steps:

1. Check if the journey is completed
2. Identify the current milestone
3. Check if the milestone is completed
4. If not completed, check which checkpoints are already satisfied
5. Select the appropriate template based on the combination of state factors

#### Example Prompt Templates

Different prompts are used depending on the journey state:

**Milestone 1 Introduction:**
```
You're currently in Milestone 1: Project Basics. Your goal is to help the user define:
1. Which room they want to renovate
2. The main purpose of their renovation (aesthetic, functional, repair)
```

**Room Known But Purpose Unknown:**
```
The user has already told you they want to renovate their {room}.
Now you need to understand the main purpose of their renovation.
```

**Milestone Complete:**
```
You know the user wants to renovate their {room} for {renovation_purpose} purposes.
Summarize what you've learned so far and explain that you'll now help them think about budget and timeline.
Use the advance_milestone function to move to Milestone 2.
```

#### Benefits

This approach provides several advantages:

- **Focused Conversations**: Each prompt focuses on exactly what information is needed next
- **Natural Progression**: Conversations flow naturally between milestones
- **Contextual Awareness**: The LLM always has awareness of what the user has already shared
- **Consistent Guidance**: Clear instructions guide the LLM on how to progress through the journey

### Function Calls

The LLM has access to several functions to update the journey state:

#### 1. save_checkpoint

Extracts and saves specific information provided by the user.

**Parameters:**
- `checkpoint_name`: Name of the checkpoint (e.g., "room", "budget_range")
- `value`: The extracted value for the checkpoint

#### 2. advance_milestone

Advances the journey to the next milestone when the current one is complete.

**Parameters:**
- `journey_id`: ID of the journey to advance

#### 3. complete_journey

Marks the journey as complete when all milestones are done.

**Parameters:**
- `journey_id`: ID of the journey to complete

## Implementation Details

### OpenAI Integration

The system uses OpenAI's function calling capabilities to:

1. Extract checkpoint information from user messages
2. Determine when to advance milestones
3. Mark journeys as complete

The OpenAI client is configured to use functions specific to each milestone:

- `save_checkpoint`: Save an extracted value to a specific checkpoint
- `advance_milestone`: Move to the next milestone when appropriate
- `complete_journey`: Mark the journey as complete

### Fallback Mechanism

If OpenAI is unavailable or encounters an error, the system includes a fallback mechanism that:

1. Uses keyword matching to extract basic information
2. Provides template-based responses based on the current journey state
3. Continues to track milestone completion

### Database Structure

The system uses SQLite with SQLAlchemy ORM for data persistence with the following tables:

- `users`: Stores user information
- `renovation_journeys`: Stores journey state and checkpoint answers
- `messages`: Stores all conversation messages
- `user_attributes`: Stores extracted user information

## Error Handling

The API uses standard HTTP status codes for error responses:

- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

Error responses include a detail message explaining the issue:

```json
{
  "detail": "User with ID 999 not found"
}
```

## Frontend Integration Guide

### Basic Flow

1. **Start a session**:
   - Call `POST /sessions` with the user information
   - Store the returned `user_id` and `journey_id` for subsequent requests

2. **Display conversation**:
   - Show messages from the `recent_messages` array
   - Order by `timestamp`
   - Display user messages and assistant messages differently

3. **Send user messages**:
   - Call `POST /messages/process` with the user's message
   - Add the user message to the conversation
   - Add the system response to the conversation
   - Update the displayed journey state

4. **Track milestone progression**:
   - Monitor `current_milestone` in the journey response
   - Update UI to reflect the current milestone
   - Use `completed_checkpoints` to show progress within the milestone

5. **Journey completion**:
   - When `status` becomes "completed", show completion UI
   - Option to start a new journey or exit

### Handling State

The frontend should maintain:

1. The current user ID and journey ID
2. The conversation history (all messages)
3. The current milestone and checkpoints completed
4. The journey status

### Example Implementation

```javascript
// Initialize session
async function startSession(firstName, lastName) {
  const response = await fetch('/sessions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      first_name: firstName,
      last_name: lastName
    }),
  });
  
  const session = await response.json();
  
  // Store session data
  localStorage.setItem('userId', session.user_id);
  localStorage.setItem('journeyId', session.journey_id);
  
  // Display initial messages
  displayMessages(session.recent_messages);
  
  return session;
}

// Send a message
async function sendMessage(message) {
  const userId = localStorage.getItem('userId');
  const journeyId = localStorage.getItem('journeyId');
  
  const response = await fetch('/messages/process', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: parseInt(userId),
      journey_id: parseInt(journeyId),
      content: message
    }),
  });
  
  const result = await response.json();
  
  // Update conversation
  addMessage({
    speaker: 'user',
    content: message,
    timestamp: new Date()
  });
  
  addMessage({
    speaker: 'assistant',
    content: result.system_response,
    timestamp: new Date()
  });
  
  // Update journey state
  updateJourneyState(result.journey);
  
  return result;
}
```

## Deployment Considerations

### Environment Variables

The application requires the following environment variables:

- `DATABASE_URL`: SQLite database URL (default: `sqlite:///./state_machine_demo.db`)
- `OPENAI_API_KEY`: OpenAI API key for GPT-4o
- `OPENAI_TEST_MODE`: Set to "true" to use mock responses (default: "false")
- `PORT`: Port for the server (default: 8000)

### Running the Server

The server can be run with uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```