import json

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.models.inspection import InspectionResult
from app.inspection.image_service import (
    analyze_image,
    validate_and_save_image,
)


class InspectionNotFoundError(Exception):
    pass


def create_inspection(
    db: Session,
    upload: UploadFile,
    device_id: str | None,
) -> InspectionResult:
    content = upload.file.read()
    max_upload_bytes = get_settings().max_upload_bytes
    path, safe_name = validate_and_save_image(
        upload.filename or "upload",
        upload.content_type or "",
        content,
        max_upload_bytes,
    )
    try:
        result, confidence, metadata = analyze_image(path)
        inspection = InspectionResult(
            device_id=device_id,
            image_filename=safe_name,
            image_path=str(path),
            inspection_type="CV_DEMONSTRATION",
            result=result,
            confidence=confidence,
            analysis_metadata=json.dumps(metadata),
            human_review_status="PENDING",
        )
        db.add(inspection)
        db.commit()
        db.refresh(inspection)
        return inspection
    except Exception:
        if path.exists():
            path.unlink()
        db.rollback()
        raise


def get_inspection(db: Session, inspection_id: str) -> InspectionResult:
    inspection = db.get(InspectionResult, inspection_id)
    if not inspection:
        raise InspectionNotFoundError("Inspection result not found")
    return inspection
