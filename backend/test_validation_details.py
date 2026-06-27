import urllib.request
import json

url = "http://localhost:8000/interaction/log"

# Let's test with various payloads that might cause 422 validation error
payloads = [
    # Test 1: Empty strings for optional fields
    {
        "hcp_id": 2,
        "interaction_type": "meeting",
        "date": "2026-06-27",
        "time": "",
        "attendees": "",
        "topics_discussed": "",
        "materials_shared": "",
        "samples_distributed": "",
        "sentiment": "",
        "outcomes": "",
        "follow_up_actions": "",
        "summary": ""
    },
    # Test 2: Null values for optional fields
    {
        "hcp_id": 2,
        "interaction_type": "meeting",
        "date": "2026-06-27",
        "time": None,
        "attendees": None,
        "topics_discussed": None,
        "materials_shared": None,
        "samples_distributed": None,
        "sentiment": None,
        "outcomes": None,
        "follow_up_actions": None,
        "summary": None
    }
]

for idx, p in enumerate(payloads):
    try:
        print(f"Testing Payload {idx+1}...")
        req = urllib.request.Request(
            url,
            data=json.dumps(p).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as res:
            print(f" -> Success! Status: {res.status}")
    except urllib.error.HTTPError as e:
        print(f" -> [HTTP Error] Status: {e.code}")
        print(f" -> Response: {e.read().decode()}")
    except Exception as e:
        print(f" -> [Error]: {str(e)}")
