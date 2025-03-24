# State Machine Demo

## Overview

This will be a demo of the basic functionality needed to progress a user through various stages of conversation using a state machine.

## Idea

- A user will be able to interact with a chatbot that will guide them through various stages of a process. Each stage of the process will have a different prompt for the chatbot to use when responding to the user.
- Information extracted from the previous stages will need to be persisted along with the state (what stage of the process are we on?). This information from the previous stages will be used in the subsequent stages to provide a more personalized experience for the user.
- Some method for determining when the user has completed a particular stage will be needed.
  - Ideally this would be a function call available to the LLM that can do only one thing: update the state of the user to the next stage.
  - The same goes for determining when the user has completed the entire process.
    - I'll want to have some function call available that will show some kind of completion message to the user.

## Terminology

We will use the following terminology consistently across the system:

- **Journey**: The overall process flow that a user follows (e.g., Home Renovation Guide)
- **Milestone**: Major stages within a journey (e.g., Project Basics, Budget and Timeline)
- **Checkpoint**: Specific information requirements within each milestone that must be satisfied
- **User Attribute**: Extracted facts about the user that are persisted for personalization

## State Machine

- Initially, this will be a simple attribute of the user object that will get updated as the user progresses through the conversation.
  - The state machine may end up being more complex than this. Instead of simple stage progressionm, each stage may have its own set of sub-stages that the user will need to progress through and we could keep track of that.

## Chat History

- All chat messages for the user will need to get stored for the user. This will be used to provide context to the chatbot when responding to the user.
- It will also allow the user to pick up where they left off if they leave the conversation and come back later.

## User Facts

- I want a method that can analyze the converstation asynchronously and extract information from the user's messages. This information will be used to provide a more personalized experience for the user.
  - Information that the user provides while chatting and deemed necessary to keep track of will get stored as part of the user object.
    - For example, if the user says "I fight with my sister a lot", then the fact that the user has a sister will need to get stored.
    - When saving these facts about the user, the system will have to do this in the context of the current facts saved about the user.

## Demo Implementation: Home Renovation Journey

Our demo implementation will be a simplified Home Renovation Guide with the following structure:

### Milestone 1: Project Basics

Purpose: Establish the fundamental project parameters.

#### Checkpoints:

Which room is being renovated
Primary purpose of the renovation (aesthetic, functional, repair)

#### Completion Requirements:

- User has identified a specific room
- User has stated at least one clear objective
- System has confirmed understanding of the basic project scope

### Milestone 2: Budget and Timeline

Purpose: Establish simple financial and time constraints.

#### Checkpoints:

Approximate budget range (can be general: low, medium, high)
Rough timeline expectation (weeks, months)

#### Completion Requirements:

- User has provided some budget indication
- User has shared a general timeline expectation
- System has acknowledged these constraints

### Milestone 3: Style Preferences and Plan

Purpose: Capture basic style preferences and create a simple plan.

#### Checkpoints:

General style preference (modern, traditional, etc.)
One or two priority features

#### Completion Requirements:

- User has indicated a style direction
- User has shared at least one key feature or priority
- System has presented a basic project summary
- User has confirmed readiness to end the process


## Database

- Initially, I'll just use a simple sqlite database to store the user information.
- I'll want to come up with a set of bare bones models that will be used for this demo.
    - User (basic for now - just a ID, First Name, and Last Name (default to "Test User" for every session in the demo unless a name is provided)) 
    - Journey - this will be specific to the Journey and will have hardcoded attributes for the the status of the user in the Journey. The idea for this model is that a Journey could be retrieved for a user and based on the status of the Journey data, we can know exactly where the user is in the Journey and will be able to pick up where they left off if they leave the conversation and come back later (which the user will absolutely do).
        - Milestones - these will be boolean values or something that will indicate whether the user has completed the milestone or not. Will be marked as complete if all the checkpoints for the milestone have been completed (have answers).
        - Checkpoints - these will be answers to the specific questions that the user needs to answer to complete the associated milestone. 
            - I want to store the answer to the checkpoint along with a "notes" attrubute that will be used to store any additional information that the user provides that might be important context for the answer.
    - ChatHistory
        - The entire chat history for a user will have to get stored in the database. 
        - For each message in the chat history, I want to store the status of what milestone and checkpoint the user is on when that message was completed. 
        - Not quite sure how to store this yet. I'm considering having the ChatHistory be made up of Message objects that have attributes like "speaker", "message", "session", "user", etc. 


## Database Schema

### User
Stores basic user information.

