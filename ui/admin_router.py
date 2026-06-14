import streamlit as st

from ui.sidebars import admin_sidebar

from ui.admin_dashboard import admin_dashboard_page
from ui.admin_shapes import admin_shape_formula_management_page
from ui.admin_users import admin_user_management_page
from ui.admin_ai_requests import admin_ai_requests_page

from ui.common import admin_placeholder_page

def admin_app():
    admin_sidebar()

    if st.session_state.admin_current_page == "admin_dashboard":
        admin_dashboard_page()

    elif st.session_state.admin_current_page == "shape_formula_management":
        admin_shape_formula_management_page()

    elif st.session_state.admin_current_page == "admin_user_management":
        admin_user_management_page()

    elif st.session_state.admin_current_page == "admin_project_monitoring":
        admin_placeholder_page("Project Monitoring")

    elif st.session_state.admin_current_page == "admin_ai_requests":
        admin_ai_requests_page()

    elif st.session_state.admin_current_page == "admin_audit_logs":
        admin_placeholder_page("Audit Logs")

    elif st.session_state.admin_current_page == "admin_settings":
        admin_placeholder_page("Settings")
