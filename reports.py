import streamlit as st
import pandas as pd

def get_utilization_by_department():
    return [
        {"department": "Engineering", "count": 34},
        {"department": "Sales", "count": 21},
        {"department": "HR", "count": 12},
        {"department": "Facilities", "count": 18},
        {"department": "IT", "count": 27},
    ]

def get_maintenance_frequency():
    return [
        {"month": "Feb", "count": 5},
        {"month": "Mar", "count": 8},
        {"month": "Apr", "count": 6},
        {"month": "May", "count": 11},
        {"month": "Jun", "count": 9},
        {"month": "Jul", "count": 14},
    ]

def get_most_used_assets():
    return [
        {"asset": "Room B2", "metric": "39 bookings this month"},
        {"asset": "Van AF-3413", "metric": "21 trips this month"},
        {"asset": "Projector AF-3351", "metric": "18 uses"},
    ]

def get_idle_assets():
    return [
        {"asset": "Camera AF-0301", "metric": "Unused 60+ days"},
        {"asset": "Chair AF-0410", "metric": "Unused 45 days"},
    ]

def get_assets_due_for_maintenance():
    return [
        {"asset": "Forklift AF-0087", "metric": "Service due in 5 days"},
        {"asset": "Laptop AF-0020", "metric": "4 years old, nearing retirement"},
    ]

def stat_card(label, value, color="#6366F1"):
    st.markdown(f"""
        <div style='background:#1E293B; border-radius:12px;
        padding:1rem 1.2rem; border:1px solid #334155;
        border-left:3px solid {color};'>
            <div style='color:#94A3B8; font-size:0.7rem;
            text-transform:uppercase; letter-spacing:1px;'>{label}</div>
            <div style='color:#F1F5F9; font-size:0.95rem;
            font-weight:600; margin-top:4px;'>{value}</div>
        </div>
    """, unsafe_allow_html=True)

def show_reports():
    st.title("Reports & Analytics")
    st.caption("Operational insights across assets, maintenance, and resource usage.")
    st.divider()

    user = st.session_state.user
    if user["role"] not in ["admin", "asset_manager"]:
        st.error("You don't have permission to view this page.")
        return

    # ── CHARTS ────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Utilization by Department")
        util_df = pd.DataFrame(get_utilization_by_department())
        st.bar_chart(
            util_df.set_index("department")["count"],
            use_container_width=True,
            color="#6366F1"
        )

    with col2:
        st.subheader("Maintenance Frequency")
        maint_df = pd.DataFrame(get_maintenance_frequency())
        st.line_chart(
            maint_df.set_index("month")["count"],
            use_container_width=True,
            color="#22C55E"
        )

    st.divider()

    # ── ASSET LISTS ───────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Most Used Assets")
        for item in get_most_used_assets():
            stat_card(item["asset"], item["metric"], "#6366F1")
            st.write("")

    with col4:
        st.subheader("Idle Assets")
        for item in get_idle_assets():
            stat_card(item["asset"], item["metric"], "#F59E0B")
            st.write("")

    st.divider()

    # ── MAINTENANCE DUE ───────────────────────────
    st.subheader("Due for Maintenance / Nearing Retirement")
    cols = st.columns(len(get_assets_due_for_maintenance()))
    for i, item in enumerate(get_assets_due_for_maintenance()):
        with cols[i]:
            stat_card(item["asset"], item["metric"], "#EF4444")

    st.divider()

    # ── EXPORT ────────────────────────────────────
    col_a, col_b, col_c = st.columns([2, 1, 2])
    with col_b:
        export_df = pd.DataFrame(
            get_most_used_assets() +
            get_idle_assets() +
            get_assets_due_for_maintenance()
        )
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Export Report as CSV",
            data=csv,
            file_name="assetflow_report.csv",
            mime="text/csv",
            use_container_width=True
        )