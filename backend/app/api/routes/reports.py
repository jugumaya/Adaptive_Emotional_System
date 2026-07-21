"""
Report routes — for Counselors, Advisors, Admins, and University Management.
Matches DFD 1.5 Generate Report + CRUD Matrix (Administrator: C,R / Advisor: R)

All data here is fully anonymized/aggregated — no individual student is identifiable.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.student import Student
from app.core.deps import require_roles
from app.services.report_service import (
    generate_aggregated_report,
    generate_weekly_trend,
)

router = APIRouter(prefix="/reports", tags=["Reports"])

ALLOWED = ("counselor", "advisor", "admin", "management")


@router.get("/aggregated")
def get_aggregated_report(
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_roles(*ALLOWED)),
):
    """Anonymized institutional report."""
    return generate_aggregated_report(db)


@router.get("/weekly-trend")
def get_weekly_trend(
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_roles(*ALLOWED)),
):
    """Average mood score per day for the last 7 days — for charts."""
    return generate_weekly_trend(db)
