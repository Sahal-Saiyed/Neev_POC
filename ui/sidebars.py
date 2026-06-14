import streamlit as st

from ui.common import logout, get_selected_project

def admin_sidebar():
    with st.sidebar:
        st.markdown("## ⚛️ BBSteel Admin")
        st.markdown("---")

        st.markdown("### ADMIN PANEL")

        if st.button("📊 Admin Dashboard", use_container_width=True):
            st.session_state.admin_current_page = "admin_dashboard"
            st.rerun()

        if st.button("📐 Shape & Formula Management", use_container_width=True):
            st.session_state.admin_current_page = "shape_formula_management"
            st.session_state.selected_admin_shape_id = None
            st.session_state.show_admin_add_shape_form = False
            st.rerun()

        if st.button("👤 User Management", use_container_width=True):
            st.session_state.admin_current_page = "admin_user_management"
            st.session_state.selected_admin_user_id = None
            st.rerun()

        if st.button("📁 Project Monitoring", use_container_width=True):
            st.session_state.admin_current_page = "admin_project_monitoring"
            st.rerun()

        if st.button("🤖 AI Requests", use_container_width=True):
            st.session_state.admin_current_page = "admin_ai_requests"
            st.session_state.selected_ai_request_id = None
            st.rerun()

        if st.button("🧾 Audit Logs", use_container_width=True):
            st.session_state.admin_current_page = "admin_audit_logs"
            st.rerun()

        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.admin_current_page = "admin_settings"
            st.rerun()

        st.markdown("---")

        st.write("Logged in as:")
        st.success(st.session_state.name)
        st.info(f"Role: {st.session_state.role}")

        if st.button("Logout", use_container_width=True):
            logout()
def main_sidebar():
    with st.sidebar:
        st.markdown("## ⚛️ BBSteel")
        st.markdown("---")

        st.markdown("### DASHBOARD")

        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()

        if st.button("👥 Project Management", use_container_width=True):
            st.session_state.current_page = "project_management"
            st.rerun()

        if st.button("🤖 AI Assistant", use_container_width=True):
            st.session_state.current_page = "ai_assistant"
            st.rerun()

        if st.button("📨 My AI Requests", use_container_width=True):
            st.session_state.current_page = "my_ai_requests"
            st.rerun()

        if st.button("👤 User Management", use_container_width=True):
            st.session_state.current_page = "user_management"
            st.rerun()

        if st.button("📅 Subscription", use_container_width=True):
            st.session_state.current_page = "subscription"
            st.rerun()

        if st.button("💳 Payment History", use_container_width=True):
            st.session_state.current_page = "payment_history"
            st.rerun()

        st.markdown("---")

        st.write("Logged in as:")
        st.success(st.session_state.name)
        st.info(f"Role: {st.session_state.role}")

        if st.button("Logout", use_container_width=True):
            logout()


def project_sidebar():
    project = get_selected_project()

    with st.sidebar:
        st.markdown("## ⚛️ BBSteel")
        st.markdown("---")

        st.markdown("### DASHBOARD")

        if project:
            st.caption(f"Project: {project.get('project_name', 'Unknown')}")

        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.project_subpage = "project_dashboard"
            st.rerun()

        if st.button("🧱 Blocks", use_container_width=True):
            st.session_state.project_subpage = "blocks"
            st.session_state.selected_block_id = None
            st.rerun()

        if st.button("📅 AutoCAD Import", use_container_width=True):
            st.session_state.project_subpage = "autocad_import"
            st.session_state.selected_autocad_import_id = None
            st.session_state.show_new_autocad_import_form = False
            st.rerun()

        if st.button("♻️ Waste Inventory", use_container_width=True):
            st.session_state.project_subpage = "waste_inventory"
            st.rerun()

        if st.button("🔐 Access Control", use_container_width=True):
            st.session_state.project_subpage = "access_control"
            st.rerun()

        st.markdown("---")

        if st.button("⬅ Back to Projects", use_container_width=True):
            st.session_state.current_page = "project_management"
            st.session_state.selected_project_id = None
            st.session_state.project_subpage = "project_dashboard"
            st.rerun()

        if st.button("Logout", use_container_width=True):
            logout()


def render_sidebar():
    if st.session_state.current_page == "project_detail":
        project_sidebar()
    else:
        main_sidebar()
