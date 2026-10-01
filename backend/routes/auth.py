# Import required modules
import secrets
from fastapi import APIRouter, Request, Response, HTTPException
from getKST import getKST
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import cast
from utils.db import ConnectDB
from utils.security import VerifyPassword

# Define router
router = APIRouter()


# Set BaseModel class
class LoginRequest(BaseModel):
    username: str
    password: str


# Router for login and cookie setting
@router.post("/api/auth/login")
def login(request: LoginRequest, response: Response):
    # Convert KST string to datetime object
    kst_str = getKST()
    kst_datetime = datetime.strptime(kst_str, "%Y-%m-%d %H:%M:%S")

    # Query user data from database
    with ConnectDB() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, password FROM users WHERE username = %s",
                (request.username,),
            )
            user = cast(dict, cursor.fetchone())

            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail="사용자를 찾을 수 없습니다.",
                )

    # Verify password against hashed password
    if not VerifyPassword(user["password"], request.password):
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")

    # Generate session token and calculate expiration time
    session_token = secrets.token_urlsafe(32)
    expires_at = kst_datetime + timedelta(hours=24)

    # Insert session token into database
    with ConnectDB() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO sessions (user_id, session_token, expires_at) VALUES (%s, %s, %s)",
                (user["id"], session_token, expires_at),
            )
        conn.commit()

    # Set session cookie in response
    response.set_cookie(
        key="sessionToken",
        value=session_token,
        max_age=86400,
        path="/",
        httponly=True,
        samesite="lax",
    )

    # Return login success response with user information
    return {
        "success": True,
        "user": {
            "id": user["id"],
            "username": user["username"],
        },
    }


@router.get("/api/auth/check")
def check(request: Request):
    kst_str = getKST()
    KST = datetime.strptime(kst_str, "%Y-%m-%d %H:%M:%S")

    session_token = request.cookies.get("sessionToken")

    if not session_token:
        raise HTTPException(
            status_code=401,
            detail="세션 토큰이 존재하지 않습니다.",
        )

    with ConnectDB() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT user_id, session_token, expires_at FROM sessions WHERE session_token = %s",
                (session_token,),
            )
            session = cast(dict, cursor.fetchone())

            if session is None:
                raise HTTPException(
                    status_code=401,
                    detail="유효하지 않은 세션입니다.",
                )

            user_id = session["user_id"]
            expires_at = session["expires_at"]

            if KST > expires_at:
                raise HTTPException(
                    status_code=401,
                    detail="세션이 만료되었습니다. 다시 로그인해주세요.",
                )

            cursor.execute(
                "SELECT username FROM users WHERE id = %s",
                (user_id,),
            )
            user = cast(dict, cursor.fetchone())

            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail="사용자를 찾을 수 없습니다.",
                )

            username = user["username"]

    return {
        "success": True,
        "user": {
            "id": user_id,
            "username": username,
        },
    }
