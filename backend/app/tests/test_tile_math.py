import math

import pytest

from app.engines.tile_math import layout_preview, tile_count


def test_guest_room_600_waste8():
    r = tile_count(6.0, 4.5, 0.6, 0.6, 8.0)
    assert r["area_m2"] == 27.0
    assert r["raw_count"] == 75
    assert r["order_count"] == 81
    assert r["layout"]["cols"] == 10
    assert r["layout"]["rows"] == 8
    assert r["layout"]["grid_count"] == 80


def test_layout_preview_small_room():
    lp = layout_preview(2.5, 2.0, 0.6, 0.6)
    assert lp["cols"] == 5
    assert lp["rows"] == 4
    assert lp["grid_count"] == 20


def test_zero_waste():
    r = tile_count(3.0, 3.0, 1.0, 1.0, 0.0)
    assert r["raw_count"] == 9
    assert r["order_count"] == 9


def test_deduct_default_matches_legacy():
    legacy = tile_count(6.0, 4.5, 0.6, 0.6, 8.0)
    explicit_zero = tile_count(6.0, 4.5, 0.6, 0.6, 8.0, deduct_area=0.0)
    assert legacy == explicit_zero
    assert explicit_zero["deduct_m2"] == 0.0
    assert explicit_zero["net_area_m2"] == explicit_zero["area_m2"]


def test_deduct_piers_net_area():
    # 27 m² gross - (0.5*0.5 + 0.4*0.3) = 26.63 m² net
    r = tile_count(6.0, 4.5, 0.6, 0.6, 8.0, deduct_area=0.25 + 0.12)
    assert r["area_m2"] == 27.0
    assert r["deduct_m2"] == 0.37
    assert r["net_area_m2"] == 26.63
    assert r["raw_count"] == math.ceil(26.63 / 0.36)  # 74
    assert r["order_count"] == math.ceil(74 * 1.08)  # 80


def test_deduct_equal_or_above_gross_fails():
    with pytest.raises(ValueError):
        tile_count(6.0, 4.5, 0.6, 0.6, 8.0, deduct_area=27.0)
    with pytest.raises(ValueError):
        tile_count(6.0, 4.5, 0.6, 0.6, 8.0, deduct_area=30.0)


def test_invalid_deduct_fails():
    with pytest.raises(ValueError):
        tile_count(6.0, 4.5, 0.6, 0.6, 8.0, deduct_area=-0.5)
    with pytest.raises(ValueError):
        tile_count(6.0, 4.5, 0.6, 0.6, 8.0, deduct_area=float("nan"))
