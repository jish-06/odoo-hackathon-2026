from db import get_db

with get_db() as conn:
    conn.execute("UPDATE users SET role='admin' WHERE email='your_test_email@example.com'")
    print("Done — user promoted to admin.")