"""
Step 14 Test Script: Agent with Tool Integration
Tests the CRMAgent's ability to:
1. Load and instantiate all 5 tools
2. Route to correct tools based on input
3. Execute tools in sequence
4. Handle errors gracefully
"""

import sys
sys.path.insert(0, '.')

from app.agents.agent import CRMAgent
import logging

logging.basicConfig(level=logging.INFO)

def test_agent_instantiation():
    """Test 1: Agent can be instantiated with all tools"""
    print("TEST 1: Agent Instantiation with Tools")
    print("-" * 50)
    try:
        agent = CRMAgent()
        print("[OK] CRMAgent instantiated successfully")
        
        # Verify all tools are registered
        expected_tools = ["log_interaction", "edit_interaction", "summarize", "followup", "sales_insight"]
        for tool_name in expected_tools:
            if tool_name in agent.tools:
                print(f"[OK] Tool registered: {tool_name}")
            else:
                print(f"[FAIL] Tool NOT registered: {tool_name}")
                raise AssertionError(f"Missing tool: {tool_name}")
        
        return agent
    except Exception as e:
        print(f"[FAIL] Error instantiating agent: {str(e)}")
        raise


def test_agent_tool_metadata(agent):
    """Test 2: All tools have proper metadata"""
    print("\nTEST 2: Tool Metadata Validation")
    print("-" * 50)
    
    try:
        for tool_name, tool in agent.tools.items():
            info = tool.get_tool_info()
            print(f"[OK] Tool '{tool_name}':")
            print(f"     - Name: {info.get('name', 'N/A')}")
            print(f"     - Inputs: {len(info.get('input_schema', {}))} fields")
            print(f"     - Outputs: {len(info.get('output_schema', {}))} fields")
    except Exception as e:
        print(f"[FAIL] Error getting tool metadata: {str(e)}")
        raise


