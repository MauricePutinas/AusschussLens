"""Erfassung und Verwaltung von Ausschuss-Events (inkl. Foto-Upload)."""
import os
import uuid

from fastapi import APIRouter, Form, File, UploadFile, HTTPException

from ..config import UPLOAD_DIR
from ..db import get_conn
from .. import repository as repo

router = APIRouter(prefix="/api/events", tags=["ausschuss"])

_ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


@router.get("")
def list_events() -> list[dict]:
    conn = get_conn()
    try:
        return repo.list_events(conn)
    finally:
        conn.close()


@router.post("")
async def create_event(
    part_no: str = Form(...),
    part_name: str | None = Form(None),
    machine_id: int = Form(...),
    cause_id: int = Form(...),
    quantity: int = Form(1),
    unit_cost: float = Form(0.0),
    note: str | None = Form(None),
    photo: UploadFile | None = File(None),
) -> dict:
    photo_path = None
    if photo is not None and photo.filename:
        ext = os.path.splitext(photo.filename)[1].lower() or ".jpg"
        if ext not in _ALLOWED_EXT:
            raise HTTPException(400, f"Dateityp {ext} nicht erlaubt.")
        fname = f"{uuid.uuid4().hex}{ext}"
        (UPLOAD_DIR / fname).write_bytes(await photo.read())
        photo_path = fname

    conn = get_conn()
    try:
        event_id = repo.create_event(
            conn, part_no=part_no, part_name=part_name, machine_id=machine_id,
            cause_id=cause_id, quantity=quantity, unit_cost=unit_cost,
            note=note, photo_path=photo_path)
        return repo.get_event(conn, event_id)
    finally:
        conn.close()


@router.get("/{event_id}")
def get_event(event_id: int) -> dict:
    conn = get_conn()
    try:
        event = repo.get_event(conn, event_id)
        if not event:
            raise HTTPException(404, "Event nicht gefunden.")
        return event
    finally:
        conn.close()


@router.delete("/{event_id}")
def delete_event(event_id: int) -> dict:
    conn = get_conn()
    try:
        if not repo.get_event(conn, event_id):
            raise HTTPException(404, "Event nicht gefunden.")
        repo.delete_event(conn, event_id)
        return {"deleted": event_id}
    finally:
        conn.close()
