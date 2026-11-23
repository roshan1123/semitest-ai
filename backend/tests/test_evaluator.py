from app.test_engine.evaluator import calculate_overall_status, evaluate_measurement


def test_evaluator_pass_fail_review_rules() -> None:
    assert evaluate_measurement(2.5, 1.5, 4.5) == "PASS"
    assert evaluate_measurement(5.0, 1.5, 4.5) == "FAIL"
    assert evaluate_measurement(None, 1.5, 4.5) == "REVIEW"
    assert evaluate_measurement(2.5, None, 4.5) == "REVIEW"
    assert evaluate_measurement(None, None, None) == "REVIEW"
    assert evaluate_measurement(2.5, None, None) == "REVIEW"
    assert calculate_overall_status(["PASS", "PASS"]) == "PASS"
    assert calculate_overall_status(["PASS", "FAIL"]) == "FAIL"
    assert calculate_overall_status(["PASS", "REVIEW"]) == "REVIEW"
    assert calculate_overall_status(["FAIL", "REVIEW"]) == "FAIL"
