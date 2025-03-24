"""
Main application module for State Machine Demo.

This is the entry point for the FastAPI application. It sets up the API
routes, middleware, and database connections.
"""

import os
import uuid
import time
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import init_db, get_db

# ------------------ Configure Logging ------------------ #
from cws_helpers.logger import configure_logging

log = configure_logging(__name__)

# Import routers
from app.routers import users, sessions, messages, journeys

# Create FastAPI app
app = FastAPI(
    title="State Machine Demo API",
    description="API for demonstrating state machine functionality for guided conversations",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo purposes - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request middleware for logging and request ID
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware to add request ID and timing information.

    Args:
        request: Incoming request
        call_next: Next middleware or route handler

    Returns:
        Response with added headers
    """
    # Generate request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    log.info(
        f"Request: {request_id} | {request.method} {request.url.path} | Params: {dict(request.query_params)}"
    )

    # Process request and measure time
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    log.info(
        f"Response: {request_id} | Status: {response.status_code} | Time: {process_time:.2f}ms"
    )

    # Add headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

    return response


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """
    Run tasks on application startup.

    Initialize the database and set up any required connections.
    """
    log.step("Initializing application")
    init_db()
    log.info("Database initialized successfully")

    # Log OpenAI client setup
    log.step("OpenAI client initialized")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns basic information about the API status.

    Returns:
        Dict with status and version information
    """
    log.info("Health check requested")
    return {"status": "ok", "version": app.version, "api": app.title}


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.

    Returns basic information about the API.

    Returns:
        Dict with API information
    """
    log.info("Root endpoint requested")
    return {
        "name": app.title,
        "version": app.version,
        "description": app.description,
        "docs_url": "/docs",
    }


# Include routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])
app.include_router(journeys.router, prefix="/journeys", tags=["Journeys"])


# Add sample placeholder endpoint
@app.get("/placeholder", tags=["Demo"])
async def placeholder_endpoint(db: Session = Depends(get_db)):
    """
    Placeholder endpoint for testing.

    This is a temporary endpoint for testing database connectivity.

    Args:
        db: Database session

    Returns:
        Dict with placeholder message
    """
    log.info("Placeholder endpoint requested")
    return {
        "message": "Placeholder endpoint - Replace with actual implementation",
        "database": "Connected" if db else "Not connected",
    }


# This is for development when running with uvicorn directly
if __name__ == "__main__":
    import uvicorn

    # Get port from environment or use default
    port_env = os.getenv("PORT", "8000")
    try:
        port = int(port_env)
    except ValueError:
        log.warning(f"Invalid PORT value: {port_env}, using default 8000")
        port = 8000

    # Run development server
    log.step(f"Starting development server on port {port}")
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=port, reload=True, log_level="info"
    )
