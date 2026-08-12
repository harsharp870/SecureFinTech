# Phase 01 — Plan 01-01 Summary
## Backend Architecture, ORM Models & Security Core

**Status**: ✅ COMPLETE  
**Commit**: feat(phase-01): implement foundation and authentication backend

---

## Files Created

| File | Purpose |
|---|---|
| `backend/.env.example` | Environment variable template |
| `backend/app/__init__.py` | App package |
| `backend/app/core/__init__.py` | Core package |
| `backend/app/core/config.py` | Pydantic-settings `Settings` class |
| `backend/app/core/database.py` | SQLAlchemy engine, `SessionLocal`, `get_db`, SQLite fallback |
| `backend/app/core/security.py` | bcrypt password hashing (direct), JWT access/refresh token creation & decoding |
| `backend/app/models/base.py` | Re-exports `Base` from database |
| `backend/app/models/user.py` | `User` ORM model with `UserRole` enum, lockout fields |
| `backend/app/models/login_attempt.py` | `LoginAttempt` ORM model for tracking auth events |
| `backend/app/models/__init__.py` | Models package exports |
| `backend/app/main.py` | FastAPI app, CORS, router registration, `create_all` on startup |

## Key Decisions

- **bcrypt direct** (not passlib) — passlib 1.7.4 is incompatible with bcrypt 5.x on Python 3.13. Using `bcrypt.gensalt()` + `bcrypt.hashpw()` directly resolves the `ValueError` detection bug.
- **SQLite fallback** — `USE_SQLITE=true` env var (defaults true) allows local development and CI without a running PostgreSQL instance.
- **UUID PKs as String(36)** — SQLite-compatible UUID primary keys.

## UAT Verification

- ✅ App starts and `/health` responds
- ✅ Database tables created on startup
- ✅ Password hashing works on Python 3.13 + bcrypt 5.x
- ✅ JWT tokens encode/decode correctly
