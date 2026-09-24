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


def list_pillars(room_id: int):
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT * FROM room_pillars WHERE room_id=? ORDER BY id", (room_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_pillar(room_id: int, length: float, width: float) -> dict:
    conn = connect()
    try:
        cur = conn.execute(
            "INSERT INTO room_pillars(room_id, length, width) VALUES (?,?,?)",
            (room_id, float(length), float(width)),
        )
        conn.commit()
        return {
            "id": int(cur.lastrowid),
            "room_id": room_id,
            "length": float(length),
            "width": float(width),
        }
    finally:
        conn.close()


def delete_pillar(room_id: int, pillar_id: int) -> bool:
    conn = connect()
    try:
        cur = conn.execute(
            "DELETE FROM room_pillars WHERE id=? AND room_id=?", (pillar_id, room_id)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
