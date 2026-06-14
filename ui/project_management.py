import streamlit as st

from services.project_service import (
    create_project,
    list_projects
)

def project_management_page():
    st.title("Project Management")
    st.caption("Home")

    st.markdown("---")

    header_col1, header_col2, header_col3 = st.columns([2, 2, 1])

    with header_col1:
        st.subheader("My Projects")

    with header_col2:
        search_text = st.text_input(
            "Search Here",
            label_visibility="collapsed",
            placeholder="Search Here"
        )

    with header_col3:
        new_project_clicked = st.button(
            "+ New Project",
            use_container_width=True
        )

    if new_project_clicked:
        st.session_state.show_new_project_form = True

    if "show_new_project_form" not in st.session_state:
        st.session_state.show_new_project_form = False

    if st.session_state.show_new_project_form:
        new_project_form()

    st.markdown("---")

    show_projects(search_text)

def new_project_form():
    st.subheader("Create New Project")

    with st.form("new_project_form"):
        project_name = st.text_input("Project Name")
        description = st.text_area("Description")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")

        col1, col2 = st.columns(2)

        with col1:
            submit = st.form_submit_button("Create Project")

        with col2:
            cancel = st.form_submit_button("Cancel")

    if cancel:
        st.session_state.show_new_project_form = False
        st.rerun()

    if submit:
        project_name = project_name.strip()
        description = description.strip()

        if not project_name:
            st.error("Project name is required.")
            return

        if end_date < start_date:
            st.error("End date cannot be before start date.")
            return

        create_project(
            project_name=project_name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            created_by=st.session_state.email,
            created_by_name=st.session_state.name
        )

        st.success("Project created successfully.")

        st.session_state.show_new_project_form = False
        st.rerun()

def show_projects(search_text=""):
    projects = list_projects(
        user_email=st.session_state.email,
        role=st.session_state.role,
        search_text=search_text
    )

    if not projects:
        st.info("No projects found.")
        return

    cols = st.columns(2)

    for index, project in enumerate(projects):
        col = cols[index % 2]

        with col:
            with st.container(border=True):
                st.caption(f"#{project.get('project_code', 'N/A')}")
                st.subheader(project.get("project_name", "Untitled Project"))

                description = project.get("description", "")
                if description:
                    st.write(description)
                else:
                    st.write("No description available.")

                st.markdown("---")

                date_col1, date_col2 = st.columns(2)

                with date_col1:
                    st.write(f"📅 Start Date: {project.get('start_date', 'N/A')}")

                with date_col2:
                    st.write(f"📅 End Date: {project.get('end_date', 'N/A')}")

                if st.button(
                    "Open Project",
                    key=f"open_project_{project['_id']}",
                    use_container_width=True
                ):
                    st.session_state.selected_project_id = str(project["_id"])
                    st.session_state.current_page = "project_detail"
                    st.session_state.project_subpage = "project_dashboard"
                    st.rerun()