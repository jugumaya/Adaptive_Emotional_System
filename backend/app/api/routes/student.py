"""
Student-facing endpoints.

Currently provides:
  - GET /student/guidance : list counselor guidance notes addressed to the
                            authenticated student (matched by anonymous_id).

Access: student only.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.database import get_db
from app.models.guidance import GuidanceNote
from app.models.student import Student
from app.schemas.counselor import GuidanceOut

router = APIRouter(prefix="/student", tags=["Student"])


@router.get("/guidance", response_model=list[GuidanceOut])
def my_guidance_notes(
    db: Session = Depends(get_db),
    me: Student = Depends(require_roles("student")),
):
    """
    Return all guidance notes whose `student_anonymous_id` matches the
    logged-in student's `anonymous_id`. General guidance (with NULL
    `student_anonymous_id`) is NOT returned here — it is only visible to
    counselors on their dashboard.
    """
    return (
        db.query(GuidanceNote)
        .filter(GuidanceNote.student_anonymous_id == me.anonymous_id)
        .order_by(GuidanceNote.created_at.desc())
        .all()
    )