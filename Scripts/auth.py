import os
import sqlite3
import secrets
import time
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get(
    "DB_PATH",
    str(BASE_DIR.parent / "Database" / "trafficIQ_users.db")
))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

JWT_SECRET = os.environ.get("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
TOKEN_TTL_MIN = 60

_login_attempts: dict = defaultdict(list)
RATE_WINDOW = 15 * 60
RATE_MAX    = 5


def _check_rate_limit(ip: str) -> None:
    now  = time.monotonic()
    keep = [t for t in _login_attempts[ip] if t > now - RATE_WINDOW]
    _login_attempts[ip] = keep
    if len(keep) >= RATE_MAX:
        raise HTTPException(429, "Too many login attempts. Please wait 15 minutes.")
    _login_attempts[ip].append(now)


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER  PRIMARY KEY AUTOINCREMENT,
            username   TEXT     NOT NULL UNIQUE,
            email      TEXT     NOT NULL UNIQUE,
            password   TEXT     NOT NULL,
            role       TEXT     DEFAULT '',
            country    TEXT     DEFAULT '',
            company    TEXT     DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_TTL_MIN),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


# Simple models — NO strict validators so no 422 errors
# Validation is done manually inside the route with friendly error messages
class UserSignup(BaseModel):
    username: str = ""
    email:    str = ""
    password: str = ""
    company:  str = ""
    role:     str = ""
    country:  str = ""


class UserLogin(BaseModel):
    username: str = ""
    password: str = ""


@router.post("/api/signup")
def signup(user: UserSignup) -> JSONResponse:
    # Manual validation with friendly messages
    username = user.username.strip()
    email    = user.email.strip().lower()
    password = user.password

    if len(username) < 3:
        return JSONResponse({"success": False, "message": "Username must be at least 3 characters."}, status_code=400)
    if len(username) > 50:
        return JSONResponse({"success": False, "message": "Username too long."}, status_code=400)
    if "@" not in email or "." not in email.split("@")[-1]:
        return JSONResponse({"success": False, "message": "Invalid email address."}, status_code=400)
    if len(password) < 8:
        return JSONResponse({"success": False, "message": "Password must be at least 8 characters."}, status_code=400)

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username,email,password,company,role,country) VALUES (?,?,?,?,?,?)",
            (username, email, hash_password(password),
             user.company.strip(), user.role.strip(), user.country.strip()),
        )
        conn.commit()
        return JSONResponse({"success": True, "message": f"Welcome to TrafficIQ, {username}!"})

    except sqlite3.IntegrityError as e:
        msg = "Username already taken." if "username" in str(e) else "Email already registered."
        return JSONResponse({"success": False, "message": msg}, status_code=409)
    except Exception as e:
        print(f"[signup error] {e}")
        return JSONResponse({"success": False, "message": "Server error."}, status_code=500)
    finally:
        conn.close()


@router.post("/api/login")
def login(user: UserLogin, request: Request) -> JSONResponse:
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    username = user.username.strip()
    if not username or not user.password:
        return JSONResponse({"success": False, "message": "Username and password are required."}, status_code=400)

    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
    finally:
        conn.close()

    dummy_hash  = bcrypt.hashpw(b"dummy", bcrypt.gensalt()).decode()
    stored_hash = row["password"] if row else dummy_hash
    valid       = verify_password(user.password, stored_hash) and row is not None

    if not valid:
        return JSONResponse(
            {"success": False, "message": "Invalid username or password."},
            status_code=401
        )

    token = create_token(row["username"])
    resp  = JSONResponse({"success": True, "username": row["username"]})
    resp.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=TOKEN_TTL_MIN * 60,
        secure=False,
    )
    return resp


@router.post("/api/logout")
def logout(response: Response) -> JSONResponse:
    response.delete_cookie("session")
    return JSONResponse({"success": True})


@router.get("/api/me")
def me(request: Request) -> JSONResponse:
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    try:
        payload = decode_token(token)
        return JSONResponse({"success": True, "username": payload["sub"]})
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session.")