from app.db import connect


def list_rooms():
    conn = connect()
    try:
        return [dict(r) for r in conn.execute("SELECT * FROM rooms ORDER BY id").fetchall()]
    finally:
        conn.close()


def get_room(room_id: int):
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM rooms WHERE id=?", (room_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_piers(room_id: int):
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT * FROM room_piers WHERE room_id=? ORDER BY id", (room_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_pier(room_id: int, name: str, length: float, width: float) -> int:
    conn = connect()
    try:
        cur = conn.execute(
            "INSERT INTO room_piers(room_id,name,length,width) VALUES (?,?,?,?)",
            (room_id, name, float(length), float(width)),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def delete_pier(room_id: int, pier_id: int) -> bool:
    conn = connect()
    try:
        cur = conn.execute(
            "DELETE FROM room_piers WHERE id=? AND room_id=?", (pier_id, room_id)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def piers_total_area(room_id: int) -> float:
    """Sum of pier footprints (m²) for a room; 0 when none."""
    conn = connect()
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(length*width), 0) AS total FROM room_piers WHERE room_id=?",
            (room_id,),
        ).fetchone()
        return float(row["total"])
    finally:
        conn.close()
