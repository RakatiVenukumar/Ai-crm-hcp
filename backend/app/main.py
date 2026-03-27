import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.db import Base, engine

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


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

    return app


app = create_app()


if __name__ == "__main__":
	host = os.getenv("HOST", "0.0.0.0")
	port = int(os.getenv("PORT", "8000"))
	reload = os.getenv("RELOAD", "true").lower() == "true"

	import uvicorn

	uvicorn.run("app.main:app", host=host, port=port, reload=reload)
