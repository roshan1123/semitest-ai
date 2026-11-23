from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


DeviceType = Literal["MOSFET", "Diode"]


class TestParameterBase(BaseModel):
    parameter_name: str = Field(min_length=1, max_length=100)
    unit: str = Field(min_length=1, max_length=30)
    lower_limit: float | None = None
    upper_limit: float | None = None
    nominal_value: float | None = None
    tolerance: float | None = Field(default=None, ge=0)
    required: bool = True
    evaluation_method: Literal["RANGE"] = "RANGE"

    @model_validator(mode="after")
    def validate_limits(self) -> "TestParameterBase":
        if (
            self.lower_limit is not None
            and self.upper_limit is not None
            and self.lower_limit > self.upper_limit
        ):
            raise ValueError("lower_limit must be less than or equal to upper_limit")
        return self


class TestParameterCreate(TestParameterBase):
    pass


class TestParameterResponse(TestParameterBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class TestProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    device_type: DeviceType
    description: str | None = Field(default=None, max_length=2000)
    is_active: bool = True
    created_by: str = Field(default="Administrator", min_length=1, max_length=100)
    parameters: list[TestParameterCreate] = Field(min_length=1)


class TestProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    device_type: DeviceType | None = None
    description: str | None = Field(default=None, max_length=2000)
    is_active: bool | None = None
    parameters: list[TestParameterCreate] | None = None


class TestProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    device_type: DeviceType
    version: int
    description: str | None
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    parameters: list[TestParameterResponse]
