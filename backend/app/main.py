import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
	load_dotenv()

	app = FastAPI(title="AI First CRM HCP API")

	app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	@app.get("/")
	async def root() -> dict[str, str]:
		return {"message": "AI First CRM HCP API"}

	@app.get("/health")
	async def health_check() -> dict[str, str]:
		return {"status": "ok"}

	return app


app = create_app()


if __name__ == "__main__":
	host = os.getenv("HOST", "0.0.0.0")
	port = int(os.getenv("PORT", "8000"))
	reload = os.getenv("RELOAD", "true").lower() == "true"

	import uvicorn

	uvicorn.run("app.main:app", host=host, port=port, reload=reload)
