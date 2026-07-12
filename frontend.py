import streamlit as st
import pandas as pd
from datetime import date
from db import get_db
from utils import (
    get_dashboard_stats, get_all_assets, get_all_categories,
    get_all_departments, get_all_users, get_active_allocations,
    get_overdue_allocations, get_all_maintenance, get_notifications,
    register_asset, allocate_asset, return_asset,
    raise_maintenance, approve_maintenance, resolve_maintenance,
    create_department, create_category, promote_user,
    ask_ai, get_user_allocations, get_active_allocation_for_asset,
    raise_transfer_request, get_all_transfer_requests,
    get_pending_transfer_requests, approve_transfer_request, reject_transfer_request
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
    user = st.session_state.user
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Active", "➕ Allocate", "↩️ Return", "🔁 Transfers"])
 
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
        users = get_all_users()
        if not assets:
            st.warning("No assets registered!")
            return
 
        asset_options = {f"{a['asset_tag']} - {a['name']}": a["id"] for a in assets}
        user_options = {u["name"]: u["id"] for u in users}
 
        asset_label = st.selectbox("Select Asset", list(asset_options.keys()))
        asset_id = asset_options[asset_label]
        target_user = st.selectbox("Assign To", list(user_options.keys()))
        return_date = st.date_input("Expected Return Date (optional)")
 
        existing = get_active_allocation_for_asset(asset_id)
 
        if existing:
            st.markdown(f"""
                <div style='background:#FEE2E2;border:1px solid #FCA5A5;border-radius:8px;
                            padding:0.85rem 1.1rem;margin:0.5rem 0;'>
                    <b>Already allocated to {existing['holder_name']}</b><br>
                    <span style='color:#B91C1C;'>Direct re-allocation is blocked — submit a transfer request below.</span>
                </div>
            """, unsafe_allow_html=True)
            notes = st.text_area("Reason for transfer", key="transfer_notes")
            if st.button("🔁 Request Transfer", use_container_width=True):
                if not notes.strip():
                    st.error("Please provide a reason for the transfer.")
                else:
                    success, msg = raise_transfer_request(
                        asset_id, user_options[target_user], user["id"], notes
                    )
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            if st.button("Allocate Asset", use_container_width=True):
                success, msg = allocate_asset(
                    asset_id,
                    user_options[target_user],
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
 
    with tab4:
        st.subheader("All Transfer Requests")
        requests = get_all_transfer_requests()
        if requests:
            df = pd.DataFrame([dict(r) for r in requests])
            st.dataframe(df[["asset_tag", "asset_name", "from_user_name",
                             "to_user_name", "status", "requested_date"]],
                        hide_index=True)
        else:
            st.info("No transfer requests yet.")
 
        if user["role"] in ["admin", "asset_manager", "dept_head"]:
            pending = get_pending_transfer_requests()
            if pending:
                st.divider()
                st.subheader("Pending Approvals")
                req_options = {
                    f"{r['asset_name']} - {r['from_user_name']} → {r['to_user_name']}": r["id"]
                    for r in pending
                }
                selected_req = st.selectbox("Select Request", list(req_options.keys()))
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Approve", use_container_width=True):
                        success, msg = approve_transfer_request(req_options[selected_req])
                        if success:
                            st.success(msg)
                            st.rerun()
                with col2:
                    if st.button("❌ Reject", use_container_width=True):
                        success, msg = reject_transfer_request(req_options[selected_req])
                        if success:
                            st.success(msg)
                            st.rerun()
 
 
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
 
 
# ── RESOURCE BOOKING ──────────────────────────────
SLOT_HOURS = ["4:00", "5:00", "6:00", "7:00", "8:00", "9:00", "10:00", "11:00", "12:00", "1:00"]
 
def show_resource_booking():
    st.title("🗓️ Resource Booking")
 
    assets = get_all_assets()
    bookable = [a for a in assets if a["is_bookable"]]
    if not bookable:
        st.info("No bookable resources yet. Mark an asset as bookable when registering it.")
        return
 
    col1, col2 = st.columns(2)
    with col1:
        resource_options = {f"{a['name']} ({a['location']})": a for a in bookable}
        resource_label = st.selectbox("Resource", list(resource_options.keys()))
        resource = resource_options[resource_label]
    with col2:
        booking_date = st.date_input("Date", value=date.today())
 
    bookings = _get_bookings(resource["id"], booking_date)
 
    st.write("")
    for hour in SLOT_HOURS:
        booking = next((b for b in bookings if b["start"] == hour), None)
        cols = st.columns([1, 8])
        with cols[0]:
            st.markdown(f"<div style='padding-top:0.4rem;color:#64748B;'>{hour}</div>",
                        unsafe_allow_html=True)
        with cols[1]:
            if booking:
                st.markdown(f"""
                    <div style='background:#DBEAFE;border:1px solid #93C5FD;border-radius:6px;
                                padding:0.5rem 0.75rem;'>
                        Booked — {booking['team']} — {booking['start']} to {booking['end']}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
 
    st.divider()
    st.subheader("Book a slot")
    b1, b2, b3 = st.columns(3)
    with b1:
        start = st.selectbox("Start", SLOT_HOURS)
    with b2:
        end = st.selectbox("End", SLOT_HOURS, index=1)
    with b3:
        team = st.text_input("Team / purpose")
 
    if st.button("Book a slot", type="primary"):
        conflict = any(b["start"] < end and start < b["end"] for b in bookings)
        if conflict:
            st.error(f"Requested {start} to {end} — conflict, slot is unavailable.")
        elif not team.strip():
            st.error("Please enter a team or purpose for the booking.")
        else:
            _add_booking(resource["id"], booking_date, start, end, team)
            st.success("Slot booked!")
            st.rerun()
 
 
# TODO(backend): replace this session_state shim with a real `bookings` table +
# create_booking()/get_bookings_for_resource() functions in utils.py.
 
def _get_bookings(resource_id, booking_date):
    key = f"{resource_id}:{booking_date}"
    return st.session_state.get("bookings", {}).get(key, [])
 
 
def _add_booking(resource_id, booking_date, start, end, team):
    key = f"{resource_id}:{booking_date}"
    if "bookings" not in st.session_state:
        st.session_state.bookings = {}
    st.session_state.bookings.setdefault(key, []).append(
        {"start": start, "end": end, "team": team}
    )
 
 
# ── MAINTENANCE (Kanban) ──────────────────────────
# Backend only tracks Pending / Approved / Resolved. "Technician assigned" and
# "In progress" are UI-only sub-stages layered on top via session_state until
# backend adds a `technician` column and richer status values.
 
KANBAN_COLUMNS = ["Pending", "Approved", "Technician Assigned", "In Progress", "Resolved"]
 
def show_maintenance():
    st.title("🔧 Maintenance Management")
    st.caption("Approving a card moves it to Under Maintenance; resolving returns it to Available.")
 
    user = st.session_state.user
    role = user["role"]
 
    tab1, tab2 = st.tabs(["📋 Board", "➕ Raise Request"])
 
    with tab1:
        requests = get_all_maintenance()
        sub_stage = st.session_state.setdefault("maintenance_substage", {})
 
        cols = st.columns(len(KANBAN_COLUMNS))
        for col, stage in zip(cols, KANBAN_COLUMNS):
            with col:
                st.markdown(f"**{stage}**")
                for req in requests:
                    local = sub_stage.get(req["id"], {})
 
                    if req["status"] == "Resolved":
                        effective_stage = "Resolved"
                    elif req["status"] == "Pending":
                        effective_stage = "Pending"
                    else:  # Approved
                        effective_stage = local.get("stage", "Approved")
 
                    if effective_stage != stage:
                        continue
 
                    _render_maintenance_card(req, local, role)
 
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
                    asset_options[asset], user["id"], description, priority
                )
                if success:
                    st.success(msg)
                    st.rerun()
 
 
def _render_maintenance_card(req, local, role):
    color = {"Low": "#D1FAE5", "Medium": "#FEF3C7", "High": "#FEE2E2",
             "Critical": "#FCA5A5"}.get(req["priority"], "#F1F5F9")
    st.markdown(f"""
        <div style='background:{color};border-radius:8px;padding:0.6rem 0.7rem;margin-bottom:0.5rem;'>
            <b>{req['asset_tag']}</b><br>
            <span style='font-size:0.85rem;'>{req['description']}</span>
            {f"<br><span style='font-size:0.8rem;color:#475569;'>tech: {local['technician']}</span>" if local.get('technician') else ""}
        </div>
    """, unsafe_allow_html=True)
 
    can_manage = role in ["admin", "asset_manager"]
    if not can_manage:
        return
 
    if req["status"] == "Pending":
        if st.button("Approve", key=f"approve_{req['id']}"):
            approve_maintenance(req["id"])
            st.rerun()
 
    elif req["status"] == "Approved" and not local.get("stage"):
        tech = st.text_input("Assign technician", key=f"tech_{req['id']}")
        if st.button("Assign", key=f"assign_{req['id']}") and tech.strip():
            st.session_state.maintenance_substage[req["id"]] = {"stage": "Technician Assigned", "technician": tech}
            st.rerun()
 
    elif local.get("stage") == "Technician Assigned":
        if st.button("Start work", key=f"start_{req['id']}"):
            local["stage"] = "In Progress"
            st.rerun()
 
    elif local.get("stage") == "In Progress":
        if st.button("Mark resolved", key=f"resolve_{req['id']}"):
            resolve_maintenance(req["id"])
            st.session_state.maintenance_substage.pop(req["id"], None)
            st.rerun()
 
 
# ── ORGANIZATION (admin) ──────────────────────────
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
 
 
# ── USERS (admin) ──────────────────────────────────
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
 
 
# ── NOTIFICATIONS ──────────────────────────────────
def show_notifications():
    st.title("🔔 Notifications")
    user = st.session_state.user
    notifs = get_notifications(user["id"])
    if notifs:
        for n in notifs:
            st.info(f"📢 {n['message']} — {n['created_at']}")
    else:
        st.info("No notifications yet.")
 