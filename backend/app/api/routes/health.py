from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings


router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str
    simulation_mode: str
    timestamp: datetime


class SystemModeResponse(BaseModel):
    simulation_mode: str
    hardware_enabled: bool


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        environment=settings.app_env,
        simulation_mode=settings.simulation_mode,
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/system/mode", response_model=SystemModeResponse)
async def system_mode() -> SystemModeResponse:
    settings = get_settings()
    return SystemModeResponse(
        simulation_mode=settings.simulation_mode,
        hardware_enabled=False,
    )
