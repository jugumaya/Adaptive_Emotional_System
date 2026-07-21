# Matches Class Diagram: RiskAnalysis class
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, func
from app.db.database import Base


class RiskAnalysis(Base):
    __tablename__ = "risk_analysis"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    emotion_data_id = Column(String, ForeignKey("emotion_data.id"))
    risk_level = Column(String)          # LOW / MODERATE / HIGH
    result_summary = Column(String)
    analyzed_at = Column(DateTime, server_default=func.now())
