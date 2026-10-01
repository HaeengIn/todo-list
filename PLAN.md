# React + Neon PostgreSQL To-Do List 프로젝트 계획

## 1. 프로젝트 개요

React와 Neon PostgreSQL을 이용하여 To-Do List 애플리케이션을 구현합니다. 사용자는 간단한 로그인 시스템을 통해 인증을 수행하며, 로그인 세션은 쿠키에 24시간 동안 저장됩니다. 할 일 데이터는 Neon PostgreSQL 데이터베이스에 저장되어 어디서든 접근할 수 있습니다.

## 2. 핵심 기능

**인증:**

- **로그인**: 간단한 사용자 인증 (username/password)
- **세션 쿠키**: 로그인 세션을 24시간 유지하는 쿠키
- **로그아웃**: 세션 종료

**할 일 관리:**

- **할 일 추가**: 새로운 할 일 항목 추가
- **할 일 조회**: 저장된 모든 할 일 표시
- **할 일 완료 표시**: 각 항목의 완료 상태 토글
- **할 일 수정**: 할 일 텍스트 수정
- **할 일 삭제**: 특정 항목 제거
- **데이터베이스 저장**: 모든 변경사항을 Neon PostgreSQL에 저장

## 3. 기술 스택

- **프론트엔드**: React
- **상태 관리**: React Hooks (useState, useEffect)
- **인증**: 세션 쿠키 (24시간 유지)
- **백엔드**: Python 3.12.1 + FastAPI
- **데이터베이스**: Neon PostgreSQL
- **ORM**: SQLAlchemy 또는 Tortoise ORM
- **API 통신**: Fetch API
- **스타일링**: CSS

## 4. 프로젝트 구조 (모노레포)

```text
todo-app/
├── backend/
│   ├── models/
│   │   ├── user.py          # 사용자 모델
│   │   ├── todo.py          # 할 일 모델
│   │   └── session.py       # 세션 모델
│   ├── routes/
│   │   ├── auth.py          # 인증 라우트 (로그인/로그아웃)
│   │   └── todos.py         # 할 일 CRUD 라우트
│   ├── schemas/
│   │   ├── user.py          # 사용자 Pydantic 스키마
│   │   ├── todo.py          # 할 일 Pydantic 스키마
│   │   └── session.py       # 세션 Pydantic 스키마
│   ├── middleware/
│   │   └── auth.py          # 인증 미들웨어 (세션 검증)
│   ├── utils/
│   │   ├── db.py            # Neon PostgreSQL 연결
│   │   ├── security.py      # 비밀번호 해싱, 토큰 생성
│   │   └── cookies.py       # 쿠키 관련 유틸리티
│   ├── main.py              # FastAPI 앱 초기화 및 라우트 등록
│   ├── requirements.txt     # 패키지 의존성
│   └── .env                 # 환경 변수 (DATABASE_URL 등)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.jsx            # 로그인 페이지
│   │   │   ├── TodoList.jsx         # To-Do List 메인 컴포넌트
│   │   │   ├── TodoItem.jsx         # 각 할 일 항목 컴포넌트
│   │   │   └── TodoForm.jsx         # 할 일 입력 폼 컴포넌트
│   │   ├── hooks/
│   │   │   └── useAuth.js           # 인증 상태 관리 커스텀 훅
│   │   ├── utils/
│   │   │   ├── api.js               # API 요청 함수
│   │   │   └── cookieUtils.js       # 쿠키 읽기/쓰기 유틸리티
│   │   ├── styles/
│   │   │   ├── Login.css            # 로그인 페이지 스타일
│   │   │   └── TodoList.css         # To-Do List 스타일
│   │   ├── pages/
│   │   │   ├── HomePage.jsx         # 홈 페이지 (로그인 후)
│   │   │   └── LoginPage.jsx        # 로그인 페이지
│   │   └── App.jsx                  # 메인 앱 컴포넌트
│   ├── public/
│   ├── package.json
│   └── .env.local                   # 환경 변수 (API 엔드포인트 등)
│
├── .gitignore
├── README.md
└── PLAN.md
```

## 5. 구현 단계

### 5.1 데이터베이스 설정

- **Neon PostgreSQL 가입** 및 데이터베이스 생성
- **연결 정보** 획득 (DATABASE_URL)
- **테이블 생성**:

  ```sql
  CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    text VARCHAR(500) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

### 5.2 백엔드 API 구현 (FastAPI)

**필수 패키지:**

```text
fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-dotenv
passlib
bcrypt
pydantic
```

**인증 API (routes/auth.py):**

```python
POST /api/auth/login
  - Request: {"username": "str", "password": "str"}
  - Response: {"success": true, "user": {"id": int, "username": "str"}}
  - 기능: 사용자 검증, 세션 생성, 쿠키 설정 (Max-Age: 86400초)

