from pydantic import BaseModel, Field


class EstimateRequest(BaseModel):
    room_id: int
    tile_id: int
    waste_pct: float | None = None
    save: bool = False
    note: str = ""


class EstimateResponse(BaseModel):
    room_id: int
    tile_id: int
    room_name: str
    tile_name: str
    area_m2: float
    deduct_m2: float = 0.0
    net_area_m2: float | None = None
    piece_m2: float
    raw_count: int
    waste_pct: float
    order_count: int
    layout: dict
    run_id: int | None = None
