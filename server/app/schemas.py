"""
SQLAlchemy ORM models for the State Machine Demo application.

This module defines the database tables and relationships using SQLAlchemy ORM.
The schema follows the design outlined in the project documentation.
"""

import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    """
    User model representing a person interacting with the system.
    
    This is a simple model storing basic user information.
    In a production system, this would include authentication details.
    
    Used in:
    - RenovationJourney: tracks user's journey progress
    - Message: associates chat messages with users
    - UserAttribute: stores extracted user information
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    journeys = relationship("RenovationJourney", back_populates="user")
    messages = relationship("Message", back_populates="user")
    attributes = relationship("UserAttribute", back_populates="user")

class RenovationJourney(Base):
    """
    RenovationJourney model tracking the user's progress through the renovation guide.
    
    This model stores:
    - The current milestone the user is on
    - Answers to all checkpoints across milestones
    - Completion status for each milestone
    
    Used in:
    - Message: tracks which journey messages belong to
    """
    __tablename__ = "renovation_journeys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    current_milestone = Column(Integer, default=1)
    status = Column(String, default="in_progress")  # in_progress, completed, abandoned
    
    # Milestone 1: Project Basics
    room = Column(String, nullable=True)
    renovation_purpose = Column(String, nullable=True)
    milestone1_completed = Column(Boolean, default=False)
    milestone1_completed_at = Column(DateTime, nullable=True)
    
    # Milestone 2: Budget and Timeline
    budget_range = Column(String, nullable=True)
    timeline = Column(String, nullable=True)
    milestone2_completed = Column(Boolean, default=False)
    milestone2_completed_at = Column(DateTime, nullable=True)
    
    # Milestone 3: Style and Plan
    style_preference = Column(String, nullable=True)
    priority_feature = Column(String, nullable=True)
    milestone3_completed = Column(Boolean, default=False)
    milestone3_completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="journeys")
    messages = relationship("Message", back_populates="journey")

class Message(Base):
    """
    Message model storing all chat interactions between user and system.
    
    Each message is associated with a user and journey, and records:
    - Who sent the message (user or system)
    - The message content
    - The milestone active when the message was sent
    - When the message was sent
    
    Used to:
    - Provide chat history
    - Track conversation context
    - Associate source of extracted user attributes
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    journey_id = Column(Integer, ForeignKey("renovation_journeys.id"), nullable=False)
    speaker = Column(String, nullable=False)  # 'user' or 'system'
    content = Column(Text, nullable=False)
    current_milestone = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="messages")
    journey = relationship("RenovationJourney", back_populates="messages")
    attributes = relationship("UserAttribute", back_populates="source_message")

class UserAttribute(Base):
    """
    UserAttribute model storing extracted information about users.
    
    This model captures facts learned about the user during conversation,
    such as preferences, family details, or other relevant information
    that can be used for personalization.
    
    Each attribute has:
    - A key (the type of information)
    - A value (the specific information)
    - A source message reference (where this information was extracted from)
    """
    __tablename__ = "user_attributes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attribute_key = Column(String, nullable=False)
    attribute_value = Column(String, nullable=False)
    source_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="attributes")
    source_message = relationship("Message", back_populates="attributes") 