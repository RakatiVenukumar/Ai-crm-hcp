"""
Agent Routes: AI-powered chat endpoint for HCP interaction processing.
Exposes the CRMAgent via REST API for natural language input.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, status
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# Request / Response Schemas
# ============================================================================

class AgentChatRequest(BaseModel):
    """Request schema for /agent/chat endpoint"""
    user_input: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Natural language description of HCP interaction"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_input": "Had a meeting with Dr. Smith about our cardiac product line yesterday afternoon. Very positive reception."
            }
        }


class AgentChatResponse(BaseModel):
    """Response schema for /agent/chat endpoint"""
    success: bool = Field(..., description="Whether processing was successful")
    user_input: str = Field(..., description="The original user input")
    extracted_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Extracted HCP interaction data (HCP name, sentiment, products, etc.)"
    )
    tool_results: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Results from tool execution (summarization, recommendations, insights)"
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Agent reasoning about the input"
    )
    complete: bool = Field(
        default=True,
        description="Whether processing completed"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if processing failed"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "user_input": "Had a meeting with Dr. Smith about cardiac products.",
                "extracted_data": {
                    "hcp_name": "Dr. Smith",
                    "sentiment": "positive",
                    "products_discussed": ["Cardiac Monitor", "EKG System"],
                    "summary": "Positive meeting discussion about cardiac products."
                },
                "tool_results": {
                    "last_result": {
                        "success": True,
                        "message": "Interaction logged successfully"
                    }
                },
                "reasoning": "Successfully extracted HCP interaction data",
                "complete": True
            }
        }


# ============================================================================
# Router Setup
# ============================================================================

router = APIRouter(prefix="/agent", tags=["agent"])

# Initialize agent once
_agent_instance = None

def get_agent():
    """Get or create singleton CRMAgent instance"""
    from app.agents.agent import CRMAgent
    global _agent_instance
    if _agent_instance is None:
        logger.info("Initializing CRMAgent...")
        _agent_instance = CRMAgent()
    return _agent_instance


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/chat", response_model=AgentChatResponse, status_code=status.HTTP_200_OK)
async def agent_chat(request: AgentChatRequest) -> AgentChatResponse:
    """
    Process natural language HCP interaction input through the AI agent.
    
    The agent will:
    1. Extract key entities (HCP name, products, sentiment, etc.)
    2. Log the interaction to the database
    3. Generate professional summary
    4. Create follow-up recommendations
    5. Identify sales insights
    
    Args:
        request: AgentChatRequest with user_input (natural language description)
    
    Returns:
        AgentChatResponse with extracted data and tool results
    
    Example:
        ```
        curl -X POST "http://localhost:8000/agent/chat" \
          -H "Content-Type: application/json" \
          -d '{
            "user_input": "Met with Dr. Chen at Central Hospital. Very positive about our joint replacement system. Wants a pilot program."
          }'
        ```
    """
    logger.info(f"[AGENT_CHAT] Received request: {request.user_input[:100]}...")
    
    try:
        # Validate input
        if not request.user_input or not request.user_input.strip():
            logger.warning("[AGENT_CHAT] Empty or whitespace-only input")
            return AgentChatResponse(
                success=False,
                user_input=request.user_input,
                error="Input cannot be empty",
                complete=False
            )
        
        # Get agent instance
        agent = get_agent()
        
        # Process input through agent
        logger.info("[AGENT_CHAT] Processing input through CRMAgent...")
        result = agent.process_input(request.user_input)
        
        # Map agent output to response schema
        response = AgentChatResponse(
            success=result.get("success", False),
            user_input=result.get("user_input", request.user_input),
            extracted_data=result.get("extracted_data"),
            tool_results=result.get("tool_results"),
            reasoning=result.get("reasoning"),
            complete=result.get("complete", False),
            error=result.get("error")
        )
        
        logger.info(f"[AGENT_CHAT] Response prepared - success: {response.success}")
        return response
        
    except Exception as e:
        logger.error(f"[AGENT_CHAT] Unexpected error: {str(e)}", exc_info=True)
        return AgentChatResponse(
            success=False,
            user_input=request.user_input,
            error=f"Server error: {str(e)}",
            complete=False
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def agent_health() -> dict:
    """
    Health check for the agent endpoint.
    
    Returns:
        Status and readiness information
    """
    try:
        agent = get_agent()
        return {
            "status": "ok",
            "service": "crm-agent",
            "tools_available": list(agent.tools.keys()),
            "ready": True
        }
    except Exception as e:
        logger.error(f"[AGENT_HEALTH] Health check failed: {str(e)}")
        return {
            "status": "error",
            "service": "crm-agent",
            "error": str(e),
            "ready": False
        }
