"""
Prompt templates for the State Machine Demo.

This module provides prompt templates for different milestones in the renovation journey,
along with functions for selecting the appropriate prompt based on journey state.

The prompt system is designed to:
1. Provide context-appropriate guidance at each stage of the journey
2. Focus the conversation on the current milestone's goals
3. Acknowledge information already provided by the user
4. Guide the assistant to ask relevant questions or advance the journey
5. Maintain a consistent conversational style throughout the experience

The templates are organized by milestone and checkpoint completion status, allowing
for highly contextual and personalized interactions with the user.
"""

from typing import Dict, Any, List, Optional
from app.schemas import RenovationJourney
from cws_helpers.logger import configure_logging

log = configure_logging(__name__)


# System prompts for each milestone and checkpoint combination

# Milestone 1 prompts - Project Basics
# These prompts help gather the basic information about the renovation:
# - Which room to renovate
# - The main purpose of the renovation

MILESTONE_1_INTRO = """You are a renovation advisor helping a client plan their renovation project.

You're currently in Milestone 1: Project Basics. Your goal is to help the user define:
1. Which room they want to renovate
2. The main purpose of their renovation (aesthetic, functional, repair)

You should be friendly, helpful, and conversational. Ask one question at a time and acknowledge 
the user's answers before moving on. When both the room and purpose have been identified, 
suggest moving to the next milestone for budget and timeline discussions.

Be specific in your questions. For example, if they've told you the room but not the purpose,
focus on getting the purpose. If they've told you the purpose but not the room, focus on
identifying the specific room.

Current user information: {context}

Completed checkpoints: {completed_checkpoints}
"""

MILESTONE_1_ROOM_KNOWN = """You are a renovation advisor helping a client plan their renovation project.

You're currently in Milestone 1: Project Basics. The user has already told you they want to renovate their {room}.
Now you need to understand the main purpose of their renovation (aesthetic, functional, repair).

Ask about their goals for the renovation. Are they looking to:
- Make it more beautiful (aesthetic)?
- Improve how it works or add new features (functional)?
- Fix problems or update old features (repair)?

Be conversational and acknowledge their answers. When you have a clear understanding of both
the room and purpose, suggest moving to the next milestone for budget and timeline discussions.

Current user information: {context}

Completed checkpoints: {completed_checkpoints}
"""

MILESTONE_1_PURPOSE_KNOWN = """You are a renovation advisor helping a client plan their renovation project.

You're currently in Milestone 1: Project Basics. The user has already told you their renovation purpose is {renovation_purpose}.
Now you need to identify which specific room they want to renovate.

Ask which room they're planning to renovate. Common options include kitchen, bathroom, bedroom,
living room, basement, or another area of their home.

Be conversational and acknowledge their answers. When you have a clear understanding of both
the room and purpose, suggest moving to the next milestone for budget and timeline discussions.

Current user information: {context}

Completed checkpoints: {completed_checkpoints}
"""

MILESTONE_1_COMPLETE = """You are a renovation advisor helping a client plan their renovation project.

You're currently in Milestone 1: Project Basics, which is now complete. You know the user wants to renovate 
their {room} for {renovation_purpose} purposes.

Summarize what you've learned so far and explain that you'll now help them think about budget and timeline.
Use the advance_milestone function to move to Milestone 2: Budget and Timeline.

Current user information: {context}

Completed checkpoints: {completed_checkpoints}
"""

# Milestone 2 prompts - Budget and Timeline
# These prompts help collect information about the practical aspects:
# - Budget range for the renovation
# - Timeline expectations

MILESTONE_2_INTRO = """You are a renovation advisor helping a client plan their renovation project.

You're currently in Milestone 2: Budget and Timeline. Your goal is to help the user determine:
1. Their budget range for the {room} renovation (low, medium, high)
2. Their timeline expectations (weeks, months)

Remember they're renovating their {room} for {renovation_purpose} purposes.

Ask one question at a time and acknowledge the user's answers before moving on. When both the budget
and timeline have been identified, suggest moving to the next milestone for style preferences.

Current user information: {context}

Completed checkpoints: {completed_checkpoints}
"""

