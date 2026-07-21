"""
Adaptive Emotional Ecosystem (AEE) — Unified Backend Entry Point
CSE307 — System Analysis and Design | Group 05 | Spring 2026

Run with:
    cd aee_backend_v2
    uvicorn main:app --reload

    http://localhost:8000/docs        → interactive API docs (all endpoints)
    http://localhost:8000/ui/login    → login page
    http://localhost:8000/health      → health check
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.db.database import engine, Base

# CRITICAL: all models must be imported BEFORE create_all()
# so SQLAlchemy knows about every table before creating them.
from app.models.student import Student            # noqa: F401
from app.models.emotion_data import EmotionData   # noqa: F401
from app.models.risk_analysis import RiskAnalysis # noqa: F401
from app.models.intervention import Intervention  # noqa: F401
from app.models.report import Report              # noqa: F401
from app.models.guidance import GuidanceNote      # noqa: F401
from app.models.notification import Notification  # noqa: F401

from app.api.routes import (
    auth,
    admin,
    mood,
    reports,
    counselor,
    management,
    notifications,
    ui,
)

# ── Database ────────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Adaptive Emotional Ecosystem (AEE)",
    description=(
        "Non-clinical emotional well-being platform for university students.\n\n"
        "**Roles:** student · counselor · advisor · admin · management\n\n"
        "All student data is anonymized. No clinical diagnoses are made."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # restrict to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router)           # POST /auth/register  /auth/login  GET /auth/me
app.include_router(mood.router)           # POST /mood/submit  GET /mood/history  PUT/DELETE /mood/{id}
app.include_router(counselor.router)      # GET /counselor/alerts  CRUD /counselor/guidance
app.include_router(reports.router)        # GET /reports/aggregated  /reports/weekly-trend
app.include_router(management.router)     # GET /management/summary  /monthly-report  /departments
app.include_router(notifications.router)  # GET/PUT/DELETE /notifications/*
app.include_router(admin.router)          # CRUD /api/admin/users  GET /api/admin/metrics
app.include_router(ui.router)             # GET /ui/login  /ui/dashboard/* (serves HTML)


# ── Root ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"], include_in_schema=False)
def root():
    return RedirectResponse(url="/ui/login")


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "version": "2.0.0",
        "project": "Adaptive Emotional Ecosystem — CSE307 Group 05",
        "docs": "/docs",
        "roles": ["student", "counselor", "advisor", "admin", "management"],
    }
