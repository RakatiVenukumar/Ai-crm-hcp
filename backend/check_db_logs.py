import sys
sys.path.insert(0, '.')

from app.database.db import SessionLocal
from app.models import HCP, Interaction

db = SessionLocal()
try:
    print("=== HCPS ===")
    hcps = db.query(HCP).all()
    for h in hcps:
        print(f"ID: {h.id} | Name: {h.name} | Specialization: {h.specialization}")

    print("\n=== INTERACTIONS ===")
    interactions = db.query(Interaction).all()
    for i in interactions:
        print(f"ID: {i.id} | HCP_ID: {i.hcp_id} | Type: {i.interaction_type} | Date: {i.date} | Time: {i.time}")
        print(f"  Summary: {i.summary}")
        print(f"  Follow-up: {i.follow_up_actions}")
        print("-" * 40)
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