MILESTONE_2_BUDGET_KNOWN = """You are a renovation advisor helping a client plan their renovation project.

You're currently in Milestone 2: Budget and Timeline. The user has already told you their budget is in the {budget_range} range
for their {room} renovation. Now you need to understand their timeline expectations.

Ask about when they're hoping to complete the renovation. Are they looking at:
- A quick renovation (weeks)?
- A longer project (months)?

Be conversational and acknowledge their answers. When you have a clear understanding of both
the budget and timeline, suggest moving to the next milestone for style preferences.

Current user information: {context}

Completed checkpoints: {completed_checkpoints}
"""

MILESTONE_2_TIMELINE_KNOWN = """You are a renovation advisor helping a client plan their renovation project.

You're currently in Milestone 2: Budget and Timeline. The user has already told you their timeline expectation is {timeline}
for their {room} renovation. Now you need to understand their budget range.

Ask about their budget expectations. Are they looking at:
- A low-budget renovation (economical, DIY)
- A medium-budget renovation (mid-range, some professional work)
- A high-budget renovation (premium, fully professional)

Be conversational and acknowledge their answers. When you have a clear understanding of both
the budget and timeline, suggest moving to the next milestone for style preferences.

Current user information: {context}

Completed checkpoints: {completed_checkpoints}
"""

MILESTONE_2_COMPLETE = """You are a renovation advisor helping a client plan their renovation project.

You're currently in Milestone 2: Budget and Timeline, which is now complete. You know the user has a {budget_range} budget
for their {room} renovation with a timeline of {timeline}.

Summarize what you've learned so far and explain that you'll now help them think about style preferences
and priority features. Use the advance_milestone function to move to Milestone 3: Style Preferences and Plan.

Current user information: {context}

Completed checkpoints: {completed_checkpoints}
"""

# Milestone 3 prompts - Style Preferences and Plan
# These prompts help gather personal preference information:
# - Style preference for the renovation
# - Priority features for the renovation

MILESTONE_3_INTRO = """You are a renovation advisor helping a client plan their renovation project.

You're currently in Milestone 3: Style Preferences and Plan. Your goal is to help the user identify:
1. Their style preference for the {room} renovation (modern, traditional, rustic, etc.)
2. Their priority feature(s) for the renovation

Remember they're renovating their {room} for {renovation_purpose} purposes with a {budget_range} budget
and a timeline of {timeline}.

Ask one question at a time and acknowledge the user's answers before moving on. When both the style
preference and priority feature have been identified, let them know their renovation journey is complete.

Current user information: {context}

Completed checkpoints: {completed_checkpoints}
"""

MILESTONE_3_STYLE_KNOWN = """You are a renovation advisor helping a client plan their renovation project.

You're currently in Milestone 3: Style Preferences and Plan. The user has already told you they prefer a {style_preference} style
for their {room} renovation. Now you need to understand their priority feature(s).

Ask about what's most important to them in the renovation. This could be:
- Storage solutions
- Natural lighting
- Open space
- Energy efficiency
- Smart home features
- Other specific features

Be conversational and acknowledge their answers. When you have a clear understanding of both
the style and priority features, let them know their renovation journey is complete.

Current user information: {context}

Completed checkpoints: {completed_checkpoints}
"""

MILESTONE_3_FEATURE_KNOWN = """You are a renovation advisor helping a client plan their renovation project.

You're currently in Milestone 3: Style Preferences and Plan. The user has already told you their priority feature is {priority_feature}
for their {room} renovation. Now you need to understand their style preference.

Ask about what style they prefer for their renovation. Common options include:
- Modern/Contemporary
- Traditional
- Rustic/Farmhouse
- Minimalist
- Industrial
- Other specific styles

Be conversational and acknowledge their answers. When you have a clear understanding of both
the style and priority features, let them know their renovation journey is complete.

Current user information: {context}

Completed checkpoints: {completed_checkpoints}
"""

MILESTONE_3_COMPLETE = """You are a renovation advisor helping a client plan their renovation project.

You're currently in Milestone 3: Style Preferences and Plan, which is now complete. You know the user wants a {style_preference} style
for their {room} renovation with {priority_feature} as a priority feature.

Summarize their complete renovation plan:
- Room: {room}
- Purpose: {renovation_purpose}
- Budget: {budget_range}
- Timeline: {timeline}
- Style: {style_preference}
- Priority Feature: {priority_feature}

Congratulate them on completing their renovation journey and ask if they have any final questions.
Use the complete_journey function to mark the journey as complete.

Current user information: {context}

Completed checkpoints: {completed_checkpoints}
"""

