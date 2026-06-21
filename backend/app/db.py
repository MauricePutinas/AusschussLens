"""SQLite-Anbindung, Schema und Seed-Daten.

Beim Start wird das Schema angelegt und - falls leer - mit realistischen
Beispieldaten befuellt, damit die Demo sofort einen aussagekraeftigen
Pareto und eine Historie zeigt.
"""
import sqlite3
from datetime import datetime, timedelta

from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS machines (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    code    TEXT NOT NULL,
    name    TEXT NOT NULL,
    area    TEXT
);

CREATE TABLE IF NOT EXISTS causes (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT NOT NULL,
    category TEXT NOT NULL          -- 6M: Maschine/Material/Mensch/Methode/Messung/Mitwelt
);

CREATE TABLE IF NOT EXISTS scrap_events (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    part_no    TEXT NOT NULL,
    part_name  TEXT,
    machine_id INTEGER REFERENCES machines(id),
    cause_id   INTEGER REFERENCES causes(id),
    quantity   INTEGER NOT NULL DEFAULT 1,
    unit_cost  REAL NOT NULL DEFAULT 0,
    total_cost REAL NOT NULL DEFAULT 0,
    photo_path TEXT,
    note       TEXT,
    status     TEXT NOT NULL DEFAULT 'offen'
);

CREATE TABLE IF NOT EXISTS reports (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id   INTEGER NOT NULL REFERENCES scrap_events(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL,
    report_no  TEXT NOT NULL,
    provider   TEXT,
    data_json  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_created ON scrap_events(created_at);
CREATE INDEX IF NOT EXISTS idx_reports_event  ON reports(event_id);
"""

_SEED_MACHINES = [
    ("M01", "Stanzautomat Bruderer", "Stanzerei"),
    ("M04", "Spritzguss Arburg 470", "Spritzguss"),
    ("M07", "CNC-Fraese DMG Mori", "Mechanik"),
    ("M12", "Schweissroboter KUKA", "Schweisserei"),
    ("M15", "Montagelinie 2", "Montage"),
]

_SEED_CAUSES = [
    ("Massabweichung / Toleranz ueberschritten", "Maschine"),  # 1
    ("Grat / Schnittfehler", "Maschine"),                       # 2
    ("Materialfehler Charge", "Material"),                      # 3
    ("Einrichtfehler Ruesten", "Mensch"),                       # 4
    ("Werkzeugverschleiss", "Maschine"),                        # 5
    ("Oberflaechenfehler / Kratzer", "Methode"),                # 6
    ("Lunker / Einfallstelle", "Material"),                     # 7
    ("Schweissnaht poroes", "Maschine"),                        # 8
    ("Falschteil montiert", "Mensch"),                          # 9
    ("Sensor-Fehlmessung", "Messung"),                          # 10
]

# (days_ago, part_no, part_name, machine_id, cause_id, qty, unit_cost, note)
_SEED_EVENTS = [
    (18, "ST-1042", "Kontaktfeder 0,8mm", 1, 5, 120, 4.20, "Grat nimmt gegen Schichtende zu"),
    (16, "ST-1042", "Kontaktfeder 0,8mm", 1, 5, 90, 4.20, "Werkzeug-Standzeit ueberschritten"),
    (14, "ST-2207", "Stanzblech Gehaeuse", 1, 2, 60, 6.50, "Schnittgrat an Kante B"),
    (12, "ST-1042", "Kontaktfeder 0,8mm", 1, 5, 140, 4.20, "erneut Werkzeugverschleiss"),
    (11, "SG-5510", "Abdeckung ABS", 2, 7, 40, 3.10, "Lunker am Anguss"),
    (10, "SG-5510", "Abdeckung ABS", 2, 1, 25, 3.10, "Mass X1 zu gross"),
    (9, "CN-3301", "Lagerbock Alu", 3, 1, 18, 12.80, "Bohrungsabstand ausserhalb Toleranz"),
    (8, "ST-1042", "Kontaktfeder 0,8mm", 1, 5, 110, 4.20, "Standzeit Stempel erreicht"),
    (7, "SW-7720", "Konsole verzinkt", 4, 8, 22, 9.40, "Pore in Naht Pos.3"),
    (6, "CN-3301", "Lagerbock Alu", 3, 6, 12, 12.80, "Kratzer auf Spannflaeche"),
    (5, "MO-9001", "Baugruppe Endmontage", 5, 9, 8, 28.00, "falsche Feder verbaut"),
    (4, "ST-2207", "Stanzblech Gehaeuse", 1, 5, 75, 6.50, "Werkzeugverschleiss Matrize"),
    (3, "SG-5510", "Abdeckung ABS", 2, 7, 30, 3.10, "Einfallstelle sichtbar"),
    (2, "ST-1042", "Kontaktfeder 0,8mm", 1, 5, 130, 4.20, "Standzeit, Nachschliff noetig"),
    (1, "MO-9001", "Baugruppe Endmontage", 5, 10, 5, 28.00, "Sensor meldet i.O. trotz NIO"),
]


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_conn()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        _seed(conn)
    finally:
        conn.close()


def _seed(conn: sqlite3.Connection) -> None:
    if conn.execute("SELECT COUNT(*) AS c FROM machines").fetchone()["c"] > 0:
        return  # bereits befuellt
    conn.executemany("INSERT INTO machines(code, name, area) VALUES (?,?,?)", _SEED_MACHINES)
    conn.executemany("INSERT INTO causes(name, category) VALUES (?,?)", _SEED_CAUSES)
    now = datetime.now()
    rows = []
    for days_ago, part_no, part_name, m_id, c_id, qty, unit_cost, note in _SEED_EVENTS:
        created = (now - timedelta(days=days_ago, hours=2)).isoformat(timespec="seconds")
        rows.append((created, part_no, part_name, m_id, c_id, qty, unit_cost,
                     round(qty * unit_cost, 2), None, note, "offen"))
    conn.executemany(
        """INSERT INTO scrap_events
           (created_at, part_no, part_name, machine_id, cause_id, quantity,
            unit_cost, total_cost, photo_path, note, status)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""", rows)
    conn.commit()
