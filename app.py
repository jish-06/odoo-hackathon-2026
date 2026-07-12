import streamlit as st
from auth import login
from reports import show_reports
from audit import show_audit
from frontend import (
    show_dashboard, show_assets, show_allocations, show_my_assets,
    show_maintenance, show_organization, show_users, show_notifications,
    show_resource_booking
)

st.set_page_config(page_title="AssetFlow", page_icon="⚡", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

# ── SIGNUP ────────────────────────────────────────
def show_signup():
    from auth import signup
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align:center; color:#4F46E5;'>Create your account</h2>",
                    unsafe_allow_html=True)
        name = st.text_input("Full name")
        email = st.text_input("Email", placeholder="name@company.com")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm password", type="password")

        if st.button("Create Account", use_container_width=True):
            if not name or not email or not password:
                st.error("All fields are required!")
            elif password != confirm:
                st.error("Passwords don't match!")
            else:
                ok, msg = signup(name, email, password)
                if ok:
                    st.success(msg)
                    st.session_state.show_signup = False
                    st.rerun()
                else:
                    st.error(msg)

        if st.button("← Back to login", use_container_width=True):
            st.session_state.show_signup = False
            st.rerun()

# ── LOGIN ─────────────────────────────────────────
def show_login():
    st.markdown("""
        <style>
        div[data-testid="stTextInput"] input {
            border-radius: 20px;
            padding: 10px 16px;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style='text-align:center; padding: 1.5rem 0 0.5rem 0;'>
                <h2 style='color:#4F46E5; margin-bottom:0;'>⚡ AssetFlow</h2>
                <p style='color:#64748B;'>Enterprise Asset & Resource Management</p>
            </div>
        """, unsafe_allow_html=True)

        email = st.text_input("Email", placeholder="name@company.com", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Sign In →", use_container_width=True):
            if not email or not password:
                st.error("Please fill in both fields!")
            else:
                user = login(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password!")

        st.divider()
        st.markdown("**New here?**")
        st.caption("Sign up creates an employee account. Admin roles are assigned later.")
        if st.button("Create Account →", use_container_width=True):
            st.session_state.show_signup = True
            st.rerun()

# ── SIDEBAR ───────────────────────────────────────
def show_sidebar():
    user = st.session_state.user
    with st.sidebar:
        st.markdown(f"""
            <div style='text-align:center; padding:1rem 0;'>
                <h2 style='color:#4F46E5;'>⚡ AssetFlow</h2>
                <h4>{user['name']}</h4>
                <span style='background:#EEF2FF; color:#4F46E5;
                padding:2px 12px; border-radius:20px; font-size:0.8rem;'>
                {user['role'].upper()}</span>
            </div>
        """, unsafe_allow_html=True)
        st.divider()

        role = user["role"]

        if role == "admin":
            pages = [
                "🏠 Dashboard", "📦 Assets", "👥 Allocations",
                "🔧 Maintenance", "🏢 Organization", "👤 Users",
                "🕵️ Audit", "📊 Reports", "🗓️ Resource Booking",
                "🔔 Notifications"
            ]
        elif role == "asset_manager":
            pages = [
                "🏠 Dashboard", "📦 Assets", "👥 Allocations",
                "🔧 Maintenance", "🕵️ Audit", "📊 Reports",
                "🔔 Notifications"
            ]
        elif role == "dept_head":
            pages = [
                "🏠 Dashboard", "👥 Allocations",
                "🔧 Maintenance", "🔔 Notifications"
            ]
        else:  # employee
            pages = [
                "🏠 Dashboard", "👥 My Assets",
                "🔧 Maintenance", "🔔 Notifications"
            ]

        page = st.radio("Navigate", pages)
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

    return page

# ── ROUTER ────────────────────────────────────────
def show_app():
    page = show_sidebar()

    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📦 Assets":
        show_assets()
    elif page == "👥 Allocations":
        show_allocations()
    elif page == "👥 My Assets":
        show_my_assets()
    elif page == "🔧 Maintenance":
        show_maintenance()
    elif page == "🏢 Organization":
        show_organization()
    elif page == "👤 Users":
        show_users()
    elif page == "🕵️ Audit":
        show_audit()
    elif page == "📊 Reports":
        show_reports()
    elif page == "🗓️ Resource Booking":
        show_resource_booking()
    elif page == "🔔 Notifications":
        show_notifications()

# ── ENTRY POINT ───────────────────────────────────
if st.session_state.logged_in:
    show_app()
elif st.session_state.get("show_signup"):
    show_signup()
else:
    show_login()