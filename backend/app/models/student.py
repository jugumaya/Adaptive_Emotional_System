# Unified Users table — holds all 4 roles:
# student, counselor, admin, management
# Table name kept as "students" for backward compatibility with existing data.
import uuid
from sqlalchemy import Column, String, DateTime, func
from app.db.database import Base

VALID_ROLES = ["student", "counselor", "admin", "management"]


class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    anonymous_id = Column(String, unique=True, default=lambda: "anon_" + str(uuid.uuid4())[:8])
    name = Column(String, nullable=True, default="")
    # `username` is a short, human-remembered identifier the user picks at
    # registration. It must be globally unique. Lookups for login accept
    # EITHER the username OR the email (whichever the user types).
    username = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="student")          # one of VALID_ROLES
    department = Column(String, nullable=True, default="")  # e.g. CSE, BBA (for students/management views)
    created_at = Column(DateTime, server_default=func.now())
