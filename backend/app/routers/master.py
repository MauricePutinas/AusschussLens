"""Stammdaten: Maschinen und Ursachen-Katalog."""
from fastapi import APIRouter

from ..db import get_conn
from .. import repository as repo

router = APIRouter(prefix="/api", tags=["stammdaten"])


@router.get("/machines")
def machines() -> list[dict]:
    conn = get_conn()
    try:
        return repo.list_machines(conn)
    finally:
        conn.close()


@router.get("/causes")
def causes() -> list[dict]:
    conn = get_conn()
    try:
        return repo.list_causes(conn)
    finally:
        conn.close()
