# Todo API

A RESTful API for managing personal todo tasks with JWT authentication.

## Stack
- Python FastAPI
- SQLite (via SQLAlchemy)
- JWT Authentication

## Quick Start

1. Clone the repository
2. Build and run using Docker Compose:

bash
docker-compose up --build


3. API will be available at http://localhost:8000

## API Docs

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

## Endpoints

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get JWT token
- `GET /tasks` - List all tasks for the authenticated user
- `POST /tasks` - Create a new task
- `PUT /tasks/{id}` - Update a task (e.g., mark completed)
- `DELETE /tasks/{id}` - Delete a task