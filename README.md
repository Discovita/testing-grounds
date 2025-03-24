# State Machine Demo

This project demonstrates a conversational state machine for guiding users through a home renovation journey. It consists of a React frontend and a FastAPI backend.

## Project Structure

```
state_machine_demo/
├── client/         # React frontend
├── server/         # FastAPI backend
```

## Prerequisites

- Python 3.10+
- Node.js v18+
- npm or yarn

## Backend Setup

1. Navigate to the server directory:
   ```bash
   cd state_machine_demo/server
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables by creating a `.env` file in the server directory:
   ```
   # Database settings
   DATABASE_URL=sqlite:///./state_machine_demo.db

   # Log settings
   LOG_LEVEL=INFO
   LOG_FORMAT=standard

   # API settings
   PORT=8000

   # LLM settings
   LLM_PROVIDER=mock
   LLM_MODEL=gpt-3.5-turbo
   # LLM_API_KEY=  # Add your API key if using a real LLM provider
   ```

5. Start the backend server:
   ```bash
   python -m app.main
   # OR
   uvicorn app.main:app --reload
   ```

   The API will be available at http://localhost:8000.  
   API documentation will be available at http://localhost:8000/docs.

## Frontend Setup

1. Open a new terminal window and navigate to the client directory:
   ```bash
   cd state_machine_demo/client
   ```

2. Install dependencies:
   ```bash
   npm install
   # OR
   yarn install
   ```

3. Start the development server:
   ```bash
   npm run dev
   # OR
   yarn dev
   ```

   The frontend will be available at http://localhost:5173.

## Using the Application

1. Start both the backend and frontend servers as described above.
2. Open http://localhost:5173 in your browser.
3. The application will guide you through a home renovation journey, collecting information about your project.

## Features

- Conversational UI that guides users through a renovation journey
- State machine that tracks progress through predefined milestones
- Checkpoint detection that extracts key information from user messages
- Backend API for managing user data and chat history
- React-based frontend with modern UI components

## Technology Stack

### Backend
- FastAPI for API endpoints
- SQLAlchemy ORM with SQLite database
- OpenAI integration for LLM-based chat

### Frontend
- React 19 with TypeScript
- Vite for fast development
- React Router for navigation
- React Query for data fetching
- Tailwind CSS for styling
- Radix UI components

## Documentation

- Backend API documentation: http://localhost:8000/docs
- Detailed backend information: [server/README.md](server/README.md)
- Detailed frontend information: [client/README.md](client/README.md) 