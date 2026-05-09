from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
import sqlite3
import jwt
import bcrypt
from datetime import datetime, timedelta
import os

DATABASE_NAME = "tasks.db"
SECRET_KEY = os.environ.get("SECRET_KEY", "mysecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()

init_db()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/register", status_code=201)
def register(user: UserRegister):
    conn = get_db()
    try:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (user.email,)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        password_hash = hash_password(user.password)
        cursor = conn.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (user.email, password_hash))
        conn.commit()
        user_id = cursor.lastrowid
        return {"message": "User registered successfully", "user_id": user_id}
    finally:
        conn.close()

@app.post("/login", response_model=Token)
def login(user: UserLogin):
    conn = get_db()
    try:
        db_user = conn.execute("SELECT * FROM users WHERE email = ?", (user.email,)).fetchone()
        if not db_user:
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        if not verify_password(user.password, db_user["password_hash"]):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user["email"], "user_id": db_user["id"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        conn.close()