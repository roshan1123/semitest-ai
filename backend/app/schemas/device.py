from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


DeviceType = Literal["MOSFET", "Diode"]
DeviceStatus = Literal["Active", "Inactive"]


class DeviceCreate(BaseModel):
    part_number: str = Field(min_length=1, max_length=100)
    device_type: DeviceType
    manufacturer: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    package_type: str | None = Field(default=None, max_length=50)
    datasheet_reference: str | None = Field(default=None, max_length=255)
    rated_voltage: float | None = Field(default=None, ge=0)
    rated_current: float | None = Field(default=None, ge=0)
    status: DeviceStatus = "Active"


class DeviceUpdate(BaseModel):
    part_number: str | None = Field(default=None, min_length=1, max_length=100)
    device_type: DeviceType | None = None
    manufacturer: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    package_type: str | None = Field(default=None, max_length=50)
    datasheet_reference: str | None = Field(default=None, max_length=255)
    rated_voltage: float | None = Field(default=None, ge=0)
    rated_current: float | None = Field(default=None, ge=0)
    status: DeviceStatus | None = None


class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    part_number: str
    device_type: DeviceType
    manufacturer: str | None
    description: str | None
    package_type: str | None
    datasheet_reference: str | None
    rated_voltage: float | None
    rated_current: float | None
    status: DeviceStatus
    created_at: datetime
    updated_at: datetime
