from fastapi import APIRouter, HTTPException

from app.repositories import rooms as room_repo
from app.schemas.pier import PierCreate
from app.services import room_service

router = APIRouter(tags=["rooms"])


@router.get("/rooms")
def list_rooms():
    return {"items": room_repo.list_rooms()}


@router.get("/rooms/{room_id}")
def get_room(room_id: int):
    row = room_repo.get_room(room_id)
    if not row:
        raise HTTPException(404, "room not found")
    piers = room_repo.list_piers(room_id)
    return {**row, "piers": piers, **room_service.pier_summary(row, piers)}


@router.get("/rooms/{room_id}/piers")
def list_piers(room_id: int):
    room = room_repo.get_room(room_id)
    if not room:
        raise HTTPException(404, "room not found")
    piers = room_repo.list_piers(room_id)
    return {"items": piers, **room_service.pier_summary(room, piers)}


@router.post("/rooms/{room_id}/piers", status_code=201)
def add_pier(room_id: int, body: PierCreate):
    room = room_repo.get_room(room_id)
    if not room:
        raise HTTPException(404, "room not found")
    if not (room_service.valid_edge(body.length) and room_service.valid_edge(body.width)):
        raise HTTPException(422, "pier edges must be positive numbers")
    piers = room_repo.list_piers(room_id)
    new_deduct = sum(float(p["length"]) * float(p["width"]) for p in piers) + body.length * body.width
    gross = float(room["length"]) * float(room["width"])
    if new_deduct >= gross:
        raise HTTPException(422, "pier deduction meets or exceeds gross room area")
    pier_id = room_repo.add_pier(room_id, body.name, body.length, body.width)
    return {"id": pier_id, "room_id": room_id, "name": body.name,
            "length": body.length, "width": body.width}


@router.delete("/rooms/{room_id}/piers/{pier_id}")
def delete_pier(room_id: int, pier_id: int):
    if not room_repo.delete_pier(room_id, pier_id):
        raise HTTPException(404, "pier not found")
    return {"ok": True}
