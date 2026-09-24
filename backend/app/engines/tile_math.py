"""Floor tile order count: area method + optional grid layout preview."""

import math

from app.engines.helpers import ceil_units


def tile_count(
    room_l: float,
    room_w: float,
    tile_l: float,
    tile_w: float,
    waste_pct: float,
    deduct_area: float = 0.0,
) -> dict:
    """
    Net area = room_l * room_w - deduct_area (piers etc.), then area method:
    raw_count: ceil(net_area / tile_piece_area)
    order_count: ceil(raw * (1 + waste_pct/100))

    deduct_area=0 behaves exactly as the pre-pier version.
    """
    gross = float(room_l) * float(room_w)
    piece = float(tile_l) * float(tile_w)
    deduct = float(deduct_area)
    if not math.isfinite(deduct) or deduct < 0:
        raise ValueError("invalid deduct area")
    net = gross - deduct
    if piece <= 0 or gross < 0:
        raise ValueError("invalid dimensions")
    if net <= 0:
        raise ValueError("deduction meets or exceeds gross area")
    raw = ceil_units(net / piece)
    with_waste = ceil_units(raw * (1 + float(waste_pct) / 100.0))
    layout = layout_preview(room_l, room_w, tile_l, tile_w)
    return {
        "area_m2": round(gross, 3),
        "deduct_m2": round(deduct, 3),
        "net_area_m2": round(net, 3),
        "piece_m2": round(piece, 4),
        "raw_count": raw,
        "waste_pct": float(waste_pct),
        "order_count": with_waste,
        "layout": layout,
    }


def layout_preview(room_l: float, room_w: float, tile_l: float, tile_w: float) -> dict:
    """Grid count if tiles are laid on a full rectangular lattice (may exceed area method)."""
    cols = ceil_units(float(room_l) / float(tile_l))
    rows = ceil_units(float(room_w) / float(tile_w))
    grid_count = cols * rows
    return {
        "cols": cols,
        "rows": rows,
        "grid_count": grid_count,
    }
