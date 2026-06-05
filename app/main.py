from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import connect_db, close_db
from app.cache import connect_cache, close_cache
from app.logger import log
from ml.anomaly_model import load_model
from routes import machines, telemetry, alerts, predict, websocket

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info(f"Starting {settings.APP_NAME}...")
    await connect_db()
    await connect_cache()
    load_model()
    log.info("App is ready.")
    yield
    log.info("Shutting down...")
    await close_db()
    await close_cache()

app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time machine monitoring and anomaly detection platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(machines.router,   prefix="/machines",  tags=["Machines"])
app.include_router(telemetry.router,  prefix="/telemetry", tags=["Telemetry"])
app.include_router(alerts.router,     prefix="/alerts",    tags=["Alerts"])
app.include_router(predict.router,    prefix="/predict",   tags=["Prediction"])
app.include_router(websocket.router,  prefix="/ws",        tags=["WebSocket"])

@app.get("/")
async def root():
    return {"status": "running", "app": settings.APP_NAME}