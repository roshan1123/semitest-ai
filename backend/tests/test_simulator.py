import pytest

from app.instruments import (
    InstrumentConfiguration,
    MeasurementDefinition,
    SimulatedInstrument,
)


MOSFET_DEFINITIONS = [
    MeasurementDefinition("VGS Threshold", "V", 1.5, 4.5, 3.0, 0.5),
    MeasurementDefinition("RDS(on) Estimate", "mOhm", 20.0, 80.0, 45.0, 5.0),
    MeasurementDefinition("IDSS", "uA", 0.0, 50.0, 20.0, 5.0),
]


def test_same_seed_and_configuration_are_repeatable() -> None:
    instrument = SimulatedInstrument()
    configuration = InstrumentConfiguration(
        scenario="NORMAL",
        random_seed=12345,
        noise_level=0.02,
        variation_percentage=0.05,
    )

    first = instrument.generate(MOSFET_DEFINITIONS, configuration)
    second = instrument.generate(MOSFET_DEFINITIONS, configuration)

    assert [item.value for item in first] == [item.value for item in second]
    assert all(item.simulation is True for item in first)
    assert all(item.scenario == "NORMAL" for item in first)


def test_different_seeds_can_generate_different_readings() -> None:
    instrument = SimulatedInstrument()
    first = instrument.generate(
        MOSFET_DEFINITIONS,
        InstrumentConfiguration(scenario="NORMAL", random_seed=10),
    )
    second = instrument.generate(
        MOSFET_DEFINITIONS,
        InstrumentConfiguration(scenario="NORMAL", random_seed=999),
    )

    assert [item.value for item in first] != [item.value for item in second]


def test_normal_borderline_abnormal_and_invalid_scenarios() -> None:
    instrument = SimulatedInstrument()

    normal = instrument.generate(
        MOSFET_DEFINITIONS,
        InstrumentConfiguration(scenario="NORMAL", random_seed=42),
    )
    borderline = instrument.generate(
        MOSFET_DEFINITIONS,
        InstrumentConfiguration(scenario="BORDERLINE", random_seed=42),
    )
    abnormal = instrument.generate(
        MOSFET_DEFINITIONS,
        InstrumentConfiguration(scenario="ABNORMAL", random_seed=42),
    )
    invalid = instrument.generate(
        MOSFET_DEFINITIONS,
        InstrumentConfiguration(scenario="INVALID", random_seed=42),
    )

    assert len(normal) == 3
    assert len(borderline) == 3
    assert len(abnormal) == 3
    assert invalid[0].value is None
    assert all(item.value is not None for item in invalid[1:])
    assert any(
        item.value is not None
        and (
            (item.upper_limit is not None and item.value > item.upper_limit)
            or (item.lower_limit is not None and item.value < item.lower_limit)
        )
        for item in abnormal
    )


def test_number_of_measurements_and_metadata() -> None:
    instrument = SimulatedInstrument()
    readings = instrument.generate(
        [
            MeasurementDefinition("Forward Voltage", "V", 0.5, 1.2, 0.8),
            MeasurementDefinition("Reverse Leakage", "uA", 0.0, 10.0, 2.0),
        ],
        InstrumentConfiguration(
            scenario="NORMAL",
            random_seed=7,
            number_of_measurements=2,
        ),
    )

    assert len(readings) == 4
    assert {item.metadata["repetition"] for item in readings} == {1, 2}
    assert all(item.metadata["synthetic"] is True for item in readings)
    assert all(item.parameter_name in {"Forward Voltage", "Reverse Leakage"} for item in readings)


def test_invalid_simulator_configuration_is_rejected() -> None:
    with pytest.raises(ValueError, match="noise_level"):
        InstrumentConfiguration(noise_level=1.5)

    with pytest.raises(ValueError, match="number_of_measurements"):
        InstrumentConfiguration(number_of_measurements=0)
