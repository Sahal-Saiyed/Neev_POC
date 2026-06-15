import streamlit as st

from agent.langgraph_agent import run_formula_update_agent
from agent.schemas import AIRequestCreate
from agent.request_service import create_ai_request

from services.ai_request_service import create_new_shape_request
from services.image_service import save_uploaded_image_to_mongodb

from ui.common import (
    render_formula_abbreviations,
    render_outputs_formula_table,
    render_abbreviations_for_outputs,
    reset_ai_assistant_state
)

def ai_assistant_page():
    st.title("AI Assistant")
    st.caption("Create formula update requests using conversation")

    st.markdown("---")

    if not st.session_state.ai_chat_display_messages:
        st.session_state.ai_chat_display_messages.append({
            "role": "assistant",
            "content": "Hi, I’m Neev, BuniyadByte's AI assistant. How can I help you today?"
        })

    for message in st.session_state.ai_chat_display_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input("Ask AI Assistant...")

    if user_input:
        st.session_state.ai_chat_display_messages.append({
            "role": "user",
            "content": user_input
        })

        st.session_state.ai_agent_conversation_messages.append({
            "role": "user",
            "content": user_input
        })

        try:
            agent_response = run_formula_update_agent(
                user_email=st.session_state.email,
                conversation_messages=st.session_state.ai_agent_conversation_messages,
                current_structured_data=st.session_state.ai_current_structured_data
            )

            st.session_state.ai_latest_agent_response = agent_response
            st.session_state.ai_current_structured_data = agent_response.get(
                "structured_data",
                {}
            )

            st.session_state.ai_chat_display_messages.append({
                "role": "assistant",
                "content": agent_response.get(
                    "response_to_user",
                    "I could not process that request."
                )
            })

            st.rerun()

        except Exception as e:
            st.session_state.ai_chat_display_messages.append({
                "role": "assistant",
                "content": f"Agent error: {str(e)}"
            })
            st.rerun()

    latest_response = st.session_state.ai_latest_agent_response

    if latest_response and latest_response.get("ready_to_submit"):
        intent = latest_response.get("intent")
        data = latest_response.get("structured_data", {})

        st.markdown("---")

        if intent == "formula_update":
            st.subheader("Request Preview")

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Project:** {data.get('project_name', 'N/A')}")
                st.write(f"**Category:** {data.get('category', 'N/A')}")
                st.write(f"**Shape:** {data.get('shape_name', 'N/A')}")
                st.write(f"**Output:** {data.get('output_name', 'N/A')}")

            with col2:
                st.write(f"**Reason:** {data.get('reason', 'N/A')}")
                st.warning("Scope: This request will apply only to this project.")

            formula_col1, formula_col2 = st.columns(2)

            with formula_col1:
                st.markdown("**Current Formula**")
                st.code(data.get("current_formula", "N/A"), language="python")

            with formula_col2:
                st.markdown("**Requested Formula**")
                st.code(data.get("requested_formula", "N/A"), language="python")

            requested_formula = data.get("requested_formula", "")
            render_formula_abbreviations(requested_formula)

            submit_col, cancel_col = st.columns(2)

            with submit_col:
                if st.button("Submit Request to Admin", use_container_width=True):
                    try:
                        request_id = submit_ai_formula_update_request(data)
                        request_code = f"AIR-{request_id[-6:].upper()}"

                        st.session_state.ai_chat_display_messages.append({
                            "role": "assistant",
                            "content": (
                                f"Your request has been submitted successfully. "
                                f"Request No: {request_code}. "
                                f"You can track it from My AI Requests."
                            )
                        })

                        st.session_state.ai_agent_conversation_messages = []
                        st.session_state.ai_current_structured_data = {}
                        st.session_state.ai_latest_agent_response = None

                        st.rerun()

                    except Exception as e:
                        st.error(f"Failed to submit request: {str(e)}")

            with cancel_col:
                if st.button("Cancel Request"):
                    reset_ai_assistant_state()
                    st.rerun()

        elif intent == "new_shape":
            st.subheader("New Shape Request")

            st.info(
                "Upload the shape image first. After upload, review the request and submit it."
            )

            uploaded_image = st.file_uploader(
                "Upload shape image",
                type=["png", "jpg", "jpeg"],
                key="new_shape_request_image"
            )

            if uploaded_image:
                st.markdown("### New Shape Request Preview")

                image_col, info_col = st.columns([1, 2])

                with image_col:
                    st.image(
                        uploaded_image,
                        caption="Shape image preview",
                        use_container_width=True
                    )

                with info_col:
                    st.write(f"**Project:** {data.get('project_name', 'N/A')}")
                    st.write(f"**Category:** {data.get('category', 'beam').title()}")
                    st.write(f"**Shape Name:** {data.get('shape_name', 'N/A')}")
                    st.write(f"**Description:** {data.get('description', 'N/A')}")
                    st.write(f"**Reason:** {data.get('reason', 'N/A')}")

                outputs = data.get("outputs", [])

                if not outputs:
                    st.warning("No outputs found. Please provide output names and formulas.")
                else:
                    render_outputs_formula_table(outputs)
                    render_abbreviations_for_outputs(outputs)

                    submit_col, cancel_col = st.columns(2)

                    with submit_col:
                        if st.button("Submit New Shape Request", type="primary"):
                            try:
                                request_id = submit_ai_new_shape_request(
                                    data,
                                    uploaded_image
                                )
                                request_code = f"AIR-{request_id[-6:].upper()}"

                                st.session_state.ai_chat_display_messages.append({
                                    "role": "assistant",
                                    "content": (
                                        f"Your new shape request has been submitted successfully. "
                                        f"Request No: {request_code}. "
                                        f"You can track it from My AI Requests."
                                    )
                                })

                                st.session_state.ai_agent_conversation_messages = []
                                st.session_state.ai_current_structured_data = {}
                                st.session_state.ai_latest_agent_response = None

                                if "new_shape_request_image" in st.session_state:
                                    del st.session_state["new_shape_request_image"]

                                st.rerun()

                            except Exception as e:
                                st.error(f"Failed to submit request: {str(e)}")

                    with cancel_col:
                        if st.button("Cancel Request"):
                            reset_ai_assistant_state()

                            if "new_shape_request_image" in st.session_state:
                                del st.session_state["new_shape_request_image"]

                            st.rerun()

            else:
                if st.button("Cancel Request"):
                    reset_ai_assistant_state()
                    st.rerun()

    else:
        if st.session_state.ai_chat_display_messages:
            st.markdown("---")

            if st.button("Clear Chat"):
                reset_ai_assistant_state()
                st.rerun()


