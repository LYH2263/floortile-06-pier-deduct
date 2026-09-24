import math

from fastapi import APIRouter, HTTPException

from app.repositories import rooms as room_repo
from app.schemas.pillar import PillarIn

router = APIRouter(tags=["rooms"])


@router.get("/rooms")
def list_rooms():
    return {"items": room_repo.list_rooms()}


@router.get("/rooms/{room_id}")
def get_room(room_id: int):
    row = room_repo.get_room(room_id)
    if not row:
        raise HTTPException(404, "room not found")
    pillars = room_repo.list_pillars(room_id)
    gross = row["length"] * row["width"]
    deduct = sum(p["length"] * p["width"] for p in pillars)
    return {
        **row,
        "pillars": pillars,
        "gross_area_m2": round(gross, 3),
        "deduct_area_m2": round(deduct, 3),
        "net_area_m2": round(gross - deduct, 3),
    }


@router.get("/rooms/{room_id}/pillars")
def list_pillars(room_id: int):
    if not room_repo.get_room(room_id):
        raise HTTPException(404, "room not found")
    return {"items": room_repo.list_pillars(room_id)}


@router.post("/rooms/{room_id}/pillars", status_code=201)
def add_pillar(room_id: int, body: PillarIn):
    if not room_repo.get_room(room_id):
        raise HTTPException(404, "room not found")
    sides_ok = all(math.isfinite(v) and v > 0 for v in (body.length, body.width))
    if not sides_ok:
        raise HTTPException(422, "pillar sides must be positive numbers")
    return room_repo.add_pillar(room_id, body.length, body.width)


@router.delete("/rooms/{room_id}/pillars/{pillar_id}")
def delete_pillar(room_id: int, pillar_id: int):
    if not room_repo.delete_pillar(room_id, pillar_id):
        raise HTTPException(404, "pillar not found")
    return {"ok": True}
