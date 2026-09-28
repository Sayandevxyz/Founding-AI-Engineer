"""Replicate.AI FastAPI Backend Application."""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Enforce Windows ProactorEventLoop for Playwright Chromium subprocesses
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    try:
        import uvicorn.loops.asyncio
        uvicorn.loops.asyncio.asyncio_setup = lambda use_subprocess=False: asyncio.set_event_loop_policy(
            asyncio.WindowsProactorEventLoopPolicy()
        )
    except Exception:
        pass

# Load .env file if present
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.models.database import init_db
from backend.app.routes import projects, health

# Ensure directories exist
os.makedirs("screenshots", exist_ok=True)
os.makedirs(os.path.join("generated", "projects"), exist_ok=True)
os.makedirs(os.path.join("generated", "snapshots"), exist_ok=True)

# Initialize database
init_db()

app = FastAPI(
    title="Replicate.AI API",
    description="Autonomous Frontend Website Cloning Agent Orchestration Engine",
    version="1.0.0",
)

# CORS middleware for Next.js dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount screenshots directory for visual preview and comparison
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

# Include routers
app.include_router(health.router)
app.include_router(projects.router)


@app.get("/")
async def root():
    return {
        "message": "Replicate.AI Orchestration Backend is running.",
        "docs": "/docs",
        "health": "/api/health"
    }
