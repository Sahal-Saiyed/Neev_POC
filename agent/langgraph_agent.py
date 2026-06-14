import json
import re
from typing import TypedDict, List, Dict, Any, Optional

from langgraph.graph import StateGraph, START, END

from agent.prompts import SYSTEM_PROMPT
from agent.llm_client import call_llm, extract_json_from_text
from agent.validators import (
    validate_formula_update_request,
    validate_new_shape_request
)
from agent.tools import find_user_projects, list_active_shapes

from abbreviation_tool import ABBREVIATION_DICTIONARY


class NeevAgentState(TypedDict, total=False):
    user_email: str
    conversation_messages: List[Dict[str, str]]
    current_structured_data: Dict[str, Any]

    context: Dict[str, Any]

    intent: str
    response_to_user: str
    missing_fields: List[str]
    ready_to_submit: bool
    structured_data: Dict[str, Any]

    validation_result: Dict[str, Any]
    extraction_error: Optional[str]


def merge_structured_data(old_data: dict, new_data: dict):
    merged = old_data.copy()

    for key, value in new_data.items():
        if value not in [None, "", []]:
            merged[key] = value

    if not merged.get("category"):
        merged["category"] = "beam"

    return merged


def normalize_text(text: str):
    return text.lower().strip()


def get_full_user_text(conversation_messages: list):
    return " ".join(
        message.get("content", "")
        for message in conversation_messages
        if message.get("role") == "user"
    )


def get_latest_user_text(conversation_messages: list):
    for message in reversed(conversation_messages):
        if message.get("role") == "user":
            return message.get("content", "")

    return ""


def improve_extraction_with_context(data: dict, context: dict, conversation_messages: list):
    improved = data.copy()

    full_user_text = get_full_user_text(conversation_messages)
    normalized_full_text = normalize_text(full_user_text)

    if not improved.get("project_name"):
        for project_name in context.get("user_projects", []):
            if project_name and normalize_text(project_name) in normalized_full_text:
                improved["project_name"] = project_name
                break

    if not improved.get("shape_name"):
        for shape in context.get("available_shapes", []):
            shape_name = shape.get("shape_name")
            if shape_name and normalize_text(shape_name) in normalized_full_text:
                improved["shape_name"] = shape_name
                improved["category"] = shape.get("category", "beam")
                break

    if not improved.get("output_name"):
        output_match = re.search(r"\bL[1-6]\b", full_user_text, re.IGNORECASE)
        if output_match:
            improved["output_name"] = output_match.group(0).upper()

    if not improved.get("reason"):
        reason_patterns = [
            r"\bbecause\b\s+(.*?)(?:\.?\s*(?:the\s+)?new formula|$)",
            r"\bas per\b\s+(.*?)(?:\.?\s*(?:the\s+)?new formula|$)",
            r"\bfor\b\s+(correction|site requirement|updated bend allowance).*?$"
        ]

        for pattern in reason_patterns:
            match = re.search(pattern, full_user_text, re.IGNORECASE)
            if match:
                reason = match.group(1).strip()
                if reason:
                    improved["reason"] = reason
                    break

    if not improved.get("category"):
        improved["category"] = "beam"

    return improved


def determine_intent(parsed_intent: str, merged_data: dict, conversation_messages: list):
    full_text = get_full_user_text(conversation_messages).lower()

    new_shape_keywords = [
        "new shape",
        "add shape",
        "create shape",
        "custom shape",
        "request shape",
        "shape request"
    ]

    formula_keywords = [
        "update formula",
        "change formula",
        "formula update",
        "new formula",
        "requested formula"
    ]

    if parsed_intent == "new_shape":
        return "new_shape"

    if any(keyword in full_text for keyword in new_shape_keywords):
        return "new_shape"

    if parsed_intent == "formula_update":
        return "formula_update"

    if any(keyword in full_text for keyword in formula_keywords):
        return "formula_update"

    if merged_data.get("requested_formula"):
        return "formula_update"

    if merged_data.get("shape_name") and merged_data.get("outputs"):
        return "new_shape"

    if merged_data.get("shape_name") and merged_data.get("output_name"):
        return "formula_update"

    return parsed_intent or "unknown"


