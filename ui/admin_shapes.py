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
    save_uploaded_shape_image,
    list_custom_shape_library_items,
    get_custom_shape_library_item_by_id,
    deactivate_custom_shape_library_item,
    reactivate_custom_shape_library_item,
    update_custom_formula_override,
    find_duplicate_project_custom_shape,
    update_project_custom_shape
)

from ui.common import (
    render_outputs_formula_table,
    render_abbreviations_for_outputs
)

def admin_shape_formula_management_page():
    st.title("Shape & Formula Management")
    st.caption("Home • Master Data • Shapes & Formulas")

    st.markdown("---")

    general_tab, custom_tab = st.tabs([
        "General Shapes & Formulas",
        "Custom Shapes & Formulas"
    ])

    with general_tab:
        admin_general_shapes_tab()

    with custom_tab:
        admin_custom_shapes_tab()

def admin_general_shapes_tab():
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

def admin_custom_shapes_tab():
    mode = st.session_state.admin_custom_shape_mode

    if mode == "list":
        tab_beam, tab_slab, tab_column, tab_footing = st.tabs(
            ["Beam", "Slab", "Column / SW", "Footing / Raft"]
        )

        with tab_beam:
            admin_custom_category_tab(category="beam", title="Beam")

        with tab_slab:
            admin_custom_category_tab(category="slab", title="Slab")

        with tab_column:
            admin_custom_category_tab(category="column", title="Column / SW")

        with tab_footing:
            admin_custom_category_tab(category="footing", title="Footing / Raft")

    elif mode == "view":
        admin_view_custom_item()

    elif mode == "edit":
        admin_edit_custom_item()


def admin_custom_category_tab(category: str, title: str):
    st.subheader(f"{title} Custom Shapes & Formulas")

    search_col, status_col = st.columns([3, 1])

    with search_col:
        search_text = st.text_input(
            "Search custom item",
            placeholder=f"Search {title.lower()} custom shape, formula, or project",
            label_visibility="collapsed",
            key=f"custom_search_{category}"
        )

    with status_col:
        status_filter = st.selectbox(
            "Status",
            ["All", "Active", "Inactive"],
            key=f"custom_status_{category}"
        )

    custom_items = list_custom_shape_library_items(
        category=category,
        search_text=search_text,
        status_filter=status_filter
    )

    if not custom_items:
        st.info(f"No custom {title.lower()} shapes or formulas found.")
        return

    for custom_item in custom_items:
        render_custom_item_card(custom_item)


def render_custom_item_card(custom_item: dict):
    custom_item_id = str(custom_item["_id"])
    customization_type = custom_item.get("customization_type_label", "Customization")
    shape_name = custom_item.get("display_shape_name", "N/A")
    description = custom_item.get("display_description", "")
    outputs = custom_item.get("display_outputs", [])
    status = "Active" if custom_item.get("is_active", True) else "Inactive"
    image_path = custom_item.get("display_image_path")

    with st.container(border=True):
        image_col, top_col1, top_col2, top_col3 = st.columns([1, 2, 2, 1])
        with image_col:
            if image_path and os.path.exists(image_path):
                st.image(
                    image_path,
                    use_container_width=True
                )
            else:
                st.caption("No image")

        with top_col1:
            st.markdown(f"### {shape_name}")
            st.write(f"**Customization Type:** {customization_type}")
            st.write(f"**Status:** {status}")

        with top_col2:
            st.write(f"**Project:** {custom_item.get('project_name', 'N/A')}")
            st.write(f"**Category:** {custom_item.get('category', 'N/A').title()}")
            st.write(f"**Request ID:** {custom_item.get('request_code', 'N/A')}")
            st.write(f"**Requested By:** {custom_item.get('requested_by_name', 'N/A')}")

        with top_col3:
            if st.button(
                "View",
                key=f"view_custom_item_{custom_item_id}",
                use_container_width=True
            ):
                st.session_state.selected_admin_custom_item_id = custom_item_id
                st.session_state.admin_custom_shape_mode = "view"
                st.rerun()

        if description:
            st.write(f"**Description:** {description}")

        if outputs:
            st.markdown("**Formulas**")

            for output in outputs:
                st.write(
                    f"**{output.get('output_name', 'Output')} "
                    f"({output.get('unit', 'm')})**: "
                    f"`{output.get('formula', 'N/A')}`"
                )


def get_selected_admin_custom_item():
    return get_custom_shape_library_item_by_id(
        st.session_state.selected_admin_custom_item_id
    )


