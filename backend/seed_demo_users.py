"""
Seed script — creates one demo account per role so you can log in
immediately and test all 5 dashboards.

Run with:
    cd backend
    python seed_demo_users.py

Demo credentials (all use password: demo1234):
    student@aee.edu      -> Student
    counselor@aee.edu    -> Counselor
    advisor@aee.edu      -> Advisor
    admin@aee.edu        -> Admin
    management@aee.edu   -> University Management
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, Base, engine
from app.models.student import Student
from app.models.emotion_data import EmotionData   # noqa: F401
from app.models.risk_analysis import RiskAnalysis  # noqa: F401
from app.models.intervention import Intervention   # noqa: F401
from app.models.report import Report               # noqa: F401
from app.models.guidance import GuidanceNote        # noqa: F401
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)

DEMO_USERS = [
    {"name": "Demo Student",    "email": "student@aee.edu",    "role": "student",   "department": "CSE"},
    {"name": "Demo Counselor",  "email": "counselor@aee.edu",  "role": "counselor", "department": ""},
    {"name": "Demo Advisor",    "email": "advisor@aee.edu",    "role": "advisor",   "department": ""},
    {"name": "Demo Admin",      "email": "admin@aee.edu",      "role": "admin",     "department": ""},
    {"name": "Demo Management", "email": "management@aee.edu", "role": "management", "department": ""},
]

PASSWORD = "demo1234"


def main():
    db = SessionLocal()
    created, skipped = 0, 0

    for u in DEMO_USERS:
        existing = db.query(Student).filter(Student.email == u["email"]).first()
        if existing:
            print(f"  - {u['email']} already exists, skipping.")
            skipped += 1
            continue

        user = Student(
            name=u["name"],
            email=u["email"],
            hashed_password=hash_password(PASSWORD),
            role=u["role"],
            department=u["department"],
        )
        db.add(user)
        created += 1
        print(f"  + Created {u['role']:<12} -> {u['email']}")

    db.commit()
    db.close()

    print(f"\nDone. Created {created}, skipped {skipped}.")
    print(f"All demo accounts use password: {PASSWORD}")


if __name__ == "__main__":
    main()
