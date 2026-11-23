from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.analytics_service import (
    get_device_statistics,
    get_failures,
    get_summary,
    get_trends,
)


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
async def analytics_summary(db: Session = Depends(get_db)) -> dict:
    return get_summary(db)


@router.get("/trends")
async def analytics_trends(db: Session = Depends(get_db)) -> list[dict]:
    return get_trends(db)


@router.get("/failures")
async def analytics_failures(db: Session = Depends(get_db)) -> list[dict]:
    return get_failures(db)


@router.get("/devices")
async def analytics_devices(db: Session = Depends(get_db)) -> list[dict]:
    return get_device_statistics(db)
