# PRD
## Description
A RESTful API for managing personal todo tasks. Users can register, login, create tasks, mark them as completed, and delete tasks. The API uses Python FastAPI and SQLite database.
## Features
- User registration and authentication (JWT-based)
- Create a new task with title and optional description
- List all tasks for the authenticated user
- Mark a task as completed
- Delete a task
- Task fields: id, title, description, completed (boolean), created_at, updated_at
## Success Criteria
- All API endpoints are functional and return appropriate HTTP status codes
- Authentication protects all task endpoints
- Database migrations are handled (using SQLite)
- API documentation (e.g., Swagger/OpenAPI) is available
- Tests cover critical flows: registration, login, CRUD operations