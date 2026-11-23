import io

from PIL import Image
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def png_bytes() -> bytes:
    buffer = io.BytesIO()
    image = Image.new("RGB", (64, 64), color=(128, 128, 128))
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_valid_image_analysis_and_persistence() -> None:
    response = client.post(
        "/api/v1/inspections/analyze",
        files={"image": ("sample.png", png_bytes(), "image/png")},
    )

    assert response.status_code == 200
    inspection = response.json()
    assert inspection["inspection_type"] == "CV_DEMONSTRATION"
    assert inspection["result"].startswith("PREDICTED_")
    assert inspection["human_review_status"] == "PENDING"
    assert 0 <= inspection["confidence"] <= 1

    detail = client.get(f"/api/v1/inspections/{inspection['id']}")
    assert detail.status_code == 200


def test_rejects_non_image_file() -> None:
    response = client.post(
        "/api/v1/inspections/analyze",
        files={"image": ("notes.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 422


def test_rejects_invalid_png_content() -> None:
    response = client.post(
        "/api/v1/inspections/analyze",
        files={"image": ("broken.png", b"broken", "image/png")},
    )
    assert response.status_code == 422
