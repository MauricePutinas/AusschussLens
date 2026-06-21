"""8D-Report: erzeugen, abrufen, als PDF exportieren."""
from fastapi import APIRouter, HTTPException, Response

from ..db import get_conn
from .. import repository as repo
from ..services import eightd
from ..services.pdf import render_report_pdf

router = APIRouter(prefix="/api/events", tags=["8d-report"])


@router.post("/{event_id}/report")
def generate_report(event_id: int) -> dict:
    conn = get_conn()
    try:
        if not repo.get_event(conn, event_id):
            raise HTTPException(404, "Event nicht gefunden.")
        return eightd.create_or_update_report(conn, event_id)
    finally:
        conn.close()


@router.get("/{event_id}/report")
def get_report(event_id: int) -> dict:
    conn = get_conn()
    try:
        report = repo.get_report_by_event(conn, event_id)
        if not report:
            raise HTTPException(404, "Noch kein 8D-Report fuer dieses Event.")
        return report
    finally:
        conn.close()


@router.get("/{event_id}/report/pdf")
def report_pdf(event_id: int) -> Response:
    conn = get_conn()
    try:
        event = repo.get_event(conn, event_id)
        if not event:
            raise HTTPException(404, "Event nicht gefunden.")
        report = repo.get_report_by_event(conn, event_id)
        if not report:
            raise HTTPException(404, "Noch kein 8D-Report - bitte zuerst generieren.")
        pdf_bytes = render_report_pdf(event, report)
        filename = f"{report['report_no']}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    finally:
        conn.close()
