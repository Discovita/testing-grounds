"""
Pydantic models for request and response validation.

This module defines the data models used for validating API requests and responses.
These models ensure data consistency and provide automatic validation.
"""

from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, Field

# User Models
class UserBase(BaseModel):
    """
    Base model for user data.
    
    Defines the common fields for user creation and updates.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    """
    Model for creating a new user.
    
    Currently inherits all fields from UserBase.
    Can be extended with additional required fields if needed.
    """
    pass

class UserResponse(UserBase):
    """
    Model for user response data.
    
    Includes all user data to be returned in API responses.
    """
    id: int
    created_at: datetime
    
    class Config:
        """Configuration for Pydantic model-ORM integration."""
        from_attributes = True

# Journey Models
class JourneyBase(BaseModel):
    """
    Base model for journey data.
    
    Defines the common fields for journey updates.
    """
    current_milestone: Optional[int] = None
    status: Optional[str] = None
    
    # Milestone 1
    room: Optional[str] = None
    renovation_purpose: Optional[str] = None
    
    # Milestone 2
    budget_range: Optional[str] = None
    timeline: Optional[str] = None
    
    # Milestone 3
    style_preference: Optional[str] = None
    priority_feature: Optional[str] = None

class JourneyCreate(BaseModel):
    """
    Model for creating a new journey.
    
    Requires user_id to associate journey with user.
    """
    user_id: int

class JourneyUpdate(JourneyBase):
    """
    Model for updating journey data.
    
    Inherits all optional fields from JourneyBase.
    """
    pass

class JourneyResponse(JourneyBase):
    """
    Model for journey response data.
    
    Includes all journey data to be returned in API responses.
    """
    id: int
    user_id: int
    milestone1_completed: bool
    milestone2_completed: bool
    milestone3_completed: bool
    milestone1_completed_at: Optional[datetime] = None
    milestone2_completed_at: Optional[datetime] = None
    milestone3_completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Configuration for Pydantic model-ORM integration."""
        from_attributes = True

# Message Models
class MessageBase(BaseModel):
    """
    Base model for message data.
    
    Defines the common fields for message creation.
    """
    content: str
    speaker: str
    current_milestone: int

class MessageCreate(MessageBase):
    """
    Model for creating a new message.
    
    Requires user_id and journey_id to associate message with user and journey.
    """
    user_id: int
    journey_id: int

class MessageResponse(MessageBase):
    """
    Model for message response data.
    
    Includes all message data to be returned in API responses.
    """
    id: int
    user_id: int
    journey_id: int
    timestamp: datetime
    
    class Config:
        """Configuration for Pydantic model-ORM integration."""
        from_attributes = True

# UserAttribute Models
class UserAttributeBase(BaseModel):
    """
    Base model for user attribute data.
    
    Defines the common fields for attribute creation.
    """
    attribute_key: str
    attribute_value: str

class UserAttributeCreate(UserAttributeBase):
    """
    Model for creating a new user attribute.
    
    Requires user_id to associate attribute with user.
    """
    user_id: int
    source_message_id: Optional[int] = None

class UserAttributeResponse(UserAttributeBase):
    """
    Model for user attribute response data.
    
    Includes all attribute data to be returned in API responses.
    """
    id: int
    user_id: int
    source_message_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        """Configuration for Pydantic model-ORM integration."""
        from_attributes = True

# Process Message Models
class ProcessMessageRequest(BaseModel):
    """
    Model for processing a user message.
    
    This model is used to handle a user message and update journey state.
    """
    user_id: int
    journey_id: int
    content: str

class ProcessMessageResponse(BaseModel):
    """
    Model for process message response.
    
    Returns the updated journey state and a system response message.
    """
    journey: JourneyResponse
    system_response: str

# Checkpoint Models
class CheckpointUpdate(BaseModel):
    """
    Model for updating a checkpoint value.
    
    Used by LLM to save extracted checkpoint answers.
    """
    value: str

# Session Models
class SessionCreate(BaseModel):
    """
    Model for creating or resuming a session.
    
    Optionally includes user details for new users.
    """
    user_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class SessionResponse(BaseModel):
    """
    Model for session response data.
    
    Returns user, journey, and recent message data.
    """
    user_id: int
    journey_id: int
    current_milestone: int
    status: str
    recent_messages: Optional[List[MessageResponse]] = None

# Journey State Models for LLM
class JourneyStateResponse(BaseModel):
    """
    Model for journey state response data for LLM.
    
    Provides LLM with current journey state information.
    """
    has_journey: bool
    milestone: Optional[int] = None
    completed_checkpoints: List[str] = []
    milestone_completed: Optional[bool] = None 