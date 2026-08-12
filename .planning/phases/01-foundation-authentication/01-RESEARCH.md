# Phase 1: Foundation & Authentication — Research

**Analysis Date:** 2026-08-13

## 1. Domain & Stack Research

### Core Technologies & Libraries
- **FastAPI (0.110+)**: Modern async Python framework providing automatic OpenAPI docs, Pydantic validation, and high performance.
- **SQLAlchemy (2.0+)**: Industry-standard ORM with declarative mapping and Type-annotated Mapped attributes.
- **Pydantic (v2.6+)**: Fast data validation using Pydantic v2 `BaseModel` & `Field`.
- **PyJWT (2.8+) / python-jose**: JWT encoding/decoding with expiration and signature verification.
- **Passlib [Argon2 / Bcrypt]**: Secure password hashing with fallback handling.
- **Psycopg2-binary / Asyncpg**: PostgreSQL database connector.
- **SlowAPI**: Rate limiting middleware for protecting `/api/v1/auth/login` against brute force attempts.

## 2. Directory Layout & Architecture Pattern

```text
backend/
├── app/
│   ├── api/
│   │   ├── deps.py             # Auth & RBAC FastAPI dependencies
│   │   └── v1/
│   │       ├── auth.py         # Login, Register, Refresh, Logout
│   │       └── users.py        # User profile & admin user management
│   ├── core/
│   │   ├── config.py           # Pydantic BaseSettings for env vars
│   │   ├── database.py         # SQLAlchemy engine & SessionLocal
│   │   └── security.py         # Password hash/verify, JWT create/verify
│   ├── models/
│   │   ├── base.py             # Base declarative model
│   │   ├── user.py             # User & UserRole ORM models
│   │   └── login_attempt.py    # Failed login attempts tracking
│   ├── schemas/
│   │   ├── auth.py             # Token, Login, Register pydantic models
│   │   └── user.py             # UserResponse, UserUpdate models
│   └── main.py                 # FastAPI application & middleware
├── alembic/                    # Database migration scripts
├── requirements.txt
└── .env.example
```

## 3. Security Requirements & Threat Mitigation

### User Authentication & JWT Flow
- Registration hashes password with Argon2id / Bcrypt before storing in PostgreSQL.
- `/api/v1/auth/login` verifies password, creates JWT Access Token (15 min exp) and Refresh Token (7 days exp).
- Protected endpoints require `Authorization: Bearer <token>` header verified via `get_current_user` dependency.

### Role-Based Access Control (RBAC)
- Roles: `USER` (standard payment user) and `ADMIN` (security analyst).
- Dependency factory `require_role(allowed_roles=[UserRole.ADMIN])` checks user role in JWT payload / database and returns 403 Forbidden if unauthorized.

### Brute-Force & Lockout Policy
- Track failed login attempts by email & IP address.
- If 5 consecutive failed attempts occur within 15 minutes, account is locked for 15 minutes or until admin unlocks.
- Endpoint rate limiting: maximum 5 login requests per minute per IP address.

## 4. Validation Architecture

- **Verification 1:** User signup creates record in DB with hashed password (no plaintext password stored).
- **Verification 2:** Valid login returns JWT token; invalid password returns 401 Unauthorized and increments failed attempt counter.
- **Verification 3:** 5 consecutive invalid logins trigger account lockout (423 Locked / 429 Too Many Requests).
- **Verification 4:** Admin-only routes return 403 Forbidden for non-admin users.

---
*Research completed: 2026-08-13*
