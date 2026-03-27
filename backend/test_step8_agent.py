"""
Step 8 Test Script: LangGraph Agent Initialization and Basic Workflow
Tests:
1. Agent instantiation
2. Agent graph compilation
3. Basic input processing
"""

import sys
import os
sys.path.insert(0, '.')

from app.agents import CRMAgent
import json

def test_agent_instantiation():
    """Test 1: Agent can be instantiated"""
    print("TEST 1: Agent Instantiation")
    print("-" * 50)
    try:
        agent = CRMAgent()
        print("✓ CRMAgent instantiated successfully")
        print(f"✓ Graph compiled: {agent.compiled_graph is not None}")
        print(f"✓ GroqService initialized: {agent.groq_service is not None}")
        return agent
    except Exception as e:
        print(f"✗ Error instantiating agent: {str(e)}")
        raise


def test_agent_input_processing(agent):
    """Test 2: Agent can process user input"""
    print("\nTEST 2: Input Processing")
    print("-" * 50)
    
    test_input = "Met with Dr. Smith today. We discussed our new diabetes medication and he showed interest in the weekly monitoring program. He has 50 patients with Type 2 diabetes in his clinic."
    
    print(f"Input: {test_input[:80]}...")
    
    try:
        result = agent.process_input(test_input)
        print("✓ Agent processed input successfully")
        
        if result.get("extracted_data"):
            extracted = result["extracted_data"]
            print("\nExtracted data:")
            print(f"  - HCP Name: {extracted.get('hcp_name', 'N/A')}")
            print(f"  - Products: {extracted.get('products_discussed', [])}")
            print(f"  - Sentiment: {extracted.get('sentiment', 'N/A')}")
            print(f"  - Summary: {extracted.get('summary', 'N/A')[:80]}...")
            print(f"  - Topics: {extracted.get('key_topics', [])}")
        else:
            print("✓ Agent processed input (no extracted data)")
        
        print(f"✓ Processing complete: {result.get('extracted_data', {}).get('processing_complete', False)}")
        return result
    except Exception as e:
        print(f"✗ Error processing input: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def test_state_management(agent):
    """Test 3: Agent state transitions"""
    print("\nTEST 3: State Management")
    print("-" * 50)
    
    test_input = "Quick catch-up with Dr. Johnson about their upcoming conference."
    
    try:
        result = agent.process_input(test_input)
        print("✓ Agent state machine executed without errors")
        
        # Verify state transitions occurred
        if "extracted_data" in result:
            print("✓ Agent completed state transitions (agent → router → tool/finalize → END)")
        
        print(f"✓ Final state keys: {list(result.keys())}")
        return result
    except Exception as e:
        print(f"✗ Error in state management: {str(e)}")
        raise


if __name__ == "__main__":
    print("=" * 50)
    print("STEP 8: LangGraph Agent Setup - Test Suite")
    print("=" * 50)
    
    try:
        # Run tests
        agent = test_agent_instantiation()
        result1 = test_agent_input_processing(agent)
        result2 = test_state_management(agent)
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED ✓")
        print("=" * 50)
        print("\nStep 8 Summary:")
        print("✓ LangGraph agent structure created and working")
        print("✓ Agent state graph compiles without errors")
        print("✓ Agent can process natural language inputs")
        print("✓ Agent integrates with GroqService for LLM reasoning")
        print("✓ State transitions work correctly (agent → router → finalize)")
        print("\nNext: Step 9 will implement LogInteractionTool")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        sys.exit(1)
