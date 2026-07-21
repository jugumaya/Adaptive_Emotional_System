from app.db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    columns_result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='notifications' ORDER BY ordinal_position"))
    columns = [row[0] for row in columns_result.fetchall()]

    query = f"SELECT {', '.join(columns)} FROM notifications ORDER BY created_at"
    result = conn.execute(text(query))
    rows = result.fetchall()

    print("Notifications table:")
    for row in rows:
        print(dict(zip(columns, row)))
