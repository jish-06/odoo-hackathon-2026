import streamlit as st
from auth import login
from reports import show_reports
from audit import show_audit
from frontend import (
    show_dashboard, show_assets, show_allocations, show_my_assets,
    show_maintenance, show_organization, show_users, show_notifications,
    show_resource_booking
)

st.set_page_config(
    page_title="AssetFlow",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"  # ← fixes disappearing sidebar
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# ── GLOBAL STYLES ─────────────────────────────────
def inject_styles():
    st.markdown("""
        <style>
        /* hide streamlit branding */
        footer {visibility: hidden;}

        /* metric cards */
        div[data-testid="metric-container"] {
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        div[data-testid="metric-container"] label {
            color: #94A3B8 !important;
            font-size: 0.75rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        div[data-testid="stMetricValue"] {
            color: #F1F5F9 !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }

        /* buttons */
        div[data-testid="stButton"] button {
            border-radius: 8px;
            font-weight: 600;
            border: none;
            transition: all 0.2s ease;
        }
        div[data-testid="stButton"] button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(99,102,241,0.4);
        }

        /* inputs */
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stNumberInput"] input {
            border-radius: 8px;
            border: 1px solid #334155 !important;
            background: #1E293B !important;
            color: #F1F5F9 !important;
        }

        /* selectbox */
        div[data-testid="stSelectbox"] > div > div {
            border-radius: 8px;
            border: 1px solid #334155 !important;
            background: #1E293B !important;
        }

        /* tabs */
        div[data-testid="stTabs"] button[data-baseweb="tab"] {
            font-weight: 600;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
        }

        /* dataframe */
        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #334155;
        }

        /* sidebar */
        section[data-testid="stSidebar"] {
            background: #0A0F1E !important;
            border-right: 1px solid #1E293B;
        }
        section[data-testid="stSidebar"] > div {
            padding-top: 0;
        }

        /* radio buttons in sidebar */
        div[data-testid="stSidebar"] .stRadio label {
            color: #94A3B8 !important;
            font-size: 0.9rem;
            padding: 6px 0;
        }
        div[data-testid="stSidebar"] .stRadio label:hover {
            color: #F1F5F9 !important;
        }

        /* alerts */
        div[data-testid="stAlert"] {
            border-radius: 10px;
            border: none;
        }

        /* divider */
        hr {
            border-color: #1E293B !important;
        }

        /* page titles */
        h1 {
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            color: #F1F5F9 !important;
            letter-spacing: -0.5px;
        }
        h2 {
            font-size: 1.2rem !important;
            color: #CBD5E1 !important;
        }
        h3 {
            font-size: 1rem !important;
            color: #94A3B8 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ── SIGNUP ────────────────────────────────────────
def show_signup():
    from auth import signup
    inject_styles()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style='text-align:center; padding:2rem 0 1rem 0;'>
                <div style='display:inline-flex; align-items:center;
                gap:10px; margin-bottom:1.5rem;'>
                    <div style='background:#6366F1; width:40px; height:40px;
                    border-radius:10px; display:flex; align-items:center;
                    justify-content:center;'>
                        <span style='color:white; font-weight:900;
                        font-size:1.2rem;'>A</span>
                    </div>
                    <span style='color:#F1F5F9; font-weight:700;
                    font-size:1.5rem; letter-spacing:1px;'>ASSET
                    <span style='color:#818CF8; font-weight:300;'>FLOW</span>
                    </span>
                </div>
                <h2 style='color:#94A3B8; font-weight:400;
                font-size:1rem;'>Create your account</h2>
            </div>
        """, unsafe_allow_html=True)

        name = st.text_input("Full name")
        email = st.text_input("Email", placeholder="name@company.com")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm password", type="password")

        st.write("")
        if st.button("Create Account", use_container_width=True):
            if not name or not email or not password:
                st.error("All fields are required!")
            elif password != confirm:
                st.error("Passwords do not match!")
            else:
                ok, msg = signup(name, email, password)
                if ok:
                    st.success(msg)
                    st.session_state.show_signup = False
                    st.rerun()
                else:
                    st.error(msg)

        if st.button("Back to Login", use_container_width=True):
            st.session_state.show_signup = False
            st.rerun()

# ── LOGIN ─────────────────────────────────────────
def show_login():
    inject_styles()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style='text-align:center; padding:3rem 0 2rem 0;'>
                <div style='display:inline-flex; align-items:center;
                gap:12px; margin-bottom:0.5rem;'>
                    <div style='background:linear-gradient(135deg,#6366F1,#4F46E5);
                    width:48px; height:48px; border-radius:12px;
                    display:flex; align-items:center; justify-content:center;
                    box-shadow:0 4px 16px rgba(99,102,241,0.4);'>
                        <span style='color:white; font-weight:900;
                        font-size:1.4rem;'>A</span>
                    </div>
                    <div style='text-align:left;'>
                        <div style='color:#F1F5F9; font-weight:700;
                        font-size:1.6rem; letter-spacing:2px;
                        line-height:1;'>ASSET<span style='color:#818CF8;
                        font-weight:300;'>FLOW</span></div>
                        <div style='color:#475569; font-size:0.7rem;
                        letter-spacing:2px; text-transform:uppercase;
                        margin-top:2px;'>Enterprise Asset Management</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        email = st.text_input("Email", placeholder="name@company.com",
                              key="login_email")
        password = st.text_input("Password", type="password",
                                 key="login_password")
        st.write("")

        if st.button("Sign In", use_container_width=True):
            if not email or not password:
                st.error("Please fill in both fields!")
            else:
                user = login(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid email or password")

        st.divider()
        st.caption("New here? Sign up creates an Employee account. "
                   "Admin assigns roles from the User Management panel.")
        if st.button("Create Account", use_container_width=True):
            st.session_state.show_signup = True
            st.rerun()

# ── SIDEBAR ───────────────────────────────────────
def show_sidebar():
    user = st.session_state.user
    role = user["role"]

    NAV = {
        "admin": [
            "Dashboard", "Assets", "Allocations", "Maintenance",
            "Organization", "Users", "Audit", "Reports",
            "Resource Booking", "Notifications"
        ],
        "asset_manager": [
            "Dashboard", "Assets", "Allocations",
            "Maintenance", "Audit", "Reports", "Notifications"
        ],
        "dept_head": [
            "Dashboard", "Allocations", "Maintenance", "Notifications"
        ],
        "employee": [
            "Dashboard", "My Assets", "Maintenance", "Notifications"
        ]
    }

    ICONS = {
        "Dashboard": "▣",
        "Assets": "◈",
        "Allocations": "◉",
        "Maintenance": "◎",
        "Organization": "◫",
        "Users": "◯",
        "Audit": "◬",
        "Reports": "◱",
        "Resource Booking": "◰",
        "Notifications": "◷",
        "My Assets": "◉"
    }

    pages = NAV.get(role, NAV["employee"])

    with st.sidebar:
        st.markdown(f"""
            <div style='padding:1.5rem 1rem 1rem 1rem;
            border-bottom:1px solid #1E293B;'>
                <div style='display:flex; align-items:center; gap:10px;'>
                    <div style='background:linear-gradient(135deg,#6366F1,#4338CA);
                    width:36px; height:36px; border-radius:9px;
                    display:flex; align-items:center; justify-content:center;
                    box-shadow:0 2px 8px rgba(99,102,241,0.4); flex-shrink:0;'>
                        <span style='color:white; font-weight:900;
                        font-size:1.1rem;'>A</span>
                    </div>
                    <div>
                        <div style='color:#F1F5F9; font-weight:700;
                        font-size:1rem; letter-spacing:1.5px;
                        line-height:1.1;'>ASSET<span style='color:#818CF8;
                        font-weight:300;'>FLOW</span></div>
                        <div style='color:#475569; font-size:0.6rem;
                        letter-spacing:1.5px; text-transform:uppercase;'>
                        Enterprise ERP</div>
                    </div>
                </div>
            </div>
            <div style='padding:1rem; border-bottom:1px solid #1E293B;
            margin-bottom:0.5rem;'>
                <div style='background:#0F172A; border-radius:8px;
                padding:0.7rem 0.8rem; border:1px solid #1E293B;'>
                    <div style='color:#475569; font-size:0.65rem;
                    text-transform:uppercase; letter-spacing:1px;'>
                    Signed in as</div>
                    <div style='color:#F1F5F9; font-weight:600;
                    font-size:0.9rem; margin-top:2px;'>{user['name']}</div>
                    <div style='display:inline-block; background:#1E1B4B;
                    color:#818CF8; padding:1px 8px; border-radius:4px;
                    font-size:0.65rem; font-weight:600; margin-top:4px;
                    letter-spacing:0.5px;'>
                    {role.replace("_"," ").upper()}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "Navigation",
            pages,
            format_func=lambda x: f"  {ICONS.get(x,'·')}  {x}",
            label_visibility="collapsed"
        )

        st.divider()
        if st.button("Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

    return page

# ── ROUTER ────────────────────────────────────────
def show_app():
    inject_styles()
    page = show_sidebar()

    if page == "Dashboard":
        show_dashboard()
    elif page == "Assets":
        show_assets()
    elif page == "Allocations":
        show_allocations()
    elif page == "My Assets":
        show_my_assets()
    elif page == "Maintenance":
        show_maintenance()
    elif page == "Organization":
        show_organization()
    elif page == "Users":
        show_users()
    elif page == "Audit":
        show_audit()
    elif page == "Reports":
        show_reports()
    elif page == "Resource Booking":
        show_resource_booking()
    elif page == "Notifications":
        show_notifications()

# ── ENTRY POINT ───────────────────────────────────
if st.session_state.logged_in:
    show_app()
elif st.session_state.get("show_signup"):
    show_signup()
else:
    show_login()