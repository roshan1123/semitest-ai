from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.profile import (
    TestProfileCreate,
    TestProfileResponse,
    TestProfileUpdate,
)
from app.services.profile_service import (
    ProfileNotFoundError,
    create_profile,
    get_profile,
    list_profiles,
    update_profile,
)


router = APIRouter(prefix="/profiles", tags=["test profiles"])


@router.post("", response_model=TestProfileResponse, status_code=201)
async def register_profile(
    payload: TestProfileCreate,
    db: Session = Depends(get_db),
) -> TestProfileResponse:
    return TestProfileResponse.model_validate(create_profile(db, payload))


@router.get("", response_model=list[TestProfileResponse])
async def profiles(
    device_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[TestProfileResponse]:
    if device_type not in (None, "MOSFET", "Diode"):
        raise HTTPException(status_code=422, detail="device_type must be MOSFET or Diode")
    return [
        TestProfileResponse.model_validate(profile)
        for profile in list_profiles(db, device_type)
    ]


@router.get("/{profile_id}", response_model=TestProfileResponse)
async def profile_details(
    profile_id: str,
    db: Session = Depends(get_db),
) -> TestProfileResponse:
    try:
        return TestProfileResponse.model_validate(get_profile(db, profile_id))
    except ProfileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{profile_id}", response_model=TestProfileResponse)
async def update_profile_details(
    profile_id: str,
    payload: TestProfileUpdate,
    db: Session = Depends(get_db),
) -> TestProfileResponse:
    try:
        return TestProfileResponse.model_validate(update_profile(db, profile_id, payload))
    except ProfileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
