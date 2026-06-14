import streamlit as st

from ui.common import get_selected_project

from ui.blocks_floors import (
    blocks_subpage,
    block_detail_subpage
)

from ui.autocad_import import (
    autocad_import_subpage,
    autocad_import_detail_subpage
)

from ui.beams import beam_detail_subpage

def project_detail_page():
    project = get_selected_project()

    if not project:
        st.error("Project not found.")
        if st.button("Back to Projects"):
            st.session_state.current_page = "project_management"
            st.session_state.selected_project_id = None
            st.session_state.selected_block_id = None
            st.session_state.selected_autocad_import_id = None
            st.rerun()
        return

    if st.session_state.project_subpage == "project_dashboard":
        project_dashboard_subpage(project)

    elif st.session_state.project_subpage == "blocks":
        blocks_subpage(project)

    elif st.session_state.project_subpage == "block_detail":
        block_detail_subpage(project)

    elif st.session_state.project_subpage == "autocad_import":
        autocad_import_subpage(project)

    elif st.session_state.project_subpage == "autocad_import_detail":
        autocad_import_detail_subpage(project)

    elif st.session_state.project_subpage == "beam_detail":
        beam_detail_subpage(project)

    elif st.session_state.project_subpage == "waste_inventory":
        waste_inventory_subpage(project)

    elif st.session_state.project_subpage == "access_control":
        access_control_subpage(project)

def project_dashboard_subpage(project):
    st.title("Project Dashboard")
    st.caption(f"Home • {project.get('project_name', 'Project')} • Dashboard")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Project Code", project.get("project_code", "N/A"))

    with col2:
        st.metric("Status", project.get("status", "N/A"))

    st.subheader(project.get("project_name", "Untitled Project"))

    st.write(project.get("description", "No description available."))

    st.markdown("---")

    date_col1, date_col2 = st.columns(2)

    with date_col1:
        st.write(f"**Start Date:** {project.get('start_date', 'N/A')}")

    with date_col2:
        st.write(f"**End Date:** {project.get('end_date', 'N/A')}")

    st.write(f"**Created By:** {project.get('created_by_name', 'N/A')}")

def waste_inventory_subpage(project):
    st.title("Waste Inventory")
    st.caption(f"Home • {project.get('project_name', 'Project')} • Waste Inventory")

    st.info("Waste Inventory page will be developed later.")

def access_control_subpage(project):
    st.title("Access Control")
    st.caption(f"Home • {project.get('project_name', 'Project')} • Access Control")

    st.info("Access Control page will be developed later.")
