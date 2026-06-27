import urllib.request
import json

url = "http://localhost:8000/interaction/timeline"

try:
    print(f"Fetching timeline from {url}...")
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as res:
        print(f"Success! Status: {res.status}")
        data = json.loads(res.read().decode())
        print(f"Timeline records count: {len(data)}")
        for idx, item in enumerate(data):
            print(f" [{idx}] ID: {item['id']} | HCP_ID: {item['hcp_id']} | Date: {item['date']} | Time: {item['time']}")
except urllib.error.HTTPError as e:
    print(f"[HTTP Error] Status: {e.code}")
    print(f"[HTTP Error] Response: {e.read().decode()}")
except Exception as e:
    print(f"[Error]: {str(e)}")
