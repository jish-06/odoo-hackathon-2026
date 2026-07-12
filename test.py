



import streamlit as st
import pandas as pd
from utils import (
    get_dashboard_stats, get_all_assets, get_all_categories,
    get_all_departments, get_all_users, get_active_allocations,
    get_overdue_allocations, get_all_maintenance, get_notifications,
    register_asset, allocate_asset, return_asset,
    raise_maintenance, approve_maintenance, resolve_maintenance,
    create_department, create_category, promote_user,
    ask_ai, get_user_allocations
)

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
        if not assets:
            st.warning("No assets registered yet!")
            return
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

def show_organization():
    st.title("🏢 Organization Setup")
    tab1, tab2 = st.tabs(["🏬 Departments", "📁 Categories"])

    with tab1:
        depts = get_all_departments()
        if depts:
            df = pd.DataFrame([dict(d) for d in depts])
            st.dataframe(df[["id", "name", "status"]], hide_index=True)
        st.divider()
        name = st.text_input("Department Name")
        if st.button("Create Department", use_container_width=True):
            if name:
                create_department(name)
                st.success(f"Department '{name}' created!")
                st.rerun()

    with tab2:
        cats = get_all_categories()
        if cats:
            df = pd.DataFrame([dict(c) for c in cats])
            st.dataframe(df[["id", "name"]], hide_index=True)
        st.divider()
        cat_name = st.text_input("Category Name")
        if st.button("Create Category", use_container_width=True):
            if cat_name:
                create_category(cat_name)
                st.success(f"Category '{cat_name}' created!")
                st.rerun()

def show_users():
    st.title("👤 User Management")
    users = get_all_users()
    if users:
        df = pd.DataFrame([dict(u) for u in users])
        st.dataframe(df[["id", "name", "email", "role", "status"]], hide_index=True)
    st.divider()
    st.subheader("Promote User")
    user_options = {u["name"]: u["id"] for u in users}
    selected = st.selectbox("Select User", list(user_options.keys()))
    role = st.selectbox("New Role", ["employee", "dept_head", "asset_manager", "admin"])
    if st.button("Promote", use_container_width=True):
        promote_user(user_options[selected], role)
        st.success("User role updated!")
        st.rerun()

def show_notifications():
    st.title("🔔 Notifications")
    user = st.session_state.user
    notifs = get_notifications(user["id"])
    if notifs:
        for n in notifs:
            st.info(f"📢 {n['message']} — {n['created_at']}")
    else:
        st.info("No notifications yet.")
 