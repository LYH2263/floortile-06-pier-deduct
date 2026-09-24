from fastapi import HTTPException

from app.engines.tile_math import tile_count
from app.repositories import history, rooms, settings_repo, tiles
from app.services.room_service import valid_edge


def run_estimate(room_id: int, tile_id: int, waste_pct: float | None, save: bool, note: str):
    room = rooms.get_room(room_id)
    if not room:
        raise HTTPException(404, "room not found")
    tile = tiles.get_tile(tile_id)
    if not tile:
        raise HTTPException(404, "tile not found")
    if room.get("data_quality") == "dirty":
        raise HTTPException(422, "room marked dirty; fix dimensions before estimate")

    piers = rooms.list_piers(room_id)
    for p in piers:
        if not (valid_edge(p["length"]) and valid_edge(p["width"])):
            raise HTTPException(422, f"pier #{p['id']} has invalid edges; fix before estimate")
    deduct = sum(float(p["length"]) * float(p["width"]) for p in piers)

    gross = float(room["length"]) * float(room["width"])
    if deduct >= gross:
        raise HTTPException(422, "pier deduction meets or exceeds gross room area")

    waste = float(waste_pct) if waste_pct is not None else settings_repo.get_waste_pct()
    try:
        calc = tile_count(
            room["length"], room["width"], tile["tile_l"], tile["tile_w"], waste,
            deduct_area=deduct,
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc))

    run_id = None
    if save:
        payload = {**calc, "room_id": room_id, "tile_id": tile_id}
        run_id = history.insert_run(room_id, tile_id, waste, payload, note)

    return {
        "room_id": room_id,
        "tile_id": tile_id,
        "room": room,
        "tile": tile,
        "piers": piers,
        "run_id": run_id,
        **calc,
    }