```sql
CREATE TABLE User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT DEFAULT NULL,
    last_name TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### RenovationJourney
Stores the journey state and answers to all checkpoints.

```sql
CREATE TABLE RenovationJourney (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    current_milestone INTEGER DEFAULT 1,
    status TEXT DEFAULT 'in_progress', -- 'in_progress', 'completed', 'abandoned'
    
    -- Milestone 1: Project Basics
    room TEXT DEFAULT NULL,
    renovation_purpose TEXT DEFAULT NULL,
    milestone1_completed BOOLEAN DEFAULT FALSE,
    milestone1_completed_at TIMESTAMP DEFAULT NULL,
    
    -- Milestone 2: Budget and Timeline
    budget_range TEXT DEFAULT NULL,
    timeline TEXT DEFAULT NULL,
    milestone2_completed BOOLEAN DEFAULT FALSE,
    milestone2_completed_at TIMESTAMP DEFAULT NULL,
    
    -- Milestone 3: Style and Plan
    style_preference TEXT DEFAULT NULL,
    priority_feature TEXT DEFAULT NULL,
    milestone3_completed BOOLEAN DEFAULT FALSE,
    milestone3_completed_at TIMESTAMP DEFAULT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES User(id)
);
```

### Message
Stores all messages exchanged in the conversation.

```sql
CREATE TABLE Message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    journey_id INTEGER NOT NULL,
    speaker TEXT NOT NULL, -- 'user' or 'system'
    content TEXT NOT NULL,
    current_milestone INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (journey_id) REFERENCES RenovationJourney(id)
);
```

### UserAttribute
Stores extracted information about the user for personalization.

```sql
CREATE TABLE UserAttribute (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    attribute_key TEXT NOT NULL,
    attribute_value TEXT NOT NULL,
    source_message_id INTEGER DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (source_message_id) REFERENCES Message(id)
);
```

## Core Operations

### Session Management

#### Starting a New Session
```python
def start_session(user_id=None, first_name=None, last_name=None):
    # Create or retrieve user
    if not user_id:
        user = create_user(first_name, last_name)
        user_id = user.id
    
    # Check for existing journey
    journey = get_active_journey(user_id)
    
    if not journey:
        # Create new journey
        journey = create_journey(user_id)
    
    return {
        'user_id': user_id,
        'journey_id': journey.id,
        'current_milestone': journey.current_milestone,
        'status': journey.status
    }
```

#### Resuming a Session
```python
def resume_session(user_id):
    # Get journey data
    journey = get_active_journey(user_id)
    
    if not journey:
        return start_session(user_id)
    
    # Get recent messages
    messages = get_recent_messages(journey.id, limit=10)
    
    # Get milestone data based on current progress
    milestone_data = {
        'milestone': journey.current_milestone,
        'completed_milestones': get_completed_milestones(journey)
    }
    
    return {
        'user_id': user_id,
        'journey_id': journey.id,
        'milestone_data': milestone_data,
        'recent_messages': messages
    }
```

### Message Processing

#### Saving Messages
```python
def save_message(user_id, journey_id, speaker, content, current_milestone):
    message = {
        'user_id': user_id,
        'journey_id': journey_id,
        'speaker': speaker,
        'content': content,
        'current_milestone': current_milestone
    }
    
    message_id = db.insert('Message', message)
    return message_id
```

#### Processing User Messages
```python
def process_user_message(user_id, journey_id, content):
    # Get current journey state
    journey = get_journey(journey_id)
    
    # Save the user message
    message_id = save_message(user_id, journey_id, 'user', content, journey.current_milestone)
    
    # Extract checkpoint answers based on milestone
    if journey.current_milestone == 1:
        process_milestone1_message(journey, content, message_id)
    elif journey.current_milestone == 2:
        process_milestone2_message(journey, content, message_id)
    elif journey.current_milestone == 3:
        process_milestone3_message(journey, content, message_id)
    
    # Extract general user attributes
    extract_user_attributes(user_id, content, message_id)
    
    # Check if milestone is complete
    check_milestone_completion(journey)
    
    return journey
```

### State Management

#### Checking Milestone Completion
```python
def check_milestone_completion(journey):
    if journey.current_milestone == 1 and not journey.milestone1_completed:
        if journey.room and journey.renovation_purpose:
            update_journey(journey.id, {
                'milestone1_completed': True,
                'milestone1_completed_at': current_timestamp()
            })
            # Don't advance milestone yet - wait for system to confirm
    
    elif journey.current_milestone == 2 and not journey.milestone2_completed:
        if journey.budget_range and journey.timeline:
            update_journey(journey.id, {
                'milestone2_completed': True,
                'milestone2_completed_at': current_timestamp()
            })
            # Don't advance milestone yet - wait for system to confirm
    
    elif journey.current_milestone == 3 and not journey.milestone3_completed:
        if journey.style_preference and journey.priority_feature:
            update_journey(journey.id, {
                'milestone3_completed': True,
                'milestone3_completed_at': current_timestamp(),
                'status': 'completed'
            })
            # Don't advance milestone since this is the last one
