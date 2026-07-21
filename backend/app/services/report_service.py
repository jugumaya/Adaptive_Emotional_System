"""
Report generation service
Matches: Generate Report (DFD Level-1 process 1.5)
CRUD Matrix: Administrator C,R — Report class generateReport()
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.emotion_data import EmotionData
from app.models.risk_analysis import RiskAnalysis
from app.models.student import Student


def generate_aggregated_report(db: Session) -> dict:
    """Anonymized, aggregated well-being statistics. No individual data is exposed."""
    total = db.query(func.count(EmotionData.id)).scalar() or 0
    avg_score = db.query(func.avg(EmotionData.mood_score)).scalar()

    high = db.query(func.count(RiskAnalysis.id)).filter(RiskAnalysis.risk_level == "HIGH").scalar() or 0
    moderate = db.query(func.count(RiskAnalysis.id)).filter(RiskAnalysis.risk_level == "MODERATE").scalar() or 0
    low = db.query(func.count(RiskAnalysis.id)).filter(RiskAnalysis.risk_level == "LOW").scalar() or 0

    return {
        "total_submissions": total,
        "average_mood_score": round(float(avg_score or 0), 2),
        "risk_distribution": {
            "HIGH": high,
            "MODERATE": moderate,
            "LOW": low,
        },
        "privacy_note": "All data is fully anonymized. No individual student is identifiable.",
    }


def generate_weekly_trend(db: Session) -> list[dict]:
    """Average mood score per day for the last 7 days (for charts)."""
    since = datetime.utcnow() - timedelta(days=7)
    rows = (
        db.query(
            func.date(EmotionData.timestamp).label("day"),
            func.avg(EmotionData.mood_score).label("avg_score"),
            func.count(EmotionData.id).label("count"),
        )
        .filter(EmotionData.timestamp >= since)
        .group_by(func.date(EmotionData.timestamp))
        .order_by(func.date(EmotionData.timestamp))
        .all()
    )
    return [
        {"date": str(r.day), "average_mood": round(float(r.avg_score), 2), "submissions": r.count}
        for r in rows
    ]


def generate_role_distribution(db: Session) -> dict:
    """Count of users per role — used by Admin dashboard."""
    rows = db.query(Student.role, func.count(Student.id)).group_by(Student.role).all()
    return {role: count for role, count in rows}
