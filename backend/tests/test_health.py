from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["simulation_mode"] == "SIMULATION_ONLY"


def test_system_mode_disables_hardware() -> None:
    response = client.get("/api/v1/system/mode")

    assert response.status_code == 200
    assert response.json() == {
        "simulation_mode": "SIMULATION_ONLY",
        "hardware_enabled": False,
    }


def test_missing_endpoint_returns_consistent_error_shape() -> None:
    response = client.get("/api/v1/missing")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "HTTP_ERROR"
    assert response.json()["error"]["path"] == "/api/v1/missing"


def test_hardware_execution_endpoint_is_not_exposed() -> None:
    response = client.post(
        "/api/v1/hardware/execute",
        json={"device_id": "DEVICE-001", "instrument": "UNKNOWN"},
    )

    assert response.status_code == 404