def fallback_extract_from_user_text(
    current_data: dict,
    conversation_messages: list
):
    """
    Deterministic fallback extraction.
    Used when LLM JSON extraction fails or misses simple new-shape details.
    """

    data = current_data.copy()

    latest_text = get_latest_user_text(conversation_messages)
    full_text = get_full_user_text(conversation_messages)

    latest_lower = latest_text.lower()
    full_lower = full_text.lower()

    new_shape_keywords = [
        "new shape",
        "add shape",
        "create shape",
        "custom shape",
        "shape request"
    ]

    if any(keyword in full_lower for keyword in new_shape_keywords):
        data["intent_hint"] = "new_shape"

    # Category detection
    for category in ["beam", "slab", "column", "footing", "raft"]:
        if category in full_lower:
            data["category"] = category
            break

    if not data.get("category"):
        data["category"] = "beam"

    # Shape name patterns
    shape_patterns = [
        r"name of shape is\s+([A-Za-z0-9 _-]+)",
        r"shape name is\s+([A-Za-z0-9 _-]+)",
        r"create\s+([A-Za-z0-9 _-]+)\s+shape",
        r"add\s+([A-Za-z0-9 _-]+)\s+shape",
        r"new\s+([A-Za-z0-9 _-]+)\s+shape",
        r"([A-Za-z0-9 _-]+)\s+shape"
    ]

    for pattern in shape_patterns:
        match = re.search(pattern, latest_text, re.IGNORECASE)
        if match:
            possible_shape_name = match.group(1).strip()

            stop_words = [
                "new",
                "a new",
                "the",
                "this",
                "which",
                "what"
            ]

            if possible_shape_name.lower() not in stop_words:
                data["shape_name"] = possible_shape_name.title()
                break

    # Description
    if not data.get("description"):
        description_patterns = [
            r"description is\s+(.+)",
            r"shape is for\s+(.+)",
            r"for\s+customized\s+(.+)",
            r"for\s+customised\s+(.+)"
        ]

        for pattern in description_patterns:
            match = re.search(pattern, latest_text, re.IGNORECASE)
            if match:
                data["description"] = match.group(1).strip()
                break

    # Reason
    if not data.get("reason"):
        reason_patterns = [
            r"reason is\s+(.+)",
            r"because\s+(.+)",
            r"required for\s+(.+)",
            r"needed for\s+(.+)",
            r"allow me to\s+(.+)"
        ]

        for pattern in reason_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                data["reason"] = match.group(1).strip()
                break

    # Output formula patterns:
    # "L1 = BX + LD"
    # "output L1 with formula BX + LD"
    outputs = data.get("outputs") or []

    output_patterns = [
        r"\b(L[0-9]+)\s*=\s*([^.,\n]+)",
        r"output\s+(L[0-9]+)\s+with\s+formula\s+([^.,\n]+)",
        r"(L[0-9]+)\s+formula\s+is\s+([^.,\n]+)"
    ]

    existing_output_names = {
        output.get("output_name", "").upper()
        for output in outputs
    }

    for pattern in output_patterns:
        matches = re.findall(pattern, latest_text, re.IGNORECASE)

        for output_name, formula in matches:
            output_name = output_name.upper().strip()
            formula = formula.strip()

            if output_name not in existing_output_names:
                outputs.append({
                    "output_name": output_name,
                    "formula": formula,
                    "unit": "m"
                })
                existing_output_names.add(output_name)

    data["outputs"] = outputs

    return data


def build_database_context(user_email: str):
    projects = find_user_projects(user_email)
    shapes = list_active_shapes("beam")

    project_names = [
        project.get("project_name")
        for project in projects
        if project.get("project_name")
    ]

    shape_info = []

    for shape in shapes:
        output_names = [
            output.get("output_name")
            for output in shape.get("outputs", [])
            if output.get("output_name")
        ]

        shape_info.append({
            "shape_name": shape.get("shape_name"),
            "category": shape.get("category"),
            "outputs": output_names
        })

    return {
        "user_projects": project_names,
        "available_shapes": shape_info,
        "abbreviations": ABBREVIATION_DICTIONARY
    }


