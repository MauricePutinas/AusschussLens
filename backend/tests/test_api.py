"""End-to-End-Tests des Kern-Demopfades im Mock-Modus."""


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["llm_provider"] == "mock"


def test_master_data_seeded(client):
    assert len(client.get("/api/machines").json()) >= 5
    assert len(client.get("/api/causes").json()) >= 10


def test_events_seeded(client):
    events = client.get("/api/events").json()
    assert len(events) >= 10
    assert all("photo_url" in e and "machine_name" in e for e in events)


def test_analytics(client):
    a = client.get("/api/analytics").json()
    assert a["total_cost"] > 0
    assert a["by_cause"] and a["by_machine"]
    assert 0 < a["top_cause_share"] <= 100


def test_create_event_and_generate_8d(client):
    new = client.post("/api/events", data={
        "part_no": "TEST-999", "part_name": "Pruefteil",
        "machine_id": 1, "cause_id": 5, "quantity": 50, "unit_cost": 3.0,
        "note": "Werkzeug stumpf",
    })
    assert new.status_code == 200, new.text
    event = new.json()
    assert event["total_cost"] == 150.0
    eid = event["id"]

    rep = client.post(f"/api/events/{eid}/report")
    assert rep.status_code == 200, rep.text
    data = rep.json()["data"]
    for key in ("d1_team", "d2_problem", "d3_sofort", "d4_five_whys",
                "d5_abstell", "d6_wirksamkeit", "d7_praevention", "d8_wuerdigung"):
        assert data.get(key), f"{key} fehlt"
    assert len(data["d4_five_whys"]) == 5
    assert data["report_no"].startswith("8D-")

    pdf = client.get(f"/api/events/{eid}/report/pdf")
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content[:4] == b"%PDF"


def test_delete_event(client):
    new = client.post("/api/events", data={
        "part_no": "DEL-1", "machine_id": 2, "cause_id": 7,
        "quantity": 2, "unit_cost": 1.0,
    })
    eid = new.json()["id"]
    assert client.delete(f"/api/events/{eid}").status_code == 200
    assert client.get(f"/api/events/{eid}").status_code == 404
