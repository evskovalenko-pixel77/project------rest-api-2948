# PRD
## Description
A REST API for managing personal tasks. Users can register, login, create tasks, mark them as completed, and delete tasks. Built with Python FastAPI and SQLite for data persistence. Authentication is JWT-based, and each task is associated with the authenticated user.
## Features
- User registration and authentication (JWT tokens)
- Create a new task (title required; description and due date optional)
- List all tasks for the authenticated user
- Get a specific task's details
- Update a task (mark completed/incomplete, edit fields)
- Delete a task
## Success Criteria
- All API endpoints return correct HTTP status codes (200, 201, 401, 404, etc.)
- Authentication prevents access to tasks of other users
- CRUD operations work correctly under valid conditions and fail gracefully under invalid ones
- SQLite database persists data across restarts
- FastAPI auto-generated documentation (Swagger UI) is available and accurate