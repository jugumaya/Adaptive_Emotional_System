"""
Shared FastAPI dependencies for authentication and role-based access control (RBAC).

Roles supported across the AEE platform:
    student     - submits mood check-ins, views own history
    counselor   - views alerts/trends, submits guidance notes
    advisor     - same access as counselor (alias role)
    admin       - full system access, user management
    management  - university management, read-only aggregated reports
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.student import Student
from app.core.security import decode_token, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

VALID_ROLES = ["student", "counselor", "advisor", "admin", "management"]


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Student:
    """Require a valid token. Returns the authenticated user (any role)."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token.",
        )
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or session expired.",
        )

    user_id = payload.get("sub")
    user = db.query(Student).filter(Student.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists.",
        )
    return user


def get_optional_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Like get_current_user, but returns None instead of raising if no/invalid token.
    Used for endpoints that work both anonymously and when logged in (e.g. mood submit)."""
    if not token:
        return None
    try:
        payload = decode_token(token)
    except JWTError:
        return None
    return db.query(Student).filter(Student.id == payload.get("sub")).first()


def require_roles(*roles: str):
    """Dependency factory: restrict an endpoint to one or more roles.

    Usage:
        @router.get("/admin-only")
        def x(user: Student = Depends(require_roles("admin"))): ...
    """

    def checker(user: Student = Depends(get_current_user)) -> Student:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. This endpoint requires one of roles: {list(roles)}.",
            )
        return user

    return checker
