import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, cleanup_expired_sessions
from app.api.chat import router as chat_router
from app.api.runs import router as runs_router
from app.api.evals import router as evals_router
from app.api.versions import router as versions_router
from app.api.experiments import router as experiments_router
from app.api.dashboard import router as dashboard_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(settings.db_path)
    cleanup_expired_sessions(settings.db_path, settings.session_expiry_days)
    yield


app = FastAPI(
    title="OpenAI Agents Lab API",
    description="Backend API for the OpenAI Agents Lab",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")
app.include_router(runs_router, prefix="/api")
app.include_router(evals_router, prefix="/api")
app.include_router(versions_router, prefix="/api")
app.include_router(experiments_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
