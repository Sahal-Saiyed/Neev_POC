import streamlit as st

from services.admin_user_service import (
    list_users,
    get_user_by_id,
    list_projects_by_user_email,
    count_projects_by_user_email,
    count_autocad_imports_by_user_email,
    count_beams_by_user_email,
    count_filled_beams_by_user_email
)
def admin_user_management_page():
    if st.session_state.selected_admin_user_id:
        admin_user_detail_page()
    else:
        admin_user_list_page()

def admin_user_list_page():
    st.title("User Management")
    st.caption("Manage platform users")

    st.markdown("---")

    search_text = st.text_input(
        "Search User",
        placeholder="Search by name or email",
        label_visibility="collapsed"
    )

    users = list_users(
        search_text=search_text,
        role_filter="user"
    )

    if not users:
        st.info("No users found.")
        return

    header_cols = st.columns([2, 2.5, 1, 1, 1.2])

    header_cols[0].markdown("**Name**")
    header_cols[1].markdown("**Email**")
    header_cols[2].markdown("**Role**")
    header_cols[3].markdown("**Projects**")
    header_cols[4].markdown("**Action**")

    st.markdown("---")

    for user in users:
        project_count = count_projects_by_user_email(user.get("email"))

        row_cols = st.columns([2, 2.5, 1, 1, 1.2])

        with row_cols[0]:
            st.write(user.get("name", "N/A"))

        with row_cols[1]:
            st.write(user.get("email", "N/A"))

        with row_cols[2]:
            st.info(user.get("role", "user"))

        with row_cols[3]:
            st.write(project_count)

        with row_cols[4]:
            if st.button(
                "Open",
                key=f"open_admin_user_{user['_id']}",
                use_container_width=True
            ):
                st.session_state.selected_admin_user_id = str(user["_id"])
                st.rerun()

        st.markdown("---")

def admin_user_detail_page():
    user = get_selected_admin_user()

    if not user:
        st.error("User not found.")

        if st.button("Back to Users"):
            st.session_state.selected_admin_user_id = None
            st.rerun()

        return

    st.title("User Detail")
    st.caption(f"Admin • User Management • {user.get('name', 'User')}")

    st.markdown("---")

    if st.button("⬅ Back to Users"):
        st.session_state.selected_admin_user_id = None
        st.rerun()

    st.markdown("---")

    user_email = user.get("email")

    total_projects = count_projects_by_user_email(user_email)
    total_imports = count_autocad_imports_by_user_email(user_email)
    total_beams = count_beams_by_user_email(user_email)
    filled_beams = count_filled_beams_by_user_email(user_email)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(user.get("name", "N/A"))
        st.write(f"**Email:** {user.get('email', 'N/A')}")
        st.write(f"**Role:** {user.get('role', 'N/A')}")

        created_at = user.get("created_at")
        if created_at:
            st.write(f"**Created At:** {created_at.strftime('%d/%m/%Y')}")
        else:
            st.write("**Created At:** N/A")

    with col2:
        st.metric("Total Projects", total_projects)
        st.metric("AutoCAD Imports", total_imports)
        st.metric("Total Beams", total_beams)
        st.metric("Filled Beams", filled_beams)

    st.markdown("---")

    st.subheader("User Projects")

    user_projects = list_projects_by_user_email(user_email)

    if not user_projects:
        st.info("This user has no projects.")
        return

    project_cols = st.columns(2)

    for index, project in enumerate(user_projects):
        col = project_cols[index % 2]

        with col:
            with st.container(border=True):
                st.caption(f"#{project.get('project_code', 'N/A')}")
                st.subheader(project.get("project_name", "Untitled Project"))

                description = project.get("description", "")
                if description:
                    st.write(description)
                else:
                    st.caption("No description available.")

                st.markdown("---")

                date_col1, date_col2 = st.columns(2)

                with date_col1:
                    st.write(f"**Start:** {project.get('start_date', 'N/A')}")

                with date_col2:
                    st.write(f"**End:** {project.get('end_date', 'N/A')}")

                st.write(f"**Status:** {project.get('status', 'N/A')}")

def get_selected_admin_user():
    return get_user_by_id(st.session_state.selected_admin_user_id)
