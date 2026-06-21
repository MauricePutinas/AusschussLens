"""FastAPI-Einstiegspunkt fuer AusschussLens."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import UPLOAD_DIR, CORS_ORIGINS, LLM_PROVIDER, ANTHROPIC_MODEL
from .db import init_db
from .routers import master, events, reports, analytics


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AusschussLens API",
    version="0.1.0",
    description="Foto + Ursache rein - fertiger 8D/5-Why-Reklamationsreport raus.",
    lifespan=lifespan,
)

_origins = ["*"] if CORS_ORIGINS == "*" else [o.strip() for o in CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.include_router(master.router)
app.include_router(events.router)
app.include_router(reports.router)
app.include_router(analytics.router)


@app.get("/api/health", tags=["meta"])
def health() -> dict:
    return {
        "status": "ok",
        "llm_provider": LLM_PROVIDER,
        "model": ANTHROPIC_MODEL if LLM_PROVIDER == "anthropic" else None,
    }
