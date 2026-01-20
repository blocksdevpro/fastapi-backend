# FastAPI Backend Template

A robust, async FastAPI backend starter template featuring authentication, product management, and modern best practices.

## 🚀 Features

- **FastAPI**: High-performance, easy-to-learn, fast-to-code, ready-for-production.
- **Async SQLAlchemy**: Fully asynchronous ORM with PostgreSQL support.
- **Authentication**: JWT-based auth with login, refresh, revoke, and logout.
- **Role-Based Access Control (RBAC)**: User roles (`user`, `admin`) for permission management.
- **Security**: Password reset, email verification, and session management (view/revoke active sessions).
- **Email Service**: Integrated with `Resend` for sending transactional emails.
- **Pydantic v2**: Data validation and settings management using the latest Pydantic.
- **Rate Limiting**: Built-in rate limiting using `slowapi`.
- **Standardized Error Handling**: Centralized error messages for consistent API responses.
- **Testing**: Ready-to-go test suite using `pytest`.
- **Linting & Formatting**: configured with `ruff`.

## 🛠️ Tech Stack

- **Python**: 3.10+
- **Framework**: FastAPI
- **Database**: PostgreSQL (Asyncpg)
- **ORM**: SQLAlchemy (Async)
- **Migrations**: Alembic
- **Email**: Resend
- **Package Manager**: standard `pip` or `poetry` (requirements.txt provided)

## 📋 Prerequisites

- Python 3.10 or higher
- PostgreSQL database
- Virtual environment tool (e.g., `venv`, `uv`)

## ⚡ Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd fastapi-backend
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/MacOS
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory. You can use the provided `.env.example` (if available) or simpler defaults:

```python
# Database
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname"

# Security
JWT_ALGORITHM = "HS256"
JWT_ACCESS_SECRET_KEY = "your-access-secret-key"
JWT_REFRESH_SECRET_KEY = "your-refresh-secret-key"
JWT_ACCESS_EXPIRE_MINUTES = 15
JWT_REFRESH_EXPIRE_MINUTES = 1440

# Verification & Password Reset
VERIFICATION_TOKEN_SECRET = "your-verification-secret"
PASSWORD_RESET_EXPIRE_MINUTES = 15
EMAIL_VERIFICATION_EXPIRE_MINUTES = 1440

# Email (Resend)
RESEND_API_KEY = "re_123456789"
RESEND_FROM_EMAIL = "onboarding@resend.dev"
RESEND_FROM_NAME = "FastAPI Backend"

# Frontend
FRONTEND_URL = "http://localhost:3000"
CORS_ORIGINS = '["http://localhost:3000", "http://localhost:8000"]'
```

### 5. Run Migrations

Initialize the database schema:

```bash
alembic upgrade head
```

### 6. Run the Application

You can use the included `Makefile` commands for convenience:

```bash
# Run in development mode (with hot reload)
make dev

# Run in production mode
make start
```

Or manually:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.
API Documentation (Swagger UI) is available at `http://localhost:8000/api/docs`.
Health check endpoint: `http://localhost:8000/api/health`

## 🧪 Running Tests

Ensure your test database environment is ready or configured in `tests/conftest.py`.

```bash
pytest
```

## 🧹 Code Quality

Run formatting and linting check:

```bash
make format
```

This runs `ruff check --fix` and `ruff format`.

## 📂 Project Structure

```
.
├── app
│   ├── api           # API endpoints grouping
│   ├── core          # Config, logger, security settings, messages
│   ├── db            # Database connection & session
│   ├── handlers      # Exception handlers & middlewares
│   ├── models        # SQLAlchemy database models
│   ├── routers       # API route definitions
│   ├── schemas       # Pydantic models (Request/Response)
│   ├── services      # Business logic layer
│   └── utils         # Helper functions
├── migrations        # Alembic migration scripts
├── tests             # Pytest suite
├── main.py           # Application entry point
├── Makefile          # Handy commands
└── requirements.txt  # Project dependencies
```
