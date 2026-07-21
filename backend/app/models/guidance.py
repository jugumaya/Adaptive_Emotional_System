# NEW: GuidanceNote — lets Counselors/Advisors record professional guidance,
# either general (student_anonymous_id = None) or targeted at one anonymized student.
# Supports full CRUD via /counselor/guidance routes.
import uuid
from sqlalchemy import Column, String, DateTime, func
from app.db.database import Base


class GuidanceNote(Base):
    __tablename__ = "guidance_notes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    counselor_id = Column(String, nullable=False)
    counselor_name = Column(String, nullable=True, default="")
    student_anonymous_id = Column(String, nullable=True)   # null = general guidance
    message = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
