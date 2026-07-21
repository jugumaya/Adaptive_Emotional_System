"""
Mood submission + intervention routes
Matches Sequence Diagram: steps 6→7→8→10→11→12
Matches DFD Level-1: 1.2 Data Collection → 1.3 Emotional Processing → 1.4 Micro-Intervention

Full CRUD:
  POST   /mood/submit          → Create mood log + run risk engine
  GET    /mood/history         → Read mood history
  PUT    /mood/{id}            → Update a mood log (score/notes)
  DELETE /mood/{id}            → Delete own mood log
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, cast
from pydantic import BaseModel, Field
from app.db.database import get_db
from app.models.student import Student
from app.models.emotion_data import EmotionData
from app.models.risk_analysis import RiskAnalysis
from app.models.intervention import Intervention
from app.schemas.emotion import MoodSubmit, MoodOut
from app.services.risk_engine import analyze_risk, get_intervention
from app.core.deps import get_optional_user, get_current_user

router = APIRouter(prefix="/mood", tags=["Mood Tracking"])


# ---------- CREATE ----------

@router.post("/submit", response_model=MoodOut)
def submit_mood(
    data: MoodSubmit,
    db: Session = Depends(get_db),
    current_user: Optional[Student] = Depends(get_optional_user),
):
    student_id = data.student_id or (str(current_user.id) if current_user else None)
    if student_id is None:
        raise HTTPException(
            status_code=400,
            detail="student_id is required. Log in, or pass student_id in the request body.",
        )

    # Step 1 — Save emotion record (saveLog)
    emotion = EmotionData(
        student_id=student_id,
        mood_score=data.mood_score,
        mood_type=data.mood_type,
        notes=data.notes,
    )
    db.add(emotion)
    db.commit()
    db.refresh(emotion)

    # Step 2 — Rule-based risk analysis (analyze)
    risk_level = analyze_risk(data.mood_score)
    analysis = RiskAnalysis(
        emotion_data_id=emotion.id,
        risk_level=risk_level,
        result_summary=f"Mood score {data.mood_score}/10 → {risk_level} risk detected",
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Step 3 — Generate intervention (returnRiskStatus + displaySuggestion)
    iv = get_intervention(risk_level)
    intervention = Intervention(
        risk_analysis_id=analysis.id,
        suggestion=iv["suggestion"],
        intervention_type=iv["type"],
    )
    db.add(intervention)
    db.commit()

    # Auto-create HIGH-risk notification for counselors/advisors
    if risk_level == "HIGH":
        student = db.query(Student).filter(Student.id == student_id).first()
        anon = str(student.anonymous_id) if student else "anon_unknown"
        _create_high_risk_notification(db, anon, data.mood_score)

    return MoodOut(
        id=cast(str, emotion.id),
        mood_score=data.mood_score,
        risk_level=risk_level,
        intervention=iv["suggestion"],
    )


# ---------- READ ----------

@router.get("/history")
def get_mood_history(
    db: Session = Depends(get_db),
    current_user: Optional[Student] = Depends(get_optional_user),
    student_id: Optional[str] = None,
    limit: int = 30,
):
    """
    - Student role: returns only their own records (privacy enforced).
    - counselor/advisor/admin/management: returns all or filtered by student_id.
    """
    query = (
        db.query(EmotionData, RiskAnalysis)
        .outerjoin(RiskAnalysis, RiskAnalysis.emotion_data_id == EmotionData.id)
    )
    if current_user is not None and cast(str, current_user.role) == "student":
        query = query.filter(EmotionData.student_id == current_user.id)
    elif student_id is not None:
        query = query.filter(EmotionData.student_id == student_id)

    records = query.order_by(EmotionData.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": emotion.id,
            "score": emotion.mood_score,
            "timestamp": emotion.timestamp.isoformat() if emotion.timestamp else None,
            "type": emotion.mood_type or "general",
            "notes": emotion.notes or "",
            "risk_level": analysis.risk_level if analysis else "UNKNOWN",
        }
        for emotion, analysis in records
    ]


# ---------- UPDATE ----------

class MoodUpdate(BaseModel):
    mood_score: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    mood_type: Optional[str] = None


@router.put("/{log_id}")
def update_mood_log(
    log_id: str,
    payload: MoodUpdate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    """
    Student can update their own mood log.
    counselor/advisor/admin can update any log.
    Re-runs the risk engine if the score changed.
    """
    emotion = db.query(EmotionData).filter(EmotionData.id == log_id).first()
    if not emotion:
        raise HTTPException(status_code=404, detail="Mood log not found.")

    if cast(str, current_user.role) == "student" and cast(str, emotion.student_id) != cast(str, current_user.id):
        raise HTTPException(status_code=403, detail="You can only edit your own mood logs.")

    if payload.mood_score is not None:
        setattr(emotion, "mood_score", payload.mood_score)
    if payload.notes is not None:
        setattr(emotion, "notes", payload.notes)
    if payload.mood_type is not None:
        setattr(emotion, "mood_type", payload.mood_type)

    db.commit()

    # Re-run risk engine if score changed
    if payload.mood_score is not None:
        analysis = db.query(RiskAnalysis).filter(
            RiskAnalysis.emotion_data_id == log_id
        ).first()
        if analysis:
            new_risk = analyze_risk(cast(int, emotion.mood_score))
            setattr(analysis, "risk_level", new_risk)
            setattr(
                analysis,
                "result_summary",
                f"Mood score {emotion.mood_score}/10 → {new_risk} risk detected (updated)",
            )
            db.commit()

    db.refresh(emotion)
    return {"message": "Mood log updated.", "id": emotion.id, "new_score": emotion.mood_score}


# ---------- DELETE ----------

@router.delete("/{log_id}")
def delete_mood_log(
    log_id: str,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    """
    Student can delete their own mood log.
    Admin can delete any log.
    """
    emotion = db.query(EmotionData).filter(EmotionData.id == log_id).first()
    if not emotion:
        raise HTTPException(status_code=404, detail="Mood log not found.")

    if cast(str, current_user.role) == "student" and cast(str, emotion.student_id) != cast(str, current_user.id):
        raise HTTPException(status_code=403, detail="You can only delete your own mood logs.")
    if str(current_user.role) not in ("student", "admin", "counselor", "advisor"):
        raise HTTPException(status_code=403, detail="Permission denied.")

    # Cascade: delete linked risk analysis and intervention first
    analysis = db.query(RiskAnalysis).filter(
        RiskAnalysis.emotion_data_id == log_id
    ).first()
    if analysis:
        db.query(Intervention).filter(
            Intervention.risk_analysis_id == analysis.id
        ).delete()
        db.delete(analysis)

    db.delete(emotion)
    db.commit()
    return {"message": "Mood log deleted successfully.", "id": log_id}


def _create_high_risk_notification(db, anonymous_id: str, score: int):
    """Auto-create a notification for counselors/advisors when HIGH risk is detected."""
    from app.models.notification import Notification
    for role in ("counselor", "advisor"):
        notif = Notification(
            recipient_role=role,
            title="⚠️ High-Risk Alert",
            message=(
                f"Student {anonymous_id} submitted a mood score of {score}/10. "
                "Immediate check-in may be needed."
            ),
            is_read=False,
        )
        db.add(notif)
    db.commit()
