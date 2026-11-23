from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def seed_ids() -> tuple[str, str]:
    devices = client.get("/api/v1/devices").json()
    profiles = client.get("/api/v1/profiles").json()
    device = next(item for item in devices if item["part_number"] == "MOS-IRF540N")
    profile = next(
        item
        for item in profiles
        if item["name"] == "Illustrative MOSFET Profile" and item["is_active"]
    )
    return device["id"], profile["id"]


def test_analytics_empty_or_after_executions() -> None:
    response = client.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    assert set(response.json()) == {
        "total_registered_devices",
        "total_test_executions",
        "pass_count",
        "fail_count",
        "review_count",
        "pass_percentage",
    }

    device_id, profile_id = seed_ids()
    executed = client.post(
        "/api/v1/tests/execute",
        json={
            "device_id": device_id,
            "profile_id": profile_id,
            "scenario": "ABNORMAL",
            "random_seed": 42,
        },
    )
    assert executed.status_code == 200

    summary = client.get("/api/v1/analytics/summary").json()
    assert summary["total_test_executions"] >= 1
    assert summary["fail_count"] >= 1

    trends = client.get("/api/v1/analytics/trends")
    failures = client.get("/api/v1/analytics/failures")
    devices = client.get("/api/v1/analytics/devices")
    assert trends.status_code == 200
    assert failures.status_code == 200
    assert devices.status_code == 200
