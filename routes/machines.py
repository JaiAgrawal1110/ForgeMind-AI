# ============================================================
# machines.py — API endpoints for managing machines
# Base URL: /machines
#
# GET    /machines          → list all machines
# POST   /machines          → add a new machine
# GET    /machines/{id}     → get one machine
# PUT    /machines/{id}     → update a machine
# DELETE /machines/{id}     → delete a machine
# ============================================================

from fastapi import APIRouter, HTTPException
from models.machine import Machine, MachineUpdate, MachineResponse
from app.database import get_db
from app.cache import get_cache
from app.logger import log
from bson import ObjectId          # MongoDB uses ObjectId for _id fields
import json

router = APIRouter()   # This is like a mini FastAPI app — gets mounted in main.py

# Helper: MongoDB stores _id as ObjectId, we need to return it as a string
def format_machine(doc) -> dict:
    doc["id"] = str(doc["_id"])    # Convert ObjectId → string
    del doc["_id"]                 # Remove the original _id
    return doc


# ------------------------------------------------------------
# POST /machines — Create a new machine
# ------------------------------------------------------------
@router.post("/", response_model=MachineResponse)
async def create_machine(machine: Machine):
    """
    Add a new machine to the system.
    Body example:
    {
        "machine_id": "CNC-001",
        "name": "Lathe Machine 1",
        "location": "Floor A"
    }
    """
    db = get_db()

    # Check if machine_id already exists
    existing = await db["machines"].find_one({"machine_id": machine.machine_id})
    if existing:
        raise HTTPException(status_code=400, detail="Machine ID already exists")

    # Insert into MongoDB
    result = await db["machines"].insert_one(machine.model_dump())
    log.info(f"New machine created: {machine.machine_id}")

    # Fetch the newly created doc and return it
    created = await db["machines"].find_one({"_id": result.inserted_id})
    return format_machine(created)


# ------------------------------------------------------------
# GET /machines — List all machines
# ------------------------------------------------------------
@router.get("/")
async def get_all_machines():
    """Returns a list of all registered machines."""
    db = get_db()
    machines = []
    # MongoDB cursor — loop through all documents in the collection
    async for doc in db["machines"].find():
        machines.append(format_machine(doc))
    log.info(f"Fetched {len(machines)} machines")
    return machines


# ------------------------------------------------------------
# GET /machines/{machine_id} — Get one machine (with caching)
# ------------------------------------------------------------
@router.get("/{machine_id}", response_model=MachineResponse)
async def get_machine(machine_id: str):
    """
    Get a single machine by its machine_id (e.g. CNC-001).
    Result is cached in Redis for 30 seconds to avoid DB hits.
    """
    db = get_db()
    cache = get_cache()
    cache_key = f"machine:{machine_id}"

    # Step 1: Check Redis cache first
    cached = await cache.get(cache_key)
    if cached:
        log.info(f"Cache HIT for machine: {machine_id}")
        return json.loads(cached)               # Return instantly from cache

    # Step 2: Cache miss — go to MongoDB
    log.info(f"Cache MISS for machine: {machine_id} — querying DB")
    doc = await db["machines"].find_one({"machine_id": machine_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Machine not found")

    result = format_machine(doc)

    # Step 3: Store in cache for 30 seconds
    await cache.setex(cache_key, 30, json.dumps(result, default=str))

    return result


# ------------------------------------------------------------
# PUT /machines/{machine_id} — Update a machine
# ------------------------------------------------------------
@router.put("/{machine_id}")
async def update_machine(machine_id: str, update: MachineUpdate):
    """
    Update machine fields. Only send the fields you want to change.
    Body example: { "status": "idle" }
    """
    db = get_db()
    cache = get_cache()

    # Only update fields that were actually provided (not None)
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await db["machines"].update_one(
        {"machine_id": machine_id},
        {"$set": update_data}             # $set = MongoDB update operator
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Machine not found")

    # Invalidate cache so next GET fetches fresh data
    await cache.delete(f"machine:{machine_id}")
    log.info(f"Machine updated: {machine_id}")
    return {"message": f"Machine {machine_id} updated"}


# ------------------------------------------------------------
# DELETE /machines/{machine_id} — Delete a machine
# ------------------------------------------------------------
@router.delete("/{machine_id}")
async def delete_machine(machine_id: str):
    """Remove a machine from the system."""
    db = get_db()
    cache = get_cache()

    result = await db["machines"].delete_one({"machine_id": machine_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Machine not found")

    await cache.delete(f"machine:{machine_id}")   # Clear cache
    log.info(f"Machine deleted: {machine_id}")
    return {"message": f"Machine {machine_id} deleted"}
