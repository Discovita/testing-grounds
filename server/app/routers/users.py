"""
Users router for State Machine Demo.

This module provides API endpoints for user management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, models, schemas
from app.database import get_db

# ------------------ Configure Logging ------------------ #
from cws_helpers.logger import configure_logging

log = configure_logging(__name__)


# Create router
router = APIRouter()


@router.post(
    "/", response_model=models.UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(user: models.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.

    Args:
        user: User data
        db: Database session

    Returns:
        Created user
    """
    # Create user
    db_user = crud.create_user(db, user)

    # Log user creation
    log.info(f"Created user, {db_user}")

    return db_user


@router.get("/{user_id}", response_model=models.UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user details.

    Args:
        user_id: User ID
        db: Database session

    Returns:
        User details

    Raises:
        HTTPException: If user not found
    """
    # Get user
    db_user = crud.get_user(db, user_id)

    # Check if user exists
    if db_user is None:
        log.warning(f"User with ID {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    log.info(f"Retrieved user with ID {user_id}")

    return db_user


@router.put("/{user_id}", response_model=models.UserResponse)
async def update_user(
    user_id: int, user: models.UserBase, db: Session = Depends(get_db)
):
    """
    Update user details.

    Args:
        user_id: User ID
        user: User data to update
        db: Database session

    Returns:
        Updated user

    Raises:
        HTTPException: If user not found
    """
    # Update user
    db_user = crud.update_user(db, user_id, user)

    data = {"user_id": user_id, "update_data": user.model_dump(exclude_unset=True)}
    # Check if user exists
    if db_user is None:
        log.warning(f"User not found for update: {data}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Log user update
    log.info(
        f"Updated user with ID {user_id}",
        {"user_id": user_id, "updated_fields": user.dict(exclude_unset=True)},
    )

    return db_user


@router.get("/", response_model=List[models.UserResponse])
async def get_all_users(db: Session = Depends(get_db)):
    """
    Get all users for admin dashboard.

    Steps:
    1. Query all users from the database
    2. Return the list of users sorted by creation date (newest first)

    Args:
        db: Database session

    Returns:
        List of all user objects
    """
    # Get all users
    users = crud.get_users(db)

    log.info(f"Retrieved all users, count: {len(users)}")

    return users


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user and all associated data.

    Steps:
    1. Delete all messages associated with the user's journeys
    2. Delete all journeys associated with the user
    3. Delete the user

    Args:
        user_id: ID of the user to delete
        db: Database session

    Returns:
        204 No Content on success

    Raises:
        HTTPException: If user not found
    """
    # Delete user and associated data
    success = crud.delete_user(db, user_id)

    # Check if user was found and deleted
    if not success:
        log.warning(f"User with ID {user_id} not found for deletion")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Log user deletion
    log.info(f"Deleted user with ID {user_id} and all associated data")

    # Return 204 No Content (default for successful deletion)
    return
