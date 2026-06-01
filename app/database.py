# ============================================================
# database.py — Connects to MongoDB
# We use Motor, which is an async MongoDB driver
# Async = your app doesn't freeze while waiting for DB replies
# ============================================================

from motor.motor_asyncio import AsyncIOMotorClient  # async MongoDB driver
from app.config import settings
from app.logger import log

# This will hold our DB connection once connected
client = None
db = None

async def connect_db():
    """Called when the app starts — opens the MongoDB connection."""
    global client, db

    log.info("Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    log.info(f"Connected to MongoDB: {settings.MONGO_DB_NAME}")

async def close_db():
    """Called when the app stops — cleanly closes the connection."""
    global client
    if client:
        client.close()
        log.info("MongoDB connection closed.")

def get_db():
    """Returns the database instance. Used in routes to access collections."""
    return db

# Usage in a route:
# db = get_db()
# await db["machines"].find_one({"_id": machine_id})
