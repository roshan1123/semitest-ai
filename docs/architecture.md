# SemiTest AI Architecture

SemiTest AI uses a React/TypeScript frontend and Python/FastAPI backend. SQLite is the development database.

Responsibilities are separated by API routes, Pydantic schemas, SQLAlchemy models, services, test-engine logic, instrument abstraction, reporting, and image inspection.

The platform is permanently scoped to `SIMULATION_ONLY`. No API or settings path enables physical instrument communication.
