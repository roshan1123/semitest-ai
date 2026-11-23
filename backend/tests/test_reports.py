from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def execute_seed_test() -> dict:
    devices = client.get("/api/v1/devices").json()
    profiles = client.get("/api/v1/profiles").json()
    device = next(item for item in devices if item["part_number"] == "MOS-IRF540N")
    profile = next(
        item
        for item in profiles
        if item["name"] == "Illustrative MOSFET Profile" and item["is_active"]
    )
    response = client.post(
        "/api/v1/tests/execute",
        json={
            "device_id": device["id"],
            "profile_id": profile["id"],
            "scenario": "NORMAL",
            "random_seed": 123,
        },
    )
    assert response.status_code == 200
    return response.json()


def test_pdf_report_download() -> None:
    test = execute_seed_test()
    response = client.get(f"/api/v1/reports/{test['id']}/pdf")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert "attachment" in response.headers["content-disposition"]


def test_csv_report_download_contains_required_fields() -> None:
    test = execute_seed_test()
    response = client.get(f"/api/v1/reports/{test['id']}/csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    csv_text = response.text
    assert "Test ID" in csv_text
    assert "Measurement Name" in csv_text
    assert "Simulation Flag" in csv_text
    assert "Profile Version" in csv_text


def test_missing_report_returns_not_found() -> None:
    assert client.get("/api/v1/reports/missing/pdf").status_code == 404
    assert client.get("/api/v1/reports/missing/csv").status_code == 404
