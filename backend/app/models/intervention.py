# Matches Class Diagram: Intervention class
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, func
from app.db.database import Base


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    risk_analysis_id = Column(String, ForeignKey("risk_analysis.id"))
    suggestion = Column(String)
    intervention_type = Column(String)    # BREATHING / FOCUS / MOTIVATIONAL
    created_at = Column(DateTime, server_default=func.now())