def node_build_context(state: NeevAgentState):
    context = build_database_context(state["user_email"])
    return {
        "context": context
    }


def node_extract_with_llm(state: NeevAgentState):
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "system",
            "content": json.dumps({
                "database_context": state.get("context", {}),
                "current_structured_data": state.get("current_structured_data", {})
            })
        }
    ]

    messages.extend(state.get("conversation_messages", []))

    try:
        llm_text = call_llm(messages)
        parsed_response = extract_json_from_text(llm_text)

        parsed_intent = parsed_response.get("intent", "unknown")
        new_data = parsed_response.get("structured_data", {})

        merged_data = merge_structured_data(
            state.get("current_structured_data", {}),
            new_data
        )

        fallback_data = fallback_extract_from_user_text(
            current_data=merged_data,
            conversation_messages=state.get("conversation_messages", [])
        )

        improved_data = improve_extraction_with_context(
            data=fallback_data,
            context=state.get("context", {}),
            conversation_messages=state.get("conversation_messages", [])
        )

        final_intent = determine_intent(
            parsed_intent=parsed_intent,
            merged_data=improved_data,
            conversation_messages=state.get("conversation_messages", [])
        )

        return {
            "intent": final_intent,
            "response_to_user": parsed_response.get(
                "response_to_user",
                "Hi, I’m Neev. How can I help you today?"
            ),
            "missing_fields": parsed_response.get("missing_fields", []),
            "ready_to_submit": False,
            "structured_data": improved_data,
            "extraction_error": None
        }


    except Exception as e:

        fallback_data = fallback_extract_from_user_text(

            current_data=state.get("current_structured_data", {}),

            conversation_messages=state.get("conversation_messages", [])

        )

        final_intent = determine_intent(

            parsed_intent=fallback_data.get("intent_hint", "unknown"),

            merged_data=fallback_data,

            conversation_messages=state.get("conversation_messages", [])

        )

        return {

            "intent": final_intent,

            "response_to_user": (

                "Please share the remaining details so I can prepare the request."

            ),

            "missing_fields": [],

            "ready_to_submit": False,

            "structured_data": fallback_data,

            "extraction_error": None

        }


def node_validate_formula_update(state: NeevAgentState):
    validation_result = validate_formula_update_request(
        user_email=state["user_email"],
        data=state.get("structured_data", {})
    )

    return {
        "validation_result": validation_result
    }


def node_validate_new_shape(state: NeevAgentState):
    validation_result = validate_new_shape_request(
        user_email=state["user_email"],
        data=state.get("structured_data", {})
    )

    return {
        "validation_result": validation_result
    }


def route_after_validation(state: NeevAgentState):
    validation_result = state.get("validation_result", {})

    if validation_result.get("is_valid"):
        return "ready_response"

    return "validation_response"


def route_after_extraction(state: NeevAgentState):
    if state.get("extraction_error"):
        return "end"

    if state.get("intent") == "formula_update":
        return "validate_formula_update"

    if state.get("intent") == "new_shape":
        return "validate_new_shape"

    return "end"


def node_ready_response(state: NeevAgentState):
    validation_result = state.get("validation_result", {})
    resolved_data = validation_result.get("resolved_data", state.get("structured_data", {}))

    if state.get("intent") == "new_shape":
        return {
            "intent": "new_shape",
            "response_to_user": (
                "Great, I have prepared the new shape request. "
                "Please review it, upload the shape image, and submit."
            ),
            "missing_fields": [],
            "ready_to_submit": True,
            "structured_data": resolved_data
        }

    return {
        "intent": "formula_update",
        "response_to_user": (
            "Great, I have prepared the formula update request. "
            "Please review it before submitting."
        ),
        "missing_fields": [],
        "ready_to_submit": True,
        "structured_data": resolved_data
    }

