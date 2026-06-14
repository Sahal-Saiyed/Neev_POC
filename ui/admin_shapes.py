import os
import streamlit as st

from services.shape_service import (
    list_shapes,
    get_shape_by_id,
    find_shape_by_name_and_category,
    find_duplicate_shape,
    create_shape,
    update_shape,
    deactivate_global_shape,
    reactivate_global_shape,
    save_uploaded_shape_image
)

def admin_shape_formula_management_page():
    st.title("Shapes")
    st.caption("Home • Master Data • Shapes")

    st.markdown("---")

    tab_beam, tab_slab, tab_column, tab_footing = st.tabs(
        ["Beam", "Slab", "Column / SW", "Footing / Raft"]
    )

    with tab_beam:
        admin_beam_shape_tab()

    with tab_slab:
        st.info("Slab shape management will be developed later.")

    with tab_column:
        st.info("Column / SW shape management will be developed later.")

    with tab_footing:
        st.info("Footing / Raft shape management will be developed later.")

def admin_beam_shape_tab():
    mode = st.session_state.admin_shape_mode

    if mode == "list":
        admin_beam_shape_list()

    elif mode == "add":
        admin_add_shape_form(category="beam")

    elif mode == "view":
        admin_view_shape_formula()

    elif mode == "edit":
        admin_edit_shape_form()

def admin_beam_shape_list():
    header_col1, header_col2 = st.columns([3, 1])

    with header_col1:
        st.subheader("Beam Shape")

    with header_col2:
        if st.button("+ Add Beam Shape", use_container_width=True):
            st.session_state.admin_shape_mode = "add"
            st.session_state.selected_admin_shape_id = None
            st.rerun()

    st.markdown("---")

    search_text = st.text_input(
        "Search Shape",
        placeholder="Search beam shape",
        label_visibility="collapsed"
    )

    shapes = list_shapes(
        category="beam",
        search_text=search_text
    )

    if not shapes:
        st.info("No beam shapes found.")
        return

    header_cols = st.columns([3, 1, 1, 1])

    header_cols[0].markdown("**Name**")
    header_cols[1].markdown("**Size**")
    header_cols[2].markdown("**Formula**")
    header_cols[3].markdown("**Action**")

    st.markdown("---")

    for shape in shapes:
        row_cols = st.columns([3, 1, 1, 1])

        with row_cols[0]:
            img_col, text_col = st.columns([1.3, 2])

            with img_col:
                image_path = shape.get("image_path")
                if image_path and os.path.exists(image_path):
                    st.image(image_path, width=180)
                else:
                    st.caption("No image")

            with text_col:
                st.write(f"**{shape.get('shape_name', 'Untitled Shape')}**")

                if shape.get("is_active", True):
                    st.success("Active")
                else:
                    st.warning("Inactive")

        with row_cols[1]:
            st.write(len(shape.get("outputs", [])))

        with row_cols[2]:
            if st.button(
                "Formula",
                key=f"view_formula_{shape['_id']}",
                use_container_width=True
            ):
                st.session_state.selected_admin_shape_id = str(shape["_id"])
                st.session_state.admin_shape_mode = "view"
                st.rerun()

        with row_cols[3]:
            if st.button(
                "Edit",
                key=f"edit_shape_{shape['_id']}",
                use_container_width=True
            ):
                st.session_state.selected_admin_shape_id = str(shape["_id"])
                st.session_state.admin_shape_mode = "edit"
                st.rerun()

        st.markdown("---")

def get_selected_admin_shape():
    return get_shape_by_id(st.session_state.selected_admin_shape_id)

def admin_view_shape_formula():
    shape = get_selected_admin_shape()

    if not shape:
        st.error("Shape not found.")

        if st.button("Back to Shapes"):
            st.session_state.admin_shape_mode = "list"
            st.session_state.selected_admin_shape_id = None
            st.rerun()

        return

    st.subheader(shape.get("shape_name", "Shape"))
    st.caption(f"Category: {shape.get('category', 'N/A')}")

    image_path = shape.get("image_path")

    if image_path and os.path.exists(image_path):
        st.image(image_path, width=400)
    else:
        st.info("No image available for this shape.")

    st.markdown("---")

    st.subheader("Formulas")

    outputs = shape.get("outputs", [])

    if not outputs:
        st.warning("No formulas added.")
    else:
        for output in outputs:
            with st.container(border=True):
                st.write(f"**Output Name:** {output.get('output_name', 'N/A')}")
                st.code(output.get("formula", ""), language="python")
                st.write(f"**Unit:** {output.get('unit', 'm')}")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Edit Formula", use_container_width=True):
            st.session_state.admin_shape_mode = "edit"
            st.rerun()

    with col2:
        if shape.get("is_active", True):
            if st.button("Deactivate Shape", use_container_width=True):
                deactivate_global_shape(str(shape["_id"]))
                st.success("Shape deactivated.")
                st.rerun()
        else:
            if st.button("Reactivate Shape", use_container_width=True):
                reactivate_global_shape(str(shape["_id"]))
                st.success("Shape reactivated.")
                st.rerun()

    with col3:
        if st.button("Back", use_container_width=True):
            st.session_state.admin_shape_mode = "list"
            st.session_state.selected_admin_shape_id = None
            st.rerun()

