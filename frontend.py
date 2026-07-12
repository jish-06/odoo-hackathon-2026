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
    get_pending_transfer_requests, approve_transfer_request,
    reject_transfer_request
)

# ── HELPERS ───────────────────────────────────────
def card(label, value, color="#6366F1", sub=None):
    sub_html = f"<div style='color:#64748B;font-size:0.75rem;margin-top:2px;'>{sub}</div>" if sub else ""
    st.markdown(f"""
        <div style='background:#1E293B;border-radius:12px;
        padding:1rem 1.2rem;border:1px solid #334155;
        border-left:3px solid {color};margin-bottom:0.5rem;'>
            <div style='color:#94A3B8;font-size:0.7rem;
            text-transform:uppercase;letter-spacing:1px;'>{label}</div>
            <div style='color:#F1F5F9;font-size:0.95rem;
            font-weight:600;margin-top:4px;'>{value}</div>
            {sub_html}
        </div>
    """, unsafe_allow_html=True)

def badge(text, color="#6366F1", bg="#1E1B4B"):
    return f"<span style='background:{bg};color:{color};padding:2px 10px;border-radius:4px;font-size:0.7rem;font-weight:600;letter-spacing:0.5px;'>{text}</span>"

def page_header(title, caption=None):
    st.markdown(f"<h1 style='margin-bottom:0;'>{title}</h1>", unsafe_allow_html=True)
    if caption:
        st.caption(caption)
    st.divider()

# ── DASHBOARD ─────────────────────────────────────
def show_dashboard():
    page_header("Dashboard", "Real-time operational snapshot of your assets.")
    stats = get_dashboard_stats()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Available", stats["available"])
    with col2:
        st.metric("Allocated", stats["allocated"])
    with col3:
        st.metric("Under Maintenance", stats["maintenance"])
    with col4:
        st.metric("Overdue Returns", stats["overdue"],
                  delta=f"-{stats['overdue']}" if stats["overdue"] > 0 else None,
                  delta_color="inverse")

    col5, col6 = st.columns(2)
    with col5:
        st.metric("Active Bookings", stats["active_bookings"])
    with col6:
        st.metric("Pending Maintenance", stats["pending_maintenance"])

    overdue = get_overdue_allocations()
    if overdue:
        st.divider()
        st.markdown("""
            <div style='background:#450A0A;border-radius:10px;
            padding:0.8rem 1.2rem;border:1px solid #7F1D1D;
            margin-bottom:1rem;'>
                <div style='color:#FCA5A5;font-weight:600;
                font-size:0.85rem;'>Overdue Returns Require Attention</div>
            </div>
        """, unsafe_allow_html=True)
        df = pd.DataFrame([dict(r) for r in overdue])
        st.dataframe(
            df[["asset_name", "user_name",
                "allocated_date", "expected_return_date"]],
            hide_index=True,
            use_container_width=True
        )

# ── ASSETS ────────────────────────────────────────
def show_assets():
    page_header("Asset Registry", "Register and track all organizational assets.")
    tab1, tab2 = st.tabs(["All Assets", "Register New Asset"])

    with tab1:
        assets = get_all_assets()
        if assets:
            df = pd.DataFrame([dict(a) for a in assets])
            st.dataframe(
                df[["asset_tag", "name", "category_name",
                    "status", "condition", "location"]],
                hide_index=True,
                use_container_width=True
            )
            st.caption(f"{len(assets)} assets total")
        else:
            st.markdown("""
                <div style='background:#1E293B;border-radius:12px;
                padding:2rem;text-align:center;border:1px solid #334155;'>
                    <div style='color:#64748B;font-size:0.9rem;'>
                    No assets registered yet.</div>
                    <div style='color:#475569;font-size:0.8rem;
                    margin-top:4px;'>Switch to the Register tab to add your first asset.</div>
                </div>
            """, unsafe_allow_html=True)

    with tab2:
        categories = get_all_categories()
        if not categories:
            st.warning("No categories yet. Ask admin to create some in Organization Setup.")
            return

        cat_options = {c["name"]: c["id"] for c in categories}
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Asset Name")
            serial = st.text_input("Serial Number")
            condition = st.selectbox("Condition", ["Good", "Fair", "Poor"])
        with col2:
            category = st.selectbox("Category", list(cat_options.keys()))
            location = st.text_input("Location")
            is_bookable = st.checkbox("Mark as Shared / Bookable Resource")

        st.write("")
        if st.button("Register Asset", use_container_width=True):
            if not name or not location:
                st.error("Asset name and location are required.")
            else:
                tag = register_asset(
                    name, cat_options[category],
                    serial, location, condition,
                    1 if is_bookable else 0
                )
                st.success(f"Asset registered — Tag: **{tag}**")
                st.rerun()

