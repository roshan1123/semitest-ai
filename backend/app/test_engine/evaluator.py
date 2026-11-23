from typing import Literal


MeasurementStatus = Literal["PASS", "FAIL", "REVIEW"]
OverallStatus = Literal["PASS", "FAIL", "REVIEW"]


def evaluate_measurement(
    measured_value: float | None,
    lower_limit: float | None,
    upper_limit: float | None,
    required: bool = True,
) -> MeasurementStatus:
    if measured_value is None:
        return "REVIEW"
    if not required:
        if lower_limit is None and upper_limit is None:
            return "PASS"
    if lower_limit is None or upper_limit is None:
        return "REVIEW"
    if lower_limit > upper_limit:
        return "REVIEW"
    if measured_value < lower_limit or measured_value > upper_limit:
        return "FAIL"
    return "PASS"


def calculate_overall_status(statuses: list[MeasurementStatus]) -> OverallStatus:
    if "FAIL" in statuses:
        return "FAIL"
    if "REVIEW" in statuses:
        return "REVIEW"
    if statuses and all(status == "PASS" for status in statuses):
        return "PASS"
    return "REVIEW"
