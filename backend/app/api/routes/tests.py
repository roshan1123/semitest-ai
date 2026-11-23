from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.test_execution import (
    MeasurementResultResponse,
    TestExecuteRequest,
    TestExecuteResponse,
    TestExecutionResponse,
)
from app.services.test_service import (
    TestExecutionInputError,
    TestExecutionNotFoundError,
    execute_test,
    get_execution,
    get_measurements,
    list_executions,
)


router = APIRouter(prefix="/tests", tags=["test execution"])


@router.post("/execute", response_model=TestExecuteResponse)
async def execute_simulated_test(
    payload: TestExecuteRequest,
    db: Session = Depends(get_db),
) -> TestExecuteResponse:
    try:
        execution, measurements = execute_test(db, payload)
        return TestExecuteResponse(
            **TestExecutionResponse.model_validate(execution).model_dump(),
            measurements=[
                MeasurementResultResponse.model_validate(measurement)
                for measurement in measurements
            ],
        )
    except TestExecutionInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("", response_model=list[TestExecutionResponse])
async def test_executions(db: Session = Depends(get_db)) -> list[TestExecutionResponse]:
    return [
        TestExecutionResponse.model_validate(execution)
        for execution in list_executions(db)
    ]


@router.get("/{test_id}", response_model=TestExecutionResponse)
async def test_execution_details(
    test_id: str,
    db: Session = Depends(get_db),
) -> TestExecutionResponse:
    try:
        return TestExecutionResponse.model_validate(get_execution(db, test_id))
    except TestExecutionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{test_id}/measurements", response_model=list[MeasurementResultResponse])
async def test_execution_measurements(
    test_id: str,
    db: Session = Depends(get_db),
) -> list[MeasurementResultResponse]:
    try:
        return [
            MeasurementResultResponse.model_validate(measurement)
            for measurement in get_measurements(db, test_id)
        ]
    except TestExecutionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
