"""
Notification routes — for counselors, advisors, and admins.

Notifications are auto-created when a HIGH-risk mood is submitted.

Full CRUD:
  GET    /notifications/         → list my role's notifications
  GET    /notifications/unread   → count of unread (for badge in UI)
  PUT    /notifications/{id}/read → mark one as read
  PUT    /notifications/read-all  → mark all as read
  DELETE /notifications/{id}     → delete a notification
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.db.database import get_db
from app.models.student import Student
from app.models.notification import Notification
from app.core.deps import require_roles

router = APIRouter(prefix="/notifications", tags=["Notifications"])

ALLOWED = ("counselor", "advisor", "admin")


class NotificationOut(BaseModel):
    id: str
    recipient_role: str
    title: str
    message: str
    is_read: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------- READ ----------

@router.get("/", response_model=list[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_roles(*ALLOWED)),
):
    """Returns all notifications for the current user's role."""
    return (
        db.query(Notification)
        .filter(Notification.recipient_role == current_user.role)
        .order_by(Notification.created_at.desc())
        .all()
    )


@router.get("/unread")
def count_unread(
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_roles(*ALLOWED)),
):
    """Returns count of unread notifications — used for sidebar badge."""
    count = (
        db.query(Notification)
        .filter(
            Notification.recipient_role == current_user.role,
            Notification.is_read == False,
        )
        .count()
    )
    return {"unread_count": count}


# ---------- UPDATE ----------

@router.put("/{notif_id}/read", response_model=NotificationOut)
def mark_as_read(
    notif_id: str,
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_roles(*ALLOWED)),
):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")
    # use getattr to ensure we compare the actual attribute value (not a SQLAlchemy column expression)
    if getattr(notif, "recipient_role") != current_user.role:
        raise HTTPException(status_code=403, detail="This notification is not yours.")

    # assign via setattr to avoid type-checker issues with SQLAlchemy Column attributes
    setattr(notif, "is_read", True)
    db.commit()
    db.refresh(notif)
    return notif


@router.put("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_roles(*ALLOWED)),
):
    db.query(Notification).filter(
        Notification.recipient_role == current_user.role,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read."}


# ---------- DELETE ----------

@router.delete("/{notif_id}")
def delete_notification(
    notif_id: str,
    db: Session = Depends(get_db),
    current_user: Student = Depends(require_roles(*ALLOWED)),
):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")
    # compare actual values to avoid SQLAlchemy ColumnElement[bool] in conditionals
    current_role = getattr(current_user, "role")
    if getattr(notif, "recipient_role") != current_role and current_role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied.")

    db.delete(notif)
    db.commit()
    return {"message": "Notification deleted."}
