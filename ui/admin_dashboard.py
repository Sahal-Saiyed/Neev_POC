import streamlit as st

from services.dashboard_service import (
    get_admin_dashboard_stats,
    get_recent_projects,
    get_recent_shapes
)
def admin_dashboard_page():
    st.title("Admin Dashboard")
    st.caption("Platform overview")

    st.markdown("---")

    stats = get_admin_dashboard_stats()

    total_users = stats["total_users"]
    total_projects = stats["total_projects"]
    total_shapes = stats["total_shapes"]
    total_imports = stats["total_imports"]
    total_beams = stats["total_beams"]
    filled_beams = stats["filled_beams"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Users", total_users)

    with col2:
        st.metric("Total Projects", total_projects)

    with col3:
        st.metric("Active Shapes", total_shapes)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("AutoCAD Imports", total_imports)

    with col5:
        st.metric("Total Beams", total_beams)

    with col6:
        st.metric("Filled Beams", filled_beams)

    st.markdown("---")

    st.subheader("Recent Projects")

    recent_projects = get_recent_projects(limit=5)

    if not recent_projects:
        st.info("No recent projects found.")
    else:
        for project in recent_projects:
            with st.container(border=True):
                st.write(f"**{project.get('project_name', 'Untitled Project')}**")
                st.caption(f"Code: {project.get('project_code', 'N/A')}")
                st.write(f"Created By: {project.get('created_by_name', 'N/A')}")
                st.write(f"Status: {project.get('status', 'N/A')}")

    st.markdown("---")

    st.subheader("Recently Added Shapes")

    recent_shapes = get_recent_shapes(limit=5)

    if not recent_shapes:
        st.info("No shapes found.")
    else:
        for shape in recent_shapes:
            with st.container(border=True):
                st.write(f"**{shape.get('shape_name', 'Untitled Shape')}**")
                st.caption(f"Category: {shape.get('category', 'N/A')}")
                st.write(f"Outputs: {len(shape.get('outputs', []))}")
