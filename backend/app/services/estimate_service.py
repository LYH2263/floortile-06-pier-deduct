import math

from fastapi import HTTPException

from app.engines.tile_math import tile_count
from app.repositories import history, rooms, settings_repo, tiles


def _valid_side(v) -> bool:
    return isinstance(v, (int, float)) and math.isfinite(v) and v > 0


def run_estimate(room_id: int, tile_id: int, waste_pct: float | None, save: bool, note: str):
    room = rooms.get_room(room_id)
    if not room:
        raise HTTPException(404, "room not found")
    tile = tiles.get_tile(tile_id)
    if not tile:
        raise HTTPException(404, "tile not found")
    if room.get("data_quality") == "dirty":
        raise HTTPException(422, "room marked dirty; fix dimensions before estimate")

    pillars = rooms.list_pillars(room_id)
    for p in pillars:
        if not _valid_side(p["length"]) or not _valid_side(p["width"]):
            raise HTTPException(422, f"pillar #{p['id']} has invalid sides; fix or remove it")
    deduct = sum(p["length"] * p["width"] for p in pillars)
    gross = float(room["length"]) * float(room["width"])
    if deduct > 0 and deduct >= gross:
        raise HTTPException(422, "pillar deduction must be smaller than gross area")

    waste = float(waste_pct) if waste_pct is not None else settings_repo.get_waste_pct()
    calc = tile_count(room["length"], room["width"], tile["tile_l"], tile["tile_w"], waste, deduct)

    run_id = None
    if save:
        payload = {**calc, "room_id": room_id, "tile_id": tile_id}
        run_id = history.insert_run(room_id, tile_id, waste, payload, note)

    return {
        "room_id": room_id,
        "tile_id": tile_id,
        "room": room,
        "tile": tile,
        "pillars": pillars,
        "run_id": run_id,
        **calc,
    }
