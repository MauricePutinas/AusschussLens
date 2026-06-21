"""Kosten-/Pareto-Analyse ueber alle Ausschuss-Events."""
from fastapi import APIRouter

from ..db import get_conn
from .. import repository as repo

router = APIRouter(prefix="/api", tags=["analyse"])


@router.get("/analytics")
def analytics() -> dict:
    conn = get_conn()
    try:
        return repo.analytics(conn)
    finally:
        conn.close()
