import json
import uuid
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


ALLOWED_TYPES = {"image/jpeg", "image/png"}
UPLOAD_DIR = Path(__file__).resolve().parents[3] / "backend" / "uploads"


class ImageValidationError(Exception):
    pass


def validate_and_save_image(
    filename: str,
    content_type: str,
    content: bytes,
    max_upload_bytes: int,
) -> tuple[Path, str]:
    if content_type not in ALLOWED_TYPES:
        raise ImageValidationError("Only JPEG and PNG images are supported")
    if len(content) > max_upload_bytes:
        raise ImageValidationError(f"Image exceeds the {max_upload_bytes // (1024 * 1024)} MB size limit")

    try:
        image = Image.open(BytesIO(content))
        image.verify()
    except Exception as exc:
        raise ImageValidationError("The uploaded file is not a valid JPEG or PNG image") from exc

    if image.format not in {"JPEG", "PNG"}:
        raise ImageValidationError("Only JPEG and PNG images are supported")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4()}.{image.format.lower()}"
    if image.format == "JPEG":
        safe_name = f"{uuid.uuid4()}.jpg"
    else:
        safe_name = f"{uuid.uuid4()}.png"
    destination = UPLOAD_DIR / safe_name

    with Image.open(BytesIO(content)) as resized:
        resized = resized.convert("RGB")
        resized.thumbnail((1600, 1600))
        resized.save(destination, format="JPEG" if image.format == "JPEG" else "PNG")
    return destination, safe_name


def analyze_image(path: Path) -> tuple[str, float, dict]:
    image = cv2.imread(str(path))
    if image is None:
        raise ImageValidationError("Unable to decode the uploaded image")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = float(np.mean(gray))
    brightness_std = float(np.std(gray))
    laplacian_variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    edges = cv2.Canny(gray, 80, 160)
    edge_density = float(np.count_nonzero(edges) / edges.size)

    if mean_brightness < 20 or mean_brightness > 235 or laplacian_variance < 100:
        result = "PREDICTED_IMAGE_QUALITY_ISSUE"
        confidence = 0.65
    elif edge_density > 0.08:
        result = "PREDICTED_SURFACE_FEATURE"
        confidence = 0.55
    else:
        result = "PREDICTED_NO_OBVIOUS_ANOMALY"
        confidence = 0.50

    metadata = {
        "mean_brightness": round(mean_brightness, 2),
        "brightness_std": round(brightness_std, 2),
        "laplacian_variance": round(laplacian_variance, 2),
        "edge_density": round(edge_density, 4),
        "image_width": int(image.shape[1]),
        "image_height": int(image.shape[0]),
        "prediction_type": "experimental_computer_vision_demonstration",
        "human_review_required": True,
    }
    return result, confidence, metadata
