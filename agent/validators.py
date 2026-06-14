from agent.tools import (
    find_project_by_name,
    find_shape_by_name,
    get_current_formula,
    get_shape_output_names
)
from abbreviation_tool import (
    find_unknown_abbreviations_in_formula,
    get_valid_abbreviation_list
)
from shape_resolver import resolve_shape_for_project
from services.project_service import find_user_project_by_name
from abbreviation_tool import find_unknown_abbreviations_in_formula

def validate_formula_update_request(user_email: str, data: dict):
    missing_fields = []

    project_name = data.get("project_name")
    category = data.get("category", "beam")
    shape_name = data.get("shape_name")
    output_name = data.get("output_name")
    requested_formula = data.get("requested_formula")
    reason = data.get("reason")

    if not project_name:
        missing_fields.append("project_name")

    if not shape_name:
        missing_fields.append("shape_name")

    if not output_name:
        missing_fields.append("output_name")

    if not requested_formula:
        missing_fields.append("requested_formula")

    if not reason:
        missing_fields.append("reason")

    if missing_fields:
        return {
            "is_valid": False,
            "missing_fields": missing_fields,
            "error": None,
            "resolved_data": data
        }

    unknown_abbreviations = find_unknown_abbreviations_in_formula(requested_formula)

    if unknown_abbreviations:
        valid_abbreviations = ", ".join(get_valid_abbreviation_list())

        return {
            "is_valid": False,
            "missing_fields": [],
            "error": (
                f"The requested formula contains unknown abbreviation(s): "
                f"{', '.join(unknown_abbreviations)}. "
                f"Please correct them. Valid abbreviations are: {valid_abbreviations}."
            ),
            "resolved_data": data
        }
    
    # 1. Find project
    project = find_project_by_name(user_email, project_name)

    if not project:
        return {
            "is_valid": False,
            "missing_fields": [],
            "error": f"Project '{project_name}' was not found for this user.",
            "resolved_data": data
        }

    # 2. Find global/base shape
    shape = find_shape_by_name(category, shape_name)

    if not shape:
        return {
            "is_valid": False,
            "missing_fields": [],
            "error": f"Shape '{shape_name}' was not found in category '{category}'.",
            "resolved_data": data
        }

    # 3. Resolve shape for this specific project
    # This checks custom_shape_library first.
    # If project has custom formula, current_formula comes from custom override.
    # Otherwise, it comes from global shape_library.
    resolved_shape = resolve_shape_for_project(
        project_id=str(project["_id"]),
        shape_id=str(shape["_id"])
    )

    if not resolved_shape:
        return {
            "is_valid": False,
            "missing_fields": [],
            "error": "Could not resolve shape formula for this project.",
            "resolved_data": data
        }

    current_formula = get_current_formula(resolved_shape, output_name)

    if not current_formula:
        output_names = get_shape_output_names(resolved_shape)

        return {
            "is_valid": False,
            "missing_fields": [],
            "error": f"Output '{output_name}' was not found. Available outputs: {', '.join(output_names)}",
            "resolved_data": data
        }

    resolved_data = {
        **data,
        "project_id": str(project["_id"]),
        "project_name": project.get("project_name"),

        "shape_id": str(shape["_id"]),
        "shape_name": shape.get("shape_name"),

        "category": shape.get("category"),
        "output_name": output_name,
        "current_formula": current_formula
    }

    return {
        "is_valid": True,
        "missing_fields": [],
        "error": None,
        "resolved_data": resolved_data
    }

def validate_new_shape_request(user_email: str, data: dict):
    project_name = data.get("project_name")
    category = data.get("category") or "beam"
    shape_name = data.get("shape_name")
    description = data.get("description")
    outputs = data.get("outputs") or []
    reason = data.get("reason")

    missing_fields = []

    if not project_name:
        missing_fields.append("project_name")

    if not category:
        missing_fields.append("category")

    if not shape_name:
        missing_fields.append("shape_name")

    if not description:
        missing_fields.append("description")

    if not outputs:
        missing_fields.append("outputs")

    if not reason:
        missing_fields.append("reason")

    if missing_fields:
        return {
            "is_valid": False,
            "missing_fields": missing_fields,
            "error": None,
            "resolved_data": data
        }

    project = find_user_project_by_name(user_email, project_name)

    if not project:
        return {
            "is_valid": False,
            "missing_fields": [],
            "error": f"I could not find project '{project_name}' in your account. Please enter the correct project name.",
            "resolved_data": data
        }

    cleaned_outputs = []

    for output in outputs:
        output_name = output.get("output_name")
        formula = output.get("formula")
        unit = output.get("unit") or "m"

        if not output_name or not formula:
            return {
                "is_valid": False,
                "missing_fields": [],
                "error": "Each output must have an output name and formula. Please provide them clearly.",
                "resolved_data": data
            }

        unknown_abbreviations = find_unknown_abbreviations_in_formula(formula)

        if unknown_abbreviations:
            return {
                "is_valid": False,
                "missing_fields": [],
                "error": (
                    f"The formula for {output_name} contains unknown abbreviation(s): "
                    f"{', '.join(unknown_abbreviations)}. Please correct them."
                ),
                "resolved_data": data
            }

        cleaned_outputs.append({
            "output_name": output_name.strip().upper(),
            "formula": formula.strip(),
            "unit": unit
        })

    resolved_data = data.copy()
    resolved_data["project_id"] = str(project["_id"])
    resolved_data["project_name"] = project.get("project_name")
    resolved_data["category"] = category.lower()
    resolved_data["shape_name"] = shape_name.strip()
    resolved_data["description"] = description.strip()
    resolved_data["outputs"] = cleaned_outputs
    resolved_data["reason"] = reason.strip()

    return {
        "is_valid": True,
        "missing_fields": [],
        "error": None,
        "resolved_data": resolved_data
    }