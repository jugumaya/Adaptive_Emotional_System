# AEE Backend v2 — Corrected & Unified

**CSE307 — System Analysis and Design | Section 01 | Group 05 | Spring 2026**

This is the corrected, unified backend. It replaces:
- the old duplicate `main.py` (which had its own inline `/ui/*` routes AND a separate `ui.py` router)
- the separate Flask `server.py` + SQLite (`aee_system.db`) backend
- the mismatch between the README (PostgreSQL + bcrypt) and the actual code (SQLite + PBKDF2)

There is now **one backend**, **one database**, **one set of routes**.

---

## What changed vs. your uploaded files

| Issue | Fix |
|---|---|
| Two backends (FastAPI + Flask) | Removed Flask `server.py`. FastAPI is the only backend. |
| `main.py` only registered `auth` + `admin` routers | All 6 routers now registered: `auth`, `admin`, `mood`, `reports`, `counselor`, `ui`. |
| Duplicate `/ui/*` routes (inline in `main.py` AND in `ui.py`) | Only `app/api/routes/ui.py` serves UI now. |
| README claimed PostgreSQL + bcrypt, code used SQLite + PBKDF2 | Docs now match code: **SQLite** (zero setup) + **PBKDF2-HMAC-SHA256**. PostgreSQL still supported by changing one line in `.env`. |
| `MoodSubmit.student_id` was required, breaking anonymous/demo flow | `student_id` is now optional — taken from JWT if logged in, or passed directly for demo mode. |
| Only 3 roles handled (`student`/`admin`/`advisor`) | Now 5 roles: `student`, `counselor`, `advisor`, `admin`, `management` — validated everywhere via `VALID_ROLES`. |
| No Counselor-specific endpoints | New `app/api/routes/counselor.py`: high-risk alerts + full CRUD guidance notes. |
| No way to know your own role from frontend | New `GET /auth/me`. |
| Admin could only list/delete users | Full CRUD: `GET/POST/PUT/DELETE /api/admin/users`. |

---

## Project Structure

```
aee_backend_v2/
│
├── main.py                     ← single entry point (run this)
├── seed_demo_users.py          ← creates 1 demo account per role
├── requirements.txt
├── .env.example
├── aee.db                      ← SQLite database (auto-created on first run)
│
└── app/
    ├── core/
    │   ├── config.py           ← settings (DATABASE_URL, SECRET_KEY)
    │   ├── security.py         ← PBKDF2 hashing + JWT create/decode
    │   └── deps.py              ← NEW: get_current_user, require_roles()
    │
    ├── db/
    │   └── database.py
    │
    ├── models/                 ← SQLAlchemy tables
    │   ├── student.py          ← unified Users table (5 roles)
    │   ├── emotion_data.py
    │   ├── risk_analysis.py
    │   ├── intervention.py
    │   ├── report.py
    │   └── guidance.py          ← NEW: counselor guidance notes
    │
    ├── schemas/                 ← Pydantic models
    │   ├── student.py          ← incl. UserUpdate for admin CRUD
    │   ├── emotion.py
    │   └── counselor.py         ← NEW: AlertOut, GuidanceCreate/Out
    │
    ├── services/
    │   ├── risk_engine.py
    │   └── report_service.py   ← + weekly trend, role distribution
    │
    └── api/routes/
        ├── auth.py              ← register/login/me (all roles)
        ├── admin.py             ← full user CRUD + metrics (admin only)
        ├── mood.py               ← submit/history (student + staff views)
        ├── reports.py            ← aggregated + weekly trend (staff only)
        ├── counselor.py          ← NEW: alerts + guidance CRUD
        └── ui.py                  ← serves frontend HTML pages
```

---

## Setup & Run

### 1. Install dependencies
```bash
cd aee_backend_v2
pip install -r requirements.txt
```

### 2. Configure environment (optional — SQLite works with zero config)
```bash
cp .env.example .env
```

### 3. Seed demo accounts (one per role)
```bash
python seed_demo_users.py
```

This creates:

| Role | Email | Password |
|---|---|---|
| Student | student@aee.edu | demo1234 |
| Counselor | counselor@aee.edu | demo1234 |
| Advisor | advisor@aee.edu | demo1234 |
| Admin | admin@aee.edu | demo1234 |
| University Management | management@aee.edu | demo1234 |

### 4. Run the server
```bash
uvicorn main:app --reload
```

- API docs: http://localhost:8000/docs
- Login page: http://localhost:8000/ui/login *(once you add `frontend/templates/login.html`)*

---

## Role-Based Access Summary

| Endpoint | student | counselor/advisor | admin | management |
|---|---|---|---|---|
| `POST /mood/submit` | ✅ (own data) | ✅ | ✅ | ❌ |
| `GET /mood/history` | ✅ (own only) | ✅ (any) | ✅ (any) | ❌ |
| `GET /counselor/alerts` | ❌ | ✅ | ✅ | ❌ |
| `GET/POST/PUT/DELETE /counselor/guidance` | ❌ | ✅ | ✅ | ❌ |
| `GET /reports/aggregated` | ❌ | ✅ | ✅ | ✅ |
| `GET /reports/weekly-trend` | ❌ | ✅ | ✅ | ✅ |
| `GET/POST/PUT/DELETE /api/admin/users` | ❌ | ❌ | ✅ | ❌ |
| `GET /api/admin/metrics` | ❌ | ❌ | ✅ | ❌ |
| `GET /auth/me` | ✅ | ✅ | ✅ | ✅ |

All enforcement happens via `app/core/deps.py:require_roles(...)`.

---

## Switching to PostgreSQL later

Edit `.env`:
```env
DATABASE_URL=postgresql://aee_user:yourpassword@localhost:5432/aee_db
```
Then add `psycopg2-binary` to `requirements.txt` and reinstall. No code changes needed — `database.py` already handles both.

---

## Next step

The frontend (`frontend/templates/...`) is not yet rebuilt to match this backend.
The `ui.py` router expects:
```
frontend/templates/
├── login.html
├── register.html
├── student/dashboard.html
├── counselor/dashboard.html
├── admin/dashboard.html
└── management/dashboard.html
```
