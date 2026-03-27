"""
FollowupRecommendationTool: Generates actionable follow-up recommendations using LLM.
This tool is called by the CRMAgent to suggest next steps after an interaction.
"""

from typing import Any, Dict, Optional
from app.services.groq_service import GroqService
import logging

logger = logging.getLogger(__name__)


class FollowupRecommendationTool:
    """
    Tool for generating follow-up recommendations for HCP interactions using LLM.
    
    Takes interaction notes and uses GroqService to produce actionable
    recommendations for follow-up activities (calls, demos, materials, etc.).
    
    Tool Input Schema:
    {
        "interaction_notes": str,  # Raw notes from the interaction (required)
        "interaction_type": str,   # Type of interaction (optional, for context)
        "hcp_name": str,           # HCP name (optional, for context)
        "current_stage": str       # Sales stage (optional, for context)
    }
    """
    
    def __init__(self):
        """Initialize the tool with GroqService"""
        self.groq_service = GroqService()
    
    def execute(
        self, 
        interaction_notes: str,
        interaction_type: Optional[str] = None,
        hcp_name: Optional[str] = None,
        current_stage: Optional[str] = None,
        **kwargs  # Catch any additional fields
    ) -> Dict[str, Any]:
        """
        Execute the tool: generate follow-up recommendations from interaction notes.
        
        Args:
            interaction_notes: Raw notes from the interaction (required)
            interaction_type: Type of interaction (optional, for context)
            hcp_name: Name of HCP (optional, for context)
            current_stage: Sales/engagement stage (optional, for context)
            **kwargs: Additional fields (ignored)
        
        Returns:
            Dictionary with:
            - success: bool
            - message: str
            - recommendations: str (if successful)
            - error: str (if failed)
        """
        logger.info(f"[FollowupRecommendationTool] Generating recommendations for {hcp_name or 'HCP'}")
        
        try:
            # Validate required field
            if not interaction_notes or not interaction_notes.strip():
                return {
                    "success": False,
                    "message": "Interaction notes are required",
                    "error": "Missing interaction_notes parameter"
                }
            
            logger.info(f"[FollowupRecommendationTool] Processing {len(interaction_notes)} characters of notes")
            
            # Build context for the LLM
            context = ""
            if hcp_name:
                context += f"HCP: {hcp_name}\n"
            if interaction_type:
                context += f"Interaction Type: {interaction_type}\n"
            if current_stage:
                context += f"Sales Stage: {current_stage}\n"
            
            # Combine context with notes
            full_notes = f"{context}Notes: {interaction_notes}" if context else interaction_notes
            
            # Call GroqService to generate recommendations
            recommendations = self.groq_service.generate_followup_recommendation(full_notes)
            
            if not recommendations or not recommendations.strip():
                return {
                    "success": False,
                    "message": "LLM returned empty recommendations",
                    "error": "Recommendation generation failed"
                }
            
            logger.info(f"[FollowupRecommendationTool] Generated recommendations: {len(recommendations)} characters")
            
            return {
                "success": True,
                "message": "Follow-up recommendations generated successfully",
                "recommendations": recommendations
            }
        
        except Exception as e:
            logger.error(f"[FollowupRecommendationTool] Error: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to generate recommendations: {str(e)}",
                "error": str(e)
            }
    
    def get_tool_info(self) -> Dict[str, Any]:
        """
        Return tool metadata for the agent.
        
        Returns:
            Dictionary describing tool purpose, inputs, outputs
        """
        return {
            "name": "FollowupRecommendationTool",
            "description": "Generates actionable follow-up recommendations (next steps, timeline, actions) for an HCP interaction using AI analysis",
            "input_schema": {
                "interaction_notes": {
                    "type": "string",
                    "description": "Raw notes from the interaction (outcomes, objections, interests, etc.)",
                    "required": True
                },
                "interaction_type": {
                    "type": "string",
                    "description": "Type of interaction (e.g., 'meeting', 'call', 'email') - optional context",
                    "required": False
                },
                "hcp_name": {
                    "type": "string",
                    "description": "Name of the healthcare professional - optional context",
                    "required": False
                },
                "current_stage": {
                    "type": "string",
                    "description": "Sales/engagement stage (e.g., 'awareness', 'consideration', 'close') - optional context",
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
                "recommendations": {
                    "type": "string",
                    "description": "Actionable follow-up recommendations and next steps"
                },
                "error": {
                    "type": "string",
                    "description": "Error message if tool failed"
                }
            }
        }
