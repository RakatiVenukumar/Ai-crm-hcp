"""
LangGraph Agent for CRM Interaction Processing
Orchestrates LLM reasoning with tool execution for extracting and analyzing HCP interactions
"""

from typing import TypedDict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from app.services.groq_service import GroqService
from app.tools import (
    LogInteractionTool,
    EditInteractionTool,
    InteractionSummaryTool,
    FollowupRecommendationTool,
    SalesInsightTool
)
import json
import logging

logger = logging.getLogger(__name__)


class AgentState(TypedDict, total=False):
    """State object passed through the agent graph"""
    user_input: str  # Original user input
    extracted_data: Optional[dict]  # Data extracted by LLM (entities, summary, etc.)
    reasoning: str  # LLM reasoning about what the user is asking
    current_tool: Optional[str]  # Name of the tool to execute (set by agent_node)
    tool_input: Optional[dict]  # Input parameters for the tool
    tool_result: Optional[Any]  # Result from tool execution
    conversation_history: list  # List of messages for multi-turn context
    is_complete: bool  # Whether the agent has finished processing
    tool_queue: list  # Queue of tools to execute in sequence


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
        """Initialize the agent with GroqService, all tools, and LangGraph"""
        self.groq_service = GroqService()
        
        # Initialize all tools
        self.log_interaction_tool = LogInteractionTool()
        self.edit_interaction_tool = EditInteractionTool()
        self.summary_tool = InteractionSummaryTool()
        self.followup_tool = FollowupRecommendationTool()
        self.sales_insight_tool = SalesInsightTool()
        
        # Register tools for easy lookup
        self.tools = {
            "log_interaction": self.log_interaction_tool,
            "edit_interaction": self.edit_interaction_tool,
            "summarize": self.summary_tool,
            "followup": self.followup_tool,
            "sales_insight": self.sales_insight_tool
        }
        
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
        Router node that decides which tool(s) to execute next.
        
        Tool routing logic:
        1. If no extracted data, finalize with error
        2. If HCP name found and interaction_type present -> log_interaction
        3. After logging, queue up analysis tools:
           - summarize (if long interaction_notes)
           - followup (to generate next steps)
           - sales_insight (to identify opportunities)
        4. If editing existing interaction -> edit_interaction
        
        Returns tools to execute in priority order via tool queue.
        """
        logger.info("[ROUTER] Deciding next action...")
        
        if state["extracted_data"] is None:
            logger.info("[ROUTER] No extracted data; proceeding to finalize")
            state["is_complete"] = True
            return state
        
        extracted = state["extracted_data"]
        
        # Initialize tool queue if not present
        if "tool_queue" not in state:
            state["tool_queue"] = []
        
        # Already have a tool in queue that was just set by agent/previous router call
        if state["current_tool"] is not None:
            logger.info(f"[ROUTER] Tool already queued: {state['current_tool']}")
            return state
        
        # Check if we have a tool queue from previous execution
        if state.get("tool_queue"):
            state["current_tool"] = state["tool_queue"].pop(0)
            state["tool_input"] = {"data": extracted}
            logger.info(f"[ROUTER] Executing next queued tool: {state['current_tool']}")
            return state
        
        # If editing an existing interaction (has interaction_id)
        if "interaction_id" in extracted and extracted["interaction_id"]:
            state["current_tool"] = "edit_interaction"
            state["tool_input"] = extracted
            logger.info("[ROUTER] Routing to edit_interaction tool")
            return state
        
        # If creating new interaction (has HCP name and interaction data)
        if "hcp_name" in extracted and extracted["hcp_name"]:
            # Queue up all analysis tools after logging
            has_notes = "interaction_notes" in extracted and extracted["interaction_notes"]
            
            tools_to_queue = []
            
            # Always queue summary and followup if we have notes
            if has_notes:
                tools_to_queue.extend(["summarize", "followup", "sales_insight"])
            
            # Log interaction is the first priority
            state["current_tool"] = "log_interaction"
            state["tool_input"] = extracted
            state["tool_queue"] = tools_to_queue  # Queue remaining tools
            
            logger.info(f"[ROUTER] Routing to log_interaction; queued tools: {tools_to_queue}")
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
        Executes the selected tool and captures its result.
        
        Supports:
        - log_interaction: Persist extracted data to database (Step 9)
        - edit_interaction: Update existing interaction (Step 10)
        - summarize: Generate professional summary (Step 11)
        - followup: Generate follow-up recommendations (Step 12)
        - sales_insight: Extract sales insights (Step 13)
        """
        tool_name = state["current_tool"]
        tool_input = state["tool_input"]
        
        logger.info(f"[TOOL_EXECUTOR] Executing tool: {tool_name}")
        logger.info(f"[TOOL_EXECUTOR] Input keys: {list(tool_input.keys()) if isinstance(tool_input, dict) else 'N/A'}")
        
        try:
            # Get the tool from registry
            tool = self.tools.get(tool_name)
            if not tool:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            # Execute the tool with appropriate parameters
            if tool_name == "log_interaction":
                result = tool.execute(**tool_input)
            
            elif tool_name == "edit_interaction":
                result = tool.execute(**tool_input)
            
            elif tool_name == "summarize":
                # Extract notes from input or state
                notes = tool_input.get("interaction_notes") or tool_input.get("data", {}).get("interaction_notes", "")
                context = {
                    "hcp_name": tool_input.get("hcp_name") or tool_input.get("data", {}).get("hcp_name"),
                    "interaction_type": tool_input.get("interaction_type") or tool_input.get("data", {}).get("interaction_type")
                }
                result = tool.execute(
                    interaction_notes=notes,
                    interaction_type=context.get("interaction_type"),
                    hcp_name=context.get("hcp_name")
                )
            
            elif tool_name == "followup":
                # Generate followup recommendations
                notes = tool_input.get("interaction_notes") or tool_input.get("data", {}).get("interaction_notes", "")
                context = {
                    "hcp_name": tool_input.get("hcp_name") or tool_input.get("data", {}).get("hcp_name"),
                    "interaction_type": tool_input.get("interaction_type") or tool_input.get("data", {}).get("interaction_type"),
                    "current_stage": tool_input.get("interaction_stage") or tool_input.get("data", {}).get("interaction_stage", "ongoing")
                }
                result = tool.execute(
                    interaction_notes=notes,
                    interaction_type=context.get("interaction_type"),
                    hcp_name=context.get("hcp_name"),
                    current_stage=context.get("current_stage")
                )
            
            elif tool_name == "sales_insight":
                # Generate sales insights
                notes = tool_input.get("interaction_notes") or tool_input.get("data", {}).get("interaction_notes", "")
                context = {
                    "hcp_name": tool_input.get("hcp_name") or tool_input.get("data", {}).get("hcp_name"),
                    "interaction_type": tool_input.get("interaction_type") or tool_input.get("data", {}).get("interaction_type"),
                    "hcp_specialty": tool_input.get("hcp_specialty") or tool_input.get("data", {}).get("hcp_specialty")
                }
                result = tool.execute(
                    interaction_notes=notes,
                    interaction_type=context.get("interaction_type"),
                    hcp_name=context.get("hcp_name"),
                    hcp_specialty=context.get("hcp_specialty")
                )
            
            else:
                result = {"success": False, "error": f"Unsupported tool: {tool_name}"}
            
            state["tool_result"] = result
            logger.info(f"[TOOL_EXECUTOR] Tool execution success: {result.get('success', False)}")
            
        except Exception as e:
            logger.error(f"[TOOL_EXECUTOR] Error executing tool {tool_name}: {str(e)}")
            state["tool_result"] = {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
        
        # If no more tools in queue, mark as complete
        if not state.get("tool_queue"):
            state["is_complete"] = True
        else:
            # Set next tool from queue
            state["current_tool"] = state["tool_queue"].pop(0)
            state["tool_input"] = {"data": state["extracted_data"]}
        
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
        
        Workflow:
        1. Agent node extracts entities from natural language input
        2. Router determines which tools to invoke based on extracted data
        3. Tool executor invokes tools in sequence (log, summary, followup, insight)
        4. Finalize node prepares comprehensive output
        
        Args:
            user_input (str): Natural language description of HCP interaction
        
        Returns:
            dict: Extracted interaction data with all tool results
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

            extracted_data = final_state.get("extracted_data")
            reasoning = final_state.get("reasoning")

            # If extraction failed (e.g., invalid API key), return explicit failure.
            extraction_failed = (
                not extracted_data
                or extracted_data.get("processing_complete") is False
                or (isinstance(reasoning, str) and reasoning.lower().startswith("error during extraction"))
            )

            if extraction_failed:
                error_message = extracted_data.get("error") if isinstance(extracted_data, dict) else None
                if not error_message:
                    error_message = reasoning or "Agent could not extract interaction data."
                return {
                    "success": False,
                    "error": error_message,
                    "user_input": user_input,
                    "extracted_data": extracted_data,
                    "tool_results": {
                        "last_result": final_state.get("tool_result")
                    },
                    "reasoning": reasoning,
                    "complete": final_state.get("is_complete", True)
                }
            
            # Format response
            return {
                "success": True,
                "user_input": user_input,
                "extracted_data": extracted_data,
                "tool_results": {
                    "last_result": final_state.get("tool_result")
                },
                "reasoning": reasoning,
                "complete": final_state.get("is_complete", True)
            }
        except Exception as e:
            logger.error(f"[CRM_AGENT] Error during agent processing: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "user_input": user_input,
                "extracted_data": None,
                "complete": False
            }
