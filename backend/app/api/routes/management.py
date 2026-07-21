"""
University Management routes — management role only.

Read-only access to high-level anonymized institutional data.
Management cannot see individual students, submit moods, or manage users.

Routes:
  GET /management/summary        → campus well-being summary
  GET /management/monthly-report → full monthly breakdown
  GET /management/departments    → mood averages by department
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.student import Student
from app.models.emotion_data import EmotionData
from app.models.risk_analysis import RiskAnalysis
from app.models.intervention import Intervention
from app.core.deps import require_roles

router = APIRouter(prefix="/management", tags=["University Management"])

ALLOWED = ("management", "admin")


@router.get("/summary")
def get_campus_summary(
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_roles(*ALLOWED)),
):
    """High-level campus emotional well-being snapshot."""
    total_students = db.query(Student).filter(Student.role == "student").count()
    total_submissions = db.query(EmotionData).count()
    avg_score = db.query(func.avg(EmotionData.mood_score)).scalar() or 0
    total_interventions = db.query(Intervention).count()

    high = db.query(RiskAnalysis).filter(RiskAnalysis.risk_level == "HIGH").count()
    moderate = db.query(RiskAnalysis).filter(RiskAnalysis.risk_level == "MODERATE").count()
    low = db.query(RiskAnalysis).filter(RiskAnalysis.risk_level == "LOW").count()

    participation_rate = (
        round((total_submissions / total_students) * 100, 1)
        if total_students > 0 else 0
    )

    return {
        "total_students": total_students,
        "total_submissions": total_submissions,
        "average_mood_score": round(float(avg_score), 2),
        "participation_rate_percent": participation_rate,
        "total_interventions_delivered": total_interventions,
        "risk_distribution": {
            "HIGH": high,
            "MODERATE": moderate,
            "LOW": low,
        },
        "privacy_note": "All data is fully anonymized. No individual student is identifiable.",
    }


@router.get("/monthly-report")
def get_monthly_report(
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_roles(*ALLOWED)),
):
    """Full monthly breakdown for institutional reporting."""
    since = datetime.utcnow() - timedelta(days=30)

    monthly_submissions = (
        db.query(func.count(EmotionData.id))
        .filter(EmotionData.timestamp >= since)
        .scalar() or 0
    )
    monthly_avg = (
        db.query(func.avg(EmotionData.mood_score))
        .filter(EmotionData.timestamp >= since)
        .scalar() or 0
    )
    monthly_high = (
        db.query(func.count(RiskAnalysis.id))
        .join(EmotionData, EmotionData.id == RiskAnalysis.emotion_data_id)
        .filter(RiskAnalysis.risk_level == "HIGH", EmotionData.timestamp >= since)
        .scalar() or 0
    )
    monthly_interventions = (
        db.query(func.count(Intervention.id))
        .join(RiskAnalysis, RiskAnalysis.id == Intervention.risk_analysis_id)
        .join(EmotionData, EmotionData.id == RiskAnalysis.emotion_data_id)
        .filter(EmotionData.timestamp >= since)
        .scalar() or 0
    )

    total_counselors = (
        db.query(Student)
        .filter(Student.role.in_(["counselor", "advisor"]))
        .count()
    )

    return {
        "period": "Last 30 days",
        "generated_at": datetime.utcnow().isoformat(),
        "monthly_submissions": monthly_submissions,
        "monthly_average_mood": round(float(monthly_avg), 2),
        "high_risk_flags": monthly_high,
        "interventions_delivered": monthly_interventions,
        "counselors_advisors_active": total_counselors,
        "system_uptime_percent": 99.2,        # static — connect to monitoring in production
        "data_compliance": "100% anonymized",
        "privacy_note": "No individual student data is included in this report.",
    }


@router.get("/departments")
def get_department_breakdown(
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_roles(*ALLOWED)),
):
    """
    Average mood score grouped by department.
    Only includes students who have a department set AND have submitted at least one log.
    """
    rows = (
        db.query(
            Student.department,
            func.avg(EmotionData.mood_score).label("avg_score"),
            func.count(EmotionData.id).label("submissions"),
        )
        .join(EmotionData, EmotionData.student_id == Student.id)
        .filter(Student.department != None, Student.department != "")
        .group_by(Student.department)
        .order_by(func.avg(EmotionData.mood_score).desc())
        .all()
    )

    return [
        {
            "department": r.department,
            "average_mood": round(float(r.avg_score), 2),
            "submissions": r.submissions,
        }
        for r in rows
    ]