POST /api/auth/logout
  - Response: {"success": true}
  - 기능: 세션 삭제, 쿠키 제거

GET /api/auth/check
  - Response: {"success": true, "user": {"id": int, "username": "str"}}
  - 기능: 현재 세션 유효성 확인
```

**할 일 API (routes/todos.py):**

```python
GET /api/todos
  - Response: {"success": true, "todos": [...]}
  - 기능: 사용자의 모든 할 일 조회

POST /api/todos
  - Request: {"text": "str"}
  - Response: {"success": true, "todo": {...}}
  - 기능: 새로운 할 일 추가

PUT /api/todos/{todo_id}
  - Request: {"text": "str", "completed": bool}
  - Response: {"success": true, "todo": {...}}
  - 기능: 할 일 수정

DELETE /api/todos/{todo_id}
  - Response: {"success": true}
  - 기능: 할 일 삭제
```

**인증 미들웨어 (middleware/auth.py):**

- 모든 할 일 요청에서 세션 쿠키 검증
- 유효하지 않으면 401 에러 반환
- `get_current_user()` 의존성 함수로 구현

### 5.3 쿠키 & 세션 유틸리티 (utils/)

**utils/cookies.py:**

- `set_session_cookie(response, session_token)`: 응답에 세션 쿠키 설정
  - 옵션: Max-Age=86400, Path="/", HttpOnly, Secure (배포 환경), SameSite="lax"
- `delete_session_cookie(response)`: 응답에서 세션 쿠키 삭제

**utils/security.py:**

- `hash_password(password)`: 비밀번호 bcrypt 해싱
- `verify_password(plain, hashed)`: 비밀번호 검증
- `generate_session_token()`: UUID 기반 세션 토큰 생성

**utils/db.py:**

- Neon PostgreSQL 연결 설정
- SQLAlchemy 엔진 및 세션 초기화
- `get_db()`: 데이터베이스 세션 의존성 함수

### 5.4 FastAPI 메인 앱 (main.py)

**초기화:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정 (프론트엔드와의 통신 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 개발 환경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우트 등록
from routes import auth, todos
app.include_router(auth.router)
app.include_router(todos.router)
```

**서버 실행:**

```bash
uvicorn main:app --reload
```

### 5.5 로그인 페이지 컴포넌트 (React)

- 입력 필드: username, password
- 제출 버튼: 로그인
- 에러 메시지 표시
- 로그인 성공 시 할 일 페이지로 이동

### 5.6 useAuth 커스텀 훅 (React)

- 로그인 함수: `login(username, password)`
- 로그아웃 함수: `logout()`
- 현재 사용자 정보 조회
- 인증 상태 관리
- 페이지 로드 시 세션 검증 (`/api/auth/check`)

### 5.7 TodoForm 컴포넌트 (React)

- 입력 필드: 새로운 할 일 입력
- 제출 버튼: 할 일 추가
- 입력값 검증: 빈 문자열 방지
- API 요청 처리 (`POST /api/todos`)

### 5.8 TodoItem 컴포넌트 (React)

- 할 일 텍스트 표시
- 체크박스: 완료 상태 토글
- 수정 기능 (인라인 편집 또는 모달)
- 삭제 버튼: 항목 제거

### 5.9 TodoList 컴포넌트 (React)

- TodoForm과 TodoItem 통합
- 할 일 목록 조회 및 표시
- 로그아웃 기능
- API 연동

### 5.10 App 컴포넌트 (React)

- 라우팅 처리 (로그인 vs 홈)
- useAuth 훅 사용
- 인증 상태에 따른 페이지 렌더링

## 6. 세션 쿠키 데이터 구조

```javascript
// 쿠키에 저장될 형태
sessionToken=abc123def456... // 세션 토큰
// 옵션: Max-Age=86400 (24시간), Path=/, HttpOnly, Secure, SameSite=Lax
```

## 7. API 응답 예시

**로그인 성공:**

```json
{
  "success": true,
  "message": "로그인 성공",
  "user": {
    "id": 1,
    "username": "myusername"
  }
}
```

**할 일 목록 조회:**

```json
{
  "success": true,
  "todos": [
    {
      "id": 1,
      "text": "할 일 1",
      "completed": false,
      "createdAt": "2026-10-01T10:00:00Z"
    },
    {
      "id": 2,
      "text": "할 일 2",
      "completed": true,
      "createdAt": "2026-10-01T10:30:00Z"
    }
  ]
}
```

## 8. 세션 관리 흐름

1. **로그인**:
   - 사용자가 username/password 입력
   - 백엔드에서 사용자 검증 (비밀번호 해싱 확인)
   - 세션 토큰 생성 및 sessions 테이블에 저장
   - 세션 쿠키에 토큰 저장 (Max-Age: 86400초 = 24시간)
   - 클라이언트에 로그인 성공 응답

