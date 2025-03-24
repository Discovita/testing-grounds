from app.schemas import RenovationJourney
from openai.types.responses import FunctionTool
import app.crud as crud
from typing import Dict, Any, Literal
from app.database import SessionLocal


from cws_helpers.logger import configure_logging
from requests import Session

log = configure_logging(__name__)

# Define checkpoint type as a Literal union of all possible checkpoint names
CheckpointName = Literal["room", "renovation_purpose", "budget_range", 
                         "timeline", "style_preference", "priority_feature"]

update_journey_function: FunctionTool = {
    "type": "function",
    "name": "update_journey",
    "function": {
        "name": "update_journey",
        "description": "Update the user's renovation journey with extracted information. Only one field can be updated at a time.",
        "parameters": {
            "type": "object",
            "properties": {
                "journey_id": {
                    "type": "integer",
                    "description": "The ID of the journey to update"
                },
                "checkpoint_name": {
                    "type": "string",
                    "description": "The specific checkpoint to update",
                    "enum": [
                        "room",
                        "renovation_purpose", 
                        "budget_range",
                        "timeline", 
                        "style_preference", 
                        "priority_feature"
                    ],
                },
                "value": {
                    "type": "string",
                    "description": "The value extracted from the user's message for the specified checkpoint"
                }
            },
            "required": ["journey_id", "checkpoint_name", "value"],
            "additionalProperties": False,
        },
    },
}


async def update_journey(
    journey_id: int,
    checkpoint_name: CheckpointName = None,
    value: str = None,
    db: Session = None
) -> Dict[str, Any]:
    """
    Handle the update_journey function call from the LLM.

    This function updates a single field in the user's renovation journey with 
    extracted information. Only one checkpoint can be updated in a single call.

    Args:
        journey_id: ID of the journey to update
        checkpoint_name: The specific checkpoint to update (room, renovation_purpose, etc.)
        value: The value extracted from the user's message
        db: Optional database session (one will be created if not provided)

    Returns:
        Response dictionary with success or error message
    """
    log.step("Sentinel is updating the user's journey")
    log.info(f"  Journey ID: {journey_id}")
    log.info(f"  Checkpoint: {checkpoint_name}")
    log.info(f"  Value: {value}")

    try:
        # Validate required parameters
        if not journey_id:
            return {"error": "Missing journey_id"}
            
        if not checkpoint_name or not value:
            return {"error": "Both checkpoint_name and value must be provided"}
            
        # Validate checkpoint_name is one of the allowed values
        valid_checkpoints = [
            "room", 
            "renovation_purpose", 
            "budget_range",
            "timeline", 
            "style_preference", 
            "priority_feature"
        ]
        
        if checkpoint_name not in valid_checkpoints:
            return {
                "error": f"Invalid checkpoint_name: {checkpoint_name}",
                "valid_checkpoints": valid_checkpoints
            }
            
        # Use provided session or create a new one
        session_created = False
        
        try:
            # Get current journey
            journey = crud.get_journey(db, journey_id)
            if not journey:
                return {"error": f"Journey {journey_id} not found"}

            # Create update data dictionary with the single field
            update_data = {checkpoint_name: value}
            log.info(f"Updating journey {journey_id}: {checkpoint_name} = {value}")

            # Update the journey
            updated_journey = crud.update_journey(db, journey_id, update_data)
            
            # Commit changes to make them visible to other sessions
            db.commit()
            
            log.info(f"Journey {journey_id} updated successfully")
            log.info(f"  Updated field: {checkpoint_name} = {value}")
            
            # Check milestone completion and update as needed
            updated_journey = update_milestone(updated_journey, db)

            return {
                "success": True,
                "message": f"Updated {checkpoint_name} to '{value}'",
                "journey_id": journey_id,
            }
        finally:
            # Only close the session if we created it
            if session_created:
                db.close()

    except Exception as e:
        log.error(f"Error in update_journey: {str(e)}")
        return {"error": str(e)}


def update_milestone(updated_journey: RenovationJourney, db: Session) -> RenovationJourney:
    """
    Check if milestones are completed and update the journey's current milestone.
    This function exists to programatically update the milestone completion flags for a users journey. Doing it this way removes a function from the LLM and focuses the Sentinel on updating the checkpoints and the journey object.
    
    This function:
    1. Checks if all checkpoints for each milestone are complete
    2. Updates milestone completion flags if needed
    3. Ensures journey.current_milestone reflects the highest completed milestone + 1
       (unless all milestones are complete)
    
    Args:
        updated_journey: Updated journey object
        db: Database session

    Returns:
        Updated journey object with correct milestone completion and current milestone
    """
    import datetime
    import app.crud as crud
    
    # Create a db session if not provided
    close_db = False
    
    try:
        # Check completion status for each milestone
        update_data = {}
        current_time = datetime.datetime.utcnow()
        highest_completed_milestone = 0
        
        # Check Milestone 1 completion
        milestone1_complete = all([updated_journey.room, updated_journey.renovation_purpose])
        if milestone1_complete and not updated_journey.milestone1_completed:
            update_data["milestone1_completed"] = True
            update_data["milestone1_completed_at"] = current_time
            highest_completed_milestone = 1
        elif milestone1_complete:
            highest_completed_milestone = 1
            
        # Check Milestone 2 completion
        milestone2_complete = all([updated_journey.budget_range, updated_journey.timeline])
        if milestone2_complete and not updated_journey.milestone2_completed:
            update_data["milestone2_completed"] = True
            update_data["milestone2_completed_at"] = current_time
            highest_completed_milestone = 2
        elif milestone2_complete:
            highest_completed_milestone = 2
            
        # Check Milestone 3 completion
        milestone3_complete = all([updated_journey.style_preference, updated_journey.priority_feature])
        if milestone3_complete and not updated_journey.milestone3_completed:
            update_data["milestone3_completed"] = True
            update_data["milestone3_completed_at"] = current_time
            update_data["status"] = "completed"  # Journey is complete when milestone 3 is complete
            highest_completed_milestone = 3
        elif milestone3_complete:
            highest_completed_milestone = 3
            
        # Update current_milestone if needed
        # If current milestone is less than highest completed + 1, update it
        # Unless all milestones are complete (milestone 3), then keep it at 3
        if highest_completed_milestone < 3:
            next_milestone = highest_completed_milestone + 1
            if updated_journey.current_milestone < next_milestone:
                update_data["current_milestone"] = next_milestone
                log.info(f"Advancing journey {updated_journey.id} milestone from {updated_journey.current_milestone} to {next_milestone}")
        
        # If there are updates to make, update the journey
        if update_data:
            log.step(f"Updating journey {updated_journey.id} milestone information:")
            for key, value in update_data.items():
                log.info(f"  {key}: {value}")
                
            updated_journey = crud.update_journey(db, updated_journey.id, update_data)
            log.info(f"Journey milestone update complete")
        
        return updated_journey
    
    finally:
        # Close db session if we created it
        if close_db:
            db.close()