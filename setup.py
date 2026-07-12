from db import get_db, init_db
from auth import hash_password

init_db()

USERS = [
    ("Admin User", "admin@assetflow.com", "admin@123", "admin"),
    ("Asset Manager", "manager@assetflow.com", "manager@123", "asset_manager"),
    ("Dept Head", "head@assetflow.com", "head@123", "dept_head"),
    ("Employee One", "emp@assetflow.com", "emp@123", "employee"),
]

with get_db() as conn:
    conn.execute("DELETE FROM users")
    conn.execute("DELETE FROM sqlite_sequence WHERE name='users'")

    for name, email, password, role in USERS:
        conn.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, hash_password(password), role)
        )

print("Setup complete! 4 users seeded fresh.")