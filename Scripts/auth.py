import os
import secrets
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text

router = APIRouter()

# ── Database ────────────────────────────────────────────────────────────────

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_engine():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable not set.")
    return create_engine(DATABASE_URL)

def init_db() -> None:
    """Create users table in Supabase if it doesn't exist."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id         SERIAL       PRIMARY KEY,
                username   TEXT         NOT NULL UNIQUE,
                email      TEXT         NOT NULL UNIQUE,
                password   TEXT         NOT NULL,
                role       TEXT         DEFAULT '',
                country    TEXT         DEFAULT '',
                company    TEXT         DEFAULT '',
                created_at TIMESTAMPTZ  DEFAULT NOW()
            )
        """))

# ── JWT ─────────────────────────────────────────────────────────────────────

JWT_SECRET    = os.environ.get("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
TOKEN_TTL_MIN = 60

# ── Rate limiting ────────────────────────────────────────────────────────────

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

# ── Password helpers ─────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

# ── Token helpers ─────────────────────────────────────────────────────────────

def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_TTL_MIN),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

# ── Pydantic models ───────────────────────────────────────────────────────────

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

# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/api/signup")
def signup(user: UserSignup) -> JSONResponse:
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

    try:
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(
                text("INSERT INTO users (username, email, password, company, role, country) VALUES (:u, :e, :p, :c, :r, :co)"),
                {"u": username, "e": email, "p": hash_password(password),
                 "c": user.company.strip(), "r": user.role.strip(), "co": user.country.strip()}
            )
        return JSONResponse({"success": True, "message": f"Welcome to TrafficIQ, {username}!"})

    except Exception as e:
        err = str(e).lower()
        if "unique" in err and "username" in err:
            return JSONResponse({"success": False, "message": "Username already taken."}, status_code=409)
        if "unique" in err and "email" in err:
            return JSONResponse({"success": False, "message": "Email already registered."}, status_code=409)
        print(f"[signup error] {e}")
        return JSONResponse({"success": False, "message": "Server error."}, status_code=500)


@router.post("/api/login")
def login(user: UserLogin, request: Request) -> JSONResponse:
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    username = user.username.strip()
    if not username or not user.password:
        return JSONResponse({"success": False, "message": "Username and password are required."}, status_code=400)

    try:
        engine = get_engine()
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT * FROM users WHERE username = :u"),
                {"u": username}
            ).fetchone()
    except Exception as e:
        print(f"[login db error] {e}")
        return JSONResponse({"success": False, "message": "Server error."}, status_code=500)

    dummy_hash  = bcrypt.hashpw(b"dummy", bcrypt.gensalt()).decode()
    stored_hash = row.password if row else dummy_hash
    valid       = verify_password(user.password, stored_hash) and row is not None

    if not valid:
        return JSONResponse(
            {"success": False, "message": "Invalid username or password."},
            status_code=401
        )

    token = create_token(row.username)
    resp  = JSONResponse({"success": True, "username": row.username})
    resp.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=TOKEN_TTL_MIN * 60,
        secure=True,
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