```

#### Advancing to Next Milestone
```python
def advance_milestone(journey_id):
    journey = get_journey(journey_id)
    
    if journey.current_milestone < 3:  # We only have 3 milestones
        new_milestone = journey.current_milestone + 1
        update_journey(journey_id, {
            'current_milestone': new_milestone,
            'updated_at': current_timestamp()
        })
        return True
    return False
```

## LLM Integration

The LLM will need function calls to:

1. **Check Journey State**: Get current milestone and completion status
2. **Save Checkpoint Data**: Update journey with answers to specific checkpoints
3. **Advance Milestone**: Move to the next milestone when current one is complete
4. **Complete Journey**: Mark the journey as complete when all milestones are done

### Example LLM Function Definitions

```python
def llm_get_journey_state(user_id):
    """
    Returns the current state of the user's journey for the LLM.
    """
    journey = get_active_journey(user_id)
    if not journey:
        return {
            'has_journey': False,
            'milestone': None,
            'completed_checkpoints': []
        }
    
    # Get completed checkpoints based on milestone
    completed_checkpoints = []
    if journey.current_milestone == 1:
        if journey.room:
            completed_checkpoints.append('room')
        if journey.renovation_purpose:
            completed_checkpoints.append('renovation_purpose')
    # Similar logic for milestones 2 and 3
    
    return {
        'has_journey': True,
        'milestone': journey.current_milestone,
        'completed_checkpoints': completed_checkpoints,
        'milestone_completed': get_current_milestone_completed(journey)
    }

def llm_save_checkpoint(journey_id, checkpoint_name, value):
    """
    Saves a checkpoint answer provided by the user.
    """
    journey = get_journey(journey_id)
    
    # Map checkpoint name to database field
    field_mapping = {
        'room': 'room',
        'renovation_purpose': 'renovation_purpose',
        'budget_range': 'budget_range',
        'timeline': 'timeline',
        'style_preference': 'style_preference',
        'priority_feature': 'priority_feature'
    }
    
    if checkpoint_name in field_mapping:
        field = field_mapping[checkpoint_name]
        update_journey(journey_id, {field: value})
        return True
    return False

def llm_advance_milestone(journey_id):
    """
    Advances to the next milestone when LLM determines current milestone is complete.
    """
    return advance_milestone(journey_id)

def llm_complete_journey(journey_id):
    """
    Marks the journey as complete.
    """
    update_journey(journey_id, {
        'status': 'completed',
        'updated_at': current_timestamp()
    })
    return True
