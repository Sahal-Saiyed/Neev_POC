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
    list_custom_shape_library_items,
    get_custom_shape_library_item_by_id,
    deactivate_custom_shape_library_item,
    reactivate_custom_shape_library_item,
    update_custom_formula_override,
    find_duplicate_project_custom_shape,
    update_project_custom_shape
)
from services.image_service import save_uploaded_image_to_mongodb

from ui.common import (
    render_outputs_formula_table,
    render_abbreviations_for_outputs,
    render_shape_image
)

GENERAL_SHAPE_CATEGORIES = [
    {
        "key": "beam",
        "label": "Beam",
        "title": "Beam Shapes"
    },
    {
        "key": "slab",
        "label": "Slab",
        "title": "Slab Shapes"
    },
    {
        "key": "column",
        "label": "Column / SW",
        "title": "Column / SW Shapes"
    },
    {
        "key": "footing",
        "label": "Footing / Raft",
        "title": "Footing / Raft Shapes"
    }
]


def get_general_shape_category_label(category: str):
    for item in GENERAL_SHAPE_CATEGORIES:
        if item["key"] == category:
            return item["label"]

    return category.title()


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
    mode = st.session_state.admin_shape_mode

    if mode == "list":
        tab_beam, tab_slab, tab_column, tab_footing = st.tabs(
            ["Beam", "Slab", "Column / SW", "Footing / Raft"]
        )

        with tab_beam:
            admin_general_shape_category_list(
                category="beam",
                title="Beam Shapes"
            )

        with tab_slab:
            admin_general_shape_category_list(
                category="slab",
                title="Slab Shapes"
            )

        with tab_column:
            admin_general_shape_category_list(
                category="column",
                title="Column / SW Shapes"
            )

        with tab_footing:
            admin_general_shape_category_list(
                category="footing",
                title="Footing / Raft Shapes"
            )

    elif mode == "add":
        admin_add_shape_form(
            category=st.session_state.get("admin_general_shape_category", "beam")
        )

    elif mode == "view":
        admin_view_shape_formula()

    elif mode == "edit":
        admin_edit_shape_form()


def admin_general_shape_category_list(category: str, title: str):
    header_col1, header_col2 = st.columns([3, 1])

    with header_col1:
        st.subheader(title)

    with header_col2:
        if st.button(
            f"+ Add {get_general_shape_category_label(category)} Shape",
            use_container_width=True,
            key=f"add_general_shape_{category}"
        ):
            st.session_state.admin_shape_mode = "add"
            st.session_state.selected_admin_shape_id = None
            st.session_state.admin_general_shape_category = category
            st.rerun()

    search_col, status_col = st.columns([3, 1])

    with search_col:
        search_text = st.text_input(
            "Search Shape",
            placeholder=f"Search {get_general_shape_category_label(category).lower()} shape",
            label_visibility="collapsed",
            key=f"general_shape_search_{category}"
        )

    with status_col:
        status_filter = st.selectbox(
            "Status",
            ["All", "Active", "Inactive"],
            key=f"general_shape_status_{category}"
        )

    shapes = list_shapes(
        category=category,
        search_text=search_text,
        status_filter=status_filter
    )

    if not shapes:
        st.info(f"No {get_general_shape_category_label(category).lower()} shapes found.")
        return

    for shape in shapes:
        render_general_shape_card(shape)


