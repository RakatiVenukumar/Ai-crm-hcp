"""
InteractionSummaryTool: Generates professional summaries of HCP interactions using LLM.
This tool is called by the CRMAgent to create concise, actionable summaries.
"""

from typing import Any, Dict, Optional
from app.services.groq_service import GroqService
import logging

logger = logging.getLogger(__name__)


class InteractionSummaryTool:
    """
    Tool for generating professional summaries of HCP interactions using LLM.
    
    Takes raw interaction notes and uses GroqService to produce a 3-5 sentence
    professional summary suitable for CRM records.
    
    Tool Input Schema:
    {
        "interaction_notes": str,  # Raw notes from the interaction (required)
        "interaction_type": str,   # Type of interaction (optional, for context)
        "hcp_name": str            # HCP name (optional, for context)
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
        **kwargs  # Catch any additional fields
    ) -> Dict[str, Any]:
        """
        Execute the tool: generate summary from interaction notes.
        
        Args:
            interaction_notes: Raw notes from the interaction (required)
            interaction_type: Type of interaction (optional, for context)
            hcp_name: Name of HCP (optional, for context)
            **kwargs: Additional fields (ignored)
        
        Returns:
            Dictionary with:
            - success: bool
            - message: str
            - summary: str (if successful)
            - error: str (if failed)
        """
        logger.info(f"[InteractionSummaryTool] Generating summary for {hcp_name or 'HCP'}")
        
        try:
            # Validate required field
            if not interaction_notes or not interaction_notes.strip():
                return {
                    "success": False,
                    "message": "Interaction notes are required",
                    "error": "Missing interaction_notes parameter"
                }
            
            logger.info(f"[InteractionSummaryTool] Processing {len(interaction_notes)} characters of notes")
            
            # Build context for the LLM
            context = ""
            if hcp_name:
                context += f"HCP: {hcp_name}\n"
            if interaction_type:
                context += f"Interaction Type: {interaction_type}\n"
            
            # Combine context with notes
            full_notes = f"{context}Notes: {interaction_notes}" if context else interaction_notes
            
            # Call GroqService to generate summary
            summary = self.groq_service.summarize_interaction(full_notes)
            
            if not summary or not summary.strip():
                return {
                    "success": False,
                    "message": "LLM returned empty summary",
                    "error": "Summary generation failed"
                }
            
            logger.info(f"[InteractionSummaryTool] Generated summary: {len(summary)} characters")
            
            return {
                "success": True,
                "message": "Summary generated successfully",
                "summary": summary
            }
        
        except Exception as e:
            logger.error(f"[InteractionSummaryTool] Error: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to generate summary: {str(e)}",
                "error": str(e)
            }
    
    def get_tool_info(self) -> Dict[str, Any]:
        """
        Return tool metadata for the agent.
        
        Returns:
            Dictionary describing tool purpose, inputs, outputs
        """
        return {
            "name": "InteractionSummaryTool",
            "description": "Generates a professional 3-5 sentence summary of an HCP interaction using AI analysis",
            "input_schema": {
                "interaction_notes": {
                    "type": "string",
                    "description": "Raw notes from the interaction (what was discussed, outcomes, etc.)",
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
                "summary": {
                    "type": "string",
                    "description": "Professional 3-5 sentence summary of the interaction"
                },
                "error": {
                    "type": "string",
                    "description": "Error message if tool failed"
                }
            }
        }
