"""
Sessions router for State Machine Demo.

This module provides API endpoints for session management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models
from app.database import get_db

# ------------------ Configure Logging ------------------ #
from cws_helpers.logger import configure_logging

log = configure_logging(__name__)

# Create router
router = APIRouter()

@router.post("/", response_model=models.SessionResponse)
async def start_session(session_data: models.SessionCreate, db: Session = Depends(get_db)):
    """
    Start a new session or resume an existing one.
    
    If user_id is provided, it will attempt to resume that user's session.
    If not, a new user will be created with the provided first_name and last_name (optional).
    
    Args:
        session_data: Session creation data
        db: Database session
        
    Returns:
        Session information including user and journey IDs
    """
    # Start session
    session_info = crud.start_session(
        db,
        user_id=session_data.user_id,
        first_name=session_data.first_name,
        last_name=session_data.last_name
    )
    
    # Log session start with appropriate level
    if session_data.user_id:
        log.step(f"Resumed session for existing user: {session_info}")
    else:
        log.info(f"Started new session for user {session_info}")
    
    return session_info

@router.get("/{user_id}", response_model=models.SessionResponse)
async def resume_session(user_id: int, db: Session = Depends(get_db)):
    """
    Resume an existing session for a user.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Session information including user, journey, and recent messages
        
    Raises:
        HTTPException: If user not found
    """
    # Check if user exists
    user = crud.get_user(db, user_id)
    if not user:
        log.warning(f"User with ID {user_id} not found for session resume")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get active journey
    journey = crud.get_active_journey(db, user_id)
    
    # If no active journey, start a new one
    if not journey:
        log.step(f"No active journey found for user {user_id}, creating new one")
        session_info = crud.start_session(db, user_id=user_id)
    else:
        # Get messages for journey
        messages = crud.get_messages_for_journey(db, journey.id, limit=10)
        
        # Create session info
        session_info = {
            'user_id': user_id,
            'journey_id': journey.id,
            'current_milestone': journey.current_milestone,
            'status': journey.status,
            'recent_messages': messages
        }
    
    # Log session resume
    log.step(f"Resumed session for user: {session_info}")
    
    return session_info 