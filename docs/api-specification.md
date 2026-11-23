# SemiTest AI API Specification

All APIs use `/api/v1`.

- System: health and simulation-mode status
- Devices: create, list, detail, update, and test-history lookup
- Profiles: create, list, detail, and versioned update
- Tests: execute simulated tests and retrieve executions/measurements
- Analytics: summary, trends, failures, and device statistics
- Reports: PDF and CSV downloads
- Inspections: image upload/analyze and inspection detail

Validation failures return HTTP 422 with `error.code = VALIDATION_ERROR`.
Not-found and route errors return JSON `error` objects. Unexpected server errors return HTTP 500 and are logged without exposing internal details.
