# Architecture
## Stack: Python FastAPI + SQLite + JWT Authentication
## Modules
- auth: user registration and login, JWT token generation/validation
- tasks: CRUD operations for todo items (create, list, update, delete)
- database: SQLite connection and migrations using Alembic
- tests: unit and integration tests for all endpoints