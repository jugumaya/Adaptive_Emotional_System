"""
Counselor / Advisor routes — NEW module.

Provides:
  - GET  /counselor/alerts          : anonymized high-risk student alerts
  - GET  /counselor/guidance         : list guidance notes (CRUD: Read)
  - POST /counselor/guidance         : create guidance note (CRUD: Create)
  - PUT  /counselor/guidance/{id}    : edit own guidance note (CRUD: Update)
  - DELETE /counselor/guidance/{id}  : delete own guidance note (CRUD: Delete)

Access: counselor, advisor, admin (admin can oversee everything).
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.student import Student
from app.models.emotion_data import EmotionData
from app.models.risk_analysis import RiskAnalysis
from app.models.guidance import GuidanceNote
from app.schemas.counselor import AlertOut, GuidanceCreate, GuidanceOut
from app.core.deps import require_roles

router = APIRouter(prefix="/counselor", tags=["Counselor"])

ALLOWED = ("counselor", "advisor", "admin")


# ---------- ALERTS (Read) ----------

@router.get("/alerts", response_model=list[AlertOut])
def get_high_risk_alerts(
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_roles(*ALLOWED)),
    limit: int = 20,
):
    """
    Returns the most recent HIGH-risk check-ins, identified only by the
    student's anonymous_id — never their real name or email.
    """
    rows = (
        db.query(EmotionData, RiskAnalysis, Student.anonymous_id)
        .join(RiskAnalysis, RiskAnalysis.emotion_data_id == EmotionData.id)
        .outerjoin(Student, Student.id == EmotionData.student_id)
        .filter(RiskAnalysis.risk_level == "HIGH")
        .order_by(EmotionData.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [
        AlertOut(
            anonymous_id=anon_id or "anon_unknown",
            mood_score=emotion.mood_score,
            risk_level=analysis.risk_level,
            result_summary=analysis.result_summary or "",
            timestamp=emotion.timestamp,
        )
        for emotion, analysis, anon_id in rows
    ]


# ---------- GUIDANCE NOTES (Full CRUD)

@router.get("/guidance", response_model=list[GuidanceOut])
def list_guidance_notes(
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_roles(*ALLOWED)),
):
    return db.query(GuidanceNote).order_by(GuidanceNote.created_at.desc()).all()


@router.post("/guidance", response_model=GuidanceOut, status_code=201)
def create_guidance_note(
    payload: GuidanceCreate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_roles(*ALLOWED)),
):
    note = GuidanceNote(
        counselor_id=current_user.id,
        counselor_name=current_user.name or current_user.email,
        student_anonymous_id=payload.student_anonymous_id,
        message=payload.message,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.put("/guidance/{note_id}", response_model=GuidanceOut)
def update_guidance_note(
    note_id: str,
    payload: GuidanceCreate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_roles(*ALLOWED)),
):
    note = db.query(GuidanceNote).filter(GuidanceNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Guidance note not found.")
    note_counselor_id: Any = note.counselor_id
    current_user_id: Any = current_user.id
    if note_counselor_id != current_user_id and getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="You can only edit your own guidance notes.")

    setattr(note, "message", payload.message)
    setattr(note, "student_anonymous_id", payload.student_anonymous_id)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/guidance/{note_id}")
def delete_guidance_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_roles(*ALLOWED)),
):
    note = db.query(GuidanceNote).filter(GuidanceNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Guidance note not found.")
    note_counselor_id: Any = note.counselor_id
    current_user_id: Any = current_user.id
    if note_counselor_id != current_user_id and getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="You can only delete your own guidance notes.")

    db.delete(note)
    db.commit()
    return {"message": "Guidance note deleted."}
