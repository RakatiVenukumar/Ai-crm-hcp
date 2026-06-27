import urllib.request
import json
import datetime

url = "http://localhost:8000/interaction/log"
# Let's create HCP first just in case
hcp_url = "http://localhost:8000/hcp"

def run_test():
    try:
        # Create HCP "Dr. Raymond"
        hcp_data = {"name": "Dr. Raymond"}
        req = urllib.request.Request(
            hcp_url,
            data=json.dumps(hcp_data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as res:
            hcp = json.loads(res.read().decode())
            print(f"HCP created/verified: {hcp}")
            hcp_id = hcp["id"]

        # Log interaction payload
        payload = {
            "hcp_id": hcp_id,
            "interaction_type": "meeting",
            "date": str(datetime.date.today()),
            "time": "15:30",
            "attendees": "Dr. Raymond",
            "topics_discussed": "CardioCare, HeartMonitor Pro",
            "materials_shared": "Not specified",
            "samples_distributed": "3 samples",
            "sentiment": "positive",
            "outcomes": "expressed interest in the products",
            "follow_up_actions": "Schedule training session next week",
            "summary": "Met Dr. Raymond to discuss CardioCare"
        }

        print(f"Sending payload to {url}: {payload}")
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req) as res:
            print(f"Response Status: {res.status}")
            body = res.read().decode()
            print(f"Response Body: {body}")
            
    except urllib.error.HTTPError as e:
        print(f"[HTTP Error] Status: {e.code}")
        print(f"[HTTP Error] Response: {e.read().decode()}")
    except Exception as e:
        print(f"[Error]: {str(e)}")

if __name__ == "__main__":
    run_test()