def node_validation_response(state: NeevAgentState):
    validation_result = state.get("validation_result", {})

    feedback = {
        "missing_fields": validation_result.get("missing_fields", []),
        "error": validation_result.get("error"),
        "structured_data": state.get("structured_data", {})
    }

    messages = [
        {
            "role": "system",
            "content": """
            You are Neev, BuniyadByte's AI assistant.
            
            Write a short, natural response to the user.
            Do not mention JSON.
            Do not mention internal validation.
            Do not expose technical field names unless needed.
            
            If project_name is missing, ask for the project name.
            If shape_name is missing, ask which shape.
            If output_name is missing, ask which output such as L1, L2, or L3.
            If requested_formula is missing, ask for the new formula.
            If reason is missing, ask why the change is needed.
            If the error says unknown abbreviation, ask the user to correct only those abbreviation(s).
            If description is missing, ask for a short shape description.
            If outputs is missing, ask for output names and formulas such as L1 = BX + LD.
            For new shape requests, do not ask for image upload in chat.
            
            Keep the message compact and friendly.

            Return only valid JSON:
            {
              "response_to_user": "your message"
            }
            """
        },
        {
            "role": "system",
            "content": json.dumps(feedback)
        }
    ]

    messages.extend(state.get("conversation_messages", [])[-4:])

    try:
        llm_text = call_llm(messages)
        parsed = extract_json_from_text(llm_text)
        response_to_user = parsed.get(
            "response_to_user",
            "Please share the missing details so I can prepare the request."
        )
    except Exception:
        response_to_user = "Please share the missing details so I can prepare the request."

    return {
        "response_to_user": response_to_user,
        "missing_fields": validation_result.get("missing_fields", []),
        "ready_to_submit": False,
        "structured_data": state.get("structured_data", {})
    }


def build_neev_graph():
    graph = StateGraph(NeevAgentState)

    graph.add_node("build_context", node_build_context)
    graph.add_node("extract_with_llm", node_extract_with_llm)
    graph.add_node("validate_formula_update", node_validate_formula_update)
    graph.add_node("ready_response", node_ready_response)
    graph.add_node("validate_new_shape", node_validate_new_shape)
    graph.add_node("validation_response", node_validation_response)

    graph.add_edge(START, "build_context")
    graph.add_edge("build_context", "extract_with_llm")

    graph.add_conditional_edges(
        "extract_with_llm",
        route_after_extraction,
        {
            "validate_formula_update": "validate_formula_update",
            "validate_new_shape": "validate_new_shape",
            "end": END
        }
    )

    graph.add_conditional_edges(
        "validate_formula_update",
        route_after_validation,
        {
            "ready_response": "ready_response",
            "validation_response": "validation_response"
        }
    )

    graph.add_conditional_edges(
        "validate_new_shape",
        route_after_validation,
        {
            "ready_response": "ready_response",
            "validation_response": "validation_response"
        }
    )

    graph.add_edge("ready_response", END)
    graph.add_edge("validation_response", END)

    return graph.compile()


neev_graph = build_neev_graph()


def run_formula_update_agent(
    user_email: str,
    conversation_messages: list,
    current_structured_data: dict
):
    initial_state = {
        "user_email": user_email,
        "conversation_messages": conversation_messages,
        "current_structured_data": current_structured_data,

        "context": {},
        "intent": "unknown",
        "response_to_user": "",
        "missing_fields": [],
        "ready_to_submit": False,
        "structured_data": current_structured_data,
        "validation_result": {},
        "extraction_error": None
    }

    result = neev_graph.invoke(initial_state)

    return {
        "intent": result.get("intent", "unknown"),
        "response_to_user": result.get(
            "response_to_user",
            "Hi, I’m Neev. How can I help you today?"
        ),
        "missing_fields": result.get("missing_fields", []),
        "ready_to_submit": result.get("ready_to_submit", False),
        "structured_data": result.get("structured_data", {})
    }