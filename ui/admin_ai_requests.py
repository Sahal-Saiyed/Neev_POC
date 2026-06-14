import streamlit as st

from services.ai_request_service import (
    list_admin_ai_requests,
    get_ai_request_by_id,
    mark_ai_request_applied,
    mark_ai_request_applied_new_shape,
    reject_ai_request as reject_ai_request_service
)

from services.shape_service import (
    get_global_shape_by_id,
    apply_project_formula_override,
    approve_new_shape_request_to_project
)

from ui.common import (
    get_ai_request_code,
    get_ai_request_type_label,
    render_formula_abbreviations,
    render_new_shape_request_details
)


def admin_ai_requests_page():
    if st.session_state.selected_ai_request_id:
        admin_ai_request_detail_page()
    else:
        admin_ai_request_list_page()


def render_admin_ai_request_card(request):
    request_type = request.get("request_type")
    request_type_label = get_ai_request_type_label(request_type)
    request_code = get_ai_request_code(request)
    status = request.get("status", "pending")

    with st.container(border=True):
        top_col1, top_col2, top_col3 = st.columns([2, 2, 1])

        with top_col1:
            st.markdown(f"### {request_code}")
            st.write(f"**Type:** {request_type_label}")
            st.write(f"**Status:** {status.title()}")

        with top_col2:
            st.write(f"**Project:** {request.get('project_name', 'N/A')}")
            st.write(f"**Requested By:** {request.get('requested_by_name', 'N/A')}")

            if request_type == "formula_update":
                st.write(f"**Shape:** {request.get('shape_name', 'N/A')}")
                st.write(f"**Output:** {request.get('output_name', 'N/A')}")

            elif request_type == "new_shape":
                payload = request.get("new_shape_payload", {}) or {}
                outputs = payload.get("outputs", []) or []

                output_names = [
                    output.get("output_name")
                    for output in outputs
                    if output.get("output_name")
                ]

                st.write(
                    f"**New Shape:** "
                    f"{payload.get('shape_name') or request.get('shape_name', 'N/A')}"
                )
                st.write(
                    f"**Outputs:** "
                    f"{', '.join(output_names) if output_names else 'N/A'}"
                )

        with top_col3:
            created_at = request.get("created_at")
            if created_at:
                st.caption(created_at.strftime("%d/%m/%Y %H:%M"))

        if st.button(
            "Open Request",
            key=f"open_admin_ai_request_{str(request['_id'])}"
        ):
            st.session_state.selected_ai_request_id = str(request["_id"])
            st.rerun()


def admin_ai_request_list_page():
    st.title("AI Requests")
    st.caption("Admin • AI-generated user requests")

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_text = st.text_input(
            "Search Request",
            placeholder="Search by shape, project, or user",
            label_visibility="collapsed"
        )

    with col2:
        status_filter = st.selectbox(
            "Status",
            ["All", "pending", "approved", "rejected", "needs_more_info", "applied"],
            label_visibility="collapsed"
        )

    with col3:
        type_filter = st.selectbox(
            "Type",
            ["All", "formula_update", "new_shape"],
            label_visibility="collapsed"
        )

    requests = list_admin_ai_requests(
        status_filter=status_filter,
        request_type_filter=type_filter,
        search_text=search_text
    )


    if not requests:
        st.info("No AI requests found.")
        return


    for request in requests:
        render_admin_ai_request_card(request)

def admin_ai_request_detail_page():
    request = get_selected_ai_request()

    if not request:
        st.error("AI request not found.")

        if st.button("Back to AI Requests"):
            st.session_state.selected_ai_request_id = None
            st.rerun()

        return

    request_type = request.get("request_type", "Request")
    request_type_label = get_ai_request_type_label(request_type)

    st.title("AI Request Detail")
    st.caption(
        f"Admin • AI Requests • {request_type_label}"
    )

    st.markdown("---")

    if st.button("⬅ Back to AI Requests"):
        st.session_state.selected_ai_request_id = None
        st.rerun()

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Request Info")
        st.write(f"**Request Type:** {request_type_label}")
        st.write(f"**Status:** {request.get('status', 'N/A')}")
        st.write(f"**Requested By:** {request.get('requested_by_name', 'N/A')}")
        st.write(f"**Email:** {request.get('requested_by', 'N/A')}")
        st.write(f"**Project:** {request.get('project_name', 'N/A')}")
        st.info("Scope: This request will apply only to the selected project.")

    with col2:
        st.subheader("Shape Info")
        st.write(f"**Category:** {request.get('category', 'N/A')}")

        if request_type == "new_shape":
            payload = request.get("new_shape_payload", {})
            st.write(
                f"**New Shape:** "
                f"{payload.get('shape_name') or request.get('shape_name', 'N/A')}"
            )
        else:
            st.write(f"**Shape:** {request.get('shape_name', 'N/A')}")
            st.write(f"**Output:** {request.get('output_name', 'N/A')}")

        created_at = request.get("created_at")
        if created_at:
            st.write(f"**Created At:** {created_at.strftime('%d/%m/%Y %H:%M')}")

    st.markdown("---")

    if request_type == "formula_update":
        st.subheader("Formula Change")

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

        st.markdown("---")

        st.subheader("Reason and AI Suggestion")

        st.write(f"**Reason:** {request.get('reason', 'N/A')}")
        st.info(request.get("ai_suggestion", "No AI suggestion available."))


    elif request_type == "new_shape":
        st.subheader("New Shape Details")

        render_new_shape_request_details(request)

    else:
        st.warning("Unsupported request type.")

    st.markdown("---")

    status = request.get("status", "pending")

    if status == "pending":
        admin_ai_request_actions(request)
    else:
        st.info(f"This request is already marked as: {status}")


