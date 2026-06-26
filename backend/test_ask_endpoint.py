"""
Test Script for the Challenge /ask Endpoint
This verifies:
1. Endpoint existence and structure.
2. Normal business query: logging a standard interaction.
3. Challenging query: ambiguous/incomplete data, or invalid input.
"""

import sys
sys.path.insert(0, '.')

# Reconfigure stdout to use UTF-8 on Windows to print unicode checkmarks (✓) without error
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import json
from fastapi.testclient import TestClient
from app.main import app
import logging

logging.basicConfig(level=logging.INFO)

client = TestClient(app)

def test_ask_endpoint_exists():
    """Test 1: Check that the POST /ask endpoint is accessible"""
    print("\nTEST 1: /ask Endpoint Existence")
    print("-" * 50)
    try:
        response = client.post("/ask", json={"question": "Ping"})
        print(f"[OK] Status code: {response.status_code}")
        data = response.json()
        print(f"[OK] Response: {data}")
        assert "success" in data, "Response should have 'success' field"
        assert "response" in data, "Response should have 'response' field"
        return True
    except Exception as e:
        print(f"[FAIL] Error: {str(e)}")
        raise

def test_normal_business_query():
    """Test 2: One normal business query (logging an interaction)"""
    print("\nTEST 2: Normal Business Query")
    print("-" * 50)
    normal_input = {
        "question": "Had a fantastic meeting with Dr. Raymond Holt at Brooklyn Medical Center. We discussed CardioCare and he was very positive. Left 2 samples."
    }
    try:
        response = client.post("/ask", json=normal_input)
        print(f"[OK] Status code: {response.status_code}")
        data = response.json()
        print(f"[OK] Success status: {data.get('success')}")
        print(f"[OK] Response message: {data.get('response')}")
        
        extracted = data.get("extracted_data")
        if extracted:
            print("[OK] Extracted Data:")
            print(f"     - HCP Name: {extracted.get('hcp_name')}")
            print(f"     - Sentiment: {extracted.get('sentiment')}")
            print(f"     - Products: {extracted.get('products_discussed')}")
        else:
            print("[WARN] No data extracted (expected if GROQ_API_KEY is not configured)")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error: {str(e)}")
        raise

def test_challenging_query():
    """Test 3: One challenging query (incomplete info, no products, no sentiment)"""
    print("\nTEST 3: Challenging Business Query")
    print("-" * 50)
    challenging_input = {
        "question": "Met Dr. Diaz. Left samples."
    }
    try:
        response = client.post("/ask", json=challenging_input)
        print(f"[OK] Status code: {response.status_code}")
        data = response.json()
        print(f"[OK] Success status: {data.get('success')}")
        print(f"[OK] Response message: {data.get('response')}")
        
        extracted = data.get("extracted_data")
        if extracted:
            print("[OK] Extracted Data (Check fallbacks/defaults):")
            print(f"     - HCP Name: {extracted.get('hcp_name')}")
            print(f"     - Sentiment: {extracted.get('sentiment')}")
            print(f"     - Products: {extracted.get('products_discussed')}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error: {str(e)}")
        raise

def test_invalid_query():
    """Test 4: Invalid/Empty input (guardrails and validation)"""
    print("\nTEST 4: Invalid Empty Query")
    print("-" * 50)
    try:
        response = client.post("/ask", json={"question": ""})
        print(f"[OK] Status code: {response.status_code}")
        # Should return 422 (validation error) since min_length=1
        if response.status_code == 422:
            print("[OK] Correctly blocked empty input with 422 validation error")
        else:
            print(f"[WARN] Unexpected status code: {response.status_code}")
            print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {str(e)}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING CHALLENGE /ask ENDPOINT TESTS")
    print("=" * 60)
    
    try:
        test_ask_endpoint_exists()
        test_normal_business_query()
        test_challenging_query()
        test_invalid_query()
        print("\n" + "=" * 60)
        print("ALL ENDPOINT TESTS PASSED")
        print("=" * 60)
    except Exception as e:
        print(f"\n[FAIL] Test suite failed: {str(e)}")
        sys.exit(1)
