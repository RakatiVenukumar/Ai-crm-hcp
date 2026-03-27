"""
LangGraph Agent for CRM Interaction Processing
Orchestrates LLM reasoning with tool execution for extracting and analyzing HCP interactions
"""

from typing import TypedDict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from app.services.groq_service import GroqService
import json
import logging

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State object passed through the agent graph"""
    user_input: str  # Original user input
    extracted_data: Optional[dict]  # Data extracted by LLM (entities, summary, etc.)
    reasoning: str  # LLM reasoning about what the user is asking
    current_tool: Optional[str]  # Name of the tool to execute (set by agent_node)
    tool_input: Optional[dict]  # Input parameters for the tool
    tool_result: Optional[Any]  # Result from tool execution
    conversation_history: list  # List of messages for multi-turn context
    is_complete: bool  # Whether the agent has finished processing


class CRMAgent:
    """
    LangGraph-based agent for processing HCP interaction inputs.
    
    Workflow:
    1. User provides natural language input about an HCP interaction
    2. Agent node invokes LLM with system context
    3. LLM reasons about the input and decides what to do next
    4. Based on LLM decision, route to appropriate tool node
    5. Tool node processes and returns result
    6. Agent decides if more tools are needed or if done
    """
    
    def __init__(self):
        """Initialize the agent with GroqService and LangGraph"""
        self.groq_service = GroqService()
        self.graph = self._build_graph()
        self.compiled_graph = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state graph with nodes and edges.
        
        Nodes:
        - agent_node: Invokes LLM to reason about user input
        - router_node: Routes to appropriate tool based on agent decision
        - tool_router: Executes the selected tool
        - finalize_node: Prepares final output
        
        Returns:
            StateGraph: Compiled agent graph
        """
        workflow = StateGraph(AgentState)
        
        # Define nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("router", self._router_node)
        workflow.add_node("tool_executor", self._tool_executor_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Define edges
        workflow.set_entry_point("agent")
        
        # After agent reasoning, route to appropriate tool
        workflow.add_edge("agent", "router")
        
        # Router decides to execute tool or finalize
        workflow.add_conditional_edges(
            "router",
            self._should_execute_tool,
            {
                "execute": "tool_executor",
                "finalize": "finalize"
            }
        )
        
        # After tool execution, check if we need more tools or finalize
        workflow.add_edge("tool_executor", "router")
        
        # Finalize node outputs the result
        workflow.add_edge("finalize", END)
        
        return workflow
    
    def _agent_node(self, state: AgentState) -> AgentState:
        """
        LLM reasoning node.
        Receives user input and uses LLM to understand what data needs extraction.
        
        Returns:
            Updated state with reasoning and extracted_data
        """
        logger.info(f"[AGENT] Processing input: {state['user_input'][:100]}...")
        
        # Build conversation context
        system_prompt = """You are an AI assistant helping a pharmaceutical sales representative 
        log and analyze HCP (Healthcare Professional) interactions.
        
        When given an interaction description, your job is to:
        1. Extract key information (HCP name, products discussed, sentiment, etc.)
        2. Provide professional summary
        3. Generate follow-up recommendations
        4. Identify sales insights
        
        Respond with structured data that can be saved to the CRM."""
        
        user_message = state["user_input"]
        
        # Call LLM to extract entities
        try:
            extracted = self.groq_service.extract_interaction_entities(user_message)
            state["extracted_data"] = extracted
            state["reasoning"] = f"Successfully extracted entities: {list(extracted.keys())}"
            logger.info(f"[AGENT] Extracted entities: {list(extracted.keys())}")
        except Exception as e:
            logger.error(f"[AGENT] Error extracting entities: {str(e)}")
            state["reasoning"] = f"Error during extraction: {str(e)}"
            state["extracted_data"] = None
        
        return state
    
    def _router_node(self, state: AgentState) -> AgentState:
        """
        Router node that decides which tool to execute next.
        
        Logic:
        - If extraction successful and HCP name found, set tool to log_interaction
        - Otherwise, if more analysis needed, set appropriate tool
        - Otherwise, mark as complete (finalize)
        """
        logger.info("[ROUTER] Deciding next action...")
        
        if state["extracted_data"] is None:
            logger.info("[ROUTER] No extracted data; proceeding to finalize")
            state["is_complete"] = True
            return state
        
        # Default: log the interaction (Step 9 tool)
        if "hcp_name" in state["extracted_data"] and state["extracted_data"]["hcp_name"]:
            state["current_tool"] = "log_interaction"
            state["tool_input"] = state["extracted_data"]
            logger.info("[ROUTER] Routing to log_interaction tool")
        else:
            state["is_complete"] = True
            logger.info("[ROUTER] No HCP name found; marking complete")
        
        return state
    
    def _should_execute_tool(self, state: AgentState) -> str:
        """
        Conditional edge function to determine if we should execute a tool or finalize.
        
        Returns:
            "execute" if current_tool is set and not complete
            "finalize" if complete or no tool selected
        """
        if state["is_complete"] or state["current_tool"] is None:
            return "finalize"
        return "execute"
    
    def _tool_executor_node(self, state: AgentState) -> AgentState:
        """
        Tool executor node.
        Executes the selected tool (placeholder implementation).
        
        Note: Actual tool implementations will be added in Steps 9-13.
        Currently just logs the tool call intent.
        """
        tool_name = state["current_tool"]
        tool_input = state["tool_input"]
        
        logger.info(f"[TOOL_EXECUTOR] Executing tool: {tool_name}")
        logger.info(f"[TOOL_EXECUTOR] Input: {tool_input}")
        
        # Placeholder: tools will be implemented in Steps 9-13
        state["tool_result"] = {
            "status": "pending",
            "message": f"Tool '{tool_name}' will be implemented in subsequent steps",
            "tool_input": tool_input
        }
        
        # After first tool execution, mark as complete (subsequent steps will add more logic)
        state["is_complete"] = True
        state["current_tool"] = None
        
        return state
    
    def _finalize_node(self, state: AgentState) -> AgentState:
        """
        Finalize node that prepares the final output.
        
        Returns:
            Updated state with comprehensive result structure
        """
        logger.info("[FINALIZE] Preparing final output...")
        
        # If we have extracted data, that's our primary output
        if state["extracted_data"]:
            state["extracted_data"]["processing_complete"] = True
        else:
            state["extracted_data"] = {"processing_complete": False, "error": state["reasoning"]}
        
        logger.info("[FINALIZE] Agent processing complete")
        return state
    
    def process_input(self, user_input: str) -> dict:
        """
        Main entry point: Process user input through the agent.
        
        Args:
            user_input (str): Natural language description of HCP interaction
        
        Returns:
            dict: Extracted interaction data with HCP info, sentiment, summary, etc.
        """
        initial_state = AgentState(
            user_input=user_input,
            extracted_data=None,
            reasoning="",
            current_tool=None,
            tool_input=None,
            tool_result=None,
            conversation_history=[HumanMessage(content=user_input)],
            is_complete=False
        )
        
        logger.info(f"[CRM_AGENT] Starting agent processing for: {user_input[:80]}...")
        
        try:
            # Execute the compiled graph
            final_state = self.compiled_graph.invoke(initial_state)
            logger.info("[CRM_AGENT] Agent processing completed successfully")
            return final_state
        except Exception as e:
            logger.error(f"[CRM_AGENT] Error during agent processing: {str(e)}")
            return {
                "error": str(e),
                "user_input": user_input,
                "extracted_data": None,
                "processing_complete": False
            }
