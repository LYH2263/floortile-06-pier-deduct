"""Room-level helpers: pier edge validation and gross/deduct/net area summary."""

import math


def valid_edge(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v > 0


def pier_summary(room: dict, piers: list[dict]) -> dict:
    gross = float(room["length"]) * float(room["width"])
    deduct = sum(float(p["length"]) * float(p["width"]) for p in piers)
    return {
        "gross_area_m2": round(gross, 3),
        "deduct_m2": round(deduct, 3),
        "net_area_m2": round(gross - deduct, 3),
    }