def render_general_shape_card(shape: dict):
    shape_id = str(shape["_id"])
    shape_name = shape.get("shape_name", "Untitled Shape")
    description = shape.get("description", "")
    category = shape.get("category", "beam")
    outputs = shape.get("outputs", [])
    image_path = shape.get("image_path")
    image_file_id = shape.get("image_file_id")
    status = "Active" if shape.get("is_active", True) else "Inactive"

    with st.container(border=True):
        image_col, info_col, formula_col, action_col = st.columns([3, 3, 3, 1])

        with image_col:
            image_rendered = render_shape_image(
                image_file_id=image_file_id,
                image_path=image_path,
                use_container_width=True,
                missing_message=None
            )

            if not image_rendered:
                st.caption("No image")

        with info_col:
            st.markdown(f"### {shape_name}")
            st.write("**Type:** General Shape")
            st.write(f"**Category:** {get_general_shape_category_label(category)}")
            st.write(f"**Status:** {status}")

            if description:
                st.write(f"**Description:** {description}")

        with formula_col:
            st.markdown("**Formulas**")

            if not outputs:
                st.caption("No formulas added.")
            else:
                for output in outputs:
                    st.write(
                        f"**{output.get('output_name', 'Output')} "
                        f"({output.get('unit', 'm')})**: "
                        f"`{output.get('formula', 'N/A')}`"
                    )

        with action_col:
            if st.button(
                "View",
                key=f"view_general_shape_{shape_id}",
                use_container_width=True
            ):
                st.session_state.selected_admin_shape_id = shape_id
                st.session_state.admin_shape_mode = "view"
                st.session_state.admin_general_shape_category = category
                st.rerun()

            if st.button(
                "Edit",
                key=f"edit_general_shape_{shape_id}",
                use_container_width=True
            ):
                st.session_state.selected_admin_shape_id = shape_id
                st.session_state.admin_shape_mode = "edit"
                st.session_state.admin_general_shape_category = category
                st.rerun()


def build_output_rows_from_form(output_count: int, existing_outputs: list, key_prefix: str):
    output_rows = []

    for i in range(int(output_count)):
        old_output = existing_outputs[i] if i < len(existing_outputs) else {}

        st.markdown(f"**Output {i + 1}**")

        col1, col2, col3 = st.columns([1, 3, 1])

        with col1:
            output_name = st.text_input(
                "Output Name",
                value=old_output.get("output_name", f"L{i + 1}"),
                key=f"{key_prefix}_output_name_{i}"
            )

        with col2:
            formula = st.text_input(
                "Formula",
                value=old_output.get("formula", ""),
                key=f"{key_prefix}_formula_{i}"
            )

        with col3:
            unit = st.text_input(
                "Unit",
                value=old_output.get("unit", "m"),
                key=f"{key_prefix}_unit_{i}"
            )

        output_rows.append({
            "output_name": output_name,
            "formula": formula,
            "unit": unit
        })

    return output_rows


def validate_output_rows(output_rows: list):
    cleaned_outputs = []

    for output in output_rows:
        output_name = output.get("output_name", "").strip()
        formula = output.get("formula", "").strip()
        unit = output.get("unit", "m").strip() or "m"

        if not output_name:
            return False, "Output name is required.", []

        if not formula:
            return False, f"Formula is required for {output_name}.", []

        cleaned_outputs.append({
            "output_name": output_name,
            "formula": formula,
            "unit": unit
        })

    return True, "", cleaned_outputs


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

    shape_name = shape.get("shape_name", "Shape")
    category = shape.get("category", "beam")
    description = shape.get("description", "")
    image_path = shape.get("image_path")
    image_file_id = shape.get("image_file_id")
    outputs = shape.get("outputs", [])

    st.subheader(shape_name)
    st.caption(f"General Shape • {get_general_shape_category_label(category)}")

    st.markdown("---")

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.write("**Type:** General Shape")
        st.write(f"**Category:** {get_general_shape_category_label(category)}")
        st.write(f"**Status:** {'Active' if shape.get('is_active', True) else 'Inactive'}")

    with info_col2:
        st.write(f"**Created By:** {shape.get('created_by', 'N/A')}")
        st.write(f"**Updated By:** {shape.get('updated_by', 'N/A')}")

        updated_at = shape.get("updated_at")
        if updated_at:
            st.write(f"**Updated At:** {updated_at.strftime('%d/%m/%Y %H:%M')}")

    if description:
        st.markdown("---")
        st.write(f"**Description:** {description}")

    if image_file_id or image_path:
        st.markdown("---")
        st.markdown("**Shape Image**")
        render_shape_image(
            image_file_id=image_file_id,
            image_path=image_path,
            width=350
        )

    st.markdown("---")

    render_outputs_formula_table(outputs)
    render_abbreviations_for_outputs(outputs)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Edit", use_container_width=True):
            st.session_state.admin_shape_mode = "edit"
            st.session_state.admin_general_shape_category = category
            st.rerun()

    with col2:
        if shape.get("is_active", True):
            if st.button("Deactivate", use_container_width=True):
                deactivate_global_shape(str(shape["_id"]))
                st.success("Shape deactivated.")
                st.rerun()
        else:
            if st.button("Reactivate", use_container_width=True):
                reactivate_global_shape(str(shape["_id"]))
                st.success("Shape reactivated.")
                st.rerun()

    with col3:
        if st.button("Back", use_container_width=True):
            st.session_state.admin_shape_mode = "list"
            st.session_state.selected_admin_shape_id = None
            st.rerun()


