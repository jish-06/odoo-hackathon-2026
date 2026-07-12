import sqlite3
import os
from datetime import date
from groq import Groq
from dotenv import load_dotenv
from db import get_db, init_db

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
init_db()

def ask_ai(prompt):
    res = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content
def get_dashboard_stats():
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
        available = conn.execute("SELECT COUNT(*) FROM assets WHERE status='Available'").fetchone()[0]
        allocated = conn.execute("SELECT COUNT(*) FROM assets WHERE status='Allocated'").fetchone()[0]
        maintenance = conn.execute("SELECT COUNT(*) FROM assets WHERE status='Under Maintenance'").fetchone()[0]
        active_bookings = conn.execute("SELECT COUNT(*) FROM allocations WHERE status='Active'").fetchone()[0]
        pending_maintenance = conn.execute("SELECT COUNT(*) FROM maintenance_requests WHERE status='Pending'").fetchone()[0]
        overdue = conn.execute("""
            SELECT COUNT(*) FROM allocations 
            WHERE status='Active' 
            AND expected_return_date < ? 
            AND expected_return_date IS NOT NULL
        """, (str(date.today()),)).fetchone()[0]
    return {
        "total": total,
        "available": available,
        "allocated": allocated,
        "maintenance": maintenance,
        "active_bookings": active_bookings,
        "pending_maintenance": pending_maintenance,
        "overdue": overdue
    }

def create_department(name):
    with get_db() as conn:
        conn.execute("INSERT INTO departments (name) VALUES (?)", (name,))
    return True

def get_all_departments():
    with get_db() as conn:
        return conn.execute("SELECT * FROM departments WHERE status='active'").fetchall()

def create_category(name):
    with get_db() as conn:
        conn.execute("INSERT INTO asset_categories (name) VALUES (?)", (name,))
    return True

def get_all_categories():
    with get_db() as conn:
        return conn.execute("SELECT * FROM asset_categories").fetchall()

def generate_asset_tag():
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
    return f"AF-{str(count + 1).zfill(4)}"

def register_asset(name, category_id, serial_number, location, condition="Good", is_bookable=0):
    tag = generate_asset_tag()
    with get_db() as conn:
        conn.execute("""
            INSERT INTO assets (name, asset_tag, category_id, serial_number, location, condition, is_bookable)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, tag, category_id, serial_number, location, condition, is_bookable))
    return tag

def get_all_assets():
    with get_db() as conn:
        return conn.execute("""
            SELECT a.*, c.name as category_name 
            FROM assets a
            LEFT JOIN asset_categories c ON a.category_id = c.id
        """).fetchall()

def get_asset_by_id(asset_id):
    with get_db() as conn:
        return conn.execute("SELECT * FROM assets WHERE id=?", (asset_id,)).fetchone()

def allocate_asset(asset_id, user_id, expected_return_date=None):
    with get_db() as conn:
        # conflict check
        existing = conn.execute("""
            SELECT al.*, u.name as holder_name
            FROM allocations al
            JOIN users u ON al.user_id = u.id
            WHERE al.asset_id=? AND al.status='Active'
        """, (asset_id,)).fetchone()

        if existing:
            return False, f"Asset currently held by {existing['holder_name']}"

        conn.execute("""
            INSERT INTO allocations (asset_id, user_id, allocated_date, expected_return_date, status)
            VALUES (?, ?, ?, ?, 'Active')
        """, (asset_id, user_id, str(date.today()), expected_return_date))

        conn.execute("UPDATE assets SET status='Allocated' WHERE id=?", (asset_id,))

    return True, "Asset allocated successfully!"

def return_asset(allocation_id, notes=""):
    with get_db() as conn:
        alloc = conn.execute(
            "SELECT * FROM allocations WHERE id=?", (allocation_id,)
        ).fetchone()

        if not alloc:
            return False, "Allocation not found"

        conn.execute("""
            UPDATE allocations 
            SET status='Returned', actual_return_date=?, notes=?
            WHERE id=?
        """, (str(date.today()), notes, allocation_id))

        conn.execute(
            "UPDATE assets SET status='Available' WHERE id=?", (alloc["asset_id"],)
        )

    return True, "Asset returned successfully!"

def get_active_allocations():
    with get_db() as conn:
        return conn.execute("""
            SELECT al.*, a.name as asset_name, a.asset_tag, u.name as user_name
            FROM allocations al
            JOIN assets a ON al.asset_id = a.id
            JOIN users u ON al.user_id = u.id
            WHERE al.status='Active'
        """).fetchall()

def get_overdue_allocations():
    with get_db() as conn:
        return conn.execute("""
            SELECT al.*, a.name as asset_name, u.name as user_name
            FROM allocations al
            JOIN assets a ON al.asset_id = a.id
            JOIN users u ON al.user_id = u.id
            WHERE al.status='Active'
            AND al.expected_return_date < ?
            AND al.expected_return_date IS NOT NULL
        """, (str(date.today()),)).fetchall()

def raise_maintenance(asset_id, user_id, description, priority="Medium"):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO maintenance_requests (asset_id, user_id, description, priority, status)
            VALUES (?, ?, ?, ?, 'Pending')
        """, (asset_id, user_id, description, priority))
    return True, "Maintenance request raised!"

def approve_maintenance(request_id):
    with get_db() as conn:
        req = conn.execute(
            "SELECT * FROM maintenance_requests WHERE id=?", (request_id,)
        ).fetchone()
        conn.execute(
            "UPDATE maintenance_requests SET status='Approved' WHERE id=?", (request_id,)
        )
        conn.execute(
            "UPDATE assets SET status='Under Maintenance' WHERE id=?", (req["asset_id"],)
        )
    return True, "Request approved!"

def resolve_maintenance(request_id):
    with get_db() as conn:
        req = conn.execute(
            "SELECT * FROM maintenance_requests WHERE id=?", (request_id,)
        ).fetchone()
        conn.execute(
            "UPDATE maintenance_requests SET status='Resolved' WHERE id=?", (request_id,)
        )
        conn.execute(
            "UPDATE assets SET status='Available' WHERE id=?", (req["asset_id"],)
        )
    return True, "Request resolved!"

def get_all_maintenance():
    with get_db() as conn:
        return conn.execute("""
            SELECT mr.*, a.name as asset_name, a.asset_tag, u.name as user_name
            FROM maintenance_requests mr
            JOIN assets a ON mr.asset_id = a.id
            JOIN users u ON mr.user_id = u.id
            ORDER BY mr.id DESC
        """).fetchall()

def get_all_users():
    with get_db() as conn:
        return conn.execute("SELECT id, name, email, role, status FROM users").fetchall()

def promote_user(user_id, role):
    with get_db() as conn:
        conn.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))
    return True

def add_notification(user_id, message):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO notifications (user_id, message, created_at)
            VALUES (?, ?, ?)
        """, (user_id, message, str(date.today())))

def get_notifications(user_id):
    with get_db() as conn:
        return conn.execute("""
            SELECT * FROM notifications 
            WHERE user_id=? 
            ORDER BY id DESC LIMIT 20
        """, (user_id,)).fetchall()
def get_user_by_id(user_id):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE id=?", (user_id,)
        ).fetchone()

def get_user_allocations(user_id):
    with get_db() as conn:
        return conn.execute("""
            SELECT al.*, a.name as asset_name, a.asset_tag
            FROM allocations al
            JOIN assets a ON al.asset_id = a.id
            WHERE al.user_id=? AND al.status='Active'
        """, (user_id,)).fetchall()