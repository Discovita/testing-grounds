"""
Chat handler module for State Machine Demo.

This module provides functions for handling chat conversations with the OpenAI API,
including message processing, function handling, and context management.
"""

from typing import Dict, Any, List
from pydantic import BaseModel

from app.openai import openai_client
from app.models import (
    MessageCreate,
)
from app.schemas import RenovationJourney
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import app.crud as crud
import datetime
from app.chat.sentinel import Sentinel
from app.chat.prompts import get_prompt_for_journey

from cws_helpers.logger import configure_logging

log = configure_logging(__name__)


class JourneyState(BaseModel):
    """
    Journey state model for chat handling.

    This is a mock implementation for the state machine demo.
    """

    id: int
    user_id: int
    current_milestone: int
    status: str
    completed_checkpoints: List[str] = []
    context: Dict[str, Any] = {}


class JourneyHandler:
    """
    Journey state machine handler.

    This handler manages the state transitions and context for a user's
    journey through the chat conversation flow.
    """

    def __init__(self, db: Session):
        """
        Initialize the journey handler.

        Args:
            db: Database session
        """
        self.db = db
        self.sentinel = Sentinel(db)

    async def process_message(
        self, user_id: int, journey_id: int, message_text: str
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response using OpenAI.

        Steps:
        1. Retrieve user and journey data
        2. Save the user message to database
        3. Run Sentinel to analyze message and update journey data if needed
        4. Build context for OpenAI based on updated journey state
        5. Generate appropriate response based on journey state
        6. Save response to database
        7. Return response with updated journey state

        Args:
            user_id: User ID
            journey_id: Journey ID
            message_text: User message text

        Returns:
            Dict with response text and updated journey state
        """
        try:
            # Retrieve actual user and journey data from database
            user = crud.get_user(self.db, user_id)
            journey = crud.get_journey(self.db, journey_id)

            if not user:
                log.error(f"User {user_id} not found")
                return {"error": f"User {user_id} not found"}

            if not journey:
                log.error(f"Journey {journey_id} not found")
                return {"error": f"Journey {journey_id} not found"}

            log.info(f"Processing message for user {user_id}")

            # Save user message to database
            message_data = MessageCreate(
                user_id=user_id,
                journey_id=journey_id,
                speaker="user",
                content=message_text,
                current_milestone=journey.current_milestone,
            )
            user_message = crud.create_message(self.db, message_data)

            # Run Sentinel to analyze the message and update journey data if needed
            # Get most recent messages for context (last 5 messages)
            recent_messages = crud.get_journey_messages(
                self.db, 
                journey_id, 
                limit=5,
                descending=True  # Get messages in descending order (newest first)
            )
            # Reverse the messages to maintain chronological order for analysis
            recent_messages.reverse()
            
            # Create Sentinel and analyze messages
            sentinel_result = await self.sentinel.analyze(journey, recent_messages)
            log.info(f"Journey details after sentinel:")
            for detail in self._format_journey_details(journey, "  "):
                log.info(detail)
                
            # Commit any pending changes to ensure they're visible to subsequent queries
            self.db.commit()
            
            # Get updated journey state after Sentinel analysis
            journey = crud.get_journey(self.db, journey_id)
            
            # Now that we have the updated journey, log the actual details
            log.info(f"Journey details after database refresh:")
            for detail in self._format_journey_details(journey, "  "):
                log.info(detail)

            # Build chat context from updated journey state
            context = self._build_context(journey)

            try:
                # Get recent messages for context (last 10 messages)
                recent_messages = crud.get_journey_messages(
                    self.db, 
                    journey_id, 
                    limit=10,
                    descending=True  # Get messages in descending order (newest first)
                )
                # Reverse the messages to maintain chronological order for the conversation
                recent_messages.reverse()

                # Build the message history for OpenAI
                messages = []

                # Get completed checkpoints for the current milestone
                completed_checkpoints = self._get_completed_checkpoints(journey)

                # Get the appropriate system prompt for the current journey state
                system_prompt = get_prompt_for_journey(
                    journey, context, completed_checkpoints
                )

                # Add system message with instructions
                system_message = {"role": "system", "content": system_prompt}
                messages.append(system_message)

                # Add conversation history
                for msg in recent_messages:
                    role = "user" if msg.speaker == "user" else "assistant"
                    messages.append({"role": role, "content": msg.content})

                # Add current user message
                messages.append({"role": "user", "content": message_text})

                # Log call to OpenAI
                log.step(f"Responding to user after Sentinel analysis")
                log.info(f"Milestone: {journey.current_milestone}")
                log.info(f"Completed Checkpoints: {completed_checkpoints}")

                # Call OpenAI without functions to get response
                response = await openai_client.create_response_with_responses(
                    input_data=messages, model="gpt-4o"
                )

                # Get response content from OpenAI
                if response.output and len(response.output) > 0:
                    # Look for text content in the first output message
                    for item in response.output:
                        # Check if this is a message with text content
                        if hasattr(item, "content") and item.content:
                            for content_item in item.content:
                                if hasattr(content_item, "text") and content_item.text:
                                    response_text = content_item.text
                                    break
                            else:
                                continue
                            break
                    else:
                        response_text = "I'm sorry, I couldn't generate a response."
                else:
                    response_text = "I'm sorry, I couldn't generate a response."

                # Save assistant response
                assistant_message_data = MessageCreate(
                    user_id=user_id,
                    journey_id=journey_id,
                    speaker="assistant",
                    content=response_text,
                    current_milestone=journey.current_milestone,
                )
                assistant_message = crud.create_message(self.db, assistant_message_data)

                # Log assistant response
                log.info(f"Generated response for user {user_id}")

                # Return the response with journey state
                return {
                    "response_text": response_text,
                    "journey_state": {
                        "milestone": journey.current_milestone,
                        "completed_checkpoints": completed_checkpoints,
                        "status": journey.status,
                    },
                    "sentinel_result": sentinel_result,
                }

            except Exception as e:
                log.error(f"Error processing message: {str(e)}")
                log.error(f"Journey ID: {journey_id}")
                log.error(f"User ID: {user_id}")

                # If OpenAI fails, fall back to manual keyword analysis
                log.info("Falling back to manual keyword analysis")

                # Analyze message to extract relevant information using our fallback method
                updated_journey = await self._analyze_message_for_checkpoints(
                    journey, message_text
                )

                # Generate response based on current state using our fallback method
                fallback_response = self._generate_response(
                    updated_journey, message_text
                )
                response_text = (
                    str(fallback_response)
                    if fallback_response is not None
                    else "I'm sorry, I couldn't process your message."
                )

                # Save assistant response
                assistant_message_data = MessageCreate(
                    user_id=user_id,
                    journey_id=journey_id,
                    speaker="assistant",
                    content=response_text,
                    current_milestone=updated_journey.current_milestone,
                )
                assistant_message = crud.create_message(self.db, assistant_message_data)

                return {
                    "response_text": response_text,
                    "journey_state": {
                        "milestone": updated_journey.current_milestone,
                        "completed_checkpoints": self._get_completed_checkpoints(
                            updated_journey
                        ),
                        "status": updated_journey.status,
                    },
                    "sentinel_result": sentinel_result,
                }

        except SQLAlchemyError as e:
            log.error(f"Database error: {str(e)}")
            log.error(f"User ID: {user_id}")
            log.error(f"Journey ID: {journey_id}")
            return {
                "error": str(e),
                "response_text": "Sorry, there was a database error. Please try again.",
            }

    def _build_context(self, journey: RenovationJourney) -> Dict[str, Any]:
        """
        Build context information for the OpenAI request based on journey state.

        Args:
            journey: Journey object

        Returns:
            Dict with journey context information
        """
        # Create context dictionary with milestone info
        context = {
            "milestone": journey.current_milestone,
            "completed_checkpoints": self._get_completed_checkpoints(journey),
        }

        # Add checkpoint values based on milestone
        if journey.current_milestone >= 1:
            if journey.room:
                context["room"] = journey.room
            if journey.renovation_purpose:
                context["renovation_purpose"] = journey.renovation_purpose

        if journey.current_milestone >= 2:
            if journey.budget_range:
                context["budget_range"] = journey.budget_range
            if journey.timeline:
                context["timeline"] = journey.timeline

        if journey.current_milestone >= 3:
            if journey.style_preference:
                context["style_preference"] = journey.style_preference
            if journey.priority_feature:
                context["priority_feature"] = journey.priority_feature

        return context

    def _get_completed_checkpoints(self, journey: RenovationJourney) -> List[str]:
        """
        Get list of completed checkpoints for the current milestone.

        Args:
            journey: Journey object

        Returns:
            List of checkpoint names that have been completed
        """
        completed = []

        if journey.current_milestone == 1:
            if journey.room:
                completed.append("room")
            if journey.renovation_purpose:
                completed.append("renovation_purpose")
        elif journey.current_milestone == 2:
            if journey.budget_range:
                completed.append("budget_range")
            if journey.timeline:
                completed.append("timeline")
        elif journey.current_milestone == 3:
            if journey.style_preference:
                completed.append("style_preference")
            if journey.priority_feature:
                completed.append("priority_feature")

        return completed

    async def _analyze_message_for_checkpoints(
        self, journey: RenovationJourney, message: str
    ) -> RenovationJourney:
        """
        Analyze user message to extract checkpoint information.

        This is a simple implementation that looks for keywords.
        In a real implementation, this would use the LLM to extract information.

        Args:
            journey: Journey object
            message: User message text

        Returns:
            Updated journey object
        """
        message_lower = message.lower()
        update_data = {}

        # Extract information based on current milestone
        if journey.current_milestone == 1:
            # Look for room information
            room_keywords = {
                "kitchen": "kitchen",
                "bathroom": "bathroom",
                "bedroom": "bedroom",
                "living room": "living room",
                "basement": "basement",
            }

            for keyword, value in room_keywords.items():
                if keyword in message_lower and not journey.room:
                    update_data["room"] = value
                    break

            # Look for renovation purpose
            purpose_keywords = {
                "aesthetic": "aesthetic",
                "functional": "functional",
                "repair": "repair",
                "expand": "expand space",
                "modern": "modernize",
            }

            for keyword, value in purpose_keywords.items():
                if keyword in message_lower and not journey.renovation_purpose:
                    update_data["renovation_purpose"] = value
                    break

        elif journey.current_milestone == 2:
            # Look for budget information
            budget_keywords = {
                "cheap": "low",
                "affordable": "low",
                "reasonable": "medium",
                "mid": "medium",
                "expensive": "high",
                "luxury": "high",
            }

            for keyword, value in budget_keywords.items():
                if keyword in message_lower and not journey.budget_range:
                    update_data["budget_range"] = value
                    break

            # Look for timeline expectations
            timeline_keywords = {
                "quick": "weeks",
                "fast": "weeks",
                "soon": "weeks",
                "month": "months",
                "long": "months",
            }

            for keyword, value in timeline_keywords.items():
                if keyword in message_lower and not journey.timeline:
                    update_data["timeline"] = value
                    break

        elif journey.current_milestone == 3:
            # Look for style preferences
            style_keywords = {
                "modern": "modern",
                "traditional": "traditional",
                "rustic": "rustic",
                "minimalist": "minimalist",
                "contemporary": "contemporary",
            }

            for keyword, value in style_keywords.items():
                if keyword in message_lower and not journey.style_preference:
                    update_data["style_preference"] = value
                    break

            # Look for priority features
            feature_keywords = {
                "storage": "increased storage",
                "light": "natural lighting",
                "space": "open space",
                "energy": "energy efficiency",
                "smart": "smart home features",
            }

            for keyword, value in feature_keywords.items():
                if keyword in message_lower and not journey.priority_feature:
                    update_data["priority_feature"] = value
                    break

        # Update journey if we extracted any information
        if update_data:
            crud.update_journey(self.db, journey.id, update_data)

            # Get updated journey
            updated_journey = crud.get_journey(self.db, journey.id)

            # Check if milestone completion criteria are met
            self._check_milestone_completion(updated_journey)

            # Get fresh data after potential milestone completion
            return crud.get_journey(self.db, journey.id)

        return journey

    def _check_milestone_completion(self, journey: RenovationJourney) -> None:
        """
        Check if current milestone is complete and update journey accordingly.

        Args:
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
            crud.update_journey(self.db, journey.id, update_data)
            log.step(f"Updated journey {journey.id} milestone completion")

    def _generate_response(self, journey: RenovationJourney, user_message: str) -> str:
        """
        Generate a response based on the current journey state.

        This is a simple template-based implementation.
        In a real implementation, this would use the LLM.

        Args:
            journey: Journey object
            user_message: User message text

        Returns:
            Response text
        """
        # Get completed checkpoints for current milestone
        completed_checkpoints = self._get_completed_checkpoints(journey)

        # Default response
        response = f"Thanks for your message! I'm helping you plan your renovation."

        # Add milestone-specific information
        if journey.current_milestone == 1:
            response += (
                " Let's start by figuring out the basic details of your project."
            )

            if "room" not in completed_checkpoints:
                response += " Which room are you planning to renovate?"
            elif "renovation_purpose" not in completed_checkpoints:
                room = getattr(journey, "room", "")
                response += f" What's the main purpose of renovating your {room}?"
            elif getattr(journey, "milestone1_completed", False):
                room = getattr(journey, "room", "")
                purpose = getattr(journey, "renovation_purpose", "")
                response += f" Great! We've established that you want to renovate your {room} for {purpose}. Let's move on to budget and timeline considerations."

        elif journey.current_milestone == 2:
            response += " Now let's talk about your budget and timeline."

            if "budget_range" not in completed_checkpoints:
                response += (
                    " What kind of budget do you have in mind? (low, medium, high)"
                )
            elif "timeline" not in completed_checkpoints:
                room = getattr(journey, "room", "")
                response += (
                    f" How quickly are you hoping to complete this {room} renovation?"
                )
            elif getattr(journey, "milestone2_completed", False):
                budget = getattr(journey, "budget_range", "")
                timeline = getattr(journey, "timeline", "")
                response += f" Perfect! You're looking at a {budget} budget with a timeline of {timeline}. Let's discuss your style preferences next."

        elif journey.current_milestone == 3:
            response += " Finally, let's talk about style and specific features."

            if "style_preference" not in completed_checkpoints:
                response += " What style are you going for? (modern, traditional, etc.)"
            elif "priority_feature" not in completed_checkpoints:
                style = getattr(journey, "style_preference", "")
                room = getattr(journey, "room", "")
                response += f" What's the most important feature you want in your {style} {room}?"
            elif getattr(journey, "milestone3_completed", False):
                style = getattr(journey, "style_preference", "")
                room = getattr(journey, "room", "")
                feature = getattr(journey, "priority_feature", "")
                budget = getattr(journey, "budget_range", "")
                timeline = getattr(journey, "timeline", "")
                response += f" Excellent! I now have a complete picture of your renovation plans. You want a {style} {room} with {feature} as a priority feature, on a {budget} budget, completing in {timeline}. Your renovation journey is complete!"

        # Special case for completed journey
        if journey.status == "completed":
            style = getattr(journey, "style_preference", "")
            room = getattr(journey, "room", "")
            purpose = getattr(journey, "renovation_purpose", "")
            feature = getattr(journey, "priority_feature", "")
            budget = getattr(journey, "budget_range", "")
            timeline = getattr(journey, "timeline", "")
            response = f"Your renovation plan is complete! To summarize: A {style} {room} renovation focusing on {purpose} with {feature} as a key feature. Your budget is in the {budget} range with a timeline of {timeline}. Thank you for using our service!"

        return response

    def _format_journey_details(
        self, journey: RenovationJourney, prefix: str = ""
    ) -> List[str]:
        """
        Format journey details into a list of formatted strings for consistent logging.

        Args:
            journey: The journey to format
            prefix: Prefix to add to each line (for indentation)

        Returns:
            List of formatted strings with journey details
        """
        return [
            f"{prefix}User ID: {journey.user_id}",
            f"{prefix}Current milestone: {journey.current_milestone}",
            f"{prefix}Status: {journey.status}",
            f"{prefix}Room: {journey.room}",
            f"{prefix}Renovation purpose: {journey.renovation_purpose}",
            f"{prefix}Budget range: {journey.budget_range}",
            f"{prefix}Timeline: {journey.timeline}",
            f"{prefix}Style preference: {journey.style_preference}",
            f"{prefix}Priority feature: {journey.priority_feature}",
            f"{prefix}Milestone 1 completed: {journey.milestone1_completed}",
            f"{prefix}Milestone 2 completed: {journey.milestone2_completed}",
            f"{prefix}Milestone 3 completed: {journey.milestone3_completed}",
        ]


# Create the handler
async def get_chat_handler(db: Session) -> JourneyHandler:
    """
    Get a chat handler instance with database session.

    Args:
        db: Database session

    Returns:
        JourneyHandler instance
    """
    return JourneyHandler(db)
