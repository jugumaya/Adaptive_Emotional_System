from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AlertOut(BaseModel):
    """Anonymized high-risk alert for the counselor dashboard."""
    anonymous_id: str
    mood_score: int
    risk_level: str
    result_summary: str
    timestamp: Optional[datetime] = None


class GuidanceCreate(BaseModel):
    student_anonymous_id: Optional[str] = None   # leave blank for general guidance
    message: str


class GuidanceOut(BaseModel):
    id: str
    counselor_id: str
    counselor_name: Optional[str] = ""
    student_anonymous_id: Optional[str] = None
    message: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