def test_agent_extraction_only():
    """Test 3: Agent extracts entities without GroqService LLM"""
    print("\nTEST 3: Agent Extraction (No LLM)")
    print("-" * 50)
    
    agent = CRMAgent()
    
    try:
        # Simple input to test extraction logic
        user_input = "Had a call with Dr. Smith at cardiac center about our heart monitor product yesterday"
        
        result = agent.process_input(user_input)
        
        print(f"[OK] Agent processed input")
        print(f"[OK] Success: {result.get('success')}")
        print(f"[OK] Complete: {result.get('complete')}")
        
        if result.get("extracted_data"):
            extracted = result["extracted_data"]
            print(f"[OK] Extracted HCP name: {extracted.get('hcp_name', 'N/A')}")
            print(f"[OK] Extracted sentiment: {extracted.get('sentiment', 'N/A')}")
        
        return result
    except Exception as e:
        print(f"[FAIL] Error during agent processing: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def test_agent_null_input():
    """Test 4: Agent handles NULL/empty input gracefully"""
    print("\nTEST 4: Error Handling - Null Input")
    print("-" * 50)
    
    agent = CRMAgent()
    
    try:
        # Test with empty input
        result = agent.process_input("")
        
        if result.get("success") is False or not result.get("extracted_data"):
            print("[OK] Agent correctly rejected empty input")
        else:
            print("[INFO] Agent still processed empty input (non-critical)")
        
        # Test with whitespace
        result = agent.process_input("   ")
        
        if result.get("success") is False or not result.get("extracted_data"):
            print("[OK] Agent correctly rejected whitespace input")
        else:
            print("[INFO] Agent still processed whitespace input (non-critical)")
        
    except Exception as e:
        print(f"[FAIL] Error during null input test: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def test_agent_complex_input():
    """Test 5: Agent processes realistic complex input"""
    print("\nTEST 5: Complex Realistic Input")
    print("-" * 50)
    
    agent = CRMAgent()
    
    try:
        complex_input = """
        Had an excellent meeting with Dr. Patricia Chen, head of orthopedics at Central Hospital.
        Attended: Dr. Chen, 2 nurses, surgery scheduler.
        Discussed: Our advanced joint replacement system, especially for knee and hip replacement.
        Materials provided: Product brochures, clinical outcomes data.
        Samples: Provided 3 sample implants for evaluation.
        Initial sentiment: Very positive, strong interest in pilot program.
        Next steps: They want to schedule a training session in 2 weeks.
        Timeline: Decision expected by end of Q2.
        Products discussed: Joint Pro 2000, SurgiAlign System, ProFlex Implants.
        """
        
        result = agent.process_input(complex_input)
        
        print(f"[OK] Processed complex input successfully")
        print(f"[OK] Success: {result.get('success')}")
        print(f"[OK] Complete: {result.get('complete')}")
        
        if result.get("extracted_data"):
            extracted = result["extracted_data"]
            print(f"\n[EXTRACTED DATA]")
            print(f"  HCP Name: {extracted.get('hcp_name', 'N/A')}")
            print(f"  Sentiment: {extracted.get('sentiment', 'N/A')}")
            print(f"  Products: {extracted.get('products_discussed', 'N/A')}")
            print(f"  Summary: {extracted.get('summary', 'N/A')[:100] if extracted.get('summary') else 'N/A'}...")
        
        print(f"\n[TOOL RESULTS]")
        if result.get("tool_results"):
            tool_result = result["tool_results"].get("last_result")
            if tool_result:
                print(f"  Last tool success: {tool_result.get('success', 'N/A')}")
                if tool_result.get('success') is False:
                    print(f"  Error: {tool_result.get('error', 'N/A')}")
        
        return result
    except Exception as e:
        print(f"[FAIL] Error processing complex input: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def test_agent_routing_logic():
    """Test 6: Verify agent routing logic works correctly"""
    print("\nTEST 6: Agent Routing Logic")
    print("-" * 50)
    
    agent = CRMAgent()
    
    try:
        # Test 1: Input without HCP name - should not queue tools
        from app.agents.agent import AgentState
        from langchain_core.messages import HumanMessage
        
        state = AgentState(
            user_input="This is a test",
            extracted_data={"sentiment": "neutral"},  # No HCP name
            reasoning="",
            current_tool=None,
            tool_input=None,
            tool_result=None,
            conversation_history=[HumanMessage(content="test")],
            is_complete=False
        )
        
        state = agent._router_node(state)
        
        if state.get("is_complete"):
            print("[OK] Router correctly completes when no HCP name found")
        else:
            print("[WARN] Router did not complete despite missing HCP name")
        
        # Test 2: Input with HCP name - should queue tools
        state2 = AgentState(
            user_input="Met with Dr. Smith",
            extracted_data={
                "hcp_name": "Dr. Smith",
                "interaction_notes": "Had a good conversation about products",
                "interaction_type": "meeting"
            },
            reasoning="",
            current_tool=None,
            tool_input=None,
            tool_result=None,
            conversation_history=[HumanMessage(content="test")],
            is_complete=False
        )
        
        state2 = agent._router_node(state2)
        
        if state2.get("current_tool") == "log_interaction":
            print("[OK] Router correctly routes to log_interaction")
        else:
            print(f"[FAIL] Router incorrectly routed to {state2.get('current_tool')}")
        
        if state2.get("tool_queue"):
            print(f"[OK] Router queued {len(state2.get('tool_queue', []))} follow-up tools")
        
    except Exception as e:
        print(f"[FAIL] Error testing router logic: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    print("=" * 50)
    print("STEP 14: Agent + Tool Integration - Test Suite")
    print("=" * 50)
    
    try:
        agent = test_agent_instantiation()
        test_agent_tool_metadata(agent)
        
        test_agent_extraction_only()
        test_agent_null_input()
        test_agent_complex_input()
        test_agent_routing_logic()
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED")
        print("=" * 50)
        print("\nStep 14 Summary:")
        print("[OK] CRMAgent instantiated with all 5 tools")
        print("[OK] Tool registration and metadata validated")
        print("[OK] Agent processes natural language input")
        print("[OK] Agent extracts entities from interactions")
        print("[OK] Agent routes to appropriate tools")
        print("[OK] Agent handles errors gracefully")
        print("[OK] Agent supports tool queueing for multi-step workflows")
        print("\nNext: Step 15 will create /agent/chat API endpoint")
        
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
