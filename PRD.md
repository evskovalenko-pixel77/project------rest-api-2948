# PRD
## Description
A REST API for managing a personal todo list with user authentication. Users can register, log in, create, read, update (mark as complete), and delete their own tasks. Built with Python FastAPI and SQLite. MVP focuses on core CRUD operations with authentication.
## Features
- User registration and login with JWT-based authentication
- Create a new task with title and optional description
- List all tasks for the authenticated user
- Update a task (mark as completed or modify details)
- Delete a task
- All endpoints return JSON responses
- Passwords hashed for security
- Error handling for invalid requests (e.g., duplicate username, unauthorized access)
## Success Criteria
- Users can register and log in successfully
- Authenticated users can create, view, update, and delete only their own tasks
- Unauthenticated requests are rejected with 401 status
- API responses follow consistent JSON structure
- All core endpoints (register, login, CRUD) are implemented and work correctly