def apply_formula_update_request(request, admin_comment=""):
    if request.get("request_type") != "formula_update":
        st.error("Only formula update requests can be applied right now.")
        return

    project_id = request.get("project_id")
    project_name = request.get("project_name")

    shape_id = request.get("shape_id")
    shape_name = request.get("shape_name")

    category = request.get("category", "beam")
    output_name = request.get("output_name")
    requested_formula = request.get("requested_formula")

    if not project_id:
        st.error("Request is missing project ID.")
        return

    if not shape_id or not shape_name:
        st.error("Request is missing shape information.")
        return

    if not output_name or not requested_formula:
        st.error("Request is missing output name or requested formula.")
        return

    shape = get_global_shape_by_id(shape_id)

    if not shape:
        st.error("Base shape not found in global shape library.")
        return

    output_unit = "m"
    output_found = False

    for output in shape.get("outputs", []):
        if output.get("output_name", "").lower() == output_name.lower():
            output_unit = output.get("unit", "m")
            output_found = True
            break

    if not output_found:
        st.error("Output was not found in the selected base shape.")
        return

    custom_doc_id = apply_project_formula_override(
        project_id=project_id,
        project_name=project_name,
        category=category,
        base_shape_id=shape_id,
        base_shape_name=shape_name,
        output_name=output_name,
        formula=requested_formula,
        unit=output_unit,
        ai_request_id=str(request["_id"]),
        admin_email=st.session_state.email
    )

    mark_ai_request_applied(
        request_id=str(request["_id"]),
        admin_email=st.session_state.email,
        admin_comment=admin_comment,
        custom_shape_library_id=custom_doc_id
    )

    st.success("Project-specific formula override applied successfully.")
    st.rerun()

def apply_new_shape_request(request, admin_comment=""):
    if request.get("request_type") != "new_shape":
        st.error("Only new shape requests can be applied here.")
        return

    try:
        custom_shape_id = approve_new_shape_request_to_project(
            request=request,
            admin_email=st.session_state.email
        )

        mark_ai_request_applied_new_shape(
            request_id=str(request["_id"]),
            admin_email=st.session_state.email,
            admin_comment=admin_comment,
            custom_shape_library_id=custom_shape_id
        )

        st.success("New shape added to the selected project successfully.")
        st.rerun()

    except Exception as error:
        st.error(str(error))

def admin_ai_request_actions(request):
    st.subheader("Admin Action")

    admin_comment = st.text_area(
        "Admin comment",
        placeholder="Optional comment for the user"
    )

    action_col1, action_col2 = st.columns(2)

    with action_col1:
        if request.get("request_type") == "formula_update":
            if st.button("Approve & Apply to Project", type="primary"):
                apply_formula_update_request(request, admin_comment)

        elif request.get("request_type") == "new_shape":
            if st.button("Approve & Add Shape to Project", type="primary"):
                apply_new_shape_request(request, admin_comment)

        else:
            st.warning("This request type is not supported yet.")

    with action_col2:
        if st.button("Reject Request"):
            reject_ai_request(request, admin_comment)

def get_selected_ai_request():
    return get_ai_request_by_id(st.session_state.selected_ai_request_id)

def reject_ai_request(request, admin_comment=""):
    reject_ai_request_service(
        request_id=str(request["_id"]),
        admin_email=st.session_state.email,
        admin_comment=admin_comment
    )

    st.success("Request rejected.")
    st.rerun()