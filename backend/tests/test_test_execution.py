from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def find_seed_ids() -> tuple[str, str]:
    devices = client.get("/api/v1/devices").json()
    profiles = client.get("/api/v1/profiles").json()
    mosfet_device = next(device for device in devices if device["device_type"] == "MOSFET")
    mosfet_profile = next(
        profile
        for profile in profiles
        if profile["device_type"] == "MOSFET"
        and profile["name"] == "Illustrative MOSFET Profile"
        and profile["is_active"]
    )
    return mosfet_device["id"], mosfet_profile["id"]


def test_execute_normal_simulated_test_and_persist() -> None:
    device_id, profile_id = find_seed_ids()
    response = client.post(
        "/api/v1/tests/execute",
        json={
            "device_id": device_id,
            "profile_id": profile_id,
            "scenario": "NORMAL",
            "random_seed": 12345,
            "operator": "Test Operator",
        },
    )

    assert response.status_code == 200
    test = response.json()
    assert test["simulation_mode"] == "SIMULATION_ONLY"
    assert test["scenario"] == "NORMAL"
    assert test["overall_status"] in {"PASS", "FAIL", "REVIEW"}
    assert len(test["measurements"]) == 3
    assert all(item["simulation_flag"] is True for item in test["measurements"])

    detail = client.get(f"/api/v1/tests/{test['id']}")
    assert detail.status_code == 200
    measurements = client.get(f"/api/v1/tests/{test['id']}/measurements")
    assert measurements.status_code == 200
    assert len(measurements.json()) == 3


def test_abnormal_and_invalid_scenarios() -> None:
    device_id, profile_id = find_seed_ids()

    abnormal = client.post(
        "/api/v1/tests/execute",
        json={
            "device_id": device_id,
            "profile_id": profile_id,
            "scenario": "ABNORMAL",
            "random_seed": 1,
        },
    )
    assert abnormal.status_code == 200
    assert abnormal.json()["overall_status"] == "FAIL"

    invalid = client.post(
        "/api/v1/tests/execute",
        json={
            "device_id": device_id,
            "profile_id": profile_id,
            "scenario": "INVALID",
            "random_seed": 1,
        },
    )
    assert invalid.status_code == 200
    assert invalid.json()["overall_status"] == "REVIEW"


def test_test_execution_rejects_mismatched_profile_and_missing_record() -> None:
    devices = client.get("/api/v1/devices").json()
    profiles = client.get("/api/v1/profiles").json()
    mosfet = next(device for device in devices if device["device_type"] == "MOSFET")
    diode_profile = next(
        profile
        for profile in profiles
        if profile["device_type"] == "Diode"
        and profile["name"] == "Illustrative Diode Profile"
        and profile["is_active"]
    )

    mismatch = client.post(
        "/api/v1/tests/execute",
        json={"device_id": mosfet["id"], "profile_id": diode_profile["id"]},
    )
    assert mismatch.status_code == 422
    assert client.get("/api/v1/tests/missing-test").status_code == 404
