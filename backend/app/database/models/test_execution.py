import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TestExecution(Base):
    __tablename__ = "test_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id: Mapped[str] = mapped_column(String(36), ForeignKey("devices.id"), nullable=False, index=True)
    device_part_number: Mapped[str] = mapped_column(String(100), nullable=False)
    device_category: Mapped[str] = mapped_column(String(20), nullable=False)
    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_profiles.id"), nullable=False, index=True)
    profile_version: Mapped[int] = mapped_column(Integer, nullable=False)
    scenario: Mapped[str] = mapped_column(String(20), nullable=False)
    simulation_mode: Mapped[str] = mapped_column(String(30), nullable=False, default="SIMULATION_ONLY")
    simulator_version: Mapped[str] = mapped_column(String(50), nullable=False)
    random_seed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    operator: Mapped[str] = mapped_column(String(100), nullable=False)
    overall_status: Mapped[str] = mapped_column(String(20), nullable=False)
    execution_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    execution_completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    test_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class MeasurementResult(Base):
    __tablename__ = "measurement_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_execution_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("test_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parameter_name: Mapped[str] = mapped_column(String(100), nullable=False)
    measured_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    lower_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    upper_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    measurement_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    simulation_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    test_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
