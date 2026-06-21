"""Test-Setup: frische Temp-DB, Mock-Provider, isolierte Uploads."""
import os
import pathlib
import tempfile

_tmp = pathlib.Path(tempfile.gettempdir())
os.environ["LLM_PROVIDER"] = "mock"
os.environ["DB_PATH"] = str(_tmp / "al_test.db")
os.environ["UPLOAD_DIR"] = str(_tmp / "al_test_uploads")

# Frische DB pro Testlauf, damit der Seed deterministisch greift
_db = pathlib.Path(os.environ["DB_PATH"])
if _db.exists():
    _db.unlink()

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
