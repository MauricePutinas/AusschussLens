"""Datenzugriff (reines SQLite, keine ORM-Magie - bewusst transparent)."""
import json
import sqlite3
from datetime import datetime

_EVENT_SELECT = """
SELECT e.*,
       m.name AS machine_name, m.code AS machine_code, m.area AS machine_area,
       c.name AS cause_name, c.category AS cause_category,
       (SELECT COUNT(*) FROM reports r WHERE r.event_id = e.id) AS report_count
FROM scrap_events e
LEFT JOIN machines m ON e.machine_id = m.id
LEFT JOIN causes   c ON e.cause_id   = c.id
"""


def _event_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["photo_url"] = f"/uploads/{d['photo_path']}" if d.get("photo_path") else None
    d["has_report"] = bool(d.pop("report_count", 0))
    return d


# ---------- Stammdaten ----------
def list_machines(conn) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT * FROM machines ORDER BY code")]


def list_causes(conn) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT * FROM causes ORDER BY category, name")]


# ---------- Ausschuss-Events ----------
def create_event(conn, *, part_no, part_name, machine_id, cause_id,
                 quantity, unit_cost, note, photo_path) -> int:
    total = round((quantity or 0) * (unit_cost or 0), 2)
    cur = conn.execute(
        """INSERT INTO scrap_events
           (created_at, part_no, part_name, machine_id, cause_id, quantity,
            unit_cost, total_cost, photo_path, note, status)
           VALUES (?,?,?,?,?,?,?,?,?,?, 'offen')""",
        (datetime.now().isoformat(timespec="seconds"), part_no, part_name,
         machine_id, cause_id, quantity, unit_cost, total, photo_path, note))
    conn.commit()
    return cur.lastrowid


def list_events(conn) -> list[dict]:
    rows = conn.execute(_EVENT_SELECT + " ORDER BY e.created_at DESC, e.id DESC")
    return [_event_dict(r) for r in rows]


def get_event(conn, event_id: int) -> dict | None:
    row = conn.execute(_EVENT_SELECT + " WHERE e.id = ?", (event_id,)).fetchone()
    return _event_dict(row) if row else None


def delete_event(conn, event_id: int) -> None:
    conn.execute("DELETE FROM reports WHERE event_id = ?", (event_id,))
    conn.execute("DELETE FROM scrap_events WHERE id = ?", (event_id,))
    conn.commit()


def set_event_status(conn, event_id: int, status: str) -> None:
    conn.execute("UPDATE scrap_events SET status = ? WHERE id = ?", (status, event_id))
    conn.commit()


# ---------- 8D-Reports ----------
def next_report_no(conn) -> str:
    n = conn.execute("SELECT COUNT(*) AS c FROM reports").fetchone()["c"] + 1
    return f"8D-{datetime.now().year}-{n:04d}"


def save_report(conn, event_id: int, report_no: str, provider: str, data: dict) -> int:
    conn.execute("DELETE FROM reports WHERE event_id = ?", (event_id,))  # upsert pro Event
    cur = conn.execute(
        """INSERT INTO reports(event_id, created_at, report_no, provider, data_json)
           VALUES (?,?,?,?,?)""",
        (event_id, datetime.now().isoformat(timespec="seconds"), report_no, provider,
         json.dumps(data, ensure_ascii=False)))
    conn.commit()
    return cur.lastrowid


def _report_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["data"] = json.loads(d.pop("data_json"))
    return d


def get_report_by_event(conn, event_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM reports WHERE event_id = ?", (event_id,)).fetchone()
    return _report_dict(row) if row else None


def get_report(conn, report_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    return _report_dict(row) if row else None


# ---------- Analytics (Pareto / Kosten) ----------
def analytics(conn) -> dict:
    totals = conn.execute(
        """SELECT COALESCE(SUM(total_cost),0) AS cost,
                  COALESCE(SUM(quantity),0)   AS qty,
                  COUNT(*)                    AS events,
                  SUM(CASE WHEN status='offen' THEN 1 ELSE 0 END) AS open_count
           FROM scrap_events""").fetchone()

    by_cause = [dict(r) for r in conn.execute(
        """SELECT c.name AS name, c.category AS category,
                  ROUND(SUM(e.total_cost),2) AS cost, SUM(e.quantity) AS qty, COUNT(*) AS events
           FROM scrap_events e LEFT JOIN causes c ON e.cause_id = c.id
           GROUP BY e.cause_id ORDER BY cost DESC""")]

    by_machine = [dict(r) for r in conn.execute(
        """SELECT m.code AS code, m.name AS name,
                  ROUND(SUM(e.total_cost),2) AS cost, SUM(e.quantity) AS qty, COUNT(*) AS events
           FROM scrap_events e LEFT JOIN machines m ON e.machine_id = m.id
           GROUP BY e.machine_id ORDER BY cost DESC""")]

    total_cost = totals["cost"] or 0
    top_cause = by_cause[0] if by_cause else None
    top_machine = by_machine[0] if by_machine else None
    return {
        "total_cost": round(total_cost, 2),
        "total_qty": totals["qty"] or 0,
        "event_count": totals["events"] or 0,
        "open_count": totals["open_count"] or 0,
        "by_cause": by_cause,
        "by_machine": by_machine,
        "top_cause": top_cause,
        "top_machine": top_machine,
        "top_cause_share": round((top_cause["cost"] / total_cost * 100), 1) if top_cause and total_cost else 0,
        "top_machine_share": round((top_machine["cost"] / total_cost * 100), 1) if top_machine and total_cost else 0,
    }
