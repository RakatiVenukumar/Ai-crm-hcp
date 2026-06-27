import urllib.request
import json

url = "http://localhost:8000/interaction/log"

# Exact payload structure from the UI screenshot
payload = {
    "hcp_id": 2, # Dr. Raymond
    "interaction_type": "meeting",
    "date": "2026-06-27",
    "time": "", # Empty time
    "attendees": "", # Empty attendees
    "topics_discussed": "CardioCare, HeartMonitor Pro",
    "materials_shared": "",
    "samples_distributed": "3", # Contains the value 3
    "sentiment": "positive",
    "outcomes": "expressed interest in the products, requested a follow-up training session",
    "follow_up_actions": "Schedule a follow-up training session next week, Confirm the training session details with Dr. Raymond",
    "summary": "Met Dr. Raymond to discuss CardioCare and HeartMonitor Pro"
}

try:
    print(f"Sending exact UI payload to {url}...")
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        print(f"Success! Status: {res.status}")
        print(f"Response Body: {res.read().decode()}")
except urllib.error.HTTPError as e:
    print(f"[HTTP Error] Status: {e.code}")
    print(f"[HTTP Error] Response: {e.read().decode()}")
except Exception as e:
    print(f"[Error]: {str(e)}")
