import streamlit as st
from db import test_connection

from ui.session_state import init_session_state
from ui.auth_pages import registration_page, login_page

from ui.user_router import user_app
from ui.admin_router import admin_app

st.set_page_config(
    page_title="AI Agent POC",
    page_icon="🤖",
    layout="centered"
)

# Temporary Dashboard
def temporary_dashboard():
    if st.session_state.role == "admin":
        admin_app()
    else:
        user_app()

# Main App
def main():
    init_session_state()

    connection_status = test_connection()

    if not connection_status:
        st.error("MongoDB connection failed. Please check your .env file or MongoDB Atlas settings.")
        return

    if st.session_state.logged_in:
        temporary_dashboard()
    else:
        menu = st.sidebar.selectbox(
            "Menu",
            ["Login", "Register"]
        )

        if menu == "Login":
            login_page()
        elif menu == "Register":
            registration_page()

if __name__ == "__main__":
    main()