from app.routes.hcp_routes import router as hcp_router
from app.routes.interaction_routes import router as interaction_router
from app.routes.agent_routes import router as agent_router

__all__ = ["interaction_router", "hcp_router", "agent_router"]