def admin_view_custom_item():
    custom_item = get_selected_admin_custom_item()

    if not custom_item:
        st.error("Custom shape/formula not found.")

        if st.button("Back to Custom Shapes & Formulas"):
            st.session_state.admin_custom_shape_mode = "list"
            st.session_state.selected_admin_custom_item_id = None
            st.rerun()

        return

    customization_type = custom_item.get("customization_type_label", "Customization")
    shape_name = custom_item.get("display_shape_name", "N/A")
    outputs = custom_item.get("display_outputs", [])
    description = custom_item.get("display_description", "")

    st.subheader(shape_name)
    st.caption(customization_type)

    st.markdown("---")

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.write(f"**Project:** {custom_item.get('project_name', 'N/A')}")
        st.write(f"**Category:** {custom_item.get('category', 'N/A').title()}")
        st.write(f"**Status:** {'Active' if custom_item.get('is_active', True) else 'Inactive'}")
        st.write(f"**Request ID:** {custom_item.get('request_code', 'N/A')}")

    with info_col2:
        st.write(f"**Requested By:** {custom_item.get('requested_by_name', 'N/A')}")
        st.write(f"**Requested Email:** {custom_item.get('requested_by', 'N/A')}")
        st.write(f"**Updated By:** {custom_item.get('updated_by', 'N/A')}")

        updated_at = custom_item.get("updated_at")
        if updated_at:
            st.write(f"**Updated At:** {updated_at.strftime('%d/%m/%Y %H:%M')}")

    if description:
        st.markdown("---")
        st.write(f"**Description:** {description}")

    if custom_item.get("type") == "custom_shape":
        image_path = custom_item.get("image_path")

        if image_path and os.path.exists(image_path):
            st.markdown("---")
            st.markdown("**Shape Image**")
            st.image(image_path, width=350)

    st.markdown("---")

    render_outputs_formula_table(outputs)
    render_abbreviations_for_outputs(outputs)

    st.markdown("---")

    action_col1, action_col2, action_col3 = st.columns(3)

    with action_col1:
        if st.button("Edit", use_container_width=True):
            st.session_state.admin_custom_shape_mode = "edit"
            st.rerun()

    with action_col2:
        if custom_item.get("is_active", True):
            if st.button("Deactivate", use_container_width=True):
                deactivate_custom_shape_library_item(
                    custom_item_id=str(custom_item["_id"]),
                    admin_email=st.session_state.email
                )
                st.success("Customization deactivated.")
                st.rerun()
        else:
            if st.button("Reactivate", use_container_width=True):
                reactivate_custom_shape_library_item(
                    custom_item_id=str(custom_item["_id"]),
                    admin_email=st.session_state.email
                )
                st.success("Customization reactivated.")
                st.rerun()

    with action_col3:
        if st.button("Back", use_container_width=True):
            st.session_state.admin_custom_shape_mode = "list"
            st.session_state.selected_admin_custom_item_id = None
            st.rerun()

def admin_edit_custom_item():
    custom_item = get_selected_admin_custom_item()

    if not custom_item:
        st.error("Custom shape/formula not found.")

        if st.button("Back to Custom Shapes & Formulas"):
            st.session_state.admin_custom_shape_mode = "list"
            st.session_state.selected_admin_custom_item_id = None
            st.rerun()

        return

    if custom_item.get("type") == "formula_override":
        admin_edit_custom_formula_form(custom_item)
    elif custom_item.get("type") == "custom_shape":
        admin_edit_custom_shape_form(custom_item)
    else:
        st.error("Unsupported customization type.")

        if st.button("Back"):
            st.session_state.admin_custom_shape_mode = "view"
            st.rerun()