def submit_ai_formula_update_request(data):
    request = AIRequestCreate(
        request_type="formula_update",
        requested_by=st.session_state.email,
        requested_by_name=st.session_state.name,

        project_id=data.get("project_id"),
        project_name=data.get("project_name"),

        category=data.get("category"),

        shape_id=data.get("shape_id"),
        shape_name=data.get("shape_name"),

        output_name=data.get("output_name"),
        current_formula=data.get("current_formula"),
        requested_formula=data.get("requested_formula"),

        reason=data.get("reason"),
        ai_summary=(
            f"User requested formula update for "
            f"{data.get('shape_name')} - {data.get('output_name')} "
            f"in project {data.get('project_name')}."
        ),
        ai_suggestion=(
            "Admin should verify the requested formula. "
            "If approved, it should be applied only to this project."
        ),
        status="pending"
    )

    return create_ai_request(request)


def submit_ai_new_shape_request(data, uploaded_image):
    image_metadata = save_uploaded_image_to_mongodb(
        uploaded_file=uploaded_image,
        shape_name=data.get("shape_name"),
        category=data.get("category", "beam"),
        uploaded_by=st.session_state.email,
        source="ai_new_shape_request"
    )

    request_id = create_new_shape_request(
        requested_by=st.session_state.email,
        requested_by_name=st.session_state.name,

        project_id=data.get("project_id"),
        project_name=data.get("project_name"),

        category=data.get("category", "beam"),
        shape_name=data.get("shape_name"),
        description=data.get("description", ""),

        outputs=data.get("outputs", []),
        reason=data.get("reason", ""),

        image_path=None,
        image_file_id=image_metadata.get("image_file_id"),
        image_filename=image_metadata.get("image_filename"),
        image_mime_type=image_metadata.get("image_mime_type"),
        image_storage=image_metadata.get("image_storage")
    )

    return request_id
