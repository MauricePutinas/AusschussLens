"""Orchestrierung der 8D-Erzeugung: Event laden, KI rufen, Report speichern."""
from ..config import UPLOAD_DIR
from .. import repository as repo
from . import llm


def create_or_update_report(conn, event_id: int) -> dict:
    event = repo.get_event(conn, event_id)
    if not event:
        raise ValueError("Event nicht gefunden")

    image_bytes = None
    if event.get("photo_path"):
        path = UPLOAD_DIR / event["photo_path"]
        if path.exists():
            image_bytes = path.read_bytes()

    data, provider = llm.generate_8d(event, image_bytes)

    # Report-Nummer stabil halten, falls regeneriert wird
    existing = repo.get_report_by_event(conn, event_id)
    report_no = existing["report_no"] if existing else repo.next_report_no(conn)
    data["report_no"] = report_no

    repo.save_report(conn, event_id, report_no, provider, data)
    repo.set_event_status(conn, event_id, "8d_erstellt")
    return repo.get_report_by_event(conn, event_id)
