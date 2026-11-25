from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routes import endpoints
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):

    yield


app = FastAPI(
    title = "SAK-AgriPolicies",
    description = "Smart Agentic Knowledgebase for Agricultural Policies in the Philippines",
    lifespan = lifespan
)

app.include_router(endpoints.router)


@app.get("/health")
def health_check():
    logger.info("Health check called.")
    return {"status": "ok", "message": "SAK-AgriPolicies API is running."}