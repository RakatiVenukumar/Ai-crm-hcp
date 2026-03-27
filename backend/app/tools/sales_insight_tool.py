"""
SalesInsightTool: Generates sales insights and analysis from HCP interactions using LLM.
This tool is called by the CRMAgent to analyze sentiment, objections, and opportunities.
"""

from typing import Any, Dict, Optional
from app.services.groq_service import GroqService
import logging

logger = logging.getLogger(__name__)


class SalesInsightTool:
    """
    Tool for generating detailed sales insights from HCP interactions using LLM.
    
    Takes interaction notes and uses GroqService to analyze sentiment,
    identify objections, uncover opportunities, and assess product interest.
    Returns structured insight data for pipeline management and forecasting.
    
    Tool Input Schema:
    {
        "interaction_notes": str,  # Raw notes from the interaction (required)
        "interaction_type": str,   # Type of interaction (optional, for context)
        "hcp_name": str,           # HCP name (optional, for context)
        "hcp_specialty": str       # HCP specialty/department (optional)
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
        hcp_specialty: Optional[str] = None,
        **kwargs  # Catch any additional fields
    ) -> Dict[str, Any]:
        """
        Execute the tool: generate sales insights from interaction notes.
        
        Args:
            interaction_notes: Raw notes from the interaction (required)
            interaction_type: Type of interaction (optional, for context)
            hcp_name: Name of HCP (optional, for context)
            hcp_specialty: Medical specialty/department (optional, for context)
            **kwargs: Additional fields (ignored)
        
        Returns:
            Dictionary with:
            - success: bool
            - message: str
            - insights: dict (if successful) containing:
              - sentiment: str (positive/negative/neutral)
              - objections: list
              - opportunities: list
              - product_interest: str (high/medium/low)
            - error: str (if failed)
        """
        logger.info(f"[SalesInsightTool] Analyzing interaction for {hcp_name or 'HCP'}")
        
        try:
            # Validate required field
            if not interaction_notes or not interaction_notes.strip():
                return {
                    "success": False,
                    "message": "Interaction notes are required",
                    "error": "Missing interaction_notes parameter"
                }
            
            logger.info(f"[SalesInsightTool] Processing {len(interaction_notes)} characters of notes")
            
            # Build context for the LLM
            context = ""
            if hcp_name:
                context += f"HCP: {hcp_name}\n"
            if interaction_type:
                context += f"Interaction Type: {interaction_type}\n"
            if hcp_specialty:
                context += f"Specialty: {hcp_specialty}\n"
            
            # Combine context with notes
            full_notes = f"{context}Notes: {interaction_notes}" if context else interaction_notes
            
            # Call GroqService to generate insights
            insights_data = self.groq_service.generate_sales_insight(full_notes)
            
            if not insights_data:
                return {
                    "success": False,
                    "message": "LLM returned empty insights",
                    "error": "Insight generation failed"
                }
            
            # Validate required insight fields
            if "sentiment" not in insights_data or "objections" not in insights_data or \
               "opportunities" not in insights_data or "product_interest" not in insights_data:
                logger.warning("[SalesInsightTool] LLM returned incomplete insight structure")
                # Provide defaults for missing fields
                insights_data.setdefault("sentiment", "neutral")
                insights_data.setdefault("objections", [])
                insights_data.setdefault("opportunities", [])
                insights_data.setdefault("product_interest", "unknown")
            
            logger.info(f"[SalesInsightTool] Generated insights with sentiment: {insights_data.get('sentiment')}")
            
            return {
                "success": True,
                "message": "Sales insights generated successfully",
                "insights": {
                    "sentiment": insights_data.get("sentiment", "neutral"),
                    "objections": insights_data.get("objections", []),
                    "opportunities": insights_data.get("opportunities", []),
                    "product_interest": insights_data.get("product_interest", "unknown")
                }
            }
        
        except Exception as e:
            logger.error(f"[SalesInsightTool] Error: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to generate insights: {str(e)}",
                "error": str(e)
            }
    
    def get_tool_info(self) -> Dict[str, Any]:
        """
        Return tool metadata for the agent.
        
        Returns:
            Dictionary describing tool purpose, inputs, outputs
        """
        return {
            "name": "SalesInsightTool",
            "description": "Analyzes HCP interactions to extract sales insights: sentiment, objections, opportunities, and product interest level",
            "input_schema": {
                "interaction_notes": {
                    "type": "string",
                    "description": "Raw notes from the interaction (reactions, concerns, interests, etc.)",
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
                "hcp_specialty": {
                    "type": "string",
                    "description": "Medical specialty/department (e.g., 'Cardiology', 'Oncology') - optional context",
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
                "insights": {
                    "type": "object",
                    "description": "Structured sales insights containing:",
                    "properties": {
                        "sentiment": {
                            "type": "string",
                            "description": "Overall sentiment of interaction (positive/negative/neutral)"
                        },
                        "objections": {
                            "type": "array",
                            "description": "List of raised objections or concerns"
                        },
                        "opportunities": {
                            "type": "array",
                            "description": "Identified sales opportunities and potential applications"
                        },
                        "product_interest": {
                            "type": "string",
                            "description": "Level of product interest (high/medium/low)"
                        }
                    }
                },
                "error": {
                    "type": "string",
                    "description": "Error message if tool failed"
                }
            }
        }
