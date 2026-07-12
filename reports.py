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
        {"asset": "Camera AF-0301", "metric": "unused 60+ days"},
        {"asset": "Chair AF-0410", "metric": "unused 45 days"},
    ]

def get_assets_due_for_maintenance():
    return [
        {"asset": "Forklift AF-0087", "metric": "service due in 5 days"},
        {"asset": "Laptop AF-0020", "metric": "4 years old, nearing retirement"},
    ]
# --- end placeholder section ---


def show_reports():
    st.title("📊 Reports & Analytics")
    user = st.session_state.user
    if user["role"] not in ["admin", "asset_manager"]:
        st.error("You don't have permission to view this page.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Utilization by Department")
        util_df = pd.DataFrame(get_utilization_by_department())
        st.bar_chart(util_df.set_index("department")["count"])

    with col2:
        st.subheader("Maintenance Frequency")
        maint_df = pd.DataFrame(get_maintenance_frequency())
        st.line_chart(maint_df.set_index("month")["count"])

    st.divider()

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("**Most used assets**")
        for item in get_most_used_assets():
            st.write(f"- {item['asset']}: {item['metric']}")

    with col4:
        st.markdown("**Idle assets**")
        for item in get_idle_assets():
            st.write(f"- {item['asset']}: {item['metric']}")

    st.divider()
    st.markdown("**Assets due for maintenance / nearing retirement**")
    for item in get_assets_due_for_maintenance():
        st.write(f"- {item['asset']}: {item['metric']}")

    st.divider()
    export_df = pd.DataFrame(get_most_used_assets() + get_idle_assets() + get_assets_due_for_maintenance())
    csv = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Export report",
        data=csv,
        file_name="assetflow_report.csv",
        mime="text/csv",
        use_container_width=True,
    )