def admin_add_shape_form(category="beam"):
    st.subheader("Add Beam Shape")

    with st.form("admin_add_shape_form"):
        shape_name = st.text_input("Shape Name")
        description = st.text_area("Description")

        uploaded_image = st.file_uploader(
            "Upload Shape Image",
            type=["png", "jpg", "jpeg"]
        )

        output_count = st.number_input(
            "Number of Outputs",
            min_value=1,
            max_value=6,
            value=1
        )

        st.markdown("### Output Formulas")

        output_rows = []

        for i in range(int(output_count)):
            st.markdown(f"**Output {i + 1}**")

            col1, col2, col3 = st.columns([1, 3, 1])

            with col1:
                output_name = st.text_input(
                    "Output Name",
                    value=f"L{i + 1}",
                    key=f"add_output_name_{i}"
                )

            with col2:
                formula = st.text_input(
                    "Formula",
                    key=f"add_formula_{i}",
                    placeholder="Example: (LD + (10 * D)) - CX - CO"
                )

            with col3:
                unit = st.text_input(
                    "Unit",
                    value="m",
                    key=f"add_unit_{i}"
                )

            output_rows.append({
                "output_name": output_name,
                "formula": formula,
                "unit": unit
            })

        col_save, col_cancel = st.columns(2)

        with col_save:
            save = st.form_submit_button("Save Shape")

        with col_cancel:
            cancel = st.form_submit_button("Cancel")

    if cancel:
        st.session_state.admin_shape_mode = "list"
        st.rerun()

    if save:
        shape_name = shape_name.strip()
        description = description.strip()

        if not shape_name:
            st.error("Shape name is required.")
            return

        cleaned_outputs = []

        for row in output_rows:
            if not row["output_name"].strip() or not row["formula"].strip():
                st.error("Each output must have output name and formula.")
                return

            cleaned_outputs.append({
                "output_name": row["output_name"].strip(),
                "formula": row["formula"].strip(),
                "unit": row["unit"].strip() or "m"
            })

        existing_shape = find_shape_by_name_and_category(
            shape_name=shape_name,
            category=category
        )

        if existing_shape:
            st.error("A shape with this name already exists in this category.")
            return

        image_path = save_uploaded_shape_image(
            uploaded_file=uploaded_image,
            shape_name=shape_name,
            category=category
        )

        create_shape(
            shape_name=shape_name,
            category=category,
            description=description,
            image_path=image_path,
            outputs=cleaned_outputs,
            created_by=st.session_state.email
        )

        st.success("Shape added successfully.")
        st.session_state.admin_shape_mode = "list"
        st.rerun()

def admin_edit_shape_form():
    shape = get_selected_admin_shape()

    if not shape:
        st.error("Shape not found.")

        if st.button("Back to Shapes"):
            st.session_state.admin_shape_mode = "list"
            st.session_state.selected_admin_shape_id = None
            st.rerun()

        return

    st.subheader(f"Edit Shape: {shape.get('shape_name', 'Shape')}")

    image_path = shape.get("image_path")

    if image_path and os.path.exists(image_path):
        st.image(image_path, width=350)

    old_outputs = shape.get("outputs", [])

    with st.form("admin_edit_shape_form"):
        shape_name = st.text_input(
            "Shape Name",
            value=shape.get("shape_name", "")
        )

        description = st.text_area(
            "Description",
            value=shape.get("description", "")
        )

        uploaded_image = st.file_uploader(
            "Upload New Shape Image",
            type=["png", "jpg", "jpeg"]
        )

        output_count = st.number_input(
            "Number of Outputs",
            min_value=1,
            max_value=6,
            value=max(1, len(old_outputs))
        )

        st.markdown("### Output Formulas")

        output_rows = []

        for i in range(int(output_count)):
            old_output = old_outputs[i] if i < len(old_outputs) else {}

            st.markdown(f"**Output {i + 1}**")

            col1, col2, col3 = st.columns([1, 3, 1])

            with col1:
                output_name = st.text_input(
                    "Output Name",
                    value=old_output.get("output_name", f"L{i + 1}"),
                    key=f"edit_output_name_{i}"
                )

            with col2:
                formula = st.text_input(
                    "Formula",
                    value=old_output.get("formula", ""),
                    key=f"edit_formula_{i}"
                )

            with col3:
                unit = st.text_input(
                    "Unit",
                    value=old_output.get("unit", "m"),
                    key=f"edit_unit_{i}"
                )

            output_rows.append({
                "output_name": output_name,
                "formula": formula,
                "unit": unit
            })

        is_active = st.checkbox(
            "Active",
            value=shape.get("is_active", True)
        )

        col_save, col_cancel = st.columns(2)

        with col_save:
            save = st.form_submit_button("Save Changes")

        with col_cancel:
            cancel = st.form_submit_button("Cancel")

    if cancel:
        st.session_state.admin_shape_mode = "view"
        st.rerun()

    if save:
        shape_name = shape_name.strip()
        description = description.strip()

        if not shape_name:
            st.error("Shape name is required.")
            return

        cleaned_outputs = []

        for row in output_rows:
            if not row["output_name"].strip() or not row["formula"].strip():
                st.error("Each output must have output name and formula.")
                return

            cleaned_outputs.append({
                "output_name": row["output_name"].strip(),
                "formula": row["formula"].strip(),
                "unit": row["unit"].strip() or "m"
            })

        duplicate_shape = find_duplicate_shape(
            shape_id=str(shape["_id"]),
            shape_name=shape_name,
            category=shape.get("category", "beam")
        )

        if duplicate_shape:
            st.error("Another shape with this name already exists.")
            return

        new_image_path = image_path

        if uploaded_image is not None:
            new_image_path = save_uploaded_shape_image(
                uploaded_file=uploaded_image,
                shape_name=shape_name,
                category=shape.get("category", "beam")
            )

        update_shape(
            shape_id=str(shape["_id"]),
            shape_name=shape_name,
            description=description,
            image_path=new_image_path,
            outputs=cleaned_outputs,
            is_active=is_active,
            updated_by=st.session_state.email
        )

        st.success("Shape updated successfully.")
        st.session_state.admin_shape_mode = "view"
        st.rerun()
