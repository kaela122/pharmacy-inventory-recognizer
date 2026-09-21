"""FastAPI application entry point.

Run:
    cd backend
    uvicorn app.main:app --reload
Then open http://localhost:8000/docs

The database is SQLite (pharmahub.db) and is created + seeded automatically
on first startup, so there is nothing to install or configure.
"""
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api_router
from app.core.config import get_settings
from app.db.seed import seed

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed()          # create tables + demo data on first run
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/")
def root():
    return {"app": settings.app_name, "docs": "/docs", "api": settings.api_prefix}
