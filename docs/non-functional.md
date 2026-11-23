# Non-Functional Requirements

## Performance

- Use the small demonstration dataset for normal dashboard loads.
- Device APIs support `limit` and `offset` query parameters.
- Test and measurement records are indexed and retrieved by primary key or execution foreign key.
- Image uploads are asynchronous to the UI and show loading/status feedback.

## Reliability

- Test execution and measurement inserts are committed as one SQLAlchemy transaction; exceptions trigger rollback.
- FastAPI logs validation and unhandled application errors.
- SQLite data persists across server restarts.
- Back up development data with:

```bash
cp backend/data/semitest.db "backend/data/semitest-backup-$(date +%Y%m%d-%H%M%S).db"
```

## Security

- Pydantic and route validation cover request inputs.
- Configuration uses environment variables; frontend secrets are not embedded.
- Uploaded images are restricted to valid JPEG/PNG content, a configurable size limit, and generated filenames.
- Upload paths use a fixed server upload directory and do not use the original filename.
- Create/update operations for devices and profiles create audit events.

## Maintainability and Extensibility

- API, service, schema, database, simulator, reporting, and inspection responsibilities remain separated.
- Alembic migrations are used for schema changes.
- The instrument interface provides a simulation-only extension point; no SCPI, USB, serial, or physical-hardware execution is implemented.
