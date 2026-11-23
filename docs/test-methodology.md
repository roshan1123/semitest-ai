# Test Methodology

The simulator supports repeatable random seeds, nominal values, tolerance/variation, noise, and NORMAL, BORDERLINE, ABNORMAL, and INVALID scenarios.

Measurement evaluation is:

- PASS when a non-missing value is inside both configured limits.
- FAIL when a valid value is outside configured limits.
- REVIEW for missing/invalid values or missing acceptance limits.

Overall status is FAIL if any measurement fails, REVIEW if no measurement fails but review is required, and PASS only when every required measurement passes.

Automated validation includes:

- Backend Pytest coverage for devices, profiles, simulator repeatability/scenarios, evaluator rules, persistence, analytics, reports, inspections, and hardware-endpoint rejection.
- Frontend Vitest/React Testing Library coverage for application/dashboard rendering, profile management, test execution/history/report links, and image-inspection disclaimer/controls.
