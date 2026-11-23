import json
import time
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database.models.device import Device
from app.database.models.profile import TestProfile
from app.database.models.test_execution import MeasurementResult, TestExecution
from app.instruments import InstrumentConfiguration, MeasurementDefinition, SimulatedInstrument
from app.schemas.test_execution import TestExecuteRequest
from app.test_engine.evaluator import calculate_overall_status, evaluate_measurement


class TestExecutionInputError(Exception):
    pass


class TestExecutionNotFoundError(Exception):
    pass


def execute_test(db: Session, payload: TestExecuteRequest) -> tuple[TestExecution, list[MeasurementResult]]:
    device = db.get(Device, payload.device_id)
    if not device:
        raise TestExecutionInputError("Device not found")

    profile = db.scalar(
        select(TestProfile)
        .options(selectinload(TestProfile.parameters))
        .where(TestProfile.id == payload.profile_id)
    )
    if not profile:
        raise TestExecutionInputError("Test profile not found")
    if not profile.is_active:
        raise TestExecutionInputError("Test profile is disabled")
    if profile.device_type != device.device_type:
        raise TestExecutionInputError("Test profile is not valid for this device type")

    started = datetime.now(timezone.utc)
    started_mono = time.monotonic()
    instrument = SimulatedInstrument()
    definitions = [
        MeasurementDefinition(
            parameter_name=parameter.parameter_name,
            unit=parameter.unit,
            lower_limit=parameter.lower_limit,
            upper_limit=parameter.upper_limit,
            nominal_value=parameter.nominal_value,
            tolerance=parameter.tolerance,
        )
        for parameter in profile.parameters
    ]
    readings = instrument.generate(
        definitions,
        InstrumentConfiguration(
            scenario=payload.scenario,
            random_seed=payload.random_seed,
            noise_level=0.02,
            variation_percentage=0.05,
            number_of_measurements=1,
            delay_ms=0,
        ),
    )

    parameter_by_name = {
        parameter.parameter_name: parameter
        for parameter in profile.parameters
    }
    measurement_statuses = [
        evaluate_measurement(
            reading.value,
            reading.lower_limit,
            reading.upper_limit,
            parameter_by_name[reading.parameter_name].required,
        )
        for reading in readings
    ]
    overall_status = calculate_overall_status(measurement_statuses)
    completed = datetime.now(timezone.utc)
    duration_ms = max(1, int((time.monotonic() - started_mono) * 1000))

    execution = TestExecution(
        device_id=device.id,
        device_part_number=device.part_number,
        device_category=device.device_type,
        profile_id=profile.id,
        profile_version=profile.version,
        scenario=payload.scenario,
        simulation_mode="SIMULATION_ONLY",
        simulator_version=instrument.simulator_version,
        random_seed=payload.random_seed,
        operator=payload.operator,
        overall_status=overall_status,
        execution_started_at=started,
        execution_completed_at=completed,
        duration_ms=duration_ms,
        test_notes=payload.test_notes,
    )

    try:
        db.add(execution)
        db.flush()
        results = []
        for reading, status in zip(readings, measurement_statuses):
            result = MeasurementResult(
                test_execution_id=execution.id,
                parameter_name=reading.parameter_name,
                measured_value=reading.value,
                unit=reading.unit,
                lower_limit=reading.lower_limit,
                upper_limit=reading.upper_limit,
                status=status,
                measurement_timestamp=reading.measured_at,
                simulation_flag=True,
                test_conditions=json.dumps({
                    "scenario": payload.scenario,
                    "random_seed": payload.random_seed,
                    "simulator_version": instrument.simulator_version,
                }),
            )
            db.add(result)
            results.append(result)
        db.commit()
        db.refresh(execution)
        for result in results:
            db.refresh(result)
        return execution, results
    except Exception:
        db.rollback()
        raise


def list_executions(db: Session) -> list[TestExecution]:
    return list(db.scalars(select(TestExecution).order_by(TestExecution.created_at.desc())).all())


def get_execution(db: Session, execution_id: str) -> TestExecution:
    execution = db.get(TestExecution, execution_id)
    if not execution:
        raise TestExecutionNotFoundError("Test execution not found")
    return execution


def get_measurements(db: Session, execution_id: str) -> list[MeasurementResult]:
    get_execution(db, execution_id)
    statement = (
        select(MeasurementResult)
        .where(MeasurementResult.test_execution_id == execution_id)
        .order_by(MeasurementResult.measurement_timestamp)
    )
    return list(db.scalars(statement).all())
