"""
Notification model — stores system-generated alerts for counselors/admins.

Notifications are created automatically when:
  - A student submits a HIGH-risk mood score
  - A counselor posts a guidance note targeting a specific student

Supports CRUD via /notifications routes.
"""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func
from app.db.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recipient_role = Column(String, nullable=False)   # counselor / advisor / admin
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
