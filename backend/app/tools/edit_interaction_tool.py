"""
EditInteractionTool: Modifies existing HCP interaction records in the database.
This tool is called by the CRMAgent to update interaction data.
"""

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.services.interaction_service import InteractionService
from app.schemas.interaction import InteractionUpdate
import json
import logging

logger = logging.getLogger(__name__)


class EditInteractionTool:
    """
    Tool for editing/updating existing HCP interactions in the database.
    
    Accepts interaction ID and updated fields, applies changes via InteractionService.
    Returns the updated interaction with confirmation of changes.
    
    Tool Input Schema:
    {
        "interaction_id": int,     # ID of interaction to update (required)
        "interaction_type": str,   # Type of interaction (optional)
        "date": str,               # Date of interaction (YYYY-MM-DD, optional)
        "time": str,               # Time (HH:MM, optional)
        "attendees": str|list,     # People who attended (will be converted to CSV string)
        "topics_discussed": str|list,  # Topics covered (will be converted to CSV string)
        "materials_shared": str|list,  # Materials given (will be converted to CSV string)
        "samples_distributed": str|dict, # Samples given (will be converted to JSON string)
        "sentiment": str,          # Emotional tone (positive/neutral/negative, optional)
        "outcomes": str,           # What was achieved (optional)
        "follow_up_actions": str|list, # Next steps (will be converted to CSV string)
        "summary": str             # Professional summary (optional)
    }
    """
    
    def __init__(self):
        """Initialize the tool (service methods are static, called directly)"""
        pass
    
    @staticmethod
    def _convert_to_string(value: Any) -> Optional[str]:
        """
        Convert lists/dicts to appropriate string format.
        Lists -> CSV string
        Dicts -> JSON string
        Strings -> as-is
        """
        if value is None:
            return None
        if isinstance(value, str):
            return value if value else None
        if isinstance(value, list):
            # Convert list to CSV string
            return ", ".join(str(item) for item in value) if value else None
        if isinstance(value, dict):
            # Convert dict to JSON string
            return json.dumps(value) if value else None
        return str(value)
    
    def execute(
        self, 
        db: Session,
        interaction_id: int,
        interaction_type: Optional[str] = None,
        date: Optional[str] = None,
        time: Optional[str] = None,
        attendees: Optional[list] = None,
        topics_discussed: Optional[list] = None,
        materials_shared: Optional[list] = None,
        samples_distributed: Optional[Dict[str, int]] = None,
        sentiment: Optional[str] = None,
        outcomes: Optional[str] = None,
        follow_up_actions: Optional[list] = None,
        summary: Optional[str] = None,
        **kwargs  # Catch any additional fields
    ) -> Dict[str, Any]:
        """
        Execute the tool: update interaction in database.
        
        Args:
            db: SQLAlchemy session
            interaction_id: ID of interaction to update (required)
            interaction_type: Type of interaction (optional - only update if provided)
            date: Interaction date (optional)
            time: Interaction time (optional)
            attendees: List of attendees (optional)
            topics_discussed: List of topics (optional)
            materials_shared: List of materials (optional)
            samples_distributed: Dict mapping product names to quantities (optional)
            sentiment: Sentiment of interaction (optional)
            outcomes: Outcomes/achievements (optional)
            follow_up_actions: List of follow-up actions (optional)
            summary: Professional summary (optional)
            **kwargs: Additional fields (ignored)
        
        Returns:
            Dictionary with:
            - success: bool
            - message: str
            - interaction_id: int (if successful)
            - updated_fields: list (fields that were modified)
            - interaction_data: dict (if successful)
            - error: str (if failed)
        """
        logger.info(f"[EditInteractionTool] Executing update for interaction ID: {interaction_id}")
        
        try:
            # Validate required field
            if not isinstance(interaction_id, int) or interaction_id <= 0:
                return {
                    "success": False,
                    "message": "Valid interaction ID is required",
                    "error": "Invalid interaction_id parameter"
                }
            
            logger.info(f"[EditInteractionTool] Building update payload...")
            
            # Build update payload with only provided fields
            # This uses InteractionUpdate which only updates provided fields
            update_data = {}
            
            if interaction_type is not None:
                update_data["interaction_type"] = interaction_type
            if date is not None:
                update_data["date"] = date
            if time is not None:
                update_data["time"] = time
            if attendees is not None:
                update_data["attendees"] = self._convert_to_string(attendees)
            if topics_discussed is not None:
                update_data["topics_discussed"] = self._convert_to_string(topics_discussed)
            if materials_shared is not None:
                update_data["materials_shared"] = self._convert_to_string(materials_shared)
            if samples_distributed is not None:
                update_data["samples_distributed"] = self._convert_to_string(samples_distributed)
            if sentiment is not None:
                update_data["sentiment"] = sentiment
            if outcomes is not None:
                update_data["outcomes"] = outcomes
            if follow_up_actions is not None:
                update_data["follow_up_actions"] = self._convert_to_string(follow_up_actions)
            if summary is not None:
                update_data["summary"] = summary
            
            # Check if any fields were provided for update
            if not update_data:
                return {
                    "success": False,
                    "message": "No fields provided for update",
                    "error": "At least one field must be provided to update"
                }
            
            logger.info(f"[EditInteractionTool] Updating fields: {list(update_data.keys())}")
            
            # Create InteractionUpdate schema with only provided fields
            interaction_update = InteractionUpdate(**update_data)
            
            # Update interaction via InteractionService (static method)
            updated_interaction = InteractionService.edit_interaction(db, interaction_id, interaction_update)
            
            logger.info(f"[EditInteractionTool] Interaction {interaction_id} updated successfully")
            
            return {
                "success": True,
                "message": f"Interaction {interaction_id} updated successfully",
                "interaction_id": updated_interaction.id,
                "updated_fields": list(update_data.keys()),
                "interaction_data": {
                    "id": updated_interaction.id,
                    "hcp_id": updated_interaction.hcp_id,
                    "interaction_type": updated_interaction.interaction_type,
                    "date": str(updated_interaction.date) if updated_interaction.date else None,
                    "time": updated_interaction.time,
                    "summary": updated_interaction.summary,
                    "sentiment": updated_interaction.sentiment,
                    "outcomes": updated_interaction.outcomes,
                    "created_at": str(updated_interaction.created_at)
                }
            }
        
        except ValueError as e:
            logger.error(f"[EditInteractionTool] Validation error: {str(e)}")
            return {
                "success": False,
                "message": f"Interaction not found: {str(e)}",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"[EditInteractionTool] Error: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to update interaction: {str(e)}",
                "error": str(e)
            }
    
    def get_tool_info(self) -> Dict[str, Any]:
        """
        Return tool metadata for the agent.
        
        Returns:
            Dictionary describing tool purpose, inputs, outputs
        """
        return {
            "name": "EditInteractionTool",
            "description": "Updates an existing HCP interaction record with new or modified data",
            "input_schema": {
                "interaction_id": {
                    "type": "integer",
                    "description": "ID of the interaction to update",
                    "required": True
                },
                "interaction_type": {
                    "type": "string",
                    "description": "Type of interaction (e.g., 'meeting', 'call', 'email')",
                    "required": False
                },
                "date": {
                    "type": "string",
                    "description": "Date of interaction (YYYY-MM-DD format)",
                    "required": False
                },
                "time": {
                    "type": "string",
                    "description": "Time of interaction (HH:MM format)",
                    "required": False
                },
                "attendees": {
                    "type": "array",
                    "description": "List of people who attended",
                    "required": False
                },
                "topics_discussed": {
                    "type": "array",
                    "description": "Topics covered during interaction",
                    "required": False
                },
                "materials_shared": {
                    "type": "array",
                    "description": "Materials/documents shared",
                    "required": False
                },
                "samples_distributed": {
                    "type": "object",
                    "description": "Samples given (product name -> quantity)",
                    "required": False
                },
                "sentiment": {
                    "type": "string",
                    "description": "Sentiment of interaction (positive/neutral/negative)",
                    "required": False
                },
                "outcomes": {
                    "type": "string",
                    "description": "Outcomes or achievements from interaction",
                    "required": False
                },
                "follow_up_actions": {
                    "type": "array",
                    "description": "Planned follow-up actions",
                    "required": False
                },
                "summary": {
                    "type": "string",
                    "description": "Professional summary of the interaction",
                    "required": False
                }
            },
            "output_schema": {
                "success": {
                    "type": "boolean",
                    "description": "Whether the tool executed successfully"
                },
                "message": {
                    "type": "string",
                    "description": "Human-readable status message"
                },
                "interaction_id": {
                    "type": "integer",
                    "description": "Database ID of updated interaction"
                },
                "updated_fields": {
                    "type": "array",
                    "description": "List of fields that were modified"
                },
                "interaction_data": {
                    "type": "object",
                    "description": "Updated interaction details"
                }
            }
        }
