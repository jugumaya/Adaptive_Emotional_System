from app.db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    tables = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")).fetchall()
    print("Tables:")
    for (table_name,) in tables:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        print(f"- {table_name}: {count} row(s)")
