"""
System Authentication Gateway
Handles registration and login for ALL roles:
student, counselor, admin, management.

Registration collects:  username, full name, email, password, role, department
Login accepts:           username OR email + password + role
    The role sent with the login MUST match the role stored on the account.
    This prevents, e.g., a student from signing in via the Counselor chip.

Returns a JWT containing {sub: user_id, role: <role>}, used by
app.core.deps.require_roles() to enforce role-based access control.
"""
from typing import Optional, cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.student import Student
from app.core.security import hash_password, verify_password, create_access_token
from app.core.deps import get_current_user
from app.schemas.student import StudentRegister, StudentLogin, StudentAuthOut, StudentOut

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _derive_username(email: str) -> str:
    """Fallback when the user didn't pick a username at registration."""
    return email.split("@", 1)[0]


@router.post("/register", response_model=StudentAuthOut)
def register(payload: StudentRegister, db: Session = Depends(get_db)):
    # Email must be unique.
    existing = db.query(Student).filter(Student.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")

    # Username must be unique too. If the user didn't pick one, derive it
    # from the email local-part. If that derived value collides, the user
    # has to pick a different one.
    requested_username: Optional[str] = payload.username or None
    chosen_username = requested_username or _derive_username(payload.email)

    if db.query(Student).filter(Student.username == chosen_username).first():
        raise HTTPException(
            status_code=400,
            detail=(
                f"Username '{chosen_username}' is already taken. "
                "Please pick a different one."
            ),
        )

    user = Student(
        name=payload.name,
        username=chosen_username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        department=payload.department,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # We deliberately do NOT issue an access_token here. The user must
    # then go to /ui/login and authenticate with their credentials —
    # same flow as any normal website.
    return StudentAuthOut(
        access_token="",
        role=str(user.role),
        user_id=str(user.id),
        anonymous_id=cast(str, user.anonymous_id),
        username=cast(str, user.username),
        name=cast(str, user.name),
        email=cast(str, user.email),
    )


@router.post("/login", response_model=StudentAuthOut)
def login(payload: StudentLogin, db: Session = Depends(get_db)):
    if not payload.identifier or not payload.password:
        raise HTTPException(status_code=400, detail="Email/username and password are required.")

    ident = payload.identifier.strip()
    # Allow login by EITHER username OR email. The DB has unique indexes
    # on both, so a single query is enough.
    user = (
        db.query(Student)
        .filter((Student.email == ident) | (Student.username == ident))
        .first()
    )

    if not user or not verify_password(payload.password, cast(str, user.hashed_password)):
        # Same message for both branches — don't leak whether the email exists.
        raise HTTPException(status_code=400, detail="Invalid email/username or password.")

    # Enforce that the role selected on the login page matches the role
    # stored on the account. If not, return a clear 403.
    if str(user.role) != payload.role:
        raise HTTPException(
            status_code=403,
            detail=(
                f"This account is registered as '{user.role}'. "
                f"Please select the '{user.role}' option on the sign-in page."
            ),
        )

    token = create_access_token({"sub": user.id, "role": str(user.role)})
    return StudentAuthOut(
        access_token=token,
        role=str(user.role),
        user_id=str(user.id),
        anonymous_id=cast(str, user.anonymous_id),
        username=cast(str, user.username) if user.username else "",
        name=cast(str, user.name),
        email=cast(str, user.email),
    )


@router.get("/me", response_model=StudentOut)
def get_my_profile(current_user: Student = Depends(get_current_user)):
    """Returns the logged-in user's profile — used by the frontend to
    decide which dashboard/sidebar items to show."""
    return current_user
