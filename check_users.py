from db import get_db

with get_db() as conn:
    for row in conn.execute("SELECT id, name, email, role FROM users"):
        print(dict(row))