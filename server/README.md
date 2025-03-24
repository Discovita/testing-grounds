# State Machine Demo Backend

This is the backend server for the State Machine Demo application. It provides the API endpoints and database for the Home Renovation Journey demo.

## Technology Stack

- **FastAPI**: Web framework for building APIs
- **SQLAlchemy**: ORM for database interactions
- **SQLite**: Database for storing user data and journey progress
- **OpenAI**: LLM integration for chat and checkpoint analysis
- **Pydantic**: Data validation for API requests/responses

## Development Setup

### Prerequisites

- Python 3.10+
- pip for dependency management

### Installation

1. Clone the repository (if not already done)

2. Navigate to the server directory:
   ```
   cd development/state_machine_demo/server
   ```

3. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Starting the Server

You can start the server using either of the following methods:

#### Method 1: Using Python module
```
python -m app.main
```

#### Method 2: Using Uvicorn directly
```
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.
API documentation will be available at http://localhost:8000/docs.

## Environment Variables

Create a `.env` file in the server directory with the following variables:

```
# Database settings
DATABASE_URL=sqlite:///./state_machine_demo.db

# Log settings
LOG_LEVEL=INFO
LOG_FORMAT=standard  # standard or json

# API settings
PORT=8000

# LLM settings
LLM_PROVIDER=mock  # mock, openai, anthropic, etc.
LLM_MODEL=gpt-3.5-turbo  # or claude-2, etc.
# LLM_API_KEY=  # Add your API key here if using a real LLM provider
```

## Architecture and Message Processing Flow

### Core Components

1. **Chat Handler**: Manages the entire conversation flow, processes user messages, and orchestrates the state machine.
2. **Sentinel**: Analyzes user messages to extract information and update journey state.
3. **State Machine**: Tracks the user's progress through the renovation journey milestones and checkpoints.
4. **OpenAI Integration**: Provides LLM-based chat capabilities and checkpoint analysis.

### Message Processing Flow

When a user sends a message, the system processes it as follows:

1. **Message Received**: The `/messages` endpoint receives the user message.
2. **User Message Saved**: The message is saved to the database.
3. **Sentinel Analysis**: 
   - The Sentinel component analyzes the message to extract information for checkpoints.
   - Uses a function-calling pattern to update the journey state when relevant information is detected.
   - Focuses on extracting only the information needed for the current milestone's checkpoints.
4. **Milestone Completion Check**: 
   - After Sentinel updates, the system checks if the current milestone is complete.
   - If all required checkpoints are filled, the milestone is marked complete.
   - The journey may advance to the next milestone if conditions are met.
5. **Response Generation**:
   - A context-aware prompt is built including the current journey state and conversation history.
   - The OpenAI client generates an appropriate response based on the journey state.
6. **Response Saved**: The system response is saved to the database.
7. **Response Returned**: The response and updated journey state are returned to the client.

This architecture allows for dynamic, guided conversations that adapt to user inputs while maintaining a structured journey flow through predefined milestones.

## API Endpoints

### Health Check
- `GET /health`: Check if the API is running

### Users
- `POST /users`: Create a new user
- `GET /users/{user_id}`: Get user details

### Sessions
- `POST /sessions`: Start a new session
- `GET /sessions/{user_id}`: Resume an existing session

### Journeys
- `POST /journeys`: Create a new journey
- `GET /journeys/{journey_id}`: Get journey details
- `PUT /journeys/{journey_id}`: Update journey
- `GET /journeys/active/{user_id}`: Get active journey for user

### Messages
- `POST /messages`: Send a message and get a response
- `GET /messages/{journey_id}`: Get messages for journey
- `GET /messages/all`: Get all messages (admin)
- `POST /messages/process`: Process a user message

## Project Structure

```
server/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI application
│   ├── models.py             # Pydantic models
│   ├── schemas.py            # SQLAlchemy models
│   ├── database.py           # Database connection
│   ├── crud.py               # Database operations
│   ├── chat/                 # Chat processing system
│   │   ├── handler.py        # Main chat handler
│   │   ├── sentinel.py       # Checkpoint detection
│   │   ├── prompts.py        # System prompts
│   │   └── sentinel_functions.py # Sentinel functions
│   ├── openai/               # OpenAI integration
│   │   ├── __init__.py       # OpenAI client initialization
│   │   ├── client/           # Client implementations
│   │   └── models/           # Model-specific code
│   ├── routers/              # API routes
│       ├── __init__.py
│       ├── users.py
│       ├── journeys.py
│       ├── messages.py
│       └── sessions.py
├── tests/                    # Tests
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Database Schema

The application uses the following database schema:

### User
Stores basic user information.
- `id`: Primary key
- `first_name`: User's first name
- `last_name`: User's last name
- `created_at`: When the user was created

### RenovationJourney
Stores the journey state and answers to all checkpoints.
- `id`: Primary key
- `user_id`: Foreign key to User
- `current_milestone`: Current milestone number
- `status`: Journey status (in_progress, completed, abandoned)
- Milestone 1 fields: `room`, `renovation_purpose`
- Milestone 2 fields: `budget_range`, `timeline`
- Milestone 3 fields: `style_preference`, `priority_feature`
- Milestone completion tracking fields

### Message
Stores all messages exchanged in the conversation.
- `id`: Primary key
- `user_id`: Foreign key to User
- `journey_id`: Foreign key to RenovationJourney
- `speaker`: Who sent the message (user or system)
- `content`: Message content
- `current_milestone`: Milestone active when message was sent
- `timestamp`: When the message was sent

### UserAttribute
Stores extracted information about the user for personalization.
- `id`: Primary key
- `user_id`: Foreign key to User
- `attribute_key`: Attribute name
- `attribute_value`: Attribute value
- `source_message_id`: Foreign key to Message where attribute was extracted
- `created_at`: When the attribute was created 

## State Machine Logic

The application implements a state machine with the following key concepts:

1. **Milestones**: Major stages in the home renovation journey (Project Basics, Budget and Timeline, Style and Plan)
2. **Checkpoints**: Specific pieces of information to collect within each milestone
3. **Sentinel**: Analyzes conversation to detect when checkpoint information is provided
4. **Transition Logic**: Rules for advancing between milestones based on checkpoint completion

This architecture allows for flexible conversations while ensuring all necessary information is collected in a structured way. 