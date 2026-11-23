import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_list_update_profile_and_version() -> None:
    payload = {
        "name": f"Profile-{uuid.uuid4()}",
        "device_type": "MOSFET",
        "description": "Illustrative test profile",
        "is_active": True,
        "created_by": "Test Operator",
        "parameters": [
            {
                "parameter_name": "VGS Threshold",
                "unit": "V",
                "lower_limit": 1.5,
                "upper_limit": 4.5,
                "nominal_value": 3.0,
                "tolerance": 0.5,
                "required": True,
                "evaluation_method": "RANGE",
            }
        ],
    }

    create_response = client.post("/api/v1/profiles", json=payload)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["version"] == 1
    assert created["device_type"] == "MOSFET"
    assert created["parameters"][0]["unit"] == "V"

    update_response = client.put(
        f"/api/v1/profiles/{created['id']}",
        json={"is_active": False, "description": "Updated profile"},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["version"] == 2
    assert updated["is_active"] is False

    detail_response = client.get(f"/api/v1/profiles/{created['id']}")
    assert detail_response.status_code == 200


def test_profile_rejects_invalid_limits() -> None:
    payload = {
        "name": f"Invalid-{uuid.uuid4()}",
        "device_type": "Diode",
        "parameters": [
            {
                "parameter_name": "Forward Voltage",
                "unit": "V",
                "lower_limit": 2.0,
                "upper_limit": 1.0,
                "required": True,
            }
        ],
    }

    response = client.post("/api/v1/profiles", json=payload)
    assert response.status_code == 422


def test_profile_filter_and_missing_profile() -> None:
    response = client.get("/api/v1/profiles", params={"device_type": "MOSFET"})
    assert response.status_code == 200
    assert all(profile["device_type"] == "MOSFET" for profile in response.json())
    assert client.get("/api/v1/profiles/missing-profile").status_code == 404
