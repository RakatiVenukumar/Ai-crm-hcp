import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.db import Base, engine
from app.models import HCP, Interaction  # Import models for table creation
from app.routes import hcp_router, interaction_router, agent_router

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db


class AskRequest(BaseModel):
    """Request schema for /ask endpoint"""
    question: str = Field(..., min_length=1, description="The user question or input")


class AskResponse(BaseModel):
    """Response schema for /ask endpoint"""
    success: bool = Field(..., description="Whether processing was successful")
    response: str = Field(..., description="The natural language response or error message")
    extracted_data: Optional[Dict[str, Any]] = Field(default=None, description="Extracted HCP interaction data")
    error: Optional[str] = Field(default=None, description="Error message if processing failed")


def create_app() -> FastAPI:
    load_dotenv()

    app = FastAPI(
        title="AI First CRM HCP Interaction Module",
        description="AI-powered CRM for pharmaceutical field representatives",
        version="0.1.0",
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create tables on startup
    @app.on_event("startup")
    async def startup_event():
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Application shutting down...")

    # Health check and root routes
    @app.get("/")
    async def root() -> dict[str, str]:
        return {"message": "AI First CRM HCP API", "status": "running"}

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "service": "ai-crm-hcp"}

    @app.post("/ask", response_model=AskResponse)
    async def ask(request: AskRequest, db: Session = Depends(get_db)) -> AskResponse:
        """
        Challenge Endpoint: Accept a user question, process it using the AI agent,
        perform the business action (logging/updating database), and return a response.
        """
        logger.info(f"[ASK] Received request: {request.question[:100]}...")
        try:
            from app.routes.agent_routes import get_agent
            
            # Process the input using the agent (stateless for /ask, passes empty conversation history)
            agent = get_agent()
            result = agent.process_input(request.question, [], db)
            
            success = result.get("success", False)
            response_msg = result.get("response_message") or result.get("error") or "Failed to process question."
            
            return AskResponse(
                success=success,
                response=response_msg,
                extracted_data=result.get("extracted_data"),
                error=result.get("error")
            )
        except Exception as e:
            logger.error(f"[ASK] Unexpected error: {str(e)}", exc_info=True)
            return AskResponse(
                success=False,
                response=f"Server error: {str(e)}",
                error=str(e)
            )

    app.include_router(interaction_router)
    app.include_router(hcp_router)
    app.include_router(agent_router)

    return app


app = create_app()


if __name__ == "__main__":
	host = os.getenv("HOST", "0.0.0.0")
	port = int(os.getenv("PORT", "8000"))
	reload = os.getenv("RELOAD", "true").lower() == "true"

	import uvicorn

	uvicorn.run("app.main:app", host=host, port=port, reload=reload)
