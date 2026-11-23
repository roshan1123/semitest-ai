import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def unique_part(prefix: str = "TEST") -> str:
    return f"{prefix}-{uuid.uuid4()}"


def test_register_list_update_and_filter_devices() -> None:
    part_number = unique_part("MOS")
    create_response = client.post(
        "/api/v1/devices",
        json={
            "part_number": part_number,
            "device_type": "MOSFET",
            "manufacturer": "Test Manufacturer",
            "package_type": "TO-220",
            "rated_voltage": 60,
            "rated_current": 20,
            "status": "Active",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["part_number"] == part_number
    assert created["device_type"] == "MOSFET"

    list_response = client.get("/api/v1/devices", params={"search": part_number})
    assert list_response.status_code == 200
    assert any(device["id"] == created["id"] for device in list_response.json())

    update_response = client.put(
        f"/api/v1/devices/{created['id']}",
        json={"status": "Inactive", "manufacturer": "Updated Manufacturer"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "Inactive"
    assert update_response.json()["manufacturer"] == "Updated Manufacturer"

    detail_response = client.get(f"/api/v1/devices/{created['id']}")
    assert detail_response.status_code == 200


def test_duplicate_part_number_is_conflict() -> None:
    part_number = unique_part("DUP")
    payload = {
        "part_number": part_number,
        "device_type": "Diode",
        "status": "Active",
    }

    assert client.post("/api/v1/devices", json=payload).status_code == 201
    duplicate = client.post("/api/v1/devices", json=payload)
    assert duplicate.status_code == 409


def test_invalid_device_type_and_missing_device() -> None:
    assert client.get("/api/v1/devices", params={"device_type": "Transistor"}).status_code == 422
    assert client.get("/api/v1/devices/missing-device").status_code == 404
    assert client.get("/api/v1/devices/missing-device/tests").status_code == 404


def test_device_pagination_is_bounded() -> None:
    response = client.get("/api/v1/devices", params={"limit": 1, "offset": 0})

    assert response.status_code == 200
    assert len(response.json()) <= 1

    invalid_limit = client.get("/api/v1/devices", params={"limit": 501})
    assert invalid_limit.status_code == 422
