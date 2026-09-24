import pytest
from fastapi import HTTPException

from app import seed
from app.engines.tile_math import tile_count
from app.repositories import history
from app.repositories import rooms as room_repo
from app.services import estimate_service


@pytest.fixture
def db(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "test.db")
    seed.init_db()
    return tmp_path / "test.db"


# --- engine: net area after pillar deduction ---

def test_deduct_shrinks_area():
    r = tile_count(6.0, 4.5, 0.6, 0.6, 8.0, deduct_area=3.0)
    assert r["gross_area_m2"] == 27.0
    assert r["deduct_area_m2"] == 3.0
    assert r["area_m2"] == 24.0
    assert r["raw_count"] == 67
    assert r["order_count"] == 73


def test_zero_deduct_matches_no_pillar():
    assert tile_count(6.0, 4.5, 0.6, 0.6, 8.0, 0.0) == tile_count(6.0, 4.5, 0.6, 0.6, 8.0)


def test_deduct_equal_gross_raises():
    with pytest.raises(ValueError):
        tile_count(6.0, 4.5, 0.6, 0.6, 8.0, deduct_area=27.0)


def test_deduct_above_gross_raises():
    with pytest.raises(ValueError):
        tile_count(6.0, 4.5, 0.6, 0.6, 8.0, deduct_area=30.0)


def test_negative_deduct_raises():
    with pytest.raises(ValueError):
        tile_count(6.0, 4.5, 0.6, 0.6, 8.0, deduct_area=-1.0)


# --- service: pillars flow into estimate, failures stay unpersisted ---

def test_estimate_without_pillars_unchanged(db):
    res = estimate_service.run_estimate(1, 1, 8.0, False, "")
    assert res["gross_area_m2"] == 27.0
    assert res["deduct_area_m2"] == 0.0
    assert res["area_m2"] == 27.0
    assert res["raw_count"] == 75
    assert res["order_count"] == 81


def test_estimate_with_pillar_dry_run(db):
    room_repo.add_pillar(1, 1.0, 1.5)
    res = estimate_service.run_estimate(1, 1, 8.0, False, "")
    assert res["deduct_area_m2"] == 1.5
    assert res["area_m2"] == 25.5
    assert res["raw_count"] == 71
    assert res["order_count"] == 77
    assert res["run_id"] is None
    assert history.list_runs() == []


def test_estimate_save_writes_deduct_and_net(db):
    room_repo.add_pillar(1, 1.0, 1.5)
    res = estimate_service.run_estimate(1, 1, 8.0, True, "t")
    run = history.get_run(res["run_id"])
    assert run["result"]["deduct_area_m2"] == 1.5
    assert run["result"]["area_m2"] == 25.5
    assert run["result"]["raw_count"] == 71
    assert run["result"]["order_count"] == 77


def test_deduct_equal_gross_fails_not_saved(db):
    room_repo.add_pillar(1, 6.0, 4.5)
    with pytest.raises(HTTPException):
        estimate_service.run_estimate(1, 1, 8.0, True, "")
    assert history.list_runs() == []


def test_invalid_pillar_side_fails_not_saved(db):
    room_repo.add_pillar(1, -1.0, 2.0)
    with pytest.raises(HTTPException):
        estimate_service.run_estimate(1, 1, 8.0, True, "")
    assert history.list_runs() == []


def test_delete_pillar_keeps_old_run(db):
    pillar = room_repo.add_pillar(1, 1.0, 1.0)
    first = estimate_service.run_estimate(1, 1, 8.0, True, "")
    assert first["area_m2"] == 26.0

    room_repo.delete_pillar(1, pillar["id"])
    second = estimate_service.run_estimate(1, 1, 8.0, True, "")
    assert second["area_m2"] == 27.0

    old = history.get_run(first["run_id"])
    assert old["result"]["area_m2"] == 26.0
    assert old["result"]["deduct_area_m2"] == 1.0
