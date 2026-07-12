import streamlit as st
from auth import login
from frontend import (
    show_dashboard, show_assets, show_allocations, show_my_assets,
    show_maintenance, show_organization, show_users, show_notifications
)

st.set_page_config(page_title="AssetFlow", page_icon="⚡", layout="wide")


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


def show_login():
    st.markdown("""
        <style>
        div[data-testid="stTextInput"] input {
            border-radius: 20px;
            padding: 10px 16px;
        }
        .af-avatar {
            width: 56px; height: 56px; border-radius: 50%;
            background: #EEF2FF; color: #4F46E5;
            display: flex; align-items: center; justify-content: center;
            font-weight: 600; font-size: 1.1rem;
            margin: 0 auto 1rem auto;
        }
        .af-divider {
            border-top: 1px solid #333; margin: 1.5rem 0 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style='text-align:center; padding: 1.5rem 0 0.5rem 0;'>
                <h2 style='color:#4F46E5; margin-bottom:0;'>⚡ AssetFlow – login</h2>
                <div class='af-avatar'>AF</div>
            </div>
        """, unsafe_allow_html=True)

        email = st.text_input("Email", placeholder="name@company.com", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        st.markdown(
            "<div style='text-align:right; font-size:0.85rem;'>"
            "<a href='#'>Forgot password</a></div>",
            unsafe_allow_html=True
        )

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

        st.markdown("<div class='af-divider'></div>", unsafe_allow_html=True)
        st.markdown("**New here?**")
        st.caption("Sign up creates an employee account. Admin roles are assigned later.")

        if st.button("Create Account", use_container_width=True):
            st.session_state.show_signup = True
            st.rerun()


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
            pages = ["🏠 Dashboard", "📦 Assets", "👥 Allocations",
                     "🔧 Maintenance", "🏢 Organization", "👤 Users", "🔔 Notifications"]
        elif role == "asset_manager":
            pages = ["🏠 Dashboard", "📦 Assets", "👥 Allocations",
                     "🔧 Maintenance", "🔔 Notifications"]
        elif role == "dept_head":
            pages = ["🏠 Dashboard", "👥 Allocations", "🔧 Maintenance", "🔔 Notifications"]
        else:
            pages = ["🏠 Dashboard", "👥 My Assets", "🔧 Maintenance", "🔔 Notifications"]

        page = st.radio("Navigate", pages)
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    return page


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
    elif page == "🔔 Notifications":
        show_notifications()


if "logged_in" not in st.session_state:
    if st.session_state.get("show_signup"):
        show_signup()
    else:
        show_login()
else:
    show_app()