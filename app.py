import streamlit as st
from auth import login
from views.dashboard import show_dashboard
from views.assets import show_assets
from views.allocations import show_allocations
from views.maintenance import show_maintenance
from views.organization import show_organization
from views.users import show_users
from views.my_assets import show_my_assets
from views.notifications import show_notifications

st.set_page_config(page_title="AssetFlow", page_icon="⚡", layout="wide")


def show_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style='text-align:center; padding: 2rem 0;'>
                <h1 style='color:#4F46E5;'>⚡ AssetFlow</h1>
                <p style='color:#64748B;'>Enterprise Asset & Resource Management</p>
            </div>
        """, unsafe_allow_html=True)
        email = st.text_input("📧 Email", key="login_email")
        password = st.text_input("🔒 Password", type="password", key="login_password")
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
    show_login()
else:
    show_app()