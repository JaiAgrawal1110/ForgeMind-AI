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
from bson import ObjectId
import json

router = APIRouter()

def format_machine(doc) -> dict:
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


# ------------------------------------------------------------
# GET /machines — List all machines (NO caching — always fresh)
# ------------------------------------------------------------
@router.get("/", response_model=list)
async def get_all_machines():
    """Returns a live list of all registered machines from MongoDB."""
    db = get_db()
    machines = []
    async for doc in db["machines"].find():
        machines.append(format_machine(doc))
    log.info(f"Fetched {len(machines)} machines")
    return machines


# ------------------------------------------------------------
# POST /machines — Create a new machine
# ------------------------------------------------------------
@router.post("/", response_model=MachineResponse)
async def create_machine(machine: Machine):
    db = get_db()
    existing = await db["machines"].find_one({"machine_id": machine.machine_id})
    if existing:
        raise HTTPException(status_code=400, detail="Machine ID already exists")
    result = await db["machines"].insert_one(machine.model_dump())
    log.info(f"New machine created: {machine.machine_id}")
    created = await db["machines"].find_one({"_id": result.inserted_id})
    return format_machine(created)


# ------------------------------------------------------------
# GET /machines/{machine_id} — Get one machine (with caching)
# ------------------------------------------------------------
@router.get("/{machine_id}", response_model=MachineResponse)
async def get_machine(machine_id: str):
    db = get_db()
    cache = get_cache()
    cache_key = f"machine:{machine_id}"

    cached = await cache.get(cache_key)
    if cached:
        log.info(f"Cache HIT for machine: {machine_id}")
        return json.loads(cached)

    log.info(f"Cache MISS for machine: {machine_id} — querying DB")
    doc = await db["machines"].find_one({"machine_id": machine_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Machine not found")

    result = format_machine(doc)
    await cache.setex(cache_key, 30, json.dumps(result, default=str))
    return result


# ------------------------------------------------------------
# PUT /machines/{machine_id} — Update a machine
# ------------------------------------------------------------
@router.put("/{machine_id}")
async def update_machine(machine_id: str, update: MachineUpdate):
    db = get_db()
    cache = get_cache()
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await db["machines"].update_one(
        {"machine_id": machine_id},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Machine not found")
    await cache.delete(f"machine:{machine_id}")
    log.info(f"Machine updated: {machine_id}")
    return {"message": f"Machine {machine_id} updated"}


# ------------------------------------------------------------
# DELETE /machines/{machine_id} — Delete a machine
# ------------------------------------------------------------
@router.delete("/{machine_id}")
async def delete_machine(machine_id: str):
    db = get_db()
    cache = get_cache()
    result = await db["machines"].delete_one({"machine_id": machine_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Machine not found")
    await cache.delete(f"machine:{machine_id}")
    log.info(f"Machine deleted: {machine_id}")
    return {"message": f"Machine {machine_id} deleted"}