from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from alembic import command
from alembic.config import Config

from app.api.routes.devices import router as devices_router
from app.api.routes.health import router as health_router
from app.api.routes.profiles import router as profiles_router
from app.api.routes.tests import router as tests_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.reports import router as reports_router
from app.api.routes.inspections import router as inspections_router
from app.core.config import get_settings
from app.core.exceptions import (
    http_exception_handler,
    request_validation_exception_handler,
    unexpected_exception_handler,
)
from app.database.database import engine
from app.database.database import SessionLocal
from app.database.models.device import Device
from app.database.models.profile import TestParameter, TestProfile
from app.core.config import PROJECT_ROOT


settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")
    config = Config("backend/alembic.ini")
    config.set_main_option("script_location", str(PROJECT_ROOT / "backend" / "alembic"))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    command.upgrade(config, "head")

    seed_devices = [
        {
            "part_number": "MOS-IRF540N",
            "device_type": "MOSFET",
            "manufacturer": "Illustrative Semiconductor",
            "description": "Sample MOSFET master record",
            "package_type": "TO-220",
            "rated_voltage": 100,
            "rated_current": 33,
        },
        {
            "part_number": "DIODE-1N4148",
            "device_type": "Diode",
            "manufacturer": "Illustrative Semiconductor",
            "description": "Sample switching diode master record",
            "package_type": "DO-35",
            "rated_voltage": 100,
            "rated_current": 0.3,
        },
    ]
    with SessionLocal() as db:
        for seed in seed_devices:
            if db.query(Device).filter(Device.part_number == seed["part_number"]).first() is None:
                db.add(Device(**seed))

        illustrative_profiles = [
            (
                "Illustrative MOSFET Profile",
                "MOSFET",
                "Illustrative limits for prototype simulation only.",
                [
                    ("VGS Threshold", "V", 1.5, 4.5, 3.0, 0.5),
                    ("RDS(on) Estimate", "mOhm", 20.0, 80.0, 45.0, 5.0),
                    ("IDSS", "uA", 0.0, 50.0, 20.0, 5.0),
                ],
            ),
            (
                "Illustrative Diode Profile",
                "Diode",
                "Illustrative limits for prototype simulation only.",
                [
                    ("Forward Voltage", "V", 0.5, 1.2, 0.8, 0.1),
                    ("Reverse Leakage", "uA", 0.0, 10.0, 2.0, 1.0),
                ],
            ),
        ]
        for name, device_type, description, parameters in illustrative_profiles:
            existing = db.query(TestProfile).filter(TestProfile.name == name).first()
            if existing is None:
                profile = TestProfile(
                    name=name,
                    device_type=device_type,
                    description=description,
                    is_active=True,
                    created_by="Administrator",
                    version=1,
                )
                profile.parameters = [
                    TestParameter(
                        parameter_name=parameter_name,
                        unit=unit,
                        lower_limit=lower_limit,
                        upper_limit=upper_limit,
                        nominal_value=nominal_value,
                        tolerance=tolerance,
                        required=True,
                        evaluation_method="RANGE",
                    )
                    for parameter_name, unit, lower_limit, upper_limit, nominal_value, tolerance in parameters
                ]
                db.add(profile)
        db.commit()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="SemiTest AI - simulation-only semiconductor test platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unexpected_exception_handler)

app.include_router(health_router, prefix="/api/v1")
app.include_router(devices_router, prefix="/api/v1")
app.include_router(profiles_router, prefix="/api/v1")
app.include_router(tests_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(inspections_router, prefix="/api/v1")
