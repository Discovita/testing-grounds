"""
Messages router for State Machine Demo.

This module provides API endpoints for chat message handling.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from app import models, crud
from app.database import get_db
from app.chat.handler import get_chat_handler

# ------------------ Configure Logging ------------------ #
from cws_helpers.logger import configure_logging

log = configure_logging(__name__)


# Request model
class MessageCreate(BaseModel):
    """
    Message creation request model.

    Fields:
        user_id: User ID
        journey_id: Journey ID
        content: Message content
    """

    user_id: int
    journey_id: int
    content: str


# Response model
class MessageResponse(BaseModel):
    """
    Message response model.

    Fields:
        id: Message ID
        journey_id: Journey ID
        user_id: User ID
        speaker: Message speaker (user, assistant, system)
        content: Message content
        timestamp: Message timestamp
        current_milestone: Current milestone when message was sent
    """

    id: Optional[int]
    journey_id: int
    user_id: int = 1  # Default to user 1 for mock data
    speaker: str
    content: str
    timestamp: Optional[str]
    current_milestone: Optional[int] = None

    class Config:
        orm_mode = True

        # Convert datetime objects to strings during model validation
        json_encoders = {datetime: lambda dt: dt.isoformat() if dt else None}

    @classmethod
    def from_orm(cls, obj):
        # Convert datetime to string before validation
        if hasattr(obj, "timestamp") and obj.timestamp:
            obj.timestamp = obj.timestamp.isoformat()
        return super().from_orm(obj)


# Journey state response model
class JourneyStateResponse(BaseModel):
    """
    Journey state response model.

    Fields:
        milestone: Current milestone
        completed_checkpoints: List of completed checkpoints
        status: Journey status
    """

    milestone: int
    completed_checkpoints: List[str]
    status: str


# Full response model
class ChatResponse(BaseModel):
    """
    Chat response model.

    Fields:
        message: Assistant message
        journey_state: Current journey state
    """

    message: MessageResponse
    journey_state: JourneyStateResponse


# Create router
router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def send_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
):
    """
    Send a chat message and get a response.

    This endpoint handles user message processing through the OpenAI API
    and returns the assistant's response along with updated journey state.

    Steps:
    1. Log the incoming message
    2. Get the chat handler
    3. Process the message with the Sentinel to analyze and extract checkpoint info
    4. Process the message with OpenAI to generate a response
    5. Return the response with updated journey state

    Args:
        message: User message data
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Chat response with assistant message and journey state

    Raises:
        HTTPException: If user or journey not found, or an error occurs
    """
    # Log the incoming message
    log.info(f"Received message for user: {message}")

    try:
        # For demo purposes, we're not doing full database validation
        # In a real application, we would check if the user and journey exist

        # Get chat handler
        chat_handler = await get_chat_handler(db)

        # Process the message with OpenAI
        log.step(f"Processing message with journey handler {message}")

        # Process message and get response
        response = await chat_handler.process_message(
            user_id=message.user_id,
            journey_id=message.journey_id,
            message_text=message.content,
        )

        # Check for errors
        if "error" in response:
            log.error(f"Error processing message: {response.get('error')}")
            log.error(f"Message: {message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.get("error", "Unknown error"),
            )

        # Log sentinel results if available
        if "sentinel_result" in response:
            sentinel_result = response["sentinel_result"]
            # Check if sentinel_result is a dict or RenovationJourney object
            if isinstance(sentinel_result, dict) and sentinel_result.get(
                "updated", False
            ):
                log.info(f"Sentinel updated journey state")
                log.info(f"Sentinel Result: {sentinel_result}")
                log.info(f"Message: {message}")
            elif hasattr(sentinel_result, "id"):  # It's a RenovationJourney object
                log.info(f"Sentinel processed journey state")
                log.info(f"Sentinel Result: {sentinel_result}")
                log.info(f"Message: {message}")
            else:
                log.info(f"Sentinel did not update journey state")
                log.info(f"Sentinel Result: {sentinel_result}")
                log.info(f"Message: {message}")

        # Create response objects
        journey_state = JourneyStateResponse(
            milestone=response["journey_state"]["milestone"],
            completed_checkpoints=response["journey_state"]["completed_checkpoints"],
            status=response["journey_state"]["status"],
        )

        # Create message response
        message_response = MessageResponse(
            id=None,  # Will be set by database
            journey_id=message.journey_id,
            user_id=message.user_id,
            speaker="assistant",
            content=response["response_text"],
            timestamp=datetime.now().isoformat(),
            current_milestone=response["journey_state"]["milestone"],
        )

        # Log successful response
        log.info(f"Processed message for user {message.user_id}")
        log.info(f"Message: {message}")
        log.info(f"Journey State: {journey_state}")

        # Return combined response
        return ChatResponse(message=message_response, journey_state=journey_state)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        log.error(f"Unexpected error processing message: {str(e)}")
        log.error(f"Message: {message}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@router.get("/all", response_model=List[MessageResponse])
async def get_all_messages(
    limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
):
    """
    Get all messages for admin dashboard.

    Steps:
    1. Query all messages from the database with pagination
    2. Return the list of messages sorted by timestamp (newest first)

    Args:
        limit: Maximum number of messages to return (default: 100)
        offset: Number of messages to skip (default: 0)
        db: Database session

    Returns:
        List of message objects
    """
    log.info(f"Retrieving all messages, limit: {limit}, offset: {offset}")

    try:
        # Get all messages from database
        messages = crud.get_all_messages(db, limit, offset)

        # Log the retrieval
        log.info(f"Retrieved all messages, count: {len(messages)}")

        # Convert messages to response model
        message_responses = []
        for msg in messages:
            # Convert timestamp to ISO format string
            if hasattr(msg, "timestamp") and msg.timestamp:
                msg.timestamp = msg.timestamp.isoformat()
            message_responses.append(msg)

        return message_responses

    except Exception as e:
        log.error(f"Error retrieving all messages: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving messages: {str(e)}",
        )


@router.get("/{journey_id}", response_model=List[MessageResponse])
async def get_messages(journey_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """
    Get messages for a journey.

    Steps:
    1. Query messages for the specified journey from the database with pagination
    2. Return the list of messages sorted by timestamp (newest first)

    Args:
        journey_id: Journey ID
        limit: Maximum number of messages to return (default: 50)
        db: Database session

    Returns:
        List of messages

    Raises:
        HTTPException: If journey not found
    """
    log.info(f"Retrieving messages for journey {journey_id}, limit: {limit}")

    try:
        # Get messages from database
        messages = crud.get_messages_for_journey(db, journey_id, limit)

        # Log the retrieval
        log.info(f"Retrieved {len(messages)} messages for journey {journey_id}")

        # Convert messages to response model
        message_responses = []
        for msg in messages:
            # Convert timestamp to ISO format string
            if hasattr(msg, "timestamp") and msg.timestamp:
                msg.timestamp = msg.timestamp.isoformat()
            message_responses.append(msg)

        return message_responses

    except Exception as e:
        log.error(f"Error retrieving messages: {str(e)}")
        log.error(f"Journey ID: {journey_id}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving messages: {str(e)}",
        )


# ProcessMessage request model
class ProcessMessageRequest(BaseModel):
    """
    Process message request model.

    Fields:
        user_id: User ID
        journey_id: Journey ID
        content: Message content
    """

    user_id: int
    journey_id: int
    content: str


# ProcessMessage response model
class ProcessMessageResponse(BaseModel):
    """
    Process message response model.

    Fields:
        journey: Updated journey state
        system_response: Response from the system
    """

    journey: models.JourneyResponse
    system_response: str


@router.post("/process", response_model=ProcessMessageResponse)
async def process_message(
    message: ProcessMessageRequest, db: Session = Depends(get_db)
):
    """
    Process a user message and update journey state.

    Steps:
    1. Save the user message to the database
    2. Process the message through the OpenAI API
    3. Generate a response and update journey state
    4. Save the assistant message to the database
    5. Return the updated journey state and system response

    Args:
        message: Message data with user_id, journey_id, and content
        db: Database session

    Returns:
        Updated journey state and system response

    Raises:
        HTTPException: If user or journey not found, or if an error occurs
    """
    log.info(f"Processing message for user")
    log.info(f"Message: {message}")

    # Verify user exists
    user = crud.get_user(db, message.user_id)
    if not user:
        log.warning(f"User with ID {message.user_id} not found for message processing")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {message.user_id} not found",
        )

    # Verify journey exists
    journey = crud.get_journey(db, message.journey_id)
    if not journey:
        log.warning(
            f"Journey with ID {message.journey_id} not found for message processing"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journey with ID {message.journey_id} not found",
        )

    # Verify journey belongs to user
    if journey.user_id != message.user_id:
        log.warning(
            f"Journey {message.journey_id} does not belong to user {message.user_id}"
        )
        log.warning(f"journey_user_id: {journey.user_id}")

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This journey does not belong to the specified user",
        )

    try:
        # Save user message
        user_message = crud.create_message(
            db,
            models.MessageCreate(
                user_id=message.user_id,
                journey_id=message.journey_id,
                speaker="user",
                content=message.content,
                current_milestone=journey.current_milestone,
            ),
        )

        # Generate dummy response for now (in a real implementation, this would use OpenAI)
        system_response = f"This is a mock response to: {message.content}"

        # Save assistant message
        assistant_message = crud.create_message(
            db,
            models.MessageCreate(
                user_id=message.user_id,
                journey_id=message.journey_id,
                speaker="assistant",
                content=system_response,
                current_milestone=journey.current_milestone,
            ),
        )

        # Return response
        return ProcessMessageResponse(journey=journey, system_response=system_response)

    except Exception as e:
        log.error(f"Error processing message: {str(e)}")
        log.error(f"Message: {message}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the message: {str(e)}",
        )