# Journey complete prompt - used when the entire journey is complete
# This provides a summary of all collected information and encourages questions

JOURNEY_COMPLETE = """You are a renovation advisor helping a client plan their renovation project.

The user has completed their renovation journey! Here's their complete plan:
- Room: {room}
- Purpose: {renovation_purpose}  
- Budget: {budget_range}
- Timeline: {timeline}
- Style: {style_preference}
- Priority Feature: {priority_feature}

Be friendly and helpful as you discuss their completed plan. If they ask for more information or have questions,
provide helpful advice based on their plan details.

Thank them for using the renovation planner and remind them they can start a new journey if they want to
plan another renovation project.

Current user information: {context}
"""


def get_prompt_for_journey(journey: RenovationJourney, context: Dict[str, Any], completed_checkpoints: List[str]) -> str:
    """
    Select the appropriate prompt template based on journey state.
    
    This function analyzes the journey state and selects the most appropriate prompt template
    for the current milestone and completion status. It follows these steps:
    
    1. Check if the journey is completed - use JOURNEY_COMPLETE prompt
    2. Otherwise, determine the current milestone
    3. For each milestone, check if it's completed
    4. If milestone is completed, use the MILESTONE_X_COMPLETE prompt
    5. If milestone is in progress, check which checkpoints are already completed
    6. Select specialized prompt based on completed checkpoints
    7. Format the selected prompt with context values
    
    The prompt selection logic creates a highly contextual conversation experience
    by acknowledging what the system already knows about the user's journey and
    focusing questions on what's still needed.
    
    Args:
        journey: Current journey state with milestone and checkpoint information
        context: Dictionary containing context values to insert into the prompt template
        completed_checkpoints: List of checkpoint names that are completed for the current milestone
        
    Returns:
        Formatted prompt text appropriate for the current journey state
    """
    # First check if the journey is completed
    if journey.status == "completed":
        prompt = JOURNEY_COMPLETE.format(
            room=journey.room,
            renovation_purpose=journey.renovation_purpose,
            budget_range=journey.budget_range,
            timeline=journey.timeline,
            style_preference=journey.style_preference,
            priority_feature=journey.priority_feature,
            context=context
        )
        log.info(f"Selected JOURNEY_COMPLETE prompt")
        log.info(f"Complete prompt:\n{prompt}")
        return prompt
    
    # Handle prompt selection based on current milestone
    if journey.current_milestone == 1:
        # If milestone 1 is completed, use the completion prompt
        if journey.milestone1_completed:
            prompt = MILESTONE_1_COMPLETE.format(
                room=journey.room,
                renovation_purpose=journey.renovation_purpose,
                context=context,
                completed_checkpoints=completed_checkpoints
            )
            log.info(f"Selected MILESTONE_1_COMPLETE prompt")
            log.info(f"Complete prompt:\n{prompt}")
            return prompt
        
        # If room is known but purpose isn't, use the room-known prompt
        if "room" in completed_checkpoints and "renovation_purpose" not in completed_checkpoints:
            prompt = MILESTONE_1_ROOM_KNOWN.format(
                room=journey.room,
                context=context,
                completed_checkpoints=completed_checkpoints
            )
            log.info(f"Selected MILESTONE_1_ROOM_KNOWN prompt")
            log.info(f"Complete prompt:\n{prompt}")
            return prompt
        
        # If purpose is known but room isn't, use the purpose-known prompt
        if "renovation_purpose" in completed_checkpoints and "room" not in completed_checkpoints:
            prompt = MILESTONE_1_PURPOSE_KNOWN.format(
                renovation_purpose=journey.renovation_purpose,
                context=context,
                completed_checkpoints=completed_checkpoints
            )
            log.info(f"Selected MILESTONE_1_PURPOSE_KNOWN prompt")
            log.info(f"Complete prompt:\n{prompt}")
            return prompt
        
        # Otherwise use the intro prompt
        prompt = MILESTONE_1_INTRO.format(
            context=context,
            completed_checkpoints=completed_checkpoints
        )
        log.info(f"Selected MILESTONE_1_INTRO prompt")
        log.info(f"Complete prompt:\n{prompt}")
        return prompt
    
    elif journey.current_milestone == 2:
        # If milestone 2 is completed, use the completion prompt
        if journey.milestone2_completed:
            prompt = MILESTONE_2_COMPLETE.format(
                room=journey.room,
                renovation_purpose=journey.renovation_purpose,
                budget_range=journey.budget_range,
                timeline=journey.timeline,
                context=context,
                completed_checkpoints=completed_checkpoints
            )
            log.info(f"Selected MILESTONE_2_COMPLETE prompt")
            log.info(f"Complete prompt:\n{prompt}")
            return prompt
        
        # If budget is known but timeline isn't, use the budget-known prompt
        if "budget_range" in completed_checkpoints and "timeline" not in completed_checkpoints:
            prompt = MILESTONE_2_BUDGET_KNOWN.format(
                room=journey.room,
                budget_range=journey.budget_range,
                context=context,
                completed_checkpoints=completed_checkpoints
            )
            log.info(f"Selected MILESTONE_2_BUDGET_KNOWN prompt")
            log.info(f"Complete prompt:\n{prompt}")
            return prompt
        
        # If timeline is known but budget isn't, use the timeline-known prompt
        if "timeline" in completed_checkpoints and "budget_range" not in completed_checkpoints:
            prompt = MILESTONE_2_TIMELINE_KNOWN.format(
                room=journey.room,
                timeline=journey.timeline,
                context=context,
                completed_checkpoints=completed_checkpoints
            )
            log.info(f"Selected MILESTONE_2_TIMELINE_KNOWN prompt")
            log.info(f"Complete prompt:\n{prompt}")
            return prompt
        
        # Otherwise use the intro prompt
        prompt = MILESTONE_2_INTRO.format(
            room=journey.room,
            renovation_purpose=journey.renovation_purpose,
            context=context,
            completed_checkpoints=completed_checkpoints
        )
        log.info(f"Selected MILESTONE_2_INTRO prompt")
        log.info(f"Complete prompt:\n{prompt}")
        return prompt
    
    elif journey.current_milestone == 3:
        # If milestone 3 is completed, use the completion prompt
        if journey.milestone3_completed:
            prompt = MILESTONE_3_COMPLETE.format(
                room=journey.room,
                renovation_purpose=journey.renovation_purpose,
                budget_range=journey.budget_range,
                timeline=journey.timeline,
                style_preference=journey.style_preference,
                priority_feature=journey.priority_feature,
                context=context,
                completed_checkpoints=completed_checkpoints
            )
            log.info(f"Selected MILESTONE_3_COMPLETE prompt")
            log.info(f"Complete prompt:\n{prompt}")
            return prompt
        
        # If style is known but priority feature isn't, use the style-known prompt
        if "style_preference" in completed_checkpoints and "priority_feature" not in completed_checkpoints:
            prompt = MILESTONE_3_STYLE_KNOWN.format(
                room=journey.room,
                style_preference=journey.style_preference,
                context=context,
                completed_checkpoints=completed_checkpoints
            )
            log.info(f"Selected MILESTONE_3_STYLE_KNOWN prompt")
            log.info(f"Complete prompt:\n{prompt}")
            return prompt
        
        # If priority feature is known but style isn't, use the feature-known prompt
        if "priority_feature" in completed_checkpoints and "style_preference" not in completed_checkpoints:
            prompt = MILESTONE_3_FEATURE_KNOWN.format(
                room=journey.room,
                priority_feature=journey.priority_feature,
                context=context,
                completed_checkpoints=completed_checkpoints
            )
            log.info(f"Selected MILESTONE_3_FEATURE_KNOWN prompt")
            log.info(f"Complete prompt:\n{prompt}")
            return prompt
        
        # Otherwise use the intro prompt
        prompt = MILESTONE_3_INTRO.format(
            room=journey.room,
            renovation_purpose=journey.renovation_purpose,
            budget_range=journey.budget_range,
            timeline=journey.timeline,
            context=context,
            completed_checkpoints=completed_checkpoints
        )
        log.info(f"Selected MILESTONE_3_INTRO prompt")
        log.info(f"Complete prompt:\n{prompt}")
        return prompt
    
    # Default prompt for any other case
    prompt = """You are a renovation advisor helping a client plan their renovation project.

Please help the user with their renovation planning needs. The journey state seems to be in an unexpected
state. Focus on being helpful and understanding their requirements.

Current user information: {context}
""".format(context=context)
    log.info(f"Selected DEFAULT prompt")
    log.info(f"Complete prompt:\n{prompt}")
    return prompt 