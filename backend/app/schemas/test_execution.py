from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Scenario = Literal["NORMAL", "BORDERLINE", "ABNORMAL", "INVALID"]
TestStatus = Literal["PASS", "FAIL", "REVIEW"]


class TestExecuteRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=36)
    profile_id: str = Field(min_length=1, max_length=36)
    scenario: Scenario = "NORMAL"
    random_seed: int | None = None
    operator: str = Field(default="Operator", min_length=1, max_length=100)
    test_notes: str | None = Field(default=None, max_length=2000)


class MeasurementResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    test_execution_id: str
    parameter_name: str
    measured_value: float | None
    unit: str
    lower_limit: float | None
    upper_limit: float | None
    status: TestStatus
    measurement_timestamp: datetime
    simulation_flag: bool
    test_conditions: str | None


class TestExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    device_id: str
    device_part_number: str
    device_category: str
    profile_id: str
    profile_version: int
    scenario: str
    simulation_mode: str
    simulator_version: str
    random_seed: int | None
    operator: str
    overall_status: TestStatus
    execution_started_at: datetime
    execution_completed_at: datetime
    duration_ms: int
    test_notes: str | None
    created_at: datetime


class TestExecuteResponse(TestExecutionResponse):
    measurements: list[MeasurementResultResponse]
