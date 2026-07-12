import bcrypt
from db import get_db

def init_users_table():
    pass  # db.py handles this now

def hash_password(plain):
    return bcrypt.hashpw(
        plain.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

def verify_password(plain, hashed):
    return bcrypt.checkpw(
        plain.encode("utf-8"),
        hashed.encode("utf-8")
    )

def create_user(name, email, password, role="employee"):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, hash_password(password), role)
        )

def login(email, password):
    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE email=?", (email,)
        ).fetchone()
    if user and verify_password(password, user["password"]):
        return dict(user)
    return None