import streamlit as st

def dashboard_page():
    st.title("Dashboard")

    st.write("Welcome to BBSteel dashboard.")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Employees", "1")

    with col2:
        st.metric("Total Projects", "2")

    with col3:
        st.metric("Total Imports", "16")

    col4, col5 = st.columns(2)

    with col4:
        st.metric("Current Subscription Plan", "11 Projects")

    with col5:
        st.metric("Total Estimated", "14808.28")