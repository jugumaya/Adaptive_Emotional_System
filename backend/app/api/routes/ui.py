"""
UI Template Server — serves the frontend HTML pages.

This is the SINGLE source of truth for frontend routes. (Previously, main.py
also defined its own duplicate /ui/* routes — that duplication has been removed;
only this router handles UI serving now.)

Expected folder layout (relative to the backend/ folder's parent):
    frontend/templates/
        login.html
        register.html
        student/dashboard.html
        counselor/dashboard.html
        admin/dashboard.html
        management/dashboard.html
"""
import os
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

router = APIRouter(prefix="/ui", tags=["Frontend UI"])

# backend/app/api/routes/ui.py -> go up 4 levels to reach the project root
# (routes -> api -> app -> backend -> project_root)
_THIS_FILE = os.path.abspath(__file__)
_BACKEND_DIR = os.path.abspath(os.path.join(_THIS_FILE, "..", "..", "..", ".."))
_PROJECT_ROOT = os.path.abspath(os.path.join(_BACKEND_DIR, ".."))

_CANDIDATE_TEMPLATE_DIRS = [
    os.path.join(_PROJECT_ROOT, "frontend", "templates"),  # project_root/frontend/templates
    os.path.join(_BACKEND_DIR, "frontend", "templates"),    # backend/frontend/templates
    os.path.join(_BACKEND_DIR, "templates"),                # backend/templates
]


def _resolve_template_dir() -> str:
    for path in _CANDIDATE_TEMPLATE_DIRS:
        if os.path.isdir(path):
            return path
    # Default to the first candidate even if missing — gives a clear error path
    return _CANDIDATE_TEMPLATE_DIRS[0]


TEMPLATE_DIR = _resolve_template_dir()


def _serve(*relative_parts: str) -> FileResponse:
    target = os.path.join(TEMPLATE_DIR, *relative_parts)
    if not os.path.exists(target):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Template '{os.path.join(*relative_parts)}' not found. "
                f"Looked in: {target}"
            ),
        )
    return FileResponse(target)


@router.get("/login")
def serve_login():
    return _serve("login.html")


@router.get("/register")
def serve_register():
    return _serve("register.html")


@router.get("/dashboard/student")
def serve_student_dashboard():
    return _serve("student", "dashboard.html")


@router.get("/dashboard/counselor")
def serve_counselor_dashboard():
    return _serve("counselor", "dashboard.html")


@router.get("/dashboard/advisor")
def serve_advisor_dashboard():
    # Advisors use the same dashboard as counselors
    return _serve("counselor", "dashboard.html")


@router.get("/dashboard/admin")
def serve_admin_dashboard():
    return _serve("admin", "dashboard.html")


@router.get("/dashboard/management")
def serve_management_dashboard():
    return _serve("management", "dashboard.html")
