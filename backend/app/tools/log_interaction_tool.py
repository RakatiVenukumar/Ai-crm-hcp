"""
LogInteractionTool: Saves extracted HCP interaction data to the database.
This tool is called by the CRMAgent to persist interaction records.
"""

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.services.interaction_service import InteractionService
from app.schemas.interaction import InteractionCreate
import json
import logging

logger = logging.getLogger(__name__)


class LogInteractionTool:
    """
    Tool for logging/saving HCP interactions to the database.
    
    Accepts extracted interaction data from the agent and persists it
    via InteractionService. Returns the created interaction with database ID.
    
    Tool Input Schema:
    {
        "hcp_name": str,           # Name of the HCP (required) - todo: will be resolved to hcp_id in future
        "interaction_type": str,   # Type of interaction (required)
        "date": str,               # Date of interaction (YYYY-MM-DD)
        "time": str,               # Time (HH:MM)
        "attendees": str|list,     # People who attended (will be converted to CSV string)
        "topics_discussed": str|list,  # Topics covered (will be converted to CSV string)
        "products_discussed": list,# Products mentioned (for reference, not stored separately)
        "materials_shared": str|list,  # Materials given (will be converted to CSV string)
        "samples_distributed": str|dict, # Samples given (will be converted to JSON string)
        "sentiment": str,          # Emotional tone (positive/neutral/negative)
        "outcomes": str,           # What was achieved
        "follow_up_actions": str|list, # Next steps (will be converted to CSV string)
        "summary": str             # Professional summary
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
        hcp_name: str,
        interaction_type: str = "meeting",
        date: Optional[str] = None,
        time: Optional[str] = None,
        attendees: Optional[list] = None,
        topics_discussed: Optional[list] = None,
        products_discussed: Optional[list] = None,
        materials_shared: Optional[list] = None,
        samples_distributed: Optional[Dict[str, int]] = None,
        sentiment: Optional[str] = None,
        outcomes: Optional[str] = None,
        follow_up_actions: Optional[list] = None,
        summary: Optional[str] = None,
        **kwargs  # Catch any additional fields
    ) -> Dict[str, Any]:
        """
        Execute the tool: save interaction to database.
        
        Args:
            db: SQLAlchemy session
            hcp_name: Name of the HCP (will be looked up in future steps)
            interaction_type: Type of interaction
            date: Interaction date
            time: Interaction time
            attendees: List of attendees
            topics_discussed: List of topics
            products_discussed: List of products
            materials_shared: List of materials
            samples_distributed: Dict mapping product names to quantities
            sentiment: Sentiment of interaction
            outcomes: Outcomes/achievements
            follow_up_actions: List of follow-up actions
            summary: Professional summary
            **kwargs: Additional fields (ignored)
        
        Returns:
            Dictionary with:
            - success: bool
            - message: str
            - interaction_id: int (if successful)
            - interaction_data: dict (if successful)
            - error: str (if failed)
        """
        logger.info(f"[LogInteractionTool] Executing with HCP: {hcp_name}")
        
        try:
            # Validate required fields
            if not hcp_name:
                return {
                    "success": False,
                    "message": "HCP name is required",
                    "error": "Missing hcp_name parameter"
                }
            
            if not interaction_type:
                return {
                    "success": False,
                    "message": "Interaction type is required",
                    "error": "Missing interaction_type parameter"
                }
            
            # TODO: In future steps, resolve hcp_name to hcp_id via HCPService
            # For now, we'll use a placeholder hcp_id (assume HCP with id=1 exists or will be created)
            # This will be enhanced to:
            # 1. Search for HCP by name
            # 2. If not found, create new HCP
            # 3. Get the hcp_id
            
            logger.info(f"[LogInteractionTool] Creating interaction record...")
            
            # Build interaction create schema, converting lists to CSV strings
            interaction_data = InteractionCreate(
                hcp_id=1,  # Placeholder - will be dynamically resolved in future
                interaction_type=interaction_type,
                date=date or "2026-03-27",  # Default to today if not provided
                time=time,
                attendees=self._convert_to_string(attendees),
                topics_discussed=self._convert_to_string(topics_discussed),
                materials_shared=self._convert_to_string(materials_shared),
                samples_distributed=self._convert_to_string(samples_distributed),
                sentiment=sentiment,
                outcomes=outcomes,
                follow_up_actions=self._convert_to_string(follow_up_actions),
                summary=summary
            )
            
            # Create interaction via InteractionService (static method)
            created_interaction = InteractionService.create_interaction(db, interaction_data)
            
            logger.info(f"[LogInteractionTool] Interaction created with ID: {created_interaction.id}")
            
            return {
                "success": True,
                "message": f"Interaction logged successfully for {hcp_name}",
                "interaction_id": created_interaction.id,
                "interaction_data": {
                    "id": created_interaction.id,
                    "hcp_id": created_interaction.hcp_id,
                    "interaction_type": created_interaction.interaction_type,
                    "date": str(created_interaction.date) if created_interaction.date else None,
                    "time": created_interaction.time,
                    "summary": created_interaction.summary,
                    "sentiment": created_interaction.sentiment,
                    "created_at": str(created_interaction.created_at)
                }
            }
        
        except Exception as e:
            logger.error(f"[LogInteractionTool] Error: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to log interaction: {str(e)}",
                "error": str(e)
            }
    
    def get_tool_info(self) -> Dict[str, Any]:
        """
        Return tool metadata for the agent.
        
        Returns:
            Dictionary describing tool purpose, inputs, outputs
        """
        return {
            "name": "LogInteractionTool",
            "description": "Saves an HCP interaction to the database after extraction by LLM",
            "input_schema": {
                "hcp_name": {
                    "type": "string",
                    "description": "Name of the healthcare professional",
                    "required": True
                },
                "interaction_type": {
                    "type": "string",
                    "description": "Type of interaction (e.g., 'meeting', 'call', 'email')",
                    "required": True
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
                "products_discussed": {
                    "type": "array",
                    "description": "Products mentioned or discussed",
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
                    "description": "Database ID of created interaction"
                },
                "interaction_data": {
                    "type": "object",
                    "description": "Created interaction details"
                }
            }
        }
