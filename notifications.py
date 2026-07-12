import streamlit as st



def get_activity_logs():
    return [
        {"type": "Bookings", "icon": "🔵", "message": "Laptop AF-0014 assigned to Priya Shah", "time": "2m ago"},
        {"type": "Approvals", "icon": "⚪", "message": "Maintenance request AF-0055 approved", "time": "15m ago"},
        {"type": "Bookings", "icon": "🔵", "message": "Booking confirmed: Room B2, 2:00 to 3:00 PM", "time": "1h ago"},
        {"type": "Approvals", "icon": "🟠", "message": "Transfer approved: AF-0033 to Facilities dept", "time": "3h ago"},
        {"type": "Alerts", "icon": "🔴", "message": "Overdue return: AF-0021 was due 3 days ago", "time": "1d ago"},
        {"type": "Alerts", "icon": "🔴", "message": "Audit discrepancy flagged: AF-0088 damaged", "time": "2d ago"},
    ]



def show_notifications():
    st.title("🔔 Activity Logs & Notifications")
    user = st.session_state.user
    if user["role"] not in ["admin", "asset_manager"]:
        st.error("You don't have permission to view this page.")
        return

    logs = get_activity_logs()

    tab_all, tab_alerts, tab_approvals, tab_bookings = st.tabs(
        ["All", "Alerts", "Approvals", "Bookings"]
    )

    def render_logs(filtered):
        if not filtered:
            st.info("No activity in this category.")
            return
        for log in filtered:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(f"{log['icon']} {log['message']}")
            with col2:
                st.caption(log["time"])

    with tab_all:
        render_logs(logs)

    with tab_alerts:
        render_logs([l for l in logs if l["type"] == "Alerts"])

    with tab_approvals:
        render_logs([l for l in logs if l["type"] == "Approvals"])

    with tab_bookings:
        render_logs([l for l in logs if l["type"] == "Bookings"])