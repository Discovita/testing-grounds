"""
Journeys router for State Machine Demo.

This module provides API endpoints for journey management, including:
- Creating new journeys
- Retrieving journey details
- Updating journey state and checkpoints
- Getting active journeys for users
- Advancing milestone progression
- Completing journeys
"""

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
import datetime
from typing import List

from app import crud, models, schemas
from app.database import get_db

# ------------------ Configure Logging ------------------ #
from cws_helpers.logger import configure_logging

log = configure_logging(__name__)

# Create router
router = APIRouter()


@router.get("/", response_model=List[models.JourneyResponse])
async def get_all_journeys(db: Session = Depends(get_db)):
    """
    Get all journeys for admin dashboard.

    Steps:
    1. Query all journeys from the database
    2. Return the list of journeys sorted by creation date (newest first)

    Args:
        db: Database session

    Returns:
        List of all journey objects
    """
    # Get all journeys
    journeys = crud.get_journeys(db)

    log.info(f"Retrieved all journeys, count: {len(journeys)}")

    return journeys


@router.post(
    "/", response_model=models.JourneyResponse, status_code=status.HTTP_201_CREATED
)
async def create_journey(journey: models.JourneyCreate, db: Session = Depends(get_db)):
    """
    Create a new journey for a user.

    Steps:
    1. Verify the user exists
    2. Check if user already has an active journey
    3. Create a new journey with initial state
    4. Return the created journey

    Args:
        journey: Journey creation data with user_id
        db: Database session

    Returns:
        Created journey object
    """
    # Verify user exists
    user = crud.get_user(db, journey.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {journey.user_id} not found",
        )

    # Check if user already has an active journey
    active_journey = crud.get_active_journey(db, journey.user_id)
    if active_journey:
        log.info(
            f"User {journey.user_id} already has an active journey: {active_journey.id}"
        )
        return active_journey

    # Create journey
    db_journey = crud.create_journey(db, journey)

    # Log journey creation
    log.info(f"Created journey with ID {db_journey.id} for user {journey.user_id}")

    return db_journey


@router.get("/{journey_id}", response_model=models.JourneyResponse)
async def get_journey(
    journey_id: int = Path(..., description="The ID of the journey to retrieve"),
    db: Session = Depends(get_db),
):
    """
    Get a journey by ID.

    Args:
        journey_id: ID of the journey to retrieve
        db: Database session

    Returns:
        Journey object
    """
    db_journey = crud.get_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journey with ID {journey_id} not found",
        )

    return db_journey


@router.put("/{journey_id}", response_model=models.JourneyResponse)
async def update_journey(
    journey_id: int, journey: models.JourneyUpdate, db: Session = Depends(get_db)
):
    """
    Update a journey.

    Args:
        journey_id: ID of the journey to update
        journey: Journey update data
        db: Database session

    Returns:
        Updated journey object
    """
    db_journey = crud.get_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journey with ID {journey_id} not found",
        )

    updated_journey = crud.update_journey(db, journey_id, journey)

    log.info(f"Updated journey with ID {journey_id}")

    return updated_journey


@router.get("/active/{user_id}", response_model=models.JourneyResponse)
async def get_active_journey(
    user_id: int = Path(..., description="The ID of the user"),
    db: Session = Depends(get_db),
):
    """
    Get the active journey for a user.

    Args:
        user_id: ID of the user
        db: Database session

    Returns:
        Active journey object if exists
    """
    # Verify user exists
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # Get active journey
    active_journey = crud.get_active_journey(db, user_id)
    if not active_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active journey found for user with ID {user_id}",
        )

    return active_journey


@router.post("/{journey_id}/checkpoints/{checkpoint_name}")
async def save_checkpoint(
    journey_id: int,
    checkpoint_name: str,
    checkpoint: models.CheckpointUpdate,
    db: Session = Depends(get_db),
):
    """
    Save a checkpoint value for a journey.

    This endpoint is used by the LLM to save extracted checkpoint answers.

    Args:
        journey_id: ID of the journey
        checkpoint_name: Name of the checkpoint to update
        checkpoint: Checkpoint value data
        db: Database session

    Returns:
        Success message
    """
    # Verify journey exists
    journey = crud.get_journey(db, journey_id)
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journey with ID {journey_id} not found",
        )

    # Map checkpoint name to journey field
    field_mapping = {
        "room": "room",
        "renovation_purpose": "renovation_purpose",
        "budget_range": "budget_range",
        "timeline": "timeline",
        "style_preference": "style_preference",
        "priority_feature": "priority_feature",
    }

    if checkpoint_name not in field_mapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown checkpoint: {checkpoint_name}",
        )

    # Update journey with checkpoint value
    field = field_mapping[checkpoint_name]
    journey_update = {field: checkpoint.value}
    crud.update_journey(db, journey_id, journey_update)

    # Log checkpoint save
    log.info(f"Saved checkpoint {checkpoint_name} for journey {journey_id}")

    # Check if milestone is complete
    updated_journey = crud.get_journey(db, journey_id)
    check_milestone_completion(db, updated_journey)

    return {
        "message": f"Saved checkpoint {checkpoint_name} with value {checkpoint.value}"
    }


