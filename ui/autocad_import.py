import streamlit as st

from services.block_service import list_blocks_by_project
from services.floor_service import list_floors_by_block
from services.autocad_service import (
    create_autocad_import,
    list_autocad_imports
)

from ui.common import get_selected_autocad_import
from ui.beams import beam_tab

def autocad_import_subpage(project):
    st.title("AutoCAD Import")
    st.caption(f"Home • {project.get('project_name', 'Project')} • AutoCAD Import")

    st.markdown("---")

    header_col1, header_col2, header_col3 = st.columns([2, 1, 1])

    with header_col1:
        st.subheader("Autocad Import")

    with header_col2:
        st.button("Merge Dwg", use_container_width=True, disabled=True)

    with header_col3:
        if st.button("+ New Import", use_container_width=True):
            st.session_state.show_new_autocad_import_form = True
            st.rerun()

    if st.session_state.show_new_autocad_import_form:
        new_autocad_import_form(project)

    st.markdown("---")

    filter_col1, filter_col2 = st.columns([3, 1])

    with filter_col1:
        search_text = st.text_input(
            "Search Import",
            label_visibility="collapsed",
            placeholder="Search Here"
        )

    with filter_col2:
        status_filter = st.selectbox(
            "Status",
            ["All", "Pending", "Imported"],
            label_visibility="collapsed"
        )

    st.markdown("---")

    show_autocad_imports(project, search_text, status_filter)

def new_autocad_import_form(project):
    st.subheader("New AutoCAD Import")

    project_id = str(project["_id"])

    blocks = list_blocks_by_project(project_id)

    if not blocks:
        st.warning("Please create at least one block before adding an AutoCAD import.")
        if st.button("Go to Blocks", key="go_to_blocks_from_import"):
            st.session_state.project_subpage = "blocks"
            st.session_state.show_new_autocad_import_form = False
            st.rerun()
        return

    block_options = {
        block.get("block_name", "Untitled Block"): str(block["_id"])
        for block in blocks
    }

    with st.form("new_autocad_import_form"):
        import_name = st.text_input("Name")

        selected_block_name = st.selectbox(
            "Block",
            list(block_options.keys())
        )

        selected_block_id = block_options[selected_block_name]

        floors = list_floors_by_block(selected_block_id)

        if floors:
            floor_options = {
                floor.get("floor_name", "Untitled Floor"): str(floor["_id"])
                for floor in floors
            }

            selected_floor_name = st.selectbox(
                "Floor",
                list(floor_options.keys())
            )

            selected_floor_id = floor_options[selected_floor_name]
        else:
            selected_floor_name = None
            selected_floor_id = None
            st.warning("No floors found for selected block. Please create a floor first.")

        drawing_number = st.text_input("Drawing Number")
        structure_name = st.text_input("Structure Name")

        col1, col2 = st.columns(2)

        with col1:
            import_clicked = st.form_submit_button("Import")

        with col2:
            cancel = st.form_submit_button("Cancel")

    if cancel:
        st.session_state.show_new_autocad_import_form = False
        st.rerun()

    if import_clicked:
        import_name = import_name.strip()
        drawing_number = drawing_number.strip()
        structure_name = structure_name.strip()

        if not import_name:
            st.error("Name is required.")
            return

        if not selected_floor_id:
            st.error("Please create/select a floor before importing.")
            return

        create_autocad_import(
            project_id=project_id,
            project_code=project.get("project_code"),
            import_name=import_name,
            block_id=selected_block_id,
            block_name=selected_block_name,
            floor_id=selected_floor_id,
            floor_name=selected_floor_name,
            drawing_number=drawing_number,
            structure_name=structure_name,
            imported_by=st.session_state.email,
            imported_by_name=st.session_state.name
        )

        st.success("AutoCAD import created successfully.")

        st.session_state.show_new_autocad_import_form = False
        st.rerun()

def show_autocad_imports(project, search_text="", status_filter="All"):
    imports = list_autocad_imports(
        project_id=str(project["_id"]),
        search_text=search_text,
        status_filter=status_filter
    )

    if not imports:
        st.info("No AutoCAD imports found.")
        return

    header_cols = st.columns([0.5, 1.8, 1.8, 1.2, 1.4, 1.4, 1.2, 1.2])

    headers = ["✓", "Name", "Imported By", "Date", "Block", "Floor", "Status", "Action"]

    for col, header in zip(header_cols, headers):
        col.markdown(f"**{header}**")

    st.markdown("---")

    for item in imports:
        row_cols = st.columns([0.5, 1.8, 1.8, 1.2, 1.4, 1.4, 1.2, 1.2])

        with row_cols[0]:
            st.checkbox(
                "",
                key=f"select_import_{item['_id']}"
            )

        with row_cols[1]:
            if st.button(
                item.get("name", "Untitled"),
                key=f"open_import_name_{item['_id']}"
            ):
                st.session_state.selected_autocad_import_id = str(item["_id"])
                st.session_state.project_subpage = "autocad_import_detail"
                st.rerun()

        with row_cols[2]:
            st.write(item.get("imported_by_name", "N/A"))

        with row_cols[3]:
            imported_at = item.get("imported_at")
            if imported_at:
                st.write(imported_at.strftime("%d/%m/%Y"))
            else:
                st.write("N/A")

        with row_cols[4]:
            st.write(item.get("block_name", "N/A"))

        with row_cols[5]:
            st.write(item.get("floor_name", "N/A"))

        with row_cols[6]:
            st.info(item.get("status", "Pending"))

        with row_cols[7]:
            if st.button(
                "Open",
                key=f"open_import_action_{item['_id']}",
                use_container_width=True
            ):
                st.session_state.selected_autocad_import_id = str(item["_id"])
                st.session_state.project_subpage = "autocad_import_detail"
                st.rerun()

        st.markdown("---")

def autocad_import_detail_subpage(project):
    import_item = get_selected_autocad_import()

    if not import_item:
        st.error("AutoCAD import not found.")

        if st.button("Back to AutoCAD Import"):
            st.session_state.project_subpage = "autocad_import"
            st.session_state.selected_autocad_import_id = None
            st.rerun()

        return

    st.title(f"Autocad Import › {import_item.get('name', 'Import')}")
    st.caption(
        f"Home • {project.get('project_name', 'Project')} • AutoCAD Import • {import_item.get('name', 'Import')}"
    )

    st.markdown("---")

    top_col1, top_col2, top_col3 = st.columns([2, 1, 1])

    with top_col1:
        st.write(
            f"**Block:** {import_item.get('block_name', 'N/A')} | "
            f"**Floor:** {import_item.get('floor_name', 'N/A')}"
        )

    with top_col2:
        st.button("Merge", use_container_width=True)

    with top_col3:
        st.button("Export", use_container_width=True)

    tab_beam, tab_slab, tab_column, tab_footing = st.tabs(
        ["Beam", "Slab", "Column / SW", "Footing / Raft"]
    )

    with tab_beam:
        beam_tab(project, import_item)

    with tab_slab:
        st.info("Slab section will be developed later.")

    with tab_column:
        st.info("Column / SW section will be developed later.")

    with tab_footing:
        st.info("Footing / Raft section will be developed later.")