# ── ALLOCATIONS ───────────────────────────────────
def show_allocations():
    page_header("Asset Allocations", "Allocate, return, and transfer assets between employees.")
    user = st.session_state.user
    tab1, tab2, tab3, tab4 = st.tabs(["Active", "Allocate", "Return", "Transfers"])

    with tab1:
        allocs = get_active_allocations()
        if allocs:
            df = pd.DataFrame([dict(a) for a in allocs])
            st.dataframe(
                df[["asset_tag", "asset_name", "user_name",
                    "allocated_date", "expected_return_date"]],
                hide_index=True,
                use_container_width=True
            )
            st.caption(f"{len(allocs)} active allocation(s)")
        else:
            st.info("No active allocations.")

    with tab2:
        assets = get_all_assets()
        users = get_all_users()
        if not assets:
            st.warning("No assets registered!")
            return

        asset_options = {f"{a['asset_tag']} — {a['name']}": a["id"] for a in assets}
        user_options = {u["name"]: u["id"] for u in users}

        col1, col2 = st.columns(2)
        with col1:
            asset_label = st.selectbox("Select Asset", list(asset_options.keys()))
        with col2:
            target_user = st.selectbox("Assign To", list(user_options.keys()))

        asset_id = asset_options[asset_label]
        return_date = st.date_input("Expected Return Date (optional)")
        existing = get_active_allocation_for_asset(asset_id)

        st.write("")
        if existing:
            st.markdown(f"""
                <div style='background:#450A0A;border:1px solid #7F1D1D;
                border-radius:10px;padding:1rem 1.2rem;margin-bottom:1rem;'>
                    <div style='color:#FCA5A5;font-weight:600;'>
                    Allocation Conflict</div>
                    <div style='color:#FCA5A5;font-size:0.85rem;margin-top:4px;'>
                    This asset is currently held by
                    <b>{existing['holder_name']}</b>.
                    Direct re-allocation is blocked.
                    Submit a transfer request instead.</div>
                </div>
            """, unsafe_allow_html=True)
            notes = st.text_area("Reason for transfer", key="transfer_notes")
            if st.button("Request Transfer", use_container_width=True):
                if not notes.strip():
                    st.error("Please provide a reason for the transfer.")
                else:
                    success, msg = raise_transfer_request(
                        asset_id, user_options[target_user],
                        user["id"], notes
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
                    st.error(msg)

    with tab3:
        allocs = get_active_allocations()
        if not allocs:
            st.info("No active allocations to return.")
            return
        alloc_options = {
            f"{a['asset_tag']} — {a['asset_name']} ({a['user_name']})": a["id"]
            for a in allocs
        }
        selected = st.selectbox("Select Allocation", list(alloc_options.keys()))
        notes = st.text_area("Condition Notes on Return")
        st.write("")
        if st.button("Confirm Return", use_container_width=True):
            success, msg = return_asset(alloc_options[selected], notes)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    with tab4:
        requests = get_all_transfer_requests()
        if requests:
            df = pd.DataFrame([dict(r) for r in requests])
            st.dataframe(
                df[["asset_tag", "asset_name", "from_user_name",
                    "to_user_name", "status", "requested_date"]],
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No transfer requests yet.")

        if user["role"] in ["admin", "asset_manager", "dept_head"]:
            pending = get_pending_transfer_requests()
            if pending:
                st.divider()
                st.subheader("Pending Approvals")
                req_options = {
                    f"{r['asset_name']} — {r['from_user_name']} to {r['to_user_name']}": r["id"]
                    for r in pending
                }
                selected_req = st.selectbox("Select Request", list(req_options.keys()))
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Approve Transfer", use_container_width=True):
                        success, msg = approve_transfer_request(req_options[selected_req])
                        if success:
                            st.success(msg)
                            st.rerun()
                with col2:
                    if st.button("Reject Transfer", use_container_width=True):
                        success, msg = reject_transfer_request(req_options[selected_req])
                        if success:
                            st.success(msg)
                            st.rerun()

# ── MY ASSETS ─────────────────────────────────────
def show_my_assets():
    page_header("My Assets", "Assets currently assigned to you.")
    user = st.session_state.user
    allocs = get_user_allocations(user["id"])
    if allocs:
        df = pd.DataFrame([dict(a) for a in allocs])
        st.dataframe(
            df[["asset_name", "asset_tag",
                "allocated_date", "expected_return_date"]],
            hide_index=True,
            use_container_width=True
        )
        st.caption(f"{len(allocs)} asset(s) assigned to you")
    else:
        st.markdown("""
            <div style='background:#1E293B;border-radius:12px;
            padding:2rem;text-align:center;border:1px solid #334155;'>
                <div style='color:#64748B;'>No assets assigned to you yet.</div>
            </div>
        """, unsafe_allow_html=True)

# ── RESOURCE BOOKING ──────────────────────────────
SLOT_HOURS = ["4:00","5:00","6:00","7:00","8:00","9:00",
              "10:00","11:00","12:00","1:00"]

def show_resource_booking():
    page_header("Resource Booking", "Book shared resources by time slot with overlap validation.")
    assets = get_all_assets()
    bookable = [a for a in assets if a["is_bookable"]]

    if not bookable:
        st.info("No bookable resources yet. Mark an asset as bookable when registering.")
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
    st.subheader("Availability")

    for hour in SLOT_HOURS:
        booking = next((b for b in bookings if b["start"] == hour), None)
        cols = st.columns([1, 8])
        with cols[0]:
            st.markdown(
                f"<div style='padding-top:0.4rem;color:#64748B;"
                f"font-size:0.85rem;'>{hour}</div>",
                unsafe_allow_html=True
            )
        with cols[1]:
            if booking:
                st.markdown(f"""
                    <div style='background:#1E1B4B;border:1px solid #3730A3;
                    border-radius:6px;padding:0.4rem 0.75rem;color:#A5B4FC;
                    font-size:0.85rem;'>
                    Booked — {booking['team']} — {booking['start']} to {booking['end']}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(
                    "<div style='height:1.8rem;border-bottom:"
                    "1px solid #1E293B;'></div>",
                    unsafe_allow_html=True
                )

    st.divider()
    st.subheader("Book a Slot")
    b1, b2, b3 = st.columns(3)
    with b1:
        start = st.selectbox("Start", SLOT_HOURS)
    with b2:
        end = st.selectbox("End", SLOT_HOURS, index=1)
    with b3:
        team = st.text_input("Team / Purpose")

    st.write("")
    if st.button("Confirm Booking", use_container_width=True):
        conflict = any(b["start"] < end and start < b["end"] for b in bookings)
        if conflict:
            st.error(f"Conflict detected — {start} to {end} overlaps with an existing booking.")
        elif not team.strip():
            st.error("Please enter a team or purpose.")
        else:
            _add_booking(resource["id"], booking_date, start, end, team)
            st.success("Slot booked successfully!")
            st.rerun()

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

# ── MAINTENANCE ───────────────────────────────────
KANBAN_COLUMNS = ["Pending","Approved","Technician Assigned","In Progress","Resolved"]

PRIORITY_COLORS = {
    "Low": ("#D1FAE5", "#065F46"),
    "Medium": ("#FEF3C7", "#92400E"),
    "High": ("#FEE2E2", "#991B1B"),
    "Critical": ("#450A0A", "#FCA5A5")
}

def show_maintenance():
    page_header("Maintenance Management",
                "Approving a request moves asset to Under Maintenance; resolving returns it to Available.")
    user = st.session_state.user
    role = user["role"]
    tab1, tab2 = st.tabs(["Board", "Raise Request"])

    with tab1:
        requests = get_all_maintenance()
        sub_stage = st.session_state.setdefault("maintenance_substage", {})
        cols = st.columns(len(KANBAN_COLUMNS))

        for col, stage in zip(cols, KANBAN_COLUMNS):
            with col:
                count = sum(
                    1 for req in requests
                    if _effective_stage(req, sub_stage) == stage
                )
                st.markdown(f"""
                    <div style='background:#1E293B;border-radius:8px;
                    padding:0.5rem 0.75rem;margin-bottom:0.75rem;
                    border:1px solid #334155;'>
                        <div style='color:#94A3B8;font-size:0.75rem;
                        text-transform:uppercase;letter-spacing:1px;
                        font-weight:600;'>{stage}</div>
                        <div style='color:#F1F5F9;font-size:1.1rem;
                        font-weight:700;'>{count}</div>
                    </div>
                """, unsafe_allow_html=True)

                for req in requests:
                    if _effective_stage(req, sub_stage) != stage:
                        continue
                    local = sub_stage.get(req["id"], {})
                    _render_maintenance_card(req, local, role)

    with tab2:
        assets = get_all_assets()
        if not assets:
            st.warning("No assets registered yet!")
            return
        asset_options = {f"{a['asset_tag']} — {a['name']}": a["id"] for a in assets}
        col1, col2 = st.columns(2)
        with col1:
            asset = st.selectbox("Select Asset", list(asset_options.keys()))
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        with col2:
            description = st.text_area("Describe the Issue", height=120)

        st.write("")
        if st.button("Submit Maintenance Request", use_container_width=True):
            if not description:
                st.error("Please describe the issue.")
            else:
                success, msg = raise_maintenance(
                    asset_options[asset], user["id"],
                    description, priority
                )
                if success:
                    st.success(msg)
                    st.rerun()

def _effective_stage(req, sub_stage):
    if req["status"] == "Resolved":
        return "Resolved"
    if req["status"] == "Pending":
        return "Pending"
    return sub_stage.get(req["id"], {}).get("stage", "Approved")

def _render_maintenance_card(req, local, role):
    bg, text = PRIORITY_COLORS.get(req["priority"], ("#1E293B", "#F1F5F9"))
    tech_html = (
        f"<div style='color:{text};font-size:0.75rem;margin-top:4px;'>"
        f"Tech: {local['technician']}</div>"
        if local.get("technician") else ""
    )
    st.markdown(f"""
        <div style='background:{bg};border-radius:8px;
        padding:0.7rem 0.8rem;margin-bottom:0.5rem;'>
            <div style='color:{text};font-weight:700;
            font-size:0.85rem;'>{req['asset_tag']}</div>
            <div style='color:{text};font-size:0.8rem;
            margin-top:2px;opacity:0.9;'>{req['description'][:60]}...</div>
            <div style='color:{text};font-size:0.7rem;
            margin-top:4px;opacity:0.7;'>{req['priority']} priority</div>
            {tech_html}
        </div>
    """, unsafe_allow_html=True)

    if role not in ["admin", "asset_manager"]:
        return

    if req["status"] == "Pending":
        if st.button("Approve", key=f"approve_{req['id']}",
                     use_container_width=True):
            approve_maintenance(req["id"])
            st.rerun()

    elif req["status"] == "Approved" and not local.get("stage"):
        tech = st.text_input("Assign technician",
                             key=f"tech_{req['id']}")
        if st.button("Assign", key=f"assign_{req['id']}",
                     use_container_width=True) and tech.strip():
            st.session_state.maintenance_substage[req["id"]] = {
                "stage": "Technician Assigned",
                "technician": tech
            }
            st.rerun()

    elif local.get("stage") == "Technician Assigned":
        if st.button("Start Work", key=f"start_{req['id']}",
                     use_container_width=True):
            local["stage"] = "In Progress"
            st.rerun()

    elif local.get("stage") == "In Progress":
        if st.button("Mark Resolved", key=f"resolve_{req['id']}",
                     use_container_width=True):
            resolve_maintenance(req["id"])
            st.session_state.maintenance_substage.pop(req["id"], None)
            st.rerun()

# ── ORGANIZATION ──────────────────────────────────
def show_organization():
    page_header("Organization Setup",
                "Manage departments and asset categories.")
    tab1, tab2 = st.tabs(["Departments", "Asset Categories"])

    with tab1:
        depts = get_all_departments()
        if depts:
            df = pd.DataFrame([dict(d) for d in depts])
            st.dataframe(df[["id", "name", "status"]],
                        hide_index=True, use_container_width=True)
        st.divider()
        st.subheader("Create Department")
        name = st.text_input("Department Name")
        if st.button("Create Department", use_container_width=True):
            if name:
                create_department(name)
                st.success(f"Department '{name}' created!")
                st.rerun()
            else:
                st.error("Please enter a department name.")

    with tab2:
        cats = get_all_categories()
        if cats:
            df = pd.DataFrame([dict(c) for c in cats])
            st.dataframe(df[["id", "name"]],
                        hide_index=True, use_container_width=True)
        st.divider()
        st.subheader("Create Category")
        cat_name = st.text_input("Category Name")
        if st.button("Create Category", use_container_width=True):
            if cat_name:
                create_category(cat_name)
                st.success(f"Category '{cat_name}' created!")
                st.rerun()
            else:
                st.error("Please enter a category name.")

# ── USERS ─────────────────────────────────────────
def show_users():
    page_header("User Management",
                "View all users and assign roles. Only admins can promote users.")
    users = get_all_users()
    if users:
        df = pd.DataFrame([dict(u) for u in users])
        st.dataframe(
            df[["id", "name", "email", "role", "status"]],
            hide_index=True,
            use_container_width=True
        )
        st.caption(f"{len(users)} user(s) registered")

    st.divider()
    st.subheader("Promote User")
    st.caption("Roles can only be assigned here — users cannot self-assign admin roles.")
    col1, col2 = st.columns(2)
    user_options = {u["name"]: u["id"] for u in users}
    with col1:
        selected = st.selectbox("Select User", list(user_options.keys()))
    with col2:
        role = st.selectbox("New Role",
                           ["employee", "dept_head", "asset_manager", "admin"])
    st.write("")
    if st.button("Update Role", use_container_width=True):
        promote_user(user_options[selected], role)
        st.success(f"Role updated to {role} successfully!")
        st.rerun()

# ── NOTIFICATIONS ─────────────────────────────────
def show_notifications():
    page_header("Notifications", "Stay updated on asset activity.")
    user = st.session_state.user
    notifs = get_notifications(user["id"])

    if notifs:
        for n in notifs:
            st.markdown(f"""
                <div style='background:#1E293B;border-radius:10px;
                padding:0.8rem 1.1rem;border:1px solid #334155;
                margin-bottom:0.5rem;border-left:3px solid #6366F1;'>
                    <div style='color:#F1F5F9;font-size:0.9rem;'>
                    {n['message']}</div>
                    <div style='color:#475569;font-size:0.75rem;
                    margin-top:4px;'>{n['created_at']}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='background:#1E293B;border-radius:12px;
            padding:2rem;text-align:center;border:1px solid #334155;'>
                <div style='color:#64748B;'>No notifications yet.</div>
            </div>
        """, unsafe_allow_html=True)