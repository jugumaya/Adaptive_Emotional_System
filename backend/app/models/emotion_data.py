# Matches Class Diagram: EmotionData class
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from app.db.database import Base


class EmotionData(Base):
    __tablename__ = "emotion_data"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"), nullable=True)
    mood_score = Column(Integer, nullable=False)     # 1-10
    mood_type = Column(String, default="")           # happy, anxious, sad, etc.
    notes = Column(String, default="")
    interaction_pattern = Column(String, default="")
    timestamp = Column(DateTime, server_default=func.now())
