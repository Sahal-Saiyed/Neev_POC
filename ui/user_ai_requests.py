import streamlit as st

from services.ai_request_service import list_user_ai_requests

from ui.common import (
    get_ai_request_code,
    get_ai_request_type_label,
    render_formula_abbreviations,
    render_new_shape_request_details
)


def render_formula_update_user_request(request):
    st.markdown("**Formula Change Details**")

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.write(f"**Project:** {request.get('project_name', 'N/A')}")
        st.write(f"**Category:** {request.get('category', 'N/A')}")
        st.write(f"**Shape:** {request.get('shape_name', 'N/A')}")
        st.write(f"**Output:** {request.get('output_name', 'N/A')}")

    with info_col2:
        st.write(f"**Reason:** {request.get('reason', 'N/A')}")
        st.write("**Scope:** This request applies only to this project.")

    formula_col1, formula_col2 = st.columns(2)

    with formula_col1:
        st.markdown("**Current Formula**")
        st.code(request.get("current_formula", "N/A"), language="python")

    with formula_col2:
        st.markdown("**Requested Formula**")
        st.code(request.get("requested_formula", "N/A"), language="python")

    render_formula_abbreviations(
        request.get("requested_formula", "")
    )


def render_new_shape_user_request(request):
    st.markdown("**New Shape Details**")

    render_new_shape_request_details(request)


def render_user_ai_request_card(request):
    request_type = request.get("request_type")
    request_type_label = get_ai_request_type_label(request_type)
    request_code = get_ai_request_code(request)
    status = request.get("status", "pending")

    with st.container(border=True):
        top_col1, top_col2, top_col3 = st.columns([2, 2, 1])

        with top_col1:
            st.markdown(f"### {request_code}")
            st.write(f"**Type:** {request_type_label}")

        with top_col2:
            st.write(f"**Project:** {request.get('project_name', 'N/A')}")
            st.write(f"**Status:** {status.title()}")

        with top_col3:
            created_at = request.get("created_at")
            if created_at:
                st.caption(created_at.strftime("%d/%m/%Y %H:%M"))

        st.markdown("---")

        if request_type == "formula_update":
            render_formula_update_user_request(request)

        elif request_type == "new_shape":
            render_new_shape_user_request(request)

        else:
            st.warning("Unsupported request type.")

        admin_comment = request.get("admin_comment")

        if admin_comment:
            st.markdown("---")
            st.write(f"**Admin Comment:** {admin_comment}")

        if status == "pending":
            st.info("This request is waiting for admin review.")
        elif status == "applied":
            st.success("This request has been approved and applied to this project.")
        elif status == "rejected":
            st.error("This request was rejected.")


def user_ai_requests_page():
    st.title("My AI Requests")
    st.caption("Track formula and shape requests submitted to admin")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        search_text = st.text_input(
            "Search Requests",
            placeholder="Search by project, shape, or request number",
            label_visibility="collapsed"
        )

    with col2:
        status_filter = st.selectbox(
            "Status",
            ["All", "pending", "applied", "rejected", "needs_more_info", "approved"],
            label_visibility="collapsed"
        )

    requests = list_user_ai_requests(
        user_email=st.session_state.email,
        status_filter=status_filter,
        search_text=search_text
    )

    if not requests:
        st.info("No AI requests found.")
        return

    for request in requests:
        render_user_ai_request_card(request)