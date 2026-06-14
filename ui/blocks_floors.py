import streamlit as st

from services.block_service import (
    create_block,
    list_blocks,
    get_block_by_id
)

from services.floor_service import (
    create_floor,
    list_floors,
    count_floors_by_block
)

def blocks_subpage(project):
    st.title("Blocks")
    st.caption(f"Home • {project.get('project_name', 'Project')} • Blocks")

    st.markdown("---")

    header_col1, header_col2, header_col3 = st.columns([2, 2, 1])

    with header_col1:
        st.subheader("Blocks")

    with header_col2:
        search_text = st.text_input(
            "Search Block",
            label_visibility="collapsed",
            placeholder="Search Here"
        )

    with header_col3:
        if st.button("+ New Block", use_container_width=True):
            st.session_state.show_new_block_form = True
            st.rerun()

    if st.session_state.show_new_block_form:
        new_block_form(project)

    st.markdown("---")

    show_blocks(project, search_text)

def block_detail_subpage(project):
    block = get_selected_block()

    if not block:
        st.error("Block not found.")

        if st.button("Back to Blocks"):
            st.session_state.project_subpage = "blocks"
            st.session_state.selected_block_id = None
            st.rerun()

        return

    st.title("Floors")
    st.caption(
        f"Home • {project.get('project_name', 'Project')} • Blocks • {block.get('block_name', 'Block')} • Floors"
    )

    st.markdown("---")

    header_col1, header_col2, header_col3, header_col4 = st.columns([1.5, 2, 1.5, 1.2])

    with header_col1:
        floor_count = count_floors_by_block(str(block["_id"]))
        st.subheader(f"{block.get('block_name', 'Block')}  >  Floors ({floor_count})")

    with header_col2:
        search_text = st.text_input(
            "Search Floor",
            label_visibility="collapsed",
            placeholder="Search Here"
        )

    with header_col3:
        st.button("+ Bulk Import Floor", use_container_width=True)

    with header_col4:
        if st.button("+ New Floor", use_container_width=True):
            st.session_state.show_new_floor_form = True
            st.rerun()

    if st.session_state.show_new_floor_form:
        new_floor_form(project, block)

    st.markdown("---")

    show_floors(project, block, search_text)


def new_block_form(project):
    st.subheader("Create New Block")

    with st.form("new_block_form"):
        block_name = st.text_input("Block Name")
        block_description = st.text_area("Block Description")

        col1, col2 = st.columns(2)

        with col1:
            save = st.form_submit_button("Save")

        with col2:
            cancel = st.form_submit_button("Cancel")

    if cancel:
        st.session_state.show_new_block_form = False
        st.rerun()

    if save:
        block_name = block_name.strip()
        block_description = block_description.strip()

        if not block_name:
            st.error("Block name is required.")
            return

        create_block(
            project_id=str(project["_id"]),
            project_code=project.get("project_code"),
            block_name=block_name,
            block_description=block_description,
            created_by=st.session_state.email,
            created_by_name=st.session_state.name
        )

        st.success("Block created successfully.")

        st.session_state.show_new_block_form = False
        st.rerun()

def show_blocks(project, search_text=""):
    blocks = list_blocks(
        project_id=str(project["_id"]),
        search_text=search_text
    )

    if not blocks:
        st.info("No blocks found.")
        return

    cols = st.columns(2)

    for index, block in enumerate(blocks):
        col = cols[index % 2]

        with col:
            with st.container(border=True):
                st.subheader(block.get("block_name", "Untitled Block"))

                description = block.get("block_description", "")
                if description:
                    st.write(description)
                else:
                    st.caption("No description available.")

                if st.button(
                    "Open Block",
                    key=f"open_block_{block['_id']}",
                    use_container_width=True
                ):
                    st.session_state.selected_block_id = str(block["_id"])
                    st.session_state.project_subpage = "block_detail"
                    st.session_state.show_new_floor_form = False
                    st.rerun()

def get_selected_block():
    return get_block_by_id(st.session_state.selected_block_id)

def new_floor_form(project, block):
    st.subheader("Create New Floor")

    with st.form("new_floor_form"):
        floor_name = st.text_input("Floor Name")
        floor_description = st.text_area("Floor Description")

        col1, col2 = st.columns(2)

        with col1:
            save = st.form_submit_button("Save")

        with col2:
            cancel = st.form_submit_button("Cancel")

    if cancel:
        st.session_state.show_new_floor_form = False
        st.rerun()

    if save:
        floor_name = floor_name.strip()
        floor_description = floor_description.strip()

        if not floor_name:
            st.error("Floor name is required.")
            return

        create_floor(
            project_id=str(project["_id"]),
            block_id=str(block["_id"]),
            project_code=project.get("project_code"),
            block_name=block.get("block_name"),
            floor_name=floor_name,
            floor_description=floor_description,
            created_by=st.session_state.email,
            created_by_name=st.session_state.name
        )

        st.success("Floor created successfully.")

        st.session_state.show_new_floor_form = False
        st.rerun()

def show_floors(project, block, search_text=""):
    floors = list_floors(
        project_id=str(project["_id"]),
        block_id=str(block["_id"]),
        search_text=search_text
    )

    if not floors:
        st.info("No floors found.")
        return

    cols = st.columns(2)

    for index, floor in enumerate(floors):
        col = cols[index % 2]

        with col:
            with st.container(border=True):
                st.subheader(floor.get("floor_name", "Untitled Floor"))

                description = floor.get("floor_description", "")
                if description:
                    st.write(description)
                else:
                    st.caption("No description available.")
