"""
System Authentication Gateway
Handles registration and login for ALL roles:
student, counselor, advisor, admin, management.

Returns a JWT containing {sub: user_id, role: <role>}, used by
app.core.deps.require_roles() to enforce role-based access control.
"""
from typing import cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.student import Student
from app.core.security import hash_password, verify_password, create_access_token
from app.core.deps import get_current_user
from app.schemas.student import StudentRegister, StudentLogin, StudentAuthOut, StudentOut

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=StudentAuthOut)
def register(payload: StudentRegister, db: Session = Depends(get_db)):
    existing = db.query(Student).filter(Student.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")

    user = Student(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        department=payload.department,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id, "role": str(user.role)})
    return StudentAuthOut(
        access_token=token,
        role=str(user.role),
        user_id=str(user.id),
        anonymous_id=cast(str, user.anonymous_id),
        name=cast(str, user.name),
        email=cast(str, user.email),
    )


@router.post("/login", response_model=StudentAuthOut)
def login(payload: StudentLogin, db: Session = Depends(get_db)):
    user = db.query(Student).filter(Student.email == payload.email).first()
    if not user or not verify_password(payload.password, cast(str, user.hashed_password)):
        raise HTTPException(status_code=400, detail="Invalid email or password.")

    token = create_access_token({"sub": user.id, "role": str(user.role)})
    return StudentAuthOut(
        access_token=token,
        role=str(user.role),
        user_id=str(user.id),
        anonymous_id=cast(str, user.anonymous_id),
        name=cast(str, user.name),
        email=cast(str, user.email),
    )


@router.get("/me", response_model=StudentOut)
def get_my_profile(current_user: Student = Depends(get_current_user)):
    """Returns the logged-in user's profile — used by the frontend to
    decide which dashboard/sidebar items to show."""
    return current_user
