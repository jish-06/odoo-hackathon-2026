import streamlit as st
import pandas as pd
from utils import (
    get_all_departments, get_all_categories,
    create_department, create_category,
    get_all_users, promote_user,
    get_notifications
)

def show_organization():
    user = st.session_state.user
    if user["role"] != "admin":
        st.error("You don't have permission to view this page.")
        return

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
    user = st.session_state.user
    if user["role"] != "admin":
        st.error("You don't have permission to view this page.")
        return

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