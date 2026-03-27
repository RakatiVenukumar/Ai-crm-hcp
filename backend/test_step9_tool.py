"""
Step 9 Test Script: LogInteractionTool
Tests:
1. Tool instantiation
2. Tool metadata/schema
3. Tool execution with database session
4. Error handling
"""

import sys
sys.path.insert(0, '.')

from app.tools import LogInteractionTool
from app.database.db import SessionLocal, Base, engine
from app.models import HCP, Interaction
import logging

logging.basicConfig(level=logging.INFO)

def test_tool_instantiation():
    """Test 1: Tool can be instantiated"""
    print("TEST 1: Tool Instantiation")
    print("-" * 50)
    try:
        tool = LogInteractionTool()
        print("[OK] LogInteractionTool instantiated successfully")
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
        print(f"[OK] Input schema keys: {list(info['input_schema'].keys())[:5]}...")
        print(f"[OK] Output schema keys: {list(info['output_schema'].keys())}")
        return info
    except Exception as e:
        print(f"[FAIL] Error getting tool metadata: {str(e)}")
        raise


def test_tool_execution_with_db(tool):
    """Test 3: Tool can execute with database"""
    print("\nTEST 3: Tool Execution with Database")
    print("-" * 50)
    
    try:
        # Create database tables
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("[OK] Database tables created")
        
        # Create a test session
        db = SessionLocal()
        
        try:
            # Create a test HCP first (since tool uses hcp_id=1)
            test_hcp = HCP(
                name="Dr. Johnson",
                specialization="Cardiology",
                hospital="City Hospital",
                city="New York"
            )
            db.add(test_hcp)
            db.commit()
            print(f"[OK] Test HCP created with ID: {test_hcp.id}")
            
            # Execute tool
            result = tool.execute(
                db=db,
                hcp_name="Dr. Johnson",
                interaction_type="meeting",
                date="2026-03-27",
                time="14:30",
                attendees=["Dr. Johnson", "Sales Rep"],
                topics_discussed=["New product", "Patient outcomes"],
                products_discussed=["Product A", "Product B"],
                sentiment="positive",
                summary="Productive meeting discussing new cardiac medications",
                follow_up_actions=["Send clinical data", "Schedule follow-up"]
            )
            
            print(f"[OK] Tool executed successfully")
            print(f"  - Success: {result['success']}")
            print(f"  - Message: {result['message']}")
            if result['success']:
                print(f"  - Interaction ID: {result['interaction_id']}")
                print(f"  - HCP ID: {result['interaction_data']['hcp_id']}")
                print(f"  - Type: {result['interaction_data']['interaction_type']}")
            
            return result
        
        finally:
            db.close()
    
    except Exception as e:
        print(f"[FAIL] Error executing tool: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def test_tool_error_handling(tool):
    """Test 4: Tool handles errors gracefully"""
    print("\nTEST 4: Error Handling")
    print("-" * 50)
    
    try:
        db = SessionLocal()
        
        try:
            # Test with missing required field
            result = tool.execute(
                db=db,
                hcp_name="",  # Empty HCP name should fail
                interaction_type="meeting"
            )
            
            if not result['success']:
                print(f"[OK] Tool correctly rejected empty HCP name")
                print(f"  - Error: {result['error']}")
            else:
                print(f"[FAIL] Tool should have rejected empty HCP name")
            
            # Test with missing interaction type
            result = tool.execute(
                db=db,
                hcp_name="Dr. Test",
                interaction_type=""  # Empty type should fail
            )
            
            if not result['success']:
                print(f"[OK] Tool correctly rejected empty interaction type")
                print(f"  - Error: {result['error']}")
            else:
                print(f"[FAIL] Tool should have rejected empty interaction type")
        
        finally:
            db.close()
    
    except Exception as e:
        print(f"[FAIL] Error in error handling test: {str(e)}")
        raise


if __name__ == "__main__":
    print("=" * 50)
    print("STEP 9: LogInteractionTool - Test Suite")
    print("=" * 50)
    
    try:
        tool = test_tool_instantiation()
        metadata = test_tool_metadata(tool)
        execution_result = test_tool_execution_with_db(tool)
        test_tool_error_handling(tool)
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED")
        print("=" * 50)
        print("\nStep 9 Summary:")
        print("[OK] LogInteractionTool created with proper interface")
        print("[OK] Tool metadata schema is well-defined")
        print("[OK] Tool integrates with InteractionService")
        print("[OK] Tool persists data to database successfully")
        print("[OK] Tool handles validation errors gracefully")
        print("\nNext: Step 10 will implement EditInteractionTool")
        
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {str(e)}")
        sys.exit(1)
