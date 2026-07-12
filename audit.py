import streamlit as st
import pandas as pd
from utils import get_all_assets, get_all_departments
from extra_utils import (
    create_audit, get_open_audit, get_audit_items,
    set_audit_item_status, close_audit_cycle, log_activity
)

def show_audit():
    st.title("🕵️ Asset Audit")
    user = st.session_state.user
    if user["role"] not in ["admin", "asset_manager"]:
        st.error("You don't have permission to view this page.")
        return

    audit = get_open_audit()

    if not audit:
        st.info("No open audit cycle. Start one below.")
        depts = get_all_departments()
        dept_names = [d["name"] for d in depts] if depts else ["All"]
        department = st.selectbox("Department", dept_names)
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
        auditors = st.text_input("Auditors (comma separated)")

        if st.button("Start Audit Cycle", use_container_width=True):
            create_audit(department, str(start_date), str(end_date), auditors)
            log_activity("Alerts", f"Audit cycle started for {department}")
            st.success("Audit cycle started!")
            st.rerun()
        return

    st.info(f"**Q audit:** {audit['department']} · {audit['start_date']} to {audit['end_date']}  \n"
            f"**Auditors:** {audit['auditors']}")

    items = get_audit_items(audit["id"])
    if not items:
        st.warning("No assets found to audit.")
        return

    df = pd.DataFrame([dict(i) for i in items])
    st.dataframe(
        df[["asset_tag", "asset_name", "expected_location", "verification_status"]],
        hide_index=True
    )

    st.divider()
    st.subheader("Update Verification")
    item_options = {
        f"{i['asset_tag']} - {i['asset_name']}": i["id"] for i in items
    }
    selected = st.selectbox("Select Asset", list(item_options.keys()))
    status = st.selectbox("Verification Status", ["Verified", "Missing", "Damaged"])
    if st.button("Update", use_container_width=True):
        set_audit_item_status(item_options[selected], status)
        st.success("Updated!")
        st.rerun()

    st.divider()
    flagged = [i for i in items if i["verification_status"] in ("Missing", "Damaged")]
    if flagged:
        st.warning(f"⚠️ {len(flagged)} asset(s) flagged - discrepancy report generated automatically")

    if st.button("Close Audit Cycle", use_container_width=True):
        discrepancies = close_audit_cycle(audit["id"])
        log_activity("Alerts", f"Audit closed for {audit['department']} - {discrepancies} discrepancies")
        st.success(f"Audit cycle closed. {discrepancies} discrepancies recorded.")
        st.rerun()