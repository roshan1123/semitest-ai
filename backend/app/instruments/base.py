from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Literal


Scenario = Literal["NORMAL", "BORDERLINE", "ABNORMAL", "INVALID"]


@dataclass(frozen=True)
class MeasurementDefinition:
    parameter_name: str
    unit: str
    lower_limit: float | None = None
    upper_limit: float | None = None
    nominal_value: float | None = None
    tolerance: float | None = None


@dataclass(frozen=True)
class InstrumentConfiguration:
    scenario: Scenario = "NORMAL"
    random_seed: int | None = None
    noise_level: float = 0.02
    variation_percentage: float = 0.05
    number_of_measurements: int = 1
    delay_ms: int = 0

    def __post_init__(self) -> None:
        if not 0 <= self.noise_level <= 1:
            raise ValueError("noise_level must be between 0 and 1")
        if not 0 <= self.variation_percentage <= 1:
            raise ValueError("variation_percentage must be between 0 and 1")
        if self.number_of_measurements < 1:
            raise ValueError("number_of_measurements must be at least 1")
        if self.delay_ms < 0:
            raise ValueError("delay_ms must not be negative")


@dataclass(frozen=True)
class SimulatedMeasurement:
    parameter_name: str
    value: float | None
    unit: str
    lower_limit: float | None
    upper_limit: float | None
    measured_at: datetime
    simulation: bool
    scenario: Scenario
    metadata: dict[str, str | int | float | bool]


class InstrumentInterface(ABC):
    @abstractmethod
    def generate(
        self,
        definitions: list[MeasurementDefinition],
        configuration: InstrumentConfiguration,
    ) -> list[SimulatedMeasurement]:
        """Generate measurements without evaluating them."""
