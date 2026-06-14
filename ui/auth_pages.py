import streamlit as st

from services.auth_service import (
    count_admin_users,
    count_normal_users,
    find_user_by_email,
    register_user,
    authenticate_user
)


def registration_page():
    st.title("User Registration")
    st.write("Create an account for the POC.")

    with st.form("registration_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        role = st.selectbox(
            "Role",
            ["user", "admin"]
        )

        submit = st.form_submit_button("Register")

    if submit:
        name = name.strip()
        email = email.strip().lower()

        if not name or not email or not password or not confirm_password:
            st.error("Please fill all fields.")
            return

        if password != confirm_password:
            st.error("Password and confirm password do not match.")
            return

        existing_user = find_user_by_email(email)

        if existing_user:
            st.error("This email is already registered.")
            return

        if role == "admin":
            admin_count = count_admin_users()

            if admin_count >= 1:
                st.error("Only one admin is allowed in this POC.")
                return

        if role == "user":
            user_count = count_normal_users()

            if user_count >= 3:
                st.error("Only three users are allowed in this POC.")
                return

        register_user(
            name=name,
            email=email,
            password=password,
            role=role
        )

        st.success("Registration successful. Please login now.")


def login_page():
    st.title("Login")
    st.write("Login to continue.")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        submit = st.form_submit_button("Login")

    if submit:
        email = email.strip().lower()

        if not email or not password:
            st.error("Please enter email and password.")
            return

        user = authenticate_user(email, password)

        if not user:
            st.error("Invalid email or password.")
            return

        st.session_state.logged_in = True
        st.session_state.user_id = str(user["_id"])
        st.session_state.name = user["name"]
        st.session_state.email = user["email"]
        st.session_state.role = user["role"]

        st.success("Login successful.")
        st.rerun()