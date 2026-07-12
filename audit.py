import streamlit as st
import pandas as pd
from utils import (
    get_all_assets, get_all_departments,
    create_audit, get_open_audit, get_audit_items,
    set_audit_item_status, close_audit_cycle, log_activity
)

def show_audit():
    st.title("Asset Audit")
    st.caption("Run structured verification cycles and generate discrepancy reports.")
    st.divider()

    user = st.session_state.user
    if user["role"] not in ["admin", "asset_manager"]:
        st.error("You don't have permission to view this page.")
        return

    audit = get_open_audit()

    # ── NO OPEN AUDIT ─────────────────────────────
    if not audit:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
                <div style='background:#1E293B; border-radius:12px;
                padding:1.5rem; border:1px solid #334155;
                margin-bottom:1rem;'>
                    <div style='color:#94A3B8; font-size:0.8rem;
                    text-transform:uppercase; letter-spacing:1px;'>
                    Status</div>
                    <div style='color:#F1F5F9; font-size:1.1rem;
                    font-weight:600; margin-top:4px;'>
                    No Active Audit Cycle</div>
                    <div style='color:#64748B; font-size:0.85rem;
                    margin-top:4px;'>Start a new cycle below to
                    begin verification.</div>
                </div>
            """, unsafe_allow_html=True)

        st.subheader("Start New Audit Cycle")
        depts = get_all_departments()
        dept_names = [d["name"] for d in depts] if depts else ["All Departments"]

        col1, col2, col3 = st.columns(3)
        with col1:
            department = st.selectbox("Department", dept_names)
        with col2:
            start_date = st.date_input("Start Date")
        with col3:
            end_date = st.date_input("End Date")

        auditors = st.text_input("Auditors", placeholder="e.g. John, Sarah, Mike")

        st.write("")
        if st.button("Start Audit Cycle", use_container_width=True):
            if not auditors:
                st.error("Please assign at least one auditor!")
            else:
                create_audit(department, str(start_date), str(end_date), auditors)
                log_activity("Audit", f"Audit cycle started for {department}")
                st.success("Audit cycle started!")
                st.rerun()
        return

    # ── OPEN AUDIT ────────────────────────────────
    items = get_audit_items(audit["id"])
    total = len(items) if items else 0
    verified = len([i for i in items if i["verification_status"] == "Verified"]) if items else 0
    flagged = [i for i in items if i["verification_status"] in ("Missing", "Damaged")] if items else []
    pending = total - verified - len(flagged)

    # status card
    st.markdown(f"""
        <div style='background:#1E293B; border-radius:12px;
        padding:1.2rem 1.5rem; border:1px solid #334155;
        margin-bottom:1.5rem;'>
            <div style='display:flex; justify-content:space-between;
            align-items:center; flex-wrap:wrap; gap:1rem;'>
                <div>
                    <div style='color:#94A3B8; font-size:0.75rem;
                    text-transform:uppercase; letter-spacing:1px;'>
                    Active Audit Cycle</div>
                    <div style='color:#F1F5F9; font-weight:600;
                    font-size:1.1rem; margin-top:2px;'>
                    {audit['department']}</div>
                    <div style='color:#64748B; font-size:0.8rem;'>
                    {audit['start_date']} to {audit['end_date']} · 
                    Auditors: {audit['auditors']}</div>
                </div>
                <div style='display:flex; gap:1rem;'>
                    <div style='text-align:center;'>
                        <div style='color:#22C55E; font-size:1.4rem;
                        font-weight:700;'>{verified}</div>
                        <div style='color:#64748B; font-size:0.7rem;'>
                        Verified</div>
                    </div>
                    <div style='text-align:center;'>
                        <div style='color:#F59E0B; font-size:1.4rem;
                        font-weight:700;'>{pending}</div>
                        <div style='color:#64748B; font-size:0.7rem;'>
                        Pending</div>
                    </div>
                    <div style='text-align:center;'>
                        <div style='color:#EF4444; font-size:1.4rem;
                        font-weight:700;'>{len(flagged)}</div>
                        <div style='color:#64748B; font-size:0.7rem;'>
                        Flagged</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if not items:
        st.warning("No assets found in this audit cycle.")
        return

    tab1, tab2 = st.tabs(["Asset List", "Update Verification"])

    with tab1:
        df = pd.DataFrame([dict(i) for i in items])
        st.dataframe(
            df[["asset_tag", "asset_name",
                "expected_location", "verification_status"]],
            hide_index=True,
            use_container_width=True
        )

        if flagged:
            st.markdown("""
                <div style='background:#450A0A; border-radius:10px;
                padding:1rem 1.2rem; border:1px solid #7F1D1D;
                margin-top:1rem;'>
                    <div style='color:#FCA5A5; font-weight:600;'>
                    Discrepancy Report</div>
                    <div style='color:#FCA5A5; font-size:0.85rem;
                    margin-top:4px;'>
            """ + f"{len(flagged)} asset(s) flagged — report will be auto-generated on cycle close." + """
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with tab2:
        item_options = {
            f"{i['asset_tag']} — {i['asset_name']}": i["id"]
            for i in items
        }
        selected = st.selectbox("Select Asset", list(item_options.keys()))
        status = st.selectbox(
            "Verification Status",
            ["Verified", "Missing", "Damaged"]
        )
        if st.button("Update Status", use_container_width=True):
            set_audit_item_status(item_options[selected], status)
            st.success("Status updated!")
            st.rerun()

    st.divider()
    st.markdown("**Close Audit Cycle**")
    st.caption("This will lock the cycle, generate the final discrepancy report, and update asset statuses.")
    if st.button("Close & Generate Report", use_container_width=True):
        discrepancies = close_audit_cycle(audit["id"])
        log_activity("Audit", f"Audit closed for {audit['department']} — {discrepancies} discrepancies")
        st.success(f"Audit cycle closed. {discrepancies} discrepancy/ies recorded.")
        st.rerun()