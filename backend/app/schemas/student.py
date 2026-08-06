from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import re

VALID_ROLES = ["student", "counselor", "admin", "management"]
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.\-]{3,30}$")


class StudentRegister(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = ""
    email: EmailStr
    password: str
    role: str = "student"
    department: Optional[str] = ""

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        # Username is optional at the API boundary. If omitted the route
        # derives one from the email local-part. If provided, enforce the
        # same rules the frontend uses so the two stay in sync.
        if v is None or v.strip() == "":
            return None
        v = v.strip()
        if not USERNAME_RE.match(v):
            raise ValueError(
                "Username must be 3–30 characters: letters, numbers, "
                "underscore, dot, or hyphen."
            )
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        # Required at the API boundary; empty strings are rejected so users
        # always have a display name.
        if v is None or not v.strip():
            raise ValueError("Full name is required.")
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters.")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in VALID_ROLES:
            raise ValueError(f"role must be one of {VALID_ROLES}")
        return v


class StudentLogin(BaseModel):
    """
    Login payload. The user types EITHER their username or their email in
    the `identifier` field. The role they selected on the login page is
    also sent so the server can refuse a wrong-role sign-in (e.g. a
    student account cannot sign in via the Counselor chip).
    """
    identifier: str
    password: str
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in VALID_ROLES:
            raise ValueError(f"role must be one of {VALID_ROLES}")
        return v


class StudentOut(BaseModel):
    id: str
    anonymous_id: str
    username: Optional[str] = ""
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
    username: Optional[str] = ""
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
