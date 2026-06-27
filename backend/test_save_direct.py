import sys
sys.path.insert(0, '.')

from app.database.db import SessionLocal, engine, Base
from app.models import HCP, Interaction
from app.services.interaction_service import InteractionService
from app.schemas import InteractionCreate
import datetime

# Create session
db = SessionLocal()

try:
    print("Checking database...")
    # Check if tables exist and count HCPs
    hcps = db.query(HCP).all()
    print(f"Total HCPs in database: {len(hcps)}")
    for h in hcps:
        print(f" - ID: {h.id}, Name: {h.name}")
        
    interactions = db.query(Interaction).all()
    print(f"Total Interactions in database: {len(interactions)}")
    
    # Let's try to find or create an HCP
    hcp_name = "Dr. Raymond"
    hcp = db.query(HCP).filter(HCP.name == hcp_name).first()
    if not hcp:
        print(f"HCP '{hcp_name}' not found. Creating...")
        hcp = HCP(name=hcp_name)
        db.add(hcp)
        db.commit()
        db.refresh(hcp)
        print(f"Created HCP with ID: {hcp.id}")
    else:
        print(f"Found existing HCP '{hcp_name}' with ID: {hcp.id}")

    # Now let's try to create an interaction via InteractionService
    payload = InteractionCreate(
        hcp_id=hcp.id,
        interaction_type="meeting",
        date=str(datetime.date.today()),
        time="15:30",
        attendees="Dr. Raymond",
        topics_discussed="CardioCare, HeartMonitor Pro",
        materials_shared="Not specified",
        samples_distributed="3 samples",
        sentiment="positive",
        outcomes="expressed interest in the products",
        follow_up_actions="Schedule training session next week",
        summary="Met Dr. Raymond to discuss CardioCare"
    )
    
    print("Attempting to log interaction through InteractionService...")
    interaction = InteractionService.create_interaction(db, payload)
    print(f"[OK] Successfully logged interaction in DB with ID: {interaction.id}")

except Exception as e:
    print(f"[FAIL] Error during database operations: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
