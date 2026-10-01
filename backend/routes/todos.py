from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import cast
from getKST import getKST
from utils.db import ConnectDB

router = APIRouter()


class RequestCreateTodo(BaseModel):
    text: str


@router.get("/api/todos")
def get_todos(request: Request):
    session_token = request.cookies.get("sessionToken")

    if not session_token:
        raise HTTPException(status_code=401, detail="세션 토큰이 없습니다.")

    with ConnectDB() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT user_id FROM sessions WHERE session_token = %s",
                (session_token,),
            )
            session = cast(dict, cursor.fetchone())

            if session is None:
                raise HTTPException(
                    status_code=401,
                    detail="유효하지 않은 세션입니다.",
                )

            user_id = session["user_id"]

    with ConnectDB() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, text, completed, created_at, updated_at FROM todos WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,),
            )
            todos = cursor.fetchall()

    return {
        "success": True,
        "todos": todos,
    }


@router.post("/api/todos")
def create_todos(request: RequestCreateTodo, http_request: Request):
    session_token = http_request.cookies.get("sessionToken")

    if not session_token:
        raise HTTPException(
            status_code=401,
            detail="세션 토큰이 없습니다.",
        )

    with ConnectDB() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT user_id FROM sessions WHERE session_token = %s",
                (session_token,),
            )
            session = cast(dict, cursor.fetchone())

            if session is None:
                raise HTTPException(status_code=401, detail="유효하지 않은 세션입니다.")

            user_id = session["user_id"]

    KST = getKST()
    with ConnectDB() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO todos (user_id, text, completed, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
                (
                    user_id,
                    request.text,
                    False,
                    KST,
                    KST,
                ),
            )
        conn.commit()

    return {
        "success": True,
        "todo": {
            "text": request.text,
            "completed": False,
            "created_at": KST,
            "updated_at": KST,
        },
    }
