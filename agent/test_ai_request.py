from agent.validators import validate_formula_update_request
from agent.request_service import create_ai_request
from agent.schemas import AIRequestCreate


def test_formula_update_request():
    user_email = "abc"
    user_name = "abc"

    raw_data = {
        "project_name": "ASP",
        "category": "beam",
        "shape_name": "BOTTOM BAR",
        "output_name": "L1",
        "requested_formula": "(LD + (12 * D)) - CX - CO",
        "reason": "Need updated bend allowance for this beam shape."
    }

    validation_result = validate_formula_update_request(
        user_email=user_email,
        data=raw_data
    )

    if not validation_result["is_valid"]:
        print("Validation failed")

        if validation_result["missing_fields"]:
            print("Missing fields:", validation_result["missing_fields"])

        if validation_result["error"]:
            print("Error:", validation_result["error"])

        return

    resolved_data = validation_result["resolved_data"]

    request = AIRequestCreate(
        request_type="formula_update",
        requested_by=user_email,
        requested_by_name=user_name,

        project_id=resolved_data.get("project_id"),
        project_name=resolved_data.get("project_name"),

        category=resolved_data.get("category"),

        shape_id=resolved_data.get("shape_id"),
        shape_name=resolved_data.get("shape_name"),

        output_name=resolved_data.get("output_name"),
        current_formula=resolved_data.get("current_formula"),
        requested_formula=resolved_data.get("requested_formula"),

        reason=resolved_data.get("reason"),
        ai_summary=(
            f"User requested formula update for "
            f"{resolved_data.get('shape_name')} - {resolved_data.get('output_name')}."
        ),
        ai_suggestion="Admin should verify the requested formula before applying it.",
        status="pending"
    )

    request_id = create_ai_request(request)

    print("AI request created successfully.")
    print("Request ID:", request_id)


if __name__ == "__main__":
    test_formula_update_request()