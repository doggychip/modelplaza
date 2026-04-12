from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from database import engine, Base
from routers import auth, models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Model Plaza API",
    description="Chinese AI Model Hub with On-Chain Provenance",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(models.router)

# Serve local storage files when using local backend
if settings.storage_backend == "local":
    storage_path = Path(settings.local_storage_path)
    storage_path.mkdir(parents=True, exist_ok=True)
    app.mount("/api/v1/files", StaticFiles(directory=str(storage_path)), name="files")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "modelplaza-api"}