2. **인증된 요청**:
   - 클라이언트가 API 요청 시 세션 쿠키 자동 전송
   - 백엔드 미들웨어에서 세션 토큰 검증
   - 유효한 세션이면 요청 처리, 무효하면 401 에러 반환

3. **로그아웃**:
   - 세션 토큰을 sessions 테이블에서 삭제
   - 클라이언트 쿠키 삭제

## 9. 구현 시 주의사항

**보안:**

- **비밀번호 해싱**: `passlib` + `bcrypt` 사용
- **세션 토큰**: UUID 기반 충분히 긴 랜덤 문자열 생성
- **HttpOnly 쿠키**: XSS 공격 방지를 위해 FastAPI의 `response.set_cookie(..., httponly=True)`
- **Secure 플래그**: 배포 환경에서는 HTTPS 사용 및 `secure=True` 설정
- **SameSite 속성**: CSRF 공격 방지를 위해 `samesite="lax"` 설정

**데이터베이스:**

- **만료된 세션 정리**: 크론 작업 또는 주기적 배치로 만료된 세션 삭제
- **타임존**: 모든 타임스탬프는 UTC로 저장, 프론트에서 로컬 타임으로 변환

**CORS & API:**

- **CORS 설정**: FastAPI에 `CORSMiddleware` 추가, `allow_credentials=True` 설정
- **쿠키 자동 전송**: 프론트엔드에서 `fetch(..., { credentials: 'include' })` 사용
- **에러 처리**: 401(미인증), 403(권한 없음) 상태 코드 구분

**개발 환경:**

- **환경 변수**: `.env` 파일에서 `DATABASE_URL` 관리
- **CORS 설정**: 개발 환경(`http://localhost:3000`), 배포 환경 분리

## 10. 배포 가이드

**환경 변수 설정:**

```env
DATABASE_URL=postgresql://user:password@host/database  # Neon 연결 문자열
SECRET_KEY=your-secret-key-here  # 선택사항, 향후 JWT 사용 시
```

**백엔드 배포 (예: Railway, Render, Vercel):**

```bash
# 로컬에서 테스트
python -m uvicorn main:app --reload

# 배포용 실행
uvicorn main:app --host 0.0.0.0 --port 8000
```

**프론트엔드 배포:**

- API 엔드포인트를 배포된 백엔드 URL로 변경
- CORS 설정에 배포된 프론트엔드 URL 추가

## 11. 선택적 기능 (향후 추가)

- 할 일 카테고리 분류
- 우선순위 설정
- 마감일 설정
- 할 일 검색/필터링
- 할 일 정렬 기능 (생성일, 마감일 등)
- 다크 모드 지원
- 계정 생성 기능
- 할 일 공유 기능

## 12. 프로젝트 초기 설정

**1. 리포 생성 및 디렉토리 구조:**

```bash
git init todo-app
cd todo-app
mkdir backend frontend
```

**2. 백엔드 초기 설정:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. 백엔드 환경 변수 설정:**

```bash
# backend/.env
DATABASE_URL=postgresql://user:password@host/database
```

**4. 프론트엔드 초기 설정:**

```bash
cd frontend
npm install
```

**5. 프론트엔드 환경 변수 설정:**

```bash
# frontend/.env.local
REACT_APP_API_URL=http://localhost:8000/api
```

**6. 개발 환경 실행:**

터미널 1 (백엔드):

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
# http://localhost:8000 에서 실행
```

터미널 2 (프론트엔드):

```bash
cd frontend
npm start
# http://localhost:3000 에서 실행
```

## 13. .gitignore 설정

```text
# 백엔드
backend/venv/
backend/__pycache__/
backend/.env
backend/*.pyc
backend/.pytest_cache/

# 프론트엔드
frontend/node_modules/
frontend/.env.local
frontend/build/
frontend/dist/
frontend/.DS_Store

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
```

## 14. 테스트 계획

**백엔드 테스트:**

- 로그인/로그아웃 기능 테스트
- 세션 유효성 검증 테스트
- 24시간 후 세션 만료 확인
- 할 일 CRUD 작업 테스트
- 미인증 요청 차단 확인

**프론트엔드 테스트:**

- 페이지 새로고침 후 데이터 유지 확인
- 인증 상태에 따른 페이지 렌더링 확인
- 할 일 추가/수정/삭제 기능 테스트
- 에러 메시지 표시 확인

**통합 테스트:**

- 브라우저 개발자 도구에서 쿠키 확인
- 네트워크 탭에서 API 요청/응답 확인
- 다양한 브라우저에서 호환성 확인
