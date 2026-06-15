import os
import streamlit as st
from abbreviation_tool import extract_abbreviations_from_formula
from services.project_service import get_project_by_id
from services.autocad_service import get_autocad_import_by_id
from services.image_service import get_mongodb_image_bytes

# Placeholder pages for undeveloped user and admin pages
def placeholder_page(title):
    st.title(title)
    st.info(f"{title} page will be developed later.")


def admin_placeholder_page(title):
    st.title(title)
    st.info(f"{title} page will be developed later.")


# Request identifier code
def get_ai_request_code(request):
    if request.get("request_code"):
        return request.get("request_code")

    return f"AIR-{str(request.get('_id'))[-6:].upper()}"


# Formula abbreviation container
def render_formula_abbreviations(formula: str):
    abbreviations_used = extract_abbreviations_from_formula(formula)

    if not abbreviations_used:
        return

    with st.container(border=True):
        st.markdown("**Abbreviations used in requested formula**")

        table_data = [
            {
                "Abbreviation": item["short_name"],
                "Meaning": item["full_form"]
            }
            for item in abbreviations_used
        ]

        st.dataframe(
            table_data,
            hide_index=True,
            use_container_width=True,
            height=min(180, 38 * (len(table_data) + 1))
        )


# AI state reset
def reset_ai_assistant_state():
    st.session_state.ai_chat_display_messages = []
    st.session_state.ai_agent_conversation_messages = []
    st.session_state.ai_current_structured_data = {}
    st.session_state.ai_latest_agent_response = None


def get_selected_autocad_import():
    return get_autocad_import_by_id(
        st.session_state.selected_autocad_import_id
    )


def get_selected_project():
    return get_project_by_id(st.session_state.selected_project_id)


def get_ai_request_type_label(request_type: str):
    labels = {
        "formula_update": "Formula Update",
        "new_shape": "New Shape Request",
        "formula_explanation": "Formula Explanation"
    }

    return labels.get(request_type, request_type or "Request")


def get_abbreviations_from_outputs(outputs: list):
    abbreviations = {}

    for output in outputs or []:
        formula = output.get("formula", "")
        formula_abbreviations = extract_abbreviations_from_formula(formula)

        for item in formula_abbreviations:
            abbreviations[item["short_name"]] = item["full_form"]

    return [
        {
            "Abbreviation": short_name,
            "Meaning": full_form
        }
        for short_name, full_form in sorted(abbreviations.items())
    ]


def render_outputs_formula_table(outputs: list):
    outputs = outputs or []

    if not outputs:
        st.warning("No output formulas found.")
        return

    table_data = []

    for output in outputs:
        table_data.append({
            "Output": output.get("output_name", "N/A"),
            "Formula": output.get("formula", "N/A"),
            "Unit": output.get("unit", "m")
        })

    with st.container(border=True):
        st.markdown("**Outputs / Formulas**")

        st.dataframe(
            table_data,
            hide_index=True,
            use_container_width=True,
            height=min(220, 38 * (len(table_data) + 1))
        )


def render_abbreviations_for_outputs(outputs: list):
    abbreviations = get_abbreviations_from_outputs(outputs)

    if not abbreviations:
        return

    with st.container(border=True):
        st.markdown("**Abbreviations used in formulas**")

        st.dataframe(
            abbreviations,
            hide_index=True,
            use_container_width=True,
            height=min(220, 38 * (len(abbreviations) + 1))
        )


def render_new_shape_request_details(request: dict):
    payload = request.get("new_shape_payload", {}) or {}

    image_file_id = (
            payload.get("image_file_id")
            or request.get("new_shape_image_file_id")
            or request.get("image_file_id")
    )

    image_path = (
            payload.get("image_path")
            or request.get("new_shape_image_path")
            or request.get("image_path")
    )
    outputs = payload.get("outputs", []) or []

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.write(f"**Project:** {request.get('project_name', 'N/A')}")
        st.write(f"**Category:** {request.get('category', 'beam').title()}")
        st.write(
            f"**Shape Name:** "
            f"{payload.get('shape_name') or request.get('shape_name', 'N/A')}"
        )

    with info_col2:
        st.write(f"**Description:** {payload.get('description', 'N/A')}")
        st.write(f"**Reason:** {request.get('reason', 'N/A')}")

    if image_file_id or image_path:
        st.markdown("**Shape Image**")
        render_shape_image(
            image_file_id=image_file_id,
            image_path=image_path,
            width=350
        )

    render_outputs_formula_table(outputs)
    render_abbreviations_for_outputs(outputs)


def render_shape_image(
    image_file_id=None,
    image_path=None,
    width=350,
    use_container_width=False,
    missing_message="Image is not available on this deployment."
):
    """
    Renders shape image safely.

    Priority:
    1. MongoDB GridFS image_file_id
    2. Local image_path if file exists
    3. Safe fallback message

    Returns True if image was rendered, False otherwise.
    """

    image_bytes = get_mongodb_image_bytes(image_file_id)

    if image_bytes:
        if use_container_width:
            st.image(image_bytes, use_container_width=True)
        else:
            st.image(image_bytes, width=width)

        return True

    if image_path and os.path.exists(image_path):
        if use_container_width:
            st.image(image_path, use_container_width=True)
        else:
            st.image(image_path, width=width)

        return True

    if missing_message:
        st.info(missing_message)

    return False


# Logout function

def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.name = None
    st.session_state.email = None
    st.session_state.role = None

    st.session_state.current_page = "dashboard"
    st.session_state.selected_project_id = None
    st.session_state.project_subpage = "project_dashboard"
    st.session_state.selected_block_id = None

    st.session_state.show_new_autocad_import_form = False
    st.session_state.selected_autocad_import_id = None

    st.session_state.show_new_block_form = False
    st.session_state.show_new_floor_form = False

    st.session_state.show_new_beam_form = False
    st.session_state.selected_beam_id = None

    st.session_state.admin_current_page = "admin_dashboard"
    st.session_state.selected_admin_user_id = None
    st.session_state.selected_admin_shape_id = None
    st.session_state.show_admin_add_shape_form = False
    st.session_state.admin_general_shape_category = "beam"
    
    st.session_state.admin_custom_shape_mode = "list"
    st.session_state.selected_admin_custom_item_id = None
    st.session_state.selected_ai_request_id = None

    st.session_state.ai_chat_display_messages = []
    st.session_state.ai_agent_conversation_messages = []
    st.session_state.ai_current_structured_data = {}
    st.session_state.ai_latest_agent_response = None

    st.success("Logged out successfully.")
    st.rerun()
