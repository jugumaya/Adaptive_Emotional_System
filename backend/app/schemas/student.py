from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

VALID_ROLES = ["student", "counselor", "advisor", "admin", "management"]


class StudentRegister(BaseModel):
    name: Optional[str] = ""
    email: EmailStr
    password: str
    role: str = "student"
    department: Optional[str] = ""

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in VALID_ROLES:
            raise ValueError(f"role must be one of {VALID_ROLES}")
        return v


class StudentLogin(BaseModel):
    email: EmailStr
    password: str


class StudentOut(BaseModel):
    id: str
    anonymous_id: str
    name: Optional[str] = ""
    email: str
    role: str
    department: Optional[str] = ""

    class Config:
        from_attributes = True


class StudentAuthOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    anonymous_id: str
    name: Optional[str] = ""
    email: str


class UserUpdate(BaseModel):
    """Used by Admin to edit any user (name, role, department)."""
    name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_ROLES:
            raise ValueError(f"role must be one of {VALID_ROLES}")
        return v