def admin_add_shape_form(category="beam"):
    category_label = get_general_shape_category_label(category)

    st.subheader(f"Add {category_label} Shape")
    st.caption("General Shapes & Formulas")

    st.markdown("---")

    with st.form(f"admin_add_shape_form_{category}"):
        shape_name = st.text_input(
            "Shape Name",
            placeholder=f"Enter {category_label.lower()} shape name"
        )

        description = st.text_area(
            "Description",
            placeholder="Short description of this shape"
        )

        uploaded_image = st.file_uploader(
            "Shape Image",
            type=["png", "jpg", "jpeg"]
        )

        output_count = st.number_input(
            "Number of Outputs",
            min_value=1,
            max_value=10,
            value=1
        )

        st.markdown("### Output Formulas")

        output_rows = build_output_rows_from_form(
            output_count=output_count,
            existing_outputs=[],
            key_prefix=f"add_general_{category}"
        )

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

        existing_shape = find_shape_by_name_and_category(
            shape_name=shape_name,
            category=category
        )

        if existing_shape:
            st.error("A general shape with this name already exists in this category.")
            return

        is_valid, error_message, cleaned_outputs = validate_output_rows(output_rows)

        if not is_valid:
            st.error(error_message)
            return

        image_path = None
        image_file_id = None
        image_filename = None
        image_mime_type = None
        image_storage = None

        if uploaded_image is not None:
            image_metadata = save_uploaded_image_to_mongodb(
                uploaded_file=uploaded_image,
                shape_name=shape_name,
                category=category,
                uploaded_by=st.session_state.email,
                source="admin_general_shape_upload"
            )

            image_file_id = image_metadata.get("image_file_id")
            image_filename = image_metadata.get("image_filename")
            image_mime_type = image_metadata.get("image_mime_type")
            image_storage = image_metadata.get("image_storage")

        create_shape(
            shape_name=shape_name,
            category=category,
            description=description,
            image_path=image_path,
            outputs=cleaned_outputs,
            created_by=st.session_state.email,
            image_file_id=image_file_id,
            image_filename=image_filename,
            image_mime_type=image_mime_type,
            image_storage=image_storage
        )

        st.success(f"{category_label} shape added successfully.")
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

    shape_id = str(shape["_id"])
    category = shape.get("category", "beam")
    category_label = get_general_shape_category_label(category)
    old_image_path = shape.get("image_path")
    old_image_file_id = shape.get("image_file_id")
    old_image_filename = shape.get("image_filename")
    old_image_mime_type = shape.get("image_mime_type")
    old_image_storage = shape.get("image_storage")
    old_outputs = shape.get("outputs", [])

    st.subheader(f"Edit {category_label} Shape")
    st.caption("General Shapes & Formulas")

    st.markdown("---")

    if old_image_file_id or old_image_path:
        st.markdown("**Current Shape Image**")
        render_shape_image(
            image_file_id=old_image_file_id,
            image_path=old_image_path,
            width=350
        )

    with st.form(f"admin_edit_shape_form_{shape_id}"):
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
            max_value=10,
            value=max(1, len(old_outputs))
        )

        st.markdown("### Output Formulas")

        output_rows = build_output_rows_from_form(
            output_count=output_count,
            existing_outputs=old_outputs,
            key_prefix=f"edit_general_{shape_id}"
        )

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

        duplicate_shape = find_duplicate_shape(
            shape_id=shape_id,
            shape_name=shape_name,
            category=category
        )

        if duplicate_shape:
            st.error("Another general shape with this name already exists in this category.")
            return

        is_valid, error_message, cleaned_outputs = validate_output_rows(output_rows)

        if not is_valid:
            st.error(error_message)
            return

        image_path = old_image_path
        image_file_id = old_image_file_id
        image_filename = old_image_filename
        image_mime_type = old_image_mime_type
        image_storage = old_image_storage

        if uploaded_image is not None:
            image_metadata = save_uploaded_image_to_mongodb(
                uploaded_file=uploaded_image,
                shape_name=shape_name,
                category=category,
                uploaded_by=st.session_state.email,
                source="admin_general_shape_edit"
            )

            image_path = None
            image_file_id = image_metadata.get("image_file_id")
            image_filename = image_metadata.get("image_filename")
            image_mime_type = image_metadata.get("image_mime_type")
            image_storage = image_metadata.get("image_storage")

        update_shape(
            shape_id=shape_id,
            shape_name=shape_name,
            description=description,
            image_path=image_path,
            outputs=cleaned_outputs,
            is_active=is_active,
            updated_by=st.session_state.email,
            image_file_id=image_file_id,
            image_filename=image_filename,
            image_mime_type=image_mime_type,
            image_storage=image_storage
        )

        st.success(f"{category_label} shape updated successfully.")
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
    image_file_id = custom_item.get("display_image_file_id")

    with st.container(border=True):
        image_col, top_col1, top_col2, top_col3 = st.columns([1, 2, 2, 1])

        with image_col:
            image_rendered = render_shape_image(
                image_file_id=image_file_id,
                image_path=image_path,
                use_container_width=True,
                missing_message=None
            )

            if not image_rendered:
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
    image_file_id = custom_item.get("image_file_id")
    image_filename = custom_item.get("image_filename")
    image_mime_type = custom_item.get("image_mime_type")
    image_storage = custom_item.get("image_storage")

    if image_file_id or image_path:
        st.markdown("**Current Shape Image**")
        render_shape_image(
            image_file_id=image_file_id,
            image_path=image_path,
            width=350
        )

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
        new_image_file_id = image_file_id
        new_image_filename = image_filename
        new_image_mime_type = image_mime_type
        new_image_storage = image_storage

        if uploaded_image is not None:
            image_metadata = save_uploaded_image_to_mongodb(
                uploaded_file=uploaded_image,
                shape_name=shape_name,
                category=custom_item.get("category", "beam"),
                uploaded_by=st.session_state.email,
                source="admin_custom_shape_edit"
            )

            new_image_path = None
            new_image_file_id = image_metadata.get("image_file_id")
            new_image_filename = image_metadata.get("image_filename")
            new_image_mime_type = image_metadata.get("image_mime_type")
            new_image_storage = image_metadata.get("image_storage")

        try:
            update_project_custom_shape(
                custom_item_id=str(custom_item["_id"]),
                shape_name=shape_name,
                description=description,
                image_path=new_image_path,
                outputs=output_rows,
                is_active=is_active,
                admin_email=st.session_state.email,
                image_file_id=new_image_file_id,
                image_filename=new_image_filename,
                image_mime_type=new_image_mime_type,
                image_storage=new_image_storage
            )

            st.success("Custom shape updated successfully.")
            st.session_state.admin_custom_shape_mode = "view"
            st.rerun()

        except Exception as error:
            st.error(str(error))