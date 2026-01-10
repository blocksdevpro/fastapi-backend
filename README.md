# FastAPI Backend Template

A robust, async FastAPI backend starter template featuring authentication, product management, and modern best practices.

## 🚀 Features

- **FastAPI**: High-performance, easy-to-learn, fast-to-code, ready-for-production.
- **Async SQLAlchemy**: Fully asynchronous ORM with PostgreSQL support.
- **Authentication**: JWT-based auth with login, refresh, revoke, and logout.
- **Pydantic v2**: Data validation and settings management using the latest Pydantic.
- **Rate Limiting**: Built-in rate limiting using `slowapi`.
- **Testing**: Ready-to-go test suite using `pytest`.
- **Linting & Formatting**: configured with `ruff`.

## 🛠️ Tech Stack

- **Python**: 3.10+
- **Framework**: FastAPI
- **Database**: PostgreSQL (Asyncpg)
- **ORM**: SQLAlchemy (Async)
- **Migrations**: (Planned/Not yet configured) -> Recommend establishing `alembic`
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
DATABASE_URL = "MAIN_DB_URL"
TEST_DATABASE_URL = "TEST_DB_URL used in pytest"

# Security
JWT_ALGORITHM = "HS256"

JWT_ACCESS_SECRET_KEY = "SUPER_SECRET_JWT_ACCESS_SECRET_KEY"
JWT_REFRESH_SECRET_KEY = "SUPER_SECRET_JWT_REFRESH_SECRET_KEY"

JWT_ACCESS_EXPIRE_MINUTES = 15
JWT_REFRESH_EXPIRE_MINUTES = 1440
```

### 5. Run the Application

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
│   ├── core          # Config, logger, security settings
│   ├── db            # Database connection & session
│   ├── handlers      # Exception handlers & middlewares
│   ├── models        # SQLAlchemy database models
│   ├── routers       # API route definitions
│   ├── schemas       # Pydantic models (Request/Response)
│   ├── services      # Business logic layer
│   └── utils         # Helper functions
├── tests             # Pytest suite
├── main.py           # Application entry point
├── Makefile          # Handy commands
└── requirements.txt  # Project dependencies
```