@router.post("/{journey_id}/advance")
async def advance_milestone(journey_id: int, db: Session = Depends(get_db)):
    """
    Advance to the next milestone in a journey.

    Args:
        journey_id: ID of the journey
        db: Database session

    Returns:
        Success message
    """
    # Verify journey exists
    journey = crud.get_journey(db, journey_id)
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journey with ID {journey_id} not found",
        )

    # Check if journey can advance
    if journey.current_milestone >= 3:
        return {"message": "Journey is already at the final milestone"}

    # Advance milestone
    new_milestone = journey.current_milestone + 1
    journey_update = {
        "current_milestone": new_milestone,
        "updated_at": datetime.datetime.utcnow(),
    }
    crud.update_journey(db, journey_id, journey_update)

    # Log milestone advancement
    log.step(f"Advanced journey {journey_id} to milestone {new_milestone}")

    return {"message": f"Advanced to milestone {new_milestone}"}


@router.post("/{journey_id}/complete")
async def complete_journey(journey_id: int, db: Session = Depends(get_db)):
    """
    Mark a journey as complete.

    Args:
        journey_id: ID of the journey
        db: Database session

    Returns:
        Success message
    """
    # Verify journey exists
    journey = crud.get_journey(db, journey_id)
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journey with ID {journey_id} not found",
        )

    # Update journey status
    journey_update = {"status": "completed", "updated_at": datetime.datetime.utcnow()}
    crud.update_journey(db, journey_id, journey_update)

    # Log journey completion
    log.info(f"Completed journey {journey_id} for user {journey.user_id}")

    return {"message": "Journey completed successfully"}


@router.get("/state/{user_id}", response_model=models.JourneyStateResponse)
async def get_journey_state(user_id: int, db: Session = Depends(get_db)):
    """
    Get the current state of a user's journey for the LLM.

    Args:
        user_id: ID of the user
        db: Database session

    Returns:
        Journey state data
    """
    # Get active journey
    journey = crud.get_active_journey(db, user_id)
    if not journey:
        return models.JourneyStateResponse(
            has_journey=False,
            milestone=None,
            completed_checkpoints=[],
            milestone_completed=None,
        )

    # Get completed checkpoints based on milestone
    completed_checkpoints = []
    if journey.current_milestone == 1:
        if journey.room:
            completed_checkpoints.append("room")
        if journey.renovation_purpose:
            completed_checkpoints.append("renovation_purpose")
    elif journey.current_milestone == 2:
        if journey.budget_range:
            completed_checkpoints.append("budget_range")
        if journey.timeline:
            completed_checkpoints.append("timeline")
    elif journey.current_milestone == 3:
        if journey.style_preference:
            completed_checkpoints.append("style_preference")
        if journey.priority_feature:
            completed_checkpoints.append("priority_feature")

    # Check if current milestone is completed
    milestone_completed = False
    if journey.current_milestone == 1:
        milestone_completed = journey.milestone1_completed
    elif journey.current_milestone == 2:
        milestone_completed = journey.milestone2_completed
    elif journey.current_milestone == 3:
        milestone_completed = journey.milestone3_completed

    return models.JourneyStateResponse(
        has_journey=True,
        milestone=journey.current_milestone,
        completed_checkpoints=completed_checkpoints,
        milestone_completed=milestone_completed,
    )


def check_milestone_completion(db: Session, journey: schemas.RenovationJourney) -> None:
    """
    Check if current milestone is complete and update journey accordingly.

    Args:
        db: Database session
        journey: Journey object
    """
    update_data = {}

    if journey.current_milestone == 1 and not journey.milestone1_completed:
        if journey.room and journey.renovation_purpose:
            update_data["milestone1_completed"] = True
            update_data["milestone1_completed_at"] = datetime.datetime.utcnow()

    elif journey.current_milestone == 2 and not journey.milestone2_completed:
        if journey.budget_range and journey.timeline:
            update_data["milestone2_completed"] = True
            update_data["milestone2_completed_at"] = datetime.datetime.utcnow()

    elif journey.current_milestone == 3 and not journey.milestone3_completed:
        if journey.style_preference and journey.priority_feature:
            update_data["milestone3_completed"] = True
            update_data["milestone3_completed_at"] = datetime.datetime.utcnow()
            update_data["status"] = "completed"

    if update_data:
        crud.update_journey(db, journey.id, update_data)
        log.step(f"Updated journey {journey.id} milestone completion")
