from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import sqlite3
import os

app = FastAPI()

DATABASE_FILE = "todo.db"
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@app.on_event("startup")
def startup():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(email: str, db: sqlite3.Connection):
    cursor = db.execute("SELECT * FROM users WHERE email = ?", (email,))
    return cursor.fetchone()

def create_user(email: str, password: str, db: sqlite3.Connection):
    hashed_password = pwd_context.hash(password)
    cursor = db.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, hashed_password))
    db.commit()
    return cursor.lastrowid

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, db: sqlite3.Connection = Depends(get_db)):
    existing_user = get_user_by_email(user.email, db)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user_id = create_user(user.email, user.password, db)
    return {"id": user_id, "message": "User created successfully"}

@app.post("/api/auth/login")
async def login(user: UserLogin, db: sqlite3.Connection = Depends(get_db)):
    db_user = get_user_by_email(user.email, db)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not pwd_context.verify(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": db_user["email"], "id": db_user["id"]})
    return {"access_token": access_token, "token_type": "bearer"}