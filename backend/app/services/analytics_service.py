from collections import Counter, defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.device import Device
from app.database.models.test_execution import MeasurementResult, TestExecution


def get_summary(db: Session) -> dict:
    executions = list(db.scalars(select(TestExecution)).all())
    counts = Counter(execution.overall_status for execution in executions)
    total = len(executions)
    pass_count = counts.get("PASS", 0)
    return {
        "total_registered_devices": len(db.scalars(select(Device)).all()),
        "total_test_executions": total,
        "pass_count": pass_count,
        "fail_count": counts.get("FAIL", 0),
        "review_count": counts.get("REVIEW", 0),
        "pass_percentage": round(pass_count / total * 100, 2) if total else 0.0,
    }


def get_trends(db: Session) -> list[dict]:
    executions = list(db.scalars(select(TestExecution).order_by(TestExecution.created_at)).all())
    grouped: Counter[str] = Counter()
    statuses: defaultdict[str, Counter] = defaultdict(Counter)
    for execution in executions:
        date = execution.created_at.strftime("%Y-%m-%d")
        grouped[date] += 1
        statuses[date][execution.overall_status] += 1

    return [
        {
            "date": date,
            "executions": grouped[date],
            "PASS": statuses[date].get("PASS", 0),
            "FAIL": statuses[date].get("FAIL", 0),
            "REVIEW": statuses[date].get("REVIEW", 0),
        }
        for date in sorted(grouped)
    ]


def get_failures(db: Session) -> list[dict]:
    results = list(
        db.scalars(
            select(MeasurementResult).where(MeasurementResult.status == "FAIL")
        ).all()
    )
    failure_counts = Counter(result.parameter_name for result in results)
    total_failures = len(results)
    return [
        {
            "parameter_name": name,
            "failure_count": count,
            "failure_percentage": round(count / total_failures * 100, 2) if total_failures else 0.0,
        }
        for name, count in sorted(
            failure_counts.items(),
            key=lambda item: (-item[1], item[0]),
        )
    ]


def get_device_statistics(db: Session) -> list[dict]:
    executions = list(db.scalars(select(TestExecution)).all())
    grouped: defaultdict[str, Counter] = defaultdict(Counter)
    categories: dict[str, str] = {}
    for execution in executions:
        categories[execution.device_part_number] = execution.device_category
        grouped[execution.device_part_number][execution.overall_status] += 1

    return [
        {
            "device_part_number": part_number,
            "device_category": categories[part_number],
            "total": sum(statuses.values()),
            "PASS": statuses.get("PASS", 0),
            "FAIL": statuses.get("FAIL", 0),
            "REVIEW": statuses.get("REVIEW", 0),
        }
        for part_number, statuses in sorted(grouped.items())
    ]
