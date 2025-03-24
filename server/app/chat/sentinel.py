"""
Sentinel module for State Machine Demo.

This module provides a lightweight analyzer that monitors conversations and makes
decisions about when to update the journey state based on specific checkpoint questions.

The Sentinel acts as a focused information extractor that:
1. Uses a faster LLM model to reduce latency
2. Only looks for answers to the current active checkpoint question
3. Updates journey state when confident information has been provided
4. Checks milestone completion criteria after updates

This approach allows for real-time journey state updates without introducing
significant latency to the user experience.
"""

from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from .sentinel_functions import update_journey_function, update_journey

from app.openai import openai_client
from app.schemas import RenovationJourney, Message
import app.crud as crud
import datetime

from cws_helpers.logger import configure_logging

log = configure_logging(__name__)


class Sentinel:
    """
    A lightweight analyzer that monitors conversations to extract specific information
    and update journey state through function calls.

    The Sentinel serves as an efficient information extraction system that:
    - Uses minimal context (only recent messages)
    - Focuses on one checkpoint question at a time
    - Employs a faster LLM model to minimize latency
    - Updates journey state conservatively (only when confident)
    - Checks milestone completion after updates

    This approach allows the system to maintain up-to-date journey state
    without significantly impacting response time for users.
    """

    def __init__(self, db: Session):
        """
        Initialize the sentinel with a database session.

        Args:
            db: Database session for accessing and updating journey data
        """
        self.db = db

    async def analyze(
        self, journey: RenovationJourney, recent_messages: List[Message]
    ) -> RenovationJourney:
        """
        Analyze recent messages and update journey if needed.

        This method examines the last few messages in the conversation to determine
        if the user has provided information that can be used to update their journey.
        The analysis is performed using an LLM with a specific function-calling capability
        that allows direct update of journey fields.

        Args:
            journey: Current journey state containing milestone and checkpoint information
            recent_messages: Recent chat messages (last 5) to analyze for checkpoint answers

        Returns:
            Updated journey object with any new information extracted from messages
        """
        try:
            # Log journey details in a readable format
            log.step(f"Sentinel analyzing messages for journey {journey.id}")
            log.info(f"Journey details:")
            for detail in self._format_journey_details(journey, "  "):
                log.info(detail)

            # Build a prompt for the LLM that explains the current journey context
            system_prompt = self._build_system_message(journey, recent_messages)

            # Format messages for the LLM context
            formatted_messages = []

            # Add system message with Sentinel instructions
            formatted_messages.append({"role": "system", "content": system_prompt})

            function_handlers = {
                "update_journey": lambda args, ctx: update_journey(
                    journey_id=args.get("journey_id", journey.id),
                    checkpoint_name=args.get("checkpoint_name"),
                    value=args.get("value"),
                    db=self.db
                )
            }

            # Call OpenAI with the function definition
            log.step(
                f"============= Sentinel calling OpenAI to analyze journey {journey.id} ============="
            )
            try:
                response = await openai_client.call_functions_with_responses(
                    input_data=formatted_messages,
                    functions=[update_journey_function],
                    function_handlers=function_handlers,
                    model="gpt-4o",
                )
                log.step(
                    f"============= Sentinel called OpenAI ============="
                )
                log.info(f"OpenAI response: {response}")
            except Exception as e:
                log.error(f"Error in OpenAI function call: {str(e)}")
                log.error("This error is non-fatal, continuing with journey update checks")
                log.step("============= Sentinel OpenAI call had errors but continuing =============")

            # Commit any pending database changes
            self.db.commit()

            # Get the updated journey after potential function calls
            updated_journey = crud.get_journey(self.db, journey.id)

            # Check if the journey was updated
            if self._journey_was_updated(journey, updated_journey):
                log.info(f"Sentinel updated journey {journey.id}")

                # Log the updated journey details
                log.info(f"Updated journey details:")
                for detail in self._format_journey_details(updated_journey, "  "):
                    log.info(detail)

                return updated_journey

            log.info(f"Sentinel did not update journey {journey.id}")
            return journey

        except Exception as e:
            log.error(f"Error in sentinel analysis: {str(e)}")
            log.error(f"Journey ID: {journey.id}")
            
            # Attempt to commit any pending changes even in case of error
            try:
                self.db.commit()
            except Exception as commit_error:
                log.error(f"Error committing database changes: {str(commit_error)}")

            return journey

    def _build_system_message(
        self, journey: RenovationJourney, recent_messages: List[Message]
    ) -> str:
        """
        Build a system message for the Sentinel analysis.

        This creates a prompt that explains:
        1. The current state of the user's journey
        2. What information we're looking for
        3. How to update the journey when information is found

        Args:
            journey: Current journey state
            recent_messages: Recent messages to analyze

        Returns:
            System prompt text
        """
        # Get the current milestone and next checkpoint needed
        next_question, next_checkpoint = self._get_next_checkpoint_to_extract(journey)

        # Get completed checkpoints as human-readable list
        completed = self._get_completed_checkpoints_text(journey)

        # Add user/assistant messages as the conversation history to analyze
        conversation_history = ""
        for msg in recent_messages:
            role = "User" if msg.speaker == "user" else "Assistant"
            conversation_history += f"\n{role}: {msg.content}"

        # Build the base prompt
        system_message = f"""You are a Journey Sentinel that analyzes conversations to extract information about a user's renovation project.

CURRENT JOURNEY STATE:
- User ID: {journey.user_id}
- Journey ID: {journey.id}
- Current Milestone: {journey.current_milestone}
- Completed checkpoints: {completed}

NEXT INFORMATION NEEDED:
- Checkpoint: {next_checkpoint if next_checkpoint else "All checkpoints for current milestone completed"}
- Question: {next_question if next_question else "No pending questions for current milestone"}

Your task is to analyze the conversation and determine if the user has provided information about their renovation journey. If you find relevant information, use the update_journey function to save it.
Here is the conversation history to analyze:
{conversation_history}

GUIDELINES:
1. Focus ONLY on extracting information for the CURRENT checkpoint
2. Be conservative - only extract information if you are confident it directly answers the needed question
3. Do not make assumptions or extract unrelated information
4. If no relevant information is found, do not call any functions

FUNCTION USAGE:
- Call update_journey with three parameters:
  - journey_id: {journey.id} (always use this exact ID)
  - checkpoint_name: The name of the checkpoint (e.g., "room", "budget_range")
  - value: The value you extracted from the conversation
- Example: update_journey(journey_id={journey.id}, checkpoint_name="room", value="kitchen")
- Only call this function when you've identified a clear answer to the current checkpoint question
"""

        # Add checkpoint-specific guidance
        if next_checkpoint:
            system_message += "\n\n" + self._get_checkpoint_specific_guidance(
                next_checkpoint
            )
        log.info(f"Sentinel system message:\n{system_message}")
        return system_message

    def _get_checkpoint_specific_guidance(self, checkpoint: str) -> str:
        """
        Get specific extraction guidelines based on checkpoint type.

        Args:
            checkpoint: The checkpoint we're trying to extract

        Returns:
            Checkpoint-specific guidance text
        """
        log.info(f"Sentinel getting guidance for checkpoint: {checkpoint}")
        if checkpoint == "room":
            return """ROOM GUIDELINES:
- Look for mentions of specific rooms (kitchen, bathroom, bedroom, etc.)
- Extract just the room name (e.g., "kitchen", "bathroom", "master bedroom")
- Examples: "I want to renovate my kitchen", "My bathroom needs work", "The living room is outdated"
- Valid values include: kitchen, bathroom, bedroom, living room, dining room, basement, attic, office, etc."""

        elif checkpoint == "renovation_purpose":
            return """RENOVATION PURPOSE GUIDELINES:
- Look for why the user wants to renovate
- Categorize as one of: aesthetic, functional, repair, modernize, expand space
- Examples: "I want it to look better" (aesthetic), "I need more counter space" (functional), "The pipes are leaking" (repair)
- The purpose should be a single word or short phrase from the standard categories"""

        elif checkpoint == "budget_range":
            return """BUDGET RANGE GUIDELINES:
- Look for mentions of budget or cost expectations
- Categorize as: low, medium, or high
- Examples: "I want to keep costs down" (low), "I have a reasonable budget" (medium), "Money is no object" (high)
- The budget should be one of the three standard categories: low, medium, high"""

        elif checkpoint == "timeline":
            return """TIMELINE GUIDELINES:
- Look for mentions of timing or scheduling expectations
- Categorize as: weeks or months
- Examples: "I need this done ASAP" (weeks), "I'm not in a rush" (months), "Before summer" (months)
- The timeline should be one of the two standard categories: weeks, months"""

        elif checkpoint == "style_preference":
            return """STYLE PREFERENCE GUIDELINES:
- Look for mentions of design style or aesthetic preferences
- Categorize as: modern, traditional, rustic, minimalist, contemporary
- Examples: "I like clean lines" (modern), "I prefer classic designs" (traditional), "I want a cabin feel" (rustic)
- The style should be one of the standard categories mentioned above"""

        elif checkpoint == "priority_feature":
            return """PRIORITY FEATURE GUIDELINES:
- Look for mentions of what features are most important to the user
- Categorize as: storage, lighting, space, energy efficiency, smart features
- Examples: "I need more cabinet space" (storage), "The room is too dark" (lighting), "I want eco-friendly appliances" (energy efficiency)
- The priority feature should be one of the standard categories mentioned above"""

        return ""

    def _get_next_checkpoint_to_extract(
        self, journey: RenovationJourney
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Determine which checkpoint question we need to extract next based on the journey state.

        Args:
            journey: Current journey state

        Returns:
            Tuple of (question text, checkpoint name) or (None, None) if no active question
        """
        # Milestone 1: Project Basics
        if journey.current_milestone == 1:
            if not journey.room:
                return "Which room do you want to renovate?", "room"
            if not journey.renovation_purpose:
                return (
                    "What is the main purpose of your renovation?",
                    "renovation_purpose",
                )

        # Milestone 2: Budget and Timeline
        elif journey.current_milestone == 2:
            if not journey.budget_range:
                return (
                    "What kind of budget do you have in mind for this renovation?",
                    "budget_range",
                )
            if not journey.timeline:
                return (
                    "How quickly are you hoping to complete this renovation?",
                    "timeline",
                )

        # Milestone 3: Style Preferences and Plan
        elif journey.current_milestone == 3:
            if not journey.style_preference:
                return (
                    "What style are you going for in this renovation?",
                    "style_preference",
                )
            if not journey.priority_feature:
                return (
                    "What's the most important feature you want in your renovation?",
                    "priority_feature",
                )

        # No active checkpoint question
        return None, None

    def _get_completed_checkpoints_text(self, journey: RenovationJourney) -> str:
        """
        Get a text representation of completed checkpoints for the prompt.

        Args:
            journey: Current journey state

        Returns:
            Text listing completed checkpoints with values
        """
        completed = []

        if journey.room:
            completed.append(f"room: {journey.room}")
        if journey.renovation_purpose:
            completed.append(f"renovation_purpose: {journey.renovation_purpose}")
        if journey.budget_range:
            completed.append(f"budget_range: {journey.budget_range}")
        if journey.timeline:
            completed.append(f"timeline: {journey.timeline}")
        if journey.style_preference:
            completed.append(f"style_preference: {journey.style_preference}")
        if journey.priority_feature:
            completed.append(f"priority_feature: {journey.priority_feature}")

        if not completed:
            return "None"

        return ", ".join(completed)

    def _get_valid_checkpoints_for_milestone(self, milestone: int) -> List[str]:
        """
        Get the valid checkpoints for a specific milestone.

        Args:
            milestone: The milestone number

        Returns:
            List of valid checkpoint names
        """
        if milestone == 1:
            return ["room", "renovation_purpose"]
        elif milestone == 2:
            return ["budget_range", "timeline"]
        elif milestone == 3:
            return ["style_preference", "priority_feature"]
        else:
            return []

    def _validate_checkpoint_value(self, checkpoint: str, value: str) -> Optional[str]:
        """
        Validate and normalize checkpoint values based on type.

        Args:
            checkpoint: The checkpoint type
            value: The proposed value

        Returns:
            Validated/normalized value or None if invalid
        """
        value = value.strip().lower()

        if checkpoint == "room":
            # Any reasonable room name is acceptable
            valid_rooms = [
                "kitchen",
                "bathroom",
                "bedroom",
                "living room",
                "dining room",
                "basement",
                "attic",
                "office",
                "master bedroom",
                "guest bedroom",
                "den",
                "family room",
                "laundry room",
                "utility room",
                "garage",
            ]
            # Allow any room that contains one of the valid room words
            for room in valid_rooms:
                if room in value:
                    return room
            return value  # Allow custom rooms

        elif checkpoint == "renovation_purpose":
            valid_purposes = [
                "aesthetic",
                "functional",
                "repair",
                "modernize",
                "expand space",
            ]
            for purpose in valid_purposes:
                if purpose in value:
                    return purpose
            # Provide some common mappings
            if "look" in value or "appearanc" in value or "beaut" in value:
                return "aesthetic"
            if "use" in value or "practi" in value or "utili" in value:
                return "functional"
            if "fix" in value or "broke" in value or "damage" in value:
                return "repair"
            if "updat" in value or "renew" in value or "fresh" in value:
                return "modernize"
            if "more room" in value or "bigger" in value or "larger" in value:
                return "expand space"
            return value

        elif checkpoint == "budget_range":
            if (
                "low" in value
                or "cheap" in value
                or "afford" in value
                or "budget" in value
                or "inexpens" in value
            ):
                return "low"
            if (
                "medium" in value
                or "moderate" in value
                or "reasonable" in value
                or "mid" in value
            ):
                return "medium"
            if (
                "high" in value
                or "expens" in value
                or "premium" in value
                or "luxury" in value
            ):
                return "high"
            # Default to medium if unclear
            return "medium"

        elif checkpoint == "timeline":
            if (
                "quick" in value
                or "fast" in value
                or "soon" in value
                or "week" in value
                or "day" in value
                or "asap" in value
            ):
                return "weeks"
            if (
                "slow" in value
                or "month" in value
                or "time" in value
                or "no rush" in value
                or "not urgent" in value
            ):
                return "months"
            # Default to months if unclear
            return "months"

        elif checkpoint == "style_preference":
            if (
                "modern" in value
                or "contemporary" in value
                or "sleek" in value
                or "clean" in value
            ):
                return "modern"
            if "tradition" in value or "classic" in value or "conventional" in value:
                return "traditional"
            if (
                "rustic" in value
                or "country" in value
                or "farmhouse" in value
                or "cabin" in value
                or "wood" in value
            ):
                return "rustic"
            if "minimal" in value or "simple" in value or "clean" in value:
                return "minimalist"
            if "contemp" in value or "current" in value:
                return "contemporary"
            # Default to modern if unclear
            return "modern"

        elif checkpoint == "priority_feature":
            if (
                "storage" in value
                or "cabinet" in value
                or "space" in value
                or "organization" in value
            ):
                return "storage"
            if (
                "light" in value
                or "bright" in value
                or "dark" in value
                or "window" in value
            ):
                return "lighting"
            if (
                "space" in value
                or "room" in value
                or "area" in value
                or "open" in value
            ):
                return "space"
            if (
                "energy" in value
                or "efficient" in value
                or "eco" in value
                or "green" in value
            ):
                return "energy efficiency"
            if (
                "smart" in value
                or "tech" in value
                or "automation" in value
                or "device" in value
            ):
                return "smart features"
            # Default to space if unclear
            return "space"

        return value

    def _check_milestone_completion(self, journey: RenovationJourney) -> None:
        """
        Check if the current milestone is complete and update journey accordingly.

        Each milestone has specific completion criteria:
        - Milestone 1: both room and renovation_purpose must be set
        - Milestone 2: both budget_range and timeline must be set
        - Milestone 3: both style_preference and priority_feature must be set
          (also marks the journey as completed)

        If all required checkpoints for a milestone are satisfied, this method updates
        the journey to reflect milestone completion.

        Args:
            journey: Journey object to check for milestone completion
        """
        update_data = {}

        # Check Milestone 1 completion (Project Basics)
        if journey.current_milestone == 1 and not journey.milestone1_completed:
            if journey.room and journey.renovation_purpose:
                update_data["milestone1_completed"] = True
                update_data["milestone1_completed_at"] = datetime.datetime.utcnow()

        # Check Milestone 2 completion (Budget and Timeline)
        elif journey.current_milestone == 2 and not journey.milestone2_completed:
            if journey.budget_range and journey.timeline:
                update_data["milestone2_completed"] = True
                update_data["milestone2_completed_at"] = datetime.datetime.utcnow()

        # Check Milestone 3 completion (Style Preferences) - also completes journey
        elif journey.current_milestone == 3 and not journey.milestone3_completed:
            if journey.style_preference and journey.priority_feature:
                update_data["milestone3_completed"] = True
                update_data["milestone3_completed_at"] = datetime.datetime.utcnow()
                update_data["status"] = "completed"

        # If any milestone was completed, update the journey
        if update_data:
            crud.update_journey(self.db, journey.id, update_data)
            log.step(f"Sentinel updated journey {journey.id} milestone completion")
            log.info(f"Journey: {journey}")

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

    def _journey_was_updated(self, original: RenovationJourney, updated: RenovationJourney) -> bool:
        """
        Check if any important fields in the journey were updated.
        
        Args:
            original: Original journey state
            updated: Updated journey state
            
        Returns:
            True if any relevant fields were updated, False otherwise
        """
        # Check all checkpoint fields
        checkpoint_fields = [
            "room", "renovation_purpose", "budget_range",
            "timeline", "style_preference", "priority_feature"
        ]
        
        for field in checkpoint_fields:
            if getattr(original, field) != getattr(updated, field):
                return True
                
        # Check milestone completion fields
        milestone_fields = [
            "milestone1_completed", "milestone2_completed", "milestone3_completed",
            "current_milestone", "status"
        ]
        
        for field in milestone_fields:
            if getattr(original, field) != getattr(updated, field):
                return True
                
        return False
