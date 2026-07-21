"""
Admin System Control routes — Admin role only.

Provides full CRUD over the Users table (all roles), plus
system-wide metrics for the Admin dashboard.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.student import Student
from app.models.risk_analysis import RiskAnalysis
from app.models.emotion_data import EmotionData
from app.core.security import hash_password
from app.core.deps import require_roles
from app.schemas.student import StudentRegister, StudentOut, UserUpdate
from app.services.report_service import generate_role_distribution

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ---------- READ ----------

@router.get("/users", response_model=list[StudentOut])
def get_all_users(
    db: Session = Depends(get_db),
    current_admin: Student = Depends(require_roles("admin")),
):
    return db.query(Student).order_by(Student.created_at.desc()).all()


@router.get("/users/{user_id}", response_model=StudentOut)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(require_roles("admin")),
):
    user = db.query(Student).filter(Student.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.get("/metrics")
def get_metrics(
    db: Session = Depends(get_db),
    current_admin: Student = Depends(require_roles("admin")),
):
    return {
        "total_users": db.query(Student).count(),
        "total_logs": db.query(EmotionData).count(),
        "role_distribution": generate_role_distribution(db),
        "risk_breakdown": {
            "low": db.query(RiskAnalysis).filter(RiskAnalysis.risk_level == "LOW").count(),
            "moderate": db.query(RiskAnalysis).filter(RiskAnalysis.risk_level == "MODERATE").count(),
            "high": db.query(RiskAnalysis).filter(RiskAnalysis.risk_level == "HIGH").count(),
        },
    }


# ---------- CREATE ----------

@router.post("/users", response_model=StudentOut, status_code=201)
def create_user(
    payload: StudentRegister,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(require_roles("admin")),
):
    """Admin can directly create a user with any role
    (e.g. add a new Counselor or University Management account)."""
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
    return user


# ---------- UPDATE ----------

@router.put("/users/{user_id}", response_model=StudentOut)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(require_roles("admin")),
):
    user = db.query(Student).filter(Student.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if payload.name is not None:
        setattr(user, "name", payload.name)
    if payload.role is not None:
        setattr(user, "role", payload.role)
    if payload.department is not None:
        setattr(user, "department", payload.department)

    db.commit()
    db.refresh(user)
    return user


# ---------- DELETE ----------

@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_admin: Student = Depends(require_roles("admin")),
):
    target = db.query(Student).filter(Student.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found.")
    if str(target.role) == "admin" and str(target.id) == str(current_admin.id):
        raise HTTPException(status_code=400, detail="You cannot delete your own admin account.")

    db.delete(target)
    db.commit()
    return {"message": f"User '{target.email}' deleted successfully."}
