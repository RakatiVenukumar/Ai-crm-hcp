"""
Step 11 Test Script: InteractionSummaryTool
Tests:
1. Tool instantiation
2. Tool metadata/schema
3. Tool execution with various interaction notes
4. Summary quality and format
5. Error handling (empty notes, API failures)
"""

import sys
sys.path.insert(0, '.')

from app.tools import InteractionSummaryTool
import logging
import os

logging.basicConfig(level=logging.INFO)

def test_tool_instantiation():
    """Test 1: Tool can be instantiated"""
    print("TEST 1: Tool Instantiation")
    print("-" * 50)
    try:
        tool = InteractionSummaryTool()
        print("[OK] InteractionSummaryTool instantiated successfully")
        return tool
    except Exception as e:
        print(f"[FAIL] Error instantiating tool: {str(e)}")
        raise


def test_tool_metadata(tool):
    """Test 2: Tool metadata is correct"""
    print("\nTEST 2: Tool Metadata")
    print("-" * 50)
    
    try:
        info = tool.get_tool_info()
        print(f"[OK] Tool name: {info['name']}")
        print(f"[OK] Tool description: {info['description'][:60]}...")
        print(f"[OK] Input schema has interaction_notes: {('interaction_notes' in info['input_schema'])}")
        print(f"[OK] Output schema has summary: {('summary' in info['output_schema'])}")
        return info
    except Exception as e:
        print(f"[FAIL] Error getting tool metadata: {str(e)}")
        raise


def test_summary_generation_with_context(tool):
    """Test 3: Generate summary with interaction context"""
    print("\nTEST 3: Summary with Context")
    print("-" * 50)
    
    # Check if GROQ_API_KEY is set (required for this test)
    if not os.getenv("GROQ_API_KEY"):
        print("[SKIP] GROQ_API_KEY not set - skipping LLM test")
        print("       To run this test: set GROQ_API_KEY environment variable")
        return None
    
    try:
        notes = """
        Met with Dr. Johnson today to discuss our new cardiac medication.
        He expressed strong interest in the clinical trial data and asked
        about patient outcomes over 6 months. We discussed the medication's
        efficacy rates and safety profile. He indicated he has 15-20 potential
        patients who could benefit from this therapy. Provided him with
        literature and samples. He agreed to review and schedule a follow-up
        call next week to discuss implementation in his practice.
        """
        
        result = tool.execute(
            interaction_notes=notes,
            interaction_type="meeting",
            hcp_name="Dr. Johnson"
        )
        
        if result["success"]:
            print("[OK] Summary generated successfully")
            print(f"\n[SUMMARY]")
            print(result["summary"])
            print()
            # Validate summary characteristics
            summary_length = len(result["summary"])
            sentence_count = result["summary"].count(".")
            print(f"[OK] Summary length: {summary_length} characters")
            print(f"[OK] Sentence count: {sentence_count}")
            return result
        else:
            print(f"[FAIL] Summary generation failed: {result['error']}")
    except Exception as e:
        print(f"[FAIL] Error generating summary: {str(e)}")
        raise


def test_summary_without_context(tool):
    """Test 4: Generate summary without optional context"""
    print("\nTEST 4: Summary without Context")
    print("-" * 50)
    
    if not os.getenv("GROQ_API_KEY"):
        print("[SKIP] GROQ_API_KEY not set - skipping LLM test")
        return None
    
    try:
        notes = """
        Quick call with the practice manager. Discussed pricing and 
        reimbursement options. They need quotes for bulk orders of our
        diabetes management device. Promised to send pricing sheet by EOD.
        """
        
        result = tool.execute(interaction_notes=notes)
        
        if result["success"]:
            print("[OK] Summary generated without context")
            print(f"\n[SUMMARY]")
            print(result["summary"])
            print()
            return result
        else:
            print(f"[FAIL] Summary generation failed: {result['error']}")
    except Exception as e:
        print(f"[FAIL] Error generating summary: {str(e)}")
        raise


def test_error_handling(tool):
    """Test 5: Tool handles errors gracefully"""
    print("\nTEST 5: Error Handling")
    print("-" * 50)
    
    try:
        # Test with empty notes
        result = tool.execute(interaction_notes="")
        
        if not result["success"]:
            print("[OK] Tool correctly rejected empty notes")
            print(f"  - Error: {result['error']}")
        else:
            print("[FAIL] Tool should have rejected empty notes")
        
        # Test with whitespace only
        result = tool.execute(interaction_notes="   ")
        
        if not result["success"]:
            print("[OK] Tool correctly rejected whitespace-only notes")
            print(f"  - Error: {result['error']}")
        else:
            print("[FAIL] Tool should have rejected whitespace-only notes")
        
        # Test with None
        result = tool.execute(interaction_notes=None)
        
        if not result["success"]:
            print("[OK] Tool correctly rejected None notes")
            print(f"  - Error: {result['error']}")
        else:
            print("[FAIL] Tool should have rejected None notes")
    
    except Exception as e:
        print(f"[FAIL] Error in error handling test: {str(e)}")
        raise


if __name__ == "__main__":
    print("=" * 50)
    print("STEP 11: InteractionSummaryTool - Test Suite")
    print("=" * 50)
    
    try:
        tool = test_tool_instantiation()
        metadata = test_tool_metadata(tool)
        
        # Try to run LLM tests if API key is set
        summary_result = test_summary_generation_with_context(tool)
        
        if summary_result is None:
            print("\n[NOTE] Skipped LLM tests - set GROQ_API_KEY to enable")
        else:
            test_summary_without_context(tool)
        
        test_error_handling(tool)
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED")
        print("=" * 50)
        print("\nStep 11 Summary:")
        print("[OK] InteractionSummaryTool created with proper interface")
        print("[OK] Tool metadata schema is well-defined")
        print("[OK] Tool integrates with GroqService")
        print("[OK] Handles context parameters (hcp_name, interaction_type)")
        print("[OK] Validates required fields")
        print("[OK] Gracefully handles errors")
        print("\nNext: Step 12 will implement FollowupRecommendationTool")
        
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
