"""Repeatable synthetic semiconductor measurement generation.

Values are software-generated distributions for prototype demonstration only.
This module produces raw readings and deliberately does not calculate PASS,
FAIL, or REVIEW statuses.
"""

import random
import time
from datetime import datetime, timezone

from app.instruments.base import (
    InstrumentConfiguration,
    InstrumentInterface,
    MeasurementDefinition,
    SimulatedMeasurement,
)


class SimulatedInstrument(InstrumentInterface):
    simulator_version = "simulation-engine-1.0"

    def generate(
        self,
        definitions: list[MeasurementDefinition],
        configuration: InstrumentConfiguration,
    ) -> list[SimulatedMeasurement]:
        if not definitions:
            raise ValueError("At least one measurement definition is required")

        rng = random.Random(configuration.random_seed)
        if configuration.delay_ms:
            time.sleep(configuration.delay_ms / 1000)

        measurements: list[SimulatedMeasurement] = []
        for repetition in range(configuration.number_of_measurements):
            for index, definition in enumerate(definitions):
                value = self._generate_value(
                    rng=rng,
                    definition=definition,
                    scenario=configuration.scenario,
                    parameter_index=index,
                    repetition=repetition,
                    configuration=configuration,
                )
                if configuration.scenario == "INVALID" and index == 0 and repetition == 0:
                    value = None

                measurements.append(
                    SimulatedMeasurement(
                        parameter_name=definition.parameter_name,
                        value=value,
                        unit=definition.unit,
                        lower_limit=definition.lower_limit,
                        upper_limit=definition.upper_limit,
                        measured_at=datetime.now(timezone.utc),
                        simulation=True,
                        scenario=configuration.scenario,
                        metadata={
                            "simulator_version": self.simulator_version,
                            "random_seed": configuration.random_seed if configuration.random_seed is not None else -1,
                            "noise_level": configuration.noise_level,
                            "variation_percentage": configuration.variation_percentage,
                            "repetition": repetition + 1,
                            "synthetic": True,
                        },
                    )
                )
        return measurements

    def _generate_value(
        self,
        rng: random.Random,
        definition: MeasurementDefinition,
        scenario: str,
        parameter_index: int,
        repetition: int,
        configuration: InstrumentConfiguration,
    ) -> float:
        nominal = self._nominal_value(definition)
        variation = (
            abs(definition.tolerance)
            if definition.tolerance is not None
            else abs(nominal) * configuration.variation_percentage
        )
        noise_scale = abs(nominal) * configuration.noise_level

        if scenario == "ABNORMAL":
            if definition.upper_limit is not None:
                return round(definition.upper_limit + max(abs(definition.upper_limit - nominal), variation) * 0.25 + rng.uniform(0, variation), 6)
            if definition.lower_limit is not None:
                return round(definition.lower_limit - max(abs(nominal - definition.lower_limit), variation) * 0.25 - rng.uniform(0, variation), 6)
            return round(nominal * 2 + rng.gauss(0, noise_scale), 6)

        if scenario == "BORDERLINE":
            if definition.lower_limit is not None and definition.upper_limit is not None:
                boundary = (
                    definition.upper_limit
                    if (parameter_index + repetition) % 2 == 0
                    else definition.lower_limit
                )
                return round(boundary + rng.gauss(0, max(noise_scale, abs(boundary) * 0.005)), 6)
            if definition.upper_limit is not None:
                return round(definition.upper_limit + rng.gauss(0, max(noise_scale, 0.001)), 6)
            if definition.lower_limit is not None:
                return round(definition.lower_limit + rng.gauss(0, max(noise_scale, 0.001)), 6)
            return round(nominal + rng.gauss(0, noise_scale), 6)

        return round(rng.gauss(nominal, max(noise_scale, variation * 0.25)), 6)

    @staticmethod
    def _nominal_value(definition: MeasurementDefinition) -> float:
        if definition.nominal_value is not None:
            return definition.nominal_value
        if definition.lower_limit is not None and definition.upper_limit is not None:
            return (definition.lower_limit + definition.upper_limit) / 2
        if definition.upper_limit is not None:
            return definition.upper_limit
        if definition.lower_limit is not None:
            return definition.lower_limit
        return 0.0
