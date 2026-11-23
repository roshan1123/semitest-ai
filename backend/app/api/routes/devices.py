from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.device import DeviceCreate, DeviceResponse, DeviceUpdate
from app.services.device_service import (
    DeviceConflictError,
    DeviceNotFoundError,
    create_device,
    get_device,
    list_devices,
    update_device,
)


router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def register_device(payload: DeviceCreate, db: Session = Depends(get_db)) -> DeviceResponse:
    try:
        return DeviceResponse.model_validate(create_device(db, payload))
    except DeviceConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("", response_model=list[DeviceResponse])
async def devices(
    search: str | None = Query(default=None, max_length=100),
    device_type: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[DeviceResponse]:
    if device_type not in (None, "MOSFET", "Diode"):
        raise HTTPException(status_code=422, detail="device_type must be MOSFET or Diode")
    return [
        DeviceResponse.model_validate(device)
        for device in list_devices(db, search, device_type, limit, offset)
    ]


@router.get("/{device_id}", response_model=DeviceResponse)
async def device_details(device_id: str, db: Session = Depends(get_db)) -> DeviceResponse:
    try:
        return DeviceResponse.model_validate(get_device(db, device_id))
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device_details(
    device_id: str,
    payload: DeviceUpdate,
    db: Session = Depends(get_db),
) -> DeviceResponse:
    try:
        return DeviceResponse.model_validate(update_device(db, device_id, payload))
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DeviceConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{device_id}/tests")
async def device_test_history(device_id: str, db: Session = Depends(get_db)) -> list[dict]:
    try:
        get_device(db, device_id)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return []
