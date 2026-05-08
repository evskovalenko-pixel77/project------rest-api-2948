import sqlite3
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, Field
from typing import List, Optional
import jwt
from datetime import date

SECRET_KEY = "mysecret"
ALGORITHM = "HS256"
DATABASE_URL = "tasks.db"

router = APIRouter(prefix="/tasks", tags=["tasks"])

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[date] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    completed: bool = False
    user_id: int

class CompleteRequest(BaseModel):
    completed: bool = True

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        email = payload.get("email")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"user_id": user_id, "email": email}
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            completed BOOLEAN DEFAULT 0,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )"""
    )
    return conn

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO tasks (title, description, due_date, completed, user_id) VALUES (?, ?, ?, ?, ?)",
            (task.title, task.description, task.due_date.isoformat() if task.due_date else None, False, current_user["user_id"])
        )
        conn.commit()
        task_id = cursor.lastrowid
        cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=500, detail="Task creation failed")
        return dict(row)
    finally:
        conn.close()

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    completed: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    try:
        query = "SELECT * FROM tasks WHERE user_id = ?"
        params = [current_user["user_id"]]
        if completed is not None:
            query += " AND completed = ?"
            params.append(completed)
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def mark_complete(
    task_id: int,
    complete_body: CompleteRequest,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    try:
        cursor = conn.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, current_user["user_id"]))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")
        conn.execute("UPDATE tasks SET completed = ? WHERE id = ?", (complete_body.completed, task_id))
        conn.commit()
        cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        return dict(row)
    finally:
        conn.close()

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    try:
        cursor = conn.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, current_user["user_id"]))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Task not found")
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    finally:
        conn.close()
