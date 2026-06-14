import streamlit as st

from ui.sidebars import render_sidebar

from ui.user_dashboard import dashboard_page
from ui.project_management import project_management_page
from ui.project_detail import project_detail_page
from ui.ai_assistant import ai_assistant_page
from ui.user_ai_requests import user_ai_requests_page

from ui.common import placeholder_page

def user_app():
    render_sidebar()

    if st.session_state.current_page == "dashboard":
        dashboard_page()

    elif st.session_state.current_page == "project_management":
        project_management_page()

    elif st.session_state.current_page == "project_detail":
        project_detail_page()

    elif st.session_state.current_page == "ai_assistant":
        ai_assistant_page()

    elif st.session_state.current_page == "my_ai_requests":
        user_ai_requests_page()

    elif st.session_state.current_page == "user_management":
        placeholder_page("User Management")

    elif st.session_state.current_page == "subscription":
        placeholder_page("Subscription")

    elif st.session_state.current_page == "payment_history":
        placeholder_page("Payment History")
