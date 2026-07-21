# Matches Class Diagram: Report class
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func
from app.db.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    aggregated_data = Column(String)      # JSON string
    is_anonymized = Column(Boolean, default=True)
    generated_at = Column(DateTime, server_default=func.now())
    generated_by = Column(String)         # admin / counselor / advisor / management / system
