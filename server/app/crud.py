"""
CRUD operations for database interactions.

This module provides functions for Creating, Reading, Updating, and Deleting
records in the database. These functions are used by the API endpoints.
"""

import datetime
from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session

from app import schemas, models

# User CRUD operations
def create_user(db: Session, user: models.UserCreate) -> schemas.User:
    """
    Create a new user in the database.
    
    Args:
        db: Database session
        user: User data to create
        
    Returns:
        The created user object
    """
    db_user = schemas.User(
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int) -> Optional[schemas.User]:
    """
    Get a user by ID.
    
    Args:
        db: Database session
        user_id: ID of the user to retrieve
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(schemas.User).filter(schemas.User.id == user_id).first()

def get_users(db: Session) -> List[schemas.User]:
    """
    Get all users for admin dashboard.
    
    Args:
        db: Database session
        
    Returns:
        List of all users, sorted by creation date (newest first)
    """
    return db.query(schemas.User).order_by(schemas.User.created_at.desc()).all()

def update_user(db: Session, user_id: int, user_data: models.UserBase) -> Optional[schemas.User]:
    """
    Update a user's information.
    
    Args:
        db: Database session
        user_id: ID of the user to update
        user_data: New user data
        
    Returns:
        Updated user object if found, None otherwise
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user and all associated data (journeys and messages).
    
    Steps:
    1. Find the user in the database
    2. Find all journeys associated with the user
    3. Delete all messages associated with those journeys
    4. Delete all journeys
    5. Delete the user
    6. Commit the transaction
    
    Args:
        db: Database session
        user_id: ID of the user to delete
        
    Returns:
        True if user was deleted, False if user not found
    """
    # Find the user
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    # Find all journeys for this user
    user_journeys = db.query(schemas.RenovationJourney).filter(
        schemas.RenovationJourney.user_id == user_id
    ).all()
    
    # Extract journey IDs
    journey_ids = [journey.id for journey in user_journeys]
    
    # Delete all messages for these journeys
    if journey_ids:
        db.query(schemas.Message).filter(
            schemas.Message.journey_id.in_(journey_ids)
        ).delete(synchronize_session=False)
    
    # Delete all journeys for this user
    db.query(schemas.RenovationJourney).filter(
        schemas.RenovationJourney.user_id == user_id
    ).delete(synchronize_session=False)
    
    # Delete user
    db.delete(db_user)
    
    # Commit changes
    db.commit()
    
    return True

# Journey CRUD operations
def create_journey(db: Session, journey: models.JourneyCreate) -> schemas.RenovationJourney:
    """
    Create a new journey in the database.
    
    Args:
        db: Database session
        journey: Journey data to create
        
    Returns:
        The created journey object
    """
    db_journey = schemas.RenovationJourney(
        user_id=journey.user_id,
        current_milestone=1,
        status="in_progress"
    )
    db.add(db_journey)
    db.commit()
    db.refresh(db_journey)
    return db_journey

def get_journey(db: Session, journey_id: int) -> Optional[schemas.RenovationJourney]:
    """
    Get a journey by ID.
    
    Args:
        db: Database session
        journey_id: ID of the journey to retrieve
        
    Returns:
        Journey object if found, None otherwise
    """
    return db.query(schemas.RenovationJourney).filter(schemas.RenovationJourney.id == journey_id).first()

def get_journeys(db: Session) -> List[schemas.RenovationJourney]:
    """
    Get all journeys for admin dashboard.
    
    Args:
        db: Database session
        
    Returns:
        List of all journeys, sorted by creation date (newest first)
    """
    return db.query(schemas.RenovationJourney).order_by(schemas.RenovationJourney.created_at.desc()).all()

def get_active_journey(db: Session, user_id: int) -> Optional[schemas.RenovationJourney]:
    """
    Get the active journey for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Active journey object if found, None otherwise
    """
    return db.query(schemas.RenovationJourney).filter(
        schemas.RenovationJourney.user_id == user_id,
        schemas.RenovationJourney.status == "in_progress"
    ).first()

def update_journey(db: Session, journey_id: int, journey_data: Dict[str, Any]) -> Optional[schemas.RenovationJourney]:
    """
    Update a journey's information.
    
    Args:
        db: Database session
        journey_id: ID of the journey to update
        journey_data: New journey data
        
    Returns:
        Updated journey object if found, None otherwise
    """
    db_journey = get_journey(db, journey_id)
    if not db_journey:
        return None
    
    # Handle the case where journey_data is a Pydantic model
    if hasattr(journey_data, "dict"):
        update_data = journey_data.dict(exclude_unset=True)
    else:
        update_data = journey_data
    
    for key, value in update_data.items():
        if hasattr(db_journey, key):
            setattr(db_journey, key, value)
    
    # Always update the timestamp
    db_journey.updated_at = datetime.datetime.utcnow()
    
    db.commit()
    db.refresh(db_journey)
    return db_journey

def advance_milestone(db: Session, journey_id: int) -> Optional[schemas.RenovationJourney]:
    """
    Advance a journey to the next milestone.
    
    Args:
        db: Database session
        journey_id: ID of the journey to advance
        
    Returns:
        Updated journey object if found and advanced, None otherwise
    """
    db_journey = get_journey(db, journey_id)
    if not db_journey or db_journey.current_milestone >= 3:
        return None
    
    db_journey.current_milestone += 1
    db_journey.updated_at = datetime.datetime.utcnow()
    
    db.commit()
    db.refresh(db_journey)
    return db_journey

# Message CRUD operations
def create_message(db: Session, message: models.MessageCreate) -> schemas.Message:
    """
    Create a new message in the database.
    
    Args:
        db: Database session
        message: Message data to create
        
    Returns:
        The created message object
    """
    db_message = schemas.Message(
        user_id=message.user_id,
        journey_id=message.journey_id,
        speaker=message.speaker,
        content=message.content,
        current_milestone=message.current_milestone
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages_for_journey(db: Session, journey_id: int, limit: int = 50) -> List[schemas.Message]:
    """
    Get messages for a journey.
    
    Args:
        db: Database session
        journey_id: ID of the journey
        limit: Maximum number of messages to return
        
    Returns:
        List of messages for the journey
    """
    return db.query(schemas.Message).filter(schemas.Message.journey_id == journey_id) \
        .order_by(schemas.Message.timestamp.desc()).limit(limit).all()

def get_journey_messages(db: Session, journey_id: int, limit: int = 50, descending: bool = False) -> List[schemas.Message]:
    """
    Get messages for a journey, ordered by timestamp.
    
    This function is used by the chat handler to retrieve recent message history
    for context when building prompts and analyzing conversations.
    
    Args:
        db: Database session
        journey_id: ID of the journey
        limit: Maximum number of messages to return
        descending: If True, return newest messages first (default: False, oldest first)
        
    Returns:
        List of messages for the journey, ordered chronologically
    """
    query = db.query(schemas.Message).filter(schemas.Message.journey_id == journey_id)
    
    # Order by timestamp (ascending or descending based on parameter)
    if descending:
        query = query.order_by(schemas.Message.timestamp.desc())
    else:
        query = query.order_by(schemas.Message.timestamp.asc())
        
    return query.limit(limit).all()

def get_all_messages(db: Session, limit: int = 100, offset: int = 0) -> List[schemas.Message]:
    """
    Get all messages for admin dashboard.
    
    Args:
        db: Database session
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        
    Returns:
        List of all messages, sorted by timestamp (newest first)
    """
    return db.query(schemas.Message) \
        .order_by(schemas.Message.timestamp.desc()) \
        .offset(offset) \
        .limit(limit) \
        .all()

# UserAttribute CRUD operations
def create_user_attribute(db: Session, attribute: models.UserAttributeCreate) -> schemas.UserAttribute:
    """
    Create a new user attribute in the database.
    
    Args:
        db: Database session
        attribute: Attribute data to create
        
    Returns:
        The created user attribute object
    """
    db_attribute = schemas.UserAttribute(
        user_id=attribute.user_id,
        attribute_key=attribute.attribute_key,
        attribute_value=attribute.attribute_value,
        source_message_id=attribute.source_message_id
    )
    db.add(db_attribute)
    db.commit()
    db.refresh(db_attribute)
    return db_attribute

def get_user_attributes(db: Session, user_id: int) -> List[schemas.UserAttribute]:
    """
    Get attributes for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        List of user attribute objects
    """
    return db.query(schemas.UserAttribute).filter(
        schemas.UserAttribute.user_id == user_id
    ).all()

# Checkpoint and milestone completion functions
def update_checkpoint(db: Session, journey_id: int, checkpoint_name: str, value: str) -> Optional[schemas.RenovationJourney]:
    """
    Update a checkpoint answer for a journey.
    
    Args:
        db: Database session
        journey_id: ID of the journey
        checkpoint_name: Name of the checkpoint to update
        value: New value for the checkpoint
        
    Returns:
        Updated journey object if found, None otherwise
    """
    # Map checkpoint names to database fields
    field_mapping = {
        'room': 'room',
        'renovation_purpose': 'renovation_purpose',
        'budget_range': 'budget_range',
        'timeline': 'timeline',
        'style_preference': 'style_preference',
        'priority_feature': 'priority_feature'
    }
    
    if checkpoint_name not in field_mapping:
        return None
    
    update_data = {field_mapping[checkpoint_name]: value}
    return update_journey(db, journey_id, update_data)

def check_milestone_completion(db: Session, journey_id: int) -> Optional[schemas.RenovationJourney]:
    """
    Check if the current milestone is complete and update the journey accordingly.
    
    Args:
        db: Database session
        journey_id: ID of the journey to check
        
    Returns:
        Updated journey object if found, None otherwise
    """
    db_journey = get_journey(db, journey_id)
    if not db_journey:
        return None
    
    update_data = {}
    
    # Check Milestone 1
    if db_journey.current_milestone == 1 and not db_journey.milestone1_completed:
        if db_journey.room and db_journey.renovation_purpose:
            update_data["milestone1_completed"] = True
            update_data["milestone1_completed_at"] = datetime.datetime.utcnow()
    
    # Check Milestone 2
    elif db_journey.current_milestone == 2 and not db_journey.milestone2_completed:
        if db_journey.budget_range and db_journey.timeline:
            update_data["milestone2_completed"] = True
            update_data["milestone2_completed_at"] = datetime.datetime.utcnow()
    
    # Check Milestone 3
    elif db_journey.current_milestone == 3 and not db_journey.milestone3_completed:
        if db_journey.style_preference and db_journey.priority_feature:
            update_data["milestone3_completed"] = True
            update_data["milestone3_completed_at"] = datetime.datetime.utcnow()
            update_data["status"] = "completed"
    
    if update_data:
        return update_journey(db, journey_id, update_data)
    
    return db_journey

def complete_journey(db: Session, journey_id: int) -> Optional[schemas.RenovationJourney]:
    """
    Mark a journey as complete.
    
    Args:
        db: Database session
        journey_id: ID of the journey to complete
        
    Returns:
        Updated journey object if found, None otherwise
    """
    update_data = {
        "status": "completed",
        "updated_at": datetime.datetime.utcnow()
    }
    return update_journey(db, journey_id, update_data)

# Session management functions
def start_session(db: Session, user_id: Optional[int] = None, 
                first_name: Optional[str] = None, 
                last_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Start a new session or continue an existing one.
    
    Args:
        db: Database session
        user_id: Optional ID of existing user
        first_name: Optional first name for new user
        last_name: Optional last name for new user
        
    Returns:
        Session information including user and journey IDs
    """
    # Create or retrieve user
    if not user_id:
        user_data = models.UserCreate(first_name=first_name, last_name=last_name)
        user = create_user(db, user_data)
        user_id = user.id
    else:
        user = get_user(db, user_id)
        if not user:
            user_data = models.UserCreate(first_name=first_name, last_name=last_name)
            user = create_user(db, user_data)
            user_id = user.id
    
    # Check for existing journey
    journey = get_active_journey(db, user_id)
    
    if not journey:
        # Create new journey
        journey_data = models.JourneyCreate(user_id=user_id)
        journey = create_journey(db, journey_data)
    
    return {
        'user_id': user_id,
        'journey_id': journey.id,
        'current_milestone': journey.current_milestone,
        'status': journey.status
    }

