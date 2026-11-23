from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.inspection.image_service import ImageValidationError
from app.schemas.inspection import InspectionResponse
from app.services.inspection_service import (
    InspectionNotFoundError,
    create_inspection,
    get_inspection,
)


router = APIRouter(prefix="/inspections", tags=["image inspection"])


@router.post("/analyze", response_model=InspectionResponse)
async def analyze(
    image: UploadFile = File(...),
    device_id: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> InspectionResponse:
    try:
        inspection = create_inspection(db, image, device_id)
        return InspectionResponse.model_validate(inspection)
    except ImageValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{inspection_id}", response_model=InspectionResponse)
async def inspection_details(
    inspection_id: str,
    db: Session = Depends(get_db),
) -> InspectionResponse:
    try:
        return InspectionResponse.model_validate(get_inspection(db, inspection_id))
    except InspectionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