```

## Implementation Notes

1. **SQLite Database**: All tables will be implemented in a SQLite database for simplicity in the demo.

2. **Transactions**: Use database transactions when updating multiple related records to ensure data consistency.

3. **Timestamp Handling**: Use UTC timestamps for all date/time fields for consistency.

4. **Error Handling**: Implement proper error handling and provide meaningful error messages, especially for database operations.

5. **Logging**: Log all major state transitions and errors for debugging and analysis.

6. **Backup**: Implement a simple backup mechanism for the SQLite database file.

This database design provides a solid foundation for the Home Renovation Journey demo while remaining simple enough for quick implementation. The structure can be easily extended with additional fields or tables as needed for future enhancements.

## Implementation Plan

### Backend Setup (FastAPI with SQLite)

1. **Project Structure**
```
development/state_machine_demo/
├── client/               # Existing React frontend
├── server/               # New backend directory
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py       # FastAPI application entry point
│   │   ├── models.py     # Pydantic models for request/response
│   │   ├── schemas.py    # SQLAlchemy ORM models
│   │   ├── database.py   # Database connection and session
│   │   ├── crud.py       # Database operations
│   │   ├── llm/          # LLM integration modules
│   │   │   ├── __init__.py
│   │   │   └── client.py # LLM client implementation
│   │   ├── utils/        # Utility modules
│   │   │   ├── __init__.py
│   │   │   └── logger.py # Custom logging implementation
│   │   └── routers/      # API route modules
│   │       ├── __init__.py
│   │       ├── users.py
│   │       ├── journeys.py
│   │       └── messages.py
│   ├── migrations/       # Database migrations (optional)
│   ├── tests/            # Unit and integration tests
│   ├── .env              # Environment variables
│   ├── pyproject.toml    # Poetry configuration file
│   ├── poetry.lock       # Poetry lock file
│   └── README.md         # Backend-specific documentation
```

2. **Dependencies (managed with Poetry)**
```
[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.108.0"      # Web framework
uvicorn = "^0.25.0"       # ASGI server
sqlalchemy = "^2.0.25"    # ORM for database operations
pydantic = "^2.5.3"       # Data validation
python-dotenv = "^1.0.0"  # Environment variable management

# Custom/personal modules will be added incrementally
# - LLM client module for making LLM calls
# - Custom logging module
```

3. **Personal Module Integration**

#### LLM Integration
- Create a dedicated module for LLM interactions
- Implement your personal LLM client for making API calls
- Configure environment variables for API keys and endpoints
- Add appropriate abstraction layer for easy swapping of LLM providers

#### Logging
- Implement custom logging utilities
- Configure different log levels for development and production
- Add structured logging for better analysis
- Include request/response logging for debugging

4. **Database Implementation**
- Implement SQLAlchemy models based on the schema defined in the README
- Create database connection handler
- Implement database initialization script
- Create CRUD operations for all models

5. **API Endpoints**

#### User Management
- `POST /users` - Create a new user
- `GET /users/{user_id}` - Get user details
- `PUT /users/{user_id}` - Update user details

#### Session Management
- `POST /sessions` - Start a new session
- `GET /sessions/{user_id}` - Resume an existing session

#### Journey Management
- `POST /journeys` - Create a new journey
- `GET /journeys/{journey_id}` - Get journey details
- `PUT /journeys/{journey_id}` - Update journey (checkpoints, milestone progression)
- `GET /journeys/active/{user_id}` - Get active journey for a user

#### Message Management
- `POST /messages` - Save a new message
- `GET /messages/{journey_id}` - Get messages for a journey
- `POST /messages/process` - Process user message and update journey state

#### LLM Integration Functions
- `GET /journey-state/{user_id}` - Get current journey state for LLM
- `POST /checkpoints/{journey_id}/{checkpoint_name}` - Save checkpoint data
- `POST /journeys/{journey_id}/advance` - Advance to next milestone
- `POST /journeys/{journey_id}/complete` - Mark journey as complete

6. **Implementation Phases**

#### Phase 1: Base Setup
- Create project structure
- Implement database models and connection
- Set up FastAPI application shell

#### Phase 2: Core Functionality
- Implement user and session management
- Implement journey creation and state management
- Implement message storage and retrieval

#### Phase 3: Business Logic
- Implement milestone progression logic
- Implement checkpoint completion logic
- Implement user attribute extraction

#### Phase 4: Integration
- Connect FastAPI backend with React frontend
- Implement CORS for cross-origin requests
- Set up proper error handling and validation

#### Phase 5: Testing & Documentation
- Write unit tests for core functions
- Write integration tests for API endpoints
- Document API endpoints with OpenAPI

### Frontend Integration

1. **API Client**
- Create API client in React frontend to communicate with backend
- Implement authentication if needed (simple token-based for demo)

2. **State Management**
- Update React state management to reflect backend state
- Implement hooks for journey progression

3. **Connection**
- Configure frontend to connect to backend API
- Set up environment variables for API endpoint URLs

### Deployment Considerations

1. **Development Environment**
- Run backend with hot-reload for development
- Configure CORS to allow frontend connections

2. **Production Setup** (if needed)
- Configure proper database path
- Set up logging
- Consider containerization for easier deployment


# Chatbot Integration

Now that we have the frontend and backend setup, we can integrate the chatbot into the system. The chatbot will interact with the user based on the journey state and user messages.

We'll need to use the /openai module we created to create a chatbot that will interact with the user

The key though for this is that the chatbot will use different prompts based on the user's journey state. For example, if the user is in Milestone 1, the chatbot will ask questions related to Project Basics. If the user is in Milestone 2, the chatbot will ask questions related to Budget and Timeline.

We've already got a system where we can switch between prompts based on the user's journey state. We can use this to determine which prompt to send to the chatbot. One important note: each milestone will have a set of questions that it is aiming to update. To accurately communicate with the user, I'll want to send both the chat history (lets start with the last 10 messages) along with the users journey data from the database. 
We are going to have to implement a system where we can update the users journey data based on the chat messages. Each message will have to get processed BEFORE we allow the LLM to respond. I think the way this could work is we send the last 5 messages to an LLM and (depending on where we are in the journey) we ask the LLM to determine if the user answered whatever the current checkpoint question is. If they did, give that LLM a function it can run to update the users journey data. Once that has happened, or it has been determined that the users data does not need to be updated, we'll then fetch the freshest data from the database, decide what the next prompt should be, and send that to the LLM to respond to the user. The LLM will then respond to the user and we'll save that message to the database. We'll then repeat this process, accepting the users response, sending that response along with a few of the previous messages, determine if updates need to be made, then respond to the user with the appropriate prompt. 