def get_journey_state_for_llm(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get the current journey state formatted for LLM consumption.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Journey state information in a format suitable for LLM
    """
    journey = get_active_journey(db, user_id)
    if not journey:
        return {
            'has_journey': False,
            'milestone': None,
            'completed_checkpoints': [],
            'milestone_completed': None
        }
    
    # Get completed checkpoints based on milestone
    completed_checkpoints = []
    
    # Milestone 1 checkpoints
    if journey.room:
        completed_checkpoints.append('room')
    if journey.renovation_purpose:
        completed_checkpoints.append('renovation_purpose')
    
    # Milestone 2 checkpoints
    if journey.budget_range:
        completed_checkpoints.append('budget_range')
    if journey.timeline:
        completed_checkpoints.append('timeline')
    
    # Milestone 3 checkpoints
    if journey.style_preference:
        completed_checkpoints.append('style_preference')
    if journey.priority_feature:
        completed_checkpoints.append('priority_feature')
    
    # Determine if current milestone is completed
    milestone_completed = False
    if journey.current_milestone == 1 and journey.milestone1_completed:
        milestone_completed = True
    elif journey.current_milestone == 2 and journey.milestone2_completed:
        milestone_completed = True
    elif journey.current_milestone == 3 and journey.milestone3_completed:
        milestone_completed = True
    
    return {
        'has_journey': True,
        'milestone': journey.current_milestone,
        'completed_checkpoints': completed_checkpoints,
        'milestone_completed': milestone_completed
    } 