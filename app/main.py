# ============================================================
# main.py — The entry point of the entire FastAPI app
# Everything starts here: routers are registered,
# DB connections are opened, and the server is configured
# ============================================================

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import connect_db, close_db
from app.cache import connect_cache, close_cache
from app.logger import log

# Import all route files (we'll build these in routes/)
from routes import machines, telemetry, alerts, predict, websocket

from ml.anomaly_model import load_model

# Inside lifespan, after connect_cache():

# ------------------------------------------------------------
# Lifespan — runs setup on startup and cleanup on shutdown
# This replaces the old @app.on_event("startup") pattern
# ------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    log.info(f"Starting {settings.APP_NAME}...")
    await connect_db()       # Open MongoDB connection
    await connect_cache()    # Open Redis connection
    load_model()
    log.info("App is ready.")

    yield  # App runs here (handles requests)

    # --- SHUTDOWN ---
    log.info("Shutting down...")
    await close_db()         # Close MongoDB cleanly
    await close_cache()      # Close Redis cleanly

# ------------------------------------------------------------
# Create the FastAPI app
# ------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time machine monitoring and anomaly detection platform",
    version="1.0.0",
    lifespan=lifespan        # Attach our startup/shutdown logic
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "ws://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# Register routers — each file handles a group of endpoints
# prefix="/machines" means all routes in machines.py start with /machines
# ------------------------------------------------------------
app.include_router(machines.router,   prefix="/machines",  tags=["Machines"])
app.include_router(telemetry.router,  prefix="/telemetry", tags=["Telemetry"])
app.include_router(alerts.router,     prefix="/alerts",    tags=["Alerts"])
app.include_router(predict.router,    prefix="/predict",   tags=["Prediction"])
app.include_router(websocket.router,  prefix="/ws",        tags=["WebSocket"])

# ------------------------------------------------------------
# Health check — hit this to verify the app is running
# GET http://localhost:8000/
# ------------------------------------------------------------
@app.get("/")
async def root():
    return {
        "status": "running",
        "app": settings.APP_NAME
    }

# ------------------------------------------------------------
# Run with: uvicorn app.main:app --reload
# --reload means server restarts when you save a file (dev only)
# ------------------------------------------------------------
