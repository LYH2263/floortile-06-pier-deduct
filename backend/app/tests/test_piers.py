"""Pier (柱墩) flow: estimate on net area, persist snapshot, validation failures."""

import pytest
from fastapi import HTTPException

import app.db as db
from app import seed
from app.repositories import history, rooms
from app.routers.rooms import add_pier, delete_pier, get_room
from app.schemas.pier import PierCreate
from app.services import estimate_service


@pytest.fixture()
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    seed.init_db()
    yield


def test_dry_run_returns_net_area_and_counts(fresh_db):
    # 客餐厅 6x4.5, seeded piers 0.5x0.5 + 0.4x0.3 -> deduct 0.37, net 26.63
    res = estimate_service.run_estimate(1, 1, None, False, "")
    assert res["run_id"] is None
    assert res["area_m2"] == 27.0
    assert res["deduct_m2"] == 0.37
    assert res["net_area_m2"] == 26.63
    assert res["raw_count"] == 74
    assert res["order_count"] == 80
    assert history.list_runs() == []  # dry run never persists


def test_no_pier_room_matches_legacy(fresh_db):
    # 狭长走廊 8x1.2, no piers -> same numbers as before the change
    res = estimate_service.run_estimate(2, 2, 8.0, False, "")
    assert res["deduct_m2"] == 0.0
    assert res["net_area_m2"] == 9.6
    assert res["raw_count"] == 15
    assert res["order_count"] == 17


def test_save_persists_snapshot_and_later_pier_delete_keeps_run(fresh_db):
    res = estimate_service.run_estimate(1, 1, None, True, "snapshot")
    run = history.get_run(res["run_id"])
    assert run["result"]["deduct_m2"] == 0.37
    assert run["result"]["net_area_m2"] == 26.63
    assert run["result"]["raw_count"] == 74
    assert run["result"]["order_count"] == 80

    # delete every pier: new estimates fall back to gross area...
    for p in rooms.list_piers(1):
        rooms.delete_pier(1, p["id"])
    res2 = estimate_service.run_estimate(1, 1, None, False, "")
    assert res2["deduct_m2"] == 0.0
    assert res2["net_area_m2"] == 27.0
    assert res2["raw_count"] == 75

    # ...but the stored run keeps its write-time net area
    run_again = history.get_run(res["run_id"])
    assert run_again["result"]["net_area_m2"] == 26.63
    assert run_again["result"]["raw_count"] == 74


def test_invalid_pier_edges_fail_and_not_saved(fresh_db):
    rooms.add_pier(2, "负边", -1.0, 0.5)  # bypasses API validation on purpose
    with pytest.raises(HTTPException) as exc:
        estimate_service.run_estimate(2, 2, None, True, "")
    assert exc.value.status_code == 422
    assert history.list_runs() == []

    rooms.add_pier(2, "零边", 0.0, 1.0)
    with pytest.raises(HTTPException) as exc:
        estimate_service.run_estimate(2, 2, None, True, "")
    assert exc.value.status_code == 422
    assert history.list_runs() == []


def test_deduction_meets_gross_fails_and_not_saved(fresh_db):
    rooms.add_pier(2, "满铺", 8.0, 1.2)  # 9.6 m² == gross
    with pytest.raises(HTTPException) as exc:
        estimate_service.run_estimate(2, 2, None, True, "")
    assert exc.value.status_code == 422
    assert history.list_runs() == []


def test_add_pier_api_validates_edges(fresh_db):
    with pytest.raises(HTTPException) as exc:
        add_pier(2, PierCreate(length=-1.0, width=0.5))
    assert exc.value.status_code == 422
    with pytest.raises(HTTPException) as exc:
        add_pier(2, PierCreate(length=0.0, width=0.5))
    assert exc.value.status_code == 422
    assert rooms.list_piers(2) == []  # nothing persisted


def test_add_pier_api_rejects_deduction_meeting_gross(fresh_db):
    with pytest.raises(HTTPException) as exc:
        add_pier(2, PierCreate(length=8.0, width=1.2))
    assert exc.value.status_code == 422
    assert rooms.list_piers(2) == []


def test_pier_crud_and_room_detail_summary(fresh_db):
    created = add_pier(2, PierCreate(name="门垛", length=0.5, width=0.4))
    assert created["id"] > 0
    detail = get_room(2)
    assert len(detail["piers"]) == 1
    assert detail["gross_area_m2"] == 9.6
    assert detail["deduct_m2"] == 0.2
    assert detail["net_area_m2"] == 9.4

    assert delete_pier(2, created["id"]) == {"ok": True}
    assert get_room(2)["piers"] == []
    with pytest.raises(HTTPException) as exc:
        delete_pier(2, created["id"])
    assert exc.value.status_code == 404
