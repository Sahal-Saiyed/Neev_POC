import streamlit as st

# Session State Setup

def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    if "name" not in st.session_state:
        st.session_state.name = None

    if "email" not in st.session_state:
        st.session_state.email = None

    if "role" not in st.session_state:
        st.session_state.role = None

    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"

    if "selected_project_id" not in st.session_state:
        st.session_state.selected_project_id = None

    if "project_subpage" not in st.session_state:
        st.session_state.project_subpage = "project_dashboard"

    if "selected_block_id" not in st.session_state:
        st.session_state.selected_block_id = None

    if "show_new_block_form" not in st.session_state:
        st.session_state.show_new_block_form = False

    if "show_new_floor_form" not in st.session_state:
        st.session_state.show_new_floor_form = False

    if "show_new_autocad_import_form" not in st.session_state:
        st.session_state.show_new_autocad_import_form = False

    if "selected_autocad_import_id" not in st.session_state:
        st.session_state.selected_autocad_import_id = None

    if "show_new_beam_form" not in st.session_state:
        st.session_state.show_new_beam_form = False

    if "selected_beam_id" not in st.session_state:
        st.session_state.selected_beam_id = None

    if "admin_current_page" not in st.session_state:
        st.session_state.admin_current_page = "admin_dashboard"

    if "selected_admin_user_id" not in st.session_state:
        st.session_state.selected_admin_user_id = None

    if "selected_admin_shape_id" not in st.session_state:
        st.session_state.selected_admin_shape_id = None

    if "show_admin_add_shape_form" not in st.session_state:
        st.session_state.show_admin_add_shape_form = False

    if "admin_shape_category" not in st.session_state:
        st.session_state.admin_shape_category = "beam"

    if "admin_shape_mode" not in st.session_state:
        st.session_state.admin_shape_mode = "list"

    if "admin_custom_shape_mode" not in st.session_state:
        st.session_state.admin_custom_shape_mode = "list"

    if "selected_admin_custom_item_id" not in st.session_state:
        st.session_state.selected_admin_custom_item_id = None

    if "selected_ai_request_id" not in st.session_state:
        st.session_state.selected_ai_request_id = None

    if "ai_chat_display_messages" not in st.session_state:
        st.session_state.ai_chat_display_messages = []

    if "ai_agent_conversation_messages" not in st.session_state:
        st.session_state.ai_agent_conversation_messages = []

    if "ai_current_structured_data" not in st.session_state:
        st.session_state.ai_current_structured_data = {}

    if "ai_latest_agent_response" not in st.session_state:
        st.session_state.ai_latest_agent_response = None
