import streamlit as st
import pandas as pd
from utils import (
    get_all_maintenance, get_all_assets,
    raise_maintenance, approve_maintenance, resolve_maintenance
)

# ── MAINTENANCE ───────────────────────────────────
def show_maintenance():
    st.title("🔧 Maintenance")
    user = st.session_state.user
    role = user["role"]

    tab1, tab2 = st.tabs(["📋 All Requests", "➕ Raise Request"])

    with tab1:
        requests = get_all_maintenance()
        if requests:
            df = pd.DataFrame([dict(r) for r in requests])
            st.dataframe(df[["asset_tag", "asset_name", "user_name",
                             "description", "priority", "status"]],
                        hide_index=True)

            if role in ["admin", "asset_manager"]:
                st.divider()
                st.subheader("Actions")
                pending = [r for r in requests if r["status"] == "Pending"]
                approved = [r for r in requests if r["status"] == "Approved"]

                if pending:
                    req_options = {
                        f"{r['asset_name']} - {r['description'][:30]}": r["id"]
                        for r in pending
                    }
                    selected = st.selectbox("Approve Request", list(req_options.keys()))
                    if st.button("✅ Approve", use_container_width=True):
                        success, msg = approve_maintenance(req_options[selected])
                        if success:
                            st.success(msg)
                            st.rerun()

                if approved:
                    req_options2 = {
                        f"{r['asset_name']} - {r['description'][:30]}": r["id"]
                        for r in approved
                    }
                    selected2 = st.selectbox("Resolve Request", list(req_options2.keys()))
                    if st.button("✅ Mark Resolved", use_container_width=True):
                        success, msg = resolve_maintenance(req_options2[selected2])
                        if success:
                            st.success(msg)
                            st.rerun()
        else:
            st.info("No maintenance requests yet.")

    with tab2:
        assets = get_all_assets()
        asset_options = {f"{a['asset_tag']} - {a['name']}": a["id"] for a in assets}
        asset = st.selectbox("Select Asset", list(asset_options.keys()))
        description = st.text_area("Describe the issue")
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])

        if st.button("Raise Request", use_container_width=True):
            if not description:
                st.error("Please describe the issue!")
            else:
                success, msg = raise_maintenance(
                    asset_options[asset],
                    user["id"],
                    description,
                    priority
                )
                if success:
                    st.success(msg)
                    st.rerun()