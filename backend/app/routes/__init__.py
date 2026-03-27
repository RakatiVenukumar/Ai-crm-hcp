from app.routes.hcp_routes import router as hcp_router
from app.routes.interaction_routes import router as interaction_router

__all__ = ["interaction_router", "hcp_router"]
