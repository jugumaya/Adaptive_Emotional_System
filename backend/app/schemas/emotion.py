from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MoodSubmit(BaseModel):
    # Optional: if the user is logged in, student_id is taken from their token.
    # If not logged in (demo/anonymous mode), student_id may be passed directly.
    student_id: Optional[str] = None
    mood_score: int = Field(..., ge=1, le=10, description="1 = very low, 10 = very high")
    mood_type: Optional[str] = ""
    notes: Optional[str] = ""


class MoodOut(BaseModel):
    id: str
    mood_score: int
    risk_level: str
    intervention: str

    class Config:
        from_attributes = True


class MoodHistoryItem(BaseModel):
    id: str
    score: int
    timestamp: Optional[datetime] = None
    type: str
    notes: str
    risk_level: str