def admin_edit_custom_formula_form(custom_item: dict):
    st.subheader("Edit Custom Formula")
    st.caption(custom_item.get("display_shape_name", "Custom Formula"))

    st.write(f"**Project:** {custom_item.get('project_name', 'N/A')}")
    st.write(f"**Base Shape:** {custom_item.get('base_shape_name', 'N/A')}")
    st.write(f"**Request ID:** {custom_item.get('request_code', 'N/A')}")
    st.write(f"**Requested By:** {custom_item.get('requested_by_name', 'N/A')}")

    st.markdown("---")

    old_outputs = custom_item.get("override_outputs", [])

    with st.form("admin_edit_custom_formula_form"):
        output_count = st.number_input(
            "Number of Formula Outputs",
            min_value=1,
            max_value=10,
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
                    key=f"custom_formula_output_name_{i}"
                )

            with col2:
                formula = st.text_input(
                    "Formula",
                    value=old_output.get("formula", ""),
                    key=f"custom_formula_formula_{i}"
                )

            with col3:
                unit = st.text_input(
                    "Unit",
                    value=old_output.get("unit", "m"),
                    key=f"custom_formula_unit_{i}"
                )

            output_rows.append({
                "output_name": output_name,
                "formula": formula,
                "unit": unit
            })

        is_active = st.checkbox(
            "Active",
            value=custom_item.get("is_active", True)
        )

        col_save, col_cancel = st.columns(2)

        with col_save:
            save = st.form_submit_button("Save Changes")

        with col_cancel:
            cancel = st.form_submit_button("Cancel")

    if cancel:
        st.session_state.admin_custom_shape_mode = "view"
        st.rerun()

    if save:
        try:
            update_custom_formula_override(
                custom_item_id=str(custom_item["_id"]),
                override_outputs=output_rows,
                is_active=is_active,
                admin_email=st.session_state.email
            )

            st.success("Custom formula updated successfully.")
            st.session_state.admin_custom_shape_mode = "view"
            st.rerun()

        except Exception as error:
            st.error(str(error))


def admin_edit_custom_shape_form(custom_item: dict):
    st.subheader("Edit Custom Shape")
    st.caption(custom_item.get("display_shape_name", "Custom Shape"))

    st.write(f"**Project:** {custom_item.get('project_name', 'N/A')}")
    st.write(f"**Request ID:** {custom_item.get('request_code', 'N/A')}")
    st.write(f"**Requested By:** {custom_item.get('requested_by_name', 'N/A')}")

    image_path = custom_item.get("image_path")

    if image_path and os.path.exists(image_path):
        st.image(image_path, width=350)

    st.markdown("---")

    old_outputs = custom_item.get("outputs", [])

    with st.form("admin_edit_custom_shape_form"):
        shape_name = st.text_input(
            "Shape Name",
            value=custom_item.get("shape_name", "")
        )

        description = st.text_area(
            "Description",
            value=custom_item.get("description", "")
        )

        uploaded_image = st.file_uploader(
            "Upload New Shape Image",
            type=["png", "jpg", "jpeg"]
        )

        output_count = st.number_input(
            "Number of Outputs",
            min_value=1,
            max_value=10,
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
                    key=f"custom_shape_output_name_{i}"
                )

            with col2:
                formula = st.text_input(
                    "Formula",
                    value=old_output.get("formula", ""),
                    key=f"custom_shape_formula_{i}"
                )

            with col3:
                unit = st.text_input(
                    "Unit",
                    value=old_output.get("unit", "m"),
                    key=f"custom_shape_unit_{i}"
                )

            output_rows.append({
                "output_name": output_name,
                "formula": formula,
                "unit": unit
            })

        is_active = st.checkbox(
            "Active",
            value=custom_item.get("is_active", True)
        )

        col_save, col_cancel = st.columns(2)

        with col_save:
            save = st.form_submit_button("Save Changes")

        with col_cancel:
            cancel = st.form_submit_button("Cancel")

    if cancel:
        st.session_state.admin_custom_shape_mode = "view"
        st.rerun()

    if save:
        shape_name = shape_name.strip()
        description = description.strip()

        if not shape_name:
            st.error("Shape name is required.")
            return

        duplicate_shape = find_duplicate_project_custom_shape(
            custom_item_id=str(custom_item["_id"]),
            project_id=custom_item.get("project_id"),
            shape_name=shape_name,
            category=custom_item.get("category", "beam")
        )

        if duplicate_shape:
            st.error("Another custom shape with this name already exists for this project.")
            return

        new_image_path = image_path

        if uploaded_image is not None:
            new_image_path = save_uploaded_shape_image(
                uploaded_file=uploaded_image,
                shape_name=shape_name,
                category=custom_item.get("category", "beam")
            )

        try:
            update_project_custom_shape(
                custom_item_id=str(custom_item["_id"]),
                shape_name=shape_name,
                description=description,
                image_path=new_image_path,
                outputs=output_rows,
                is_active=is_active,
                admin_email=st.session_state.email
            )

            st.success("Custom shape updated successfully.")
            st.session_state.admin_custom_shape_mode = "view"
            st.rerun()

        except Exception as error:
            st.error(str(error))