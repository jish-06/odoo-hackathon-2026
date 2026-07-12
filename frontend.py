import streamlit as st
import pandas as pd
from utils import (
    get_dashboard_stats, get_all_assets, get_all_categories,
    get_all_users, get_active_allocations, get_overdue_allocations,
    register_asset, allocate_asset, return_asset, get_user_allocations
)
 
# ── DASHBOARD ─────────────────────────────────────
def show_dashboard():
    st.title("🏠 Dashboard")
    stats = get_dashboard_stats()
 
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Available", stats["available"])
    with col2:
        st.metric("📦 Allocated", stats["allocated"])
    with col3:
        st.metric("🔧 Maintenance", stats["maintenance"])
    with col4:
        st.metric("⚠️ Overdue", stats["overdue"])
 
    col5, col6 = st.columns(2)
    with col5:
        st.metric("📋 Active Bookings", stats["active_bookings"])
    with col6:
        st.metric("🔔 Pending Requests", stats["pending_maintenance"])
 
    st.divider()
 
    overdue = get_overdue_allocations()
    if overdue:
        st.subheader("⚠️ Overdue Returns")
        df = pd.DataFrame([dict(r) for r in overdue])
        st.dataframe(df[["asset_name", "user_name",
                         "allocated_date", "expected_return_date"]],
                    hide_index=True)
 
# ── ASSETS ────────────────────────────────────────
def show_assets():
    st.title("📦 Asset Registry")
    tab1, tab2 = st.tabs(["📋 All Assets", "➕ Register Asset"])
 
    with tab1:
        assets = get_all_assets()
        if assets:
            df = pd.DataFrame([dict(a) for a in assets])
            st.dataframe(df[["asset_tag", "name", "category_name",
                             "status", "condition", "location"]],
                        hide_index=True)
        else:
            st.info("No assets registered yet.")
 
    with tab2:
        categories = get_all_categories()
        if not categories:
            st.warning("No categories yet. Ask admin to create some!")
            return
        cat_options = {c["name"]: c["id"] for c in categories}
        name = st.text_input("Asset Name")
        category = st.selectbox("Category", list(cat_options.keys()))
        serial = st.text_input("Serial Number")
        location = st.text_input("Location")
        condition = st.selectbox("Condition", ["Good", "Fair", "Poor"])
        is_bookable = st.checkbox("Shared/Bookable Resource")
 
        if st.button("Register Asset", use_container_width=True):
            if not name or not location:
                st.error("Name and location are required!")
            else:
                tag = register_asset(
                    name, cat_options[category],
                    serial, location, condition,
                    1 if is_bookable else 0
                )
                st.success(f"Asset registered! Tag: {tag}")
                st.rerun()
 
# ── ALLOCATIONS ───────────────────────────────────
def show_allocations():
    st.title("👥 Asset Allocations")
    tab1, tab2, tab3 = st.tabs(["📋 Active", "➕ Allocate", "↩️ Return"])
 
    with tab1:
        allocs = get_active_allocations()
        if allocs:
            df = pd.DataFrame([dict(a) for a in allocs])
            st.dataframe(df[["asset_tag", "asset_name", "user_name",
                             "allocated_date", "expected_return_date"]],
                        hide_index=True)
        else:
            st.info("No active allocations.")
 
    with tab2:
        assets = get_all_assets()
        available = [a for a in assets if a["status"] == "Available"]
        users = get_all_users()
 
        if not available:
            st.warning("No available assets!")
            return
 
        asset_options = {f"{a['asset_tag']} - {a['name']}": a["id"] for a in available}
        user_options = {u["name"]: u["id"] for u in users}
 
        asset = st.selectbox("Select Asset", list(asset_options.keys()))
        user = st.selectbox("Assign To", list(user_options.keys()))
        return_date = st.date_input("Expected Return Date (optional)")
 
        if st.button("Allocate Asset", use_container_width=True):
            success, msg = allocate_asset(
                asset_options[asset],
                user_options[user],
                str(return_date) if return_date else None
            )
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(f"❌ {msg}")
 
    with tab3:
        allocs = get_active_allocations()
        if not allocs:
            st.info("No active allocations to return.")
            return
        alloc_options = {
            f"{a['asset_tag']} - {a['asset_name']} ({a['user_name']})": a["id"]
            for a in allocs
        }
        selected = st.selectbox("Select Allocation", list(alloc_options.keys()))
        notes = st.text_area("Condition Notes")
 
        if st.button("Return Asset", use_container_width=True):
            success, msg = return_asset(alloc_options[selected], notes)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
 
# ── MY ASSETS (employee) ──────────────────────────
def show_my_assets():
    st.title("👤 My Assets")
    user = st.session_state.user
    allocs = get_user_allocations(user["id"])
    if allocs:
        df = pd.DataFrame([dict(a) for a in allocs])
        st.dataframe(df[["asset_name", "asset_tag", "allocated_date",
                         "expected_return_date"]], hide_index=True)
    else:
        st.info("No assets assigned to you currently.")
 