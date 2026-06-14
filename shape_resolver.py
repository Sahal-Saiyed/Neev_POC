from cProfile import label
from copy import deepcopy
from datetime import datetime
from bson.objectid import ObjectId

from db import (
    shape_library_collection,
    custom_shape_library_collection
)

def get_available_shapes_for_project(project_id: str, category: str = "beam"):
    """
    Returns
    - all global active shapes
    -project-specific custom shapes
    """

    available_shapes = []

    global_shapes = list(
        shape_library_collection.find({
            "category": category,
            "is_active": True
        }).sort("shape_name",1)
    )

    for shape in global_shapes:
        shape_id = str(shape["_id"])

        override_exists = custom_shape_library_collection.find_one({
            "project_id": project_id,
            "type": "formula_override",
            "base_shape_id": shape_id,
            "is_active": True
        })

        label = shape.get("shape_name","Untitled shape")

        if override_exists:
            label = f"{label} (project formula available)"

        available_shapes.append({
            "option_label": label,
            "option_key": f"global:{shape_id}",
            "shape_id": shape_id,
            "shape_name": shape.get("shape_name"),
            "shape_source": "global"
        })

    custom_shapes = list(
        custom_shape_library_collection.find({
            "project_id": project_id,
            "type": "custom_shape",
            "category": category,
            "is_active": True
        }).sort("shape_name",1)
    )

    for shape in custom_shapes:
        custom_shape_id = str(shape["_id"])

        available_shapes.append({
            "option_label": f"{shape.get('shape_name', 'Custom Shape')} (Custom shape)",
            "option_key": f"custom:{custom_shape_id}",
            "shape_id": custom_shape_id,
            "shape_name": shape.get("shape_name"),
            "shape_source": "custom"
        })

    return available_shapes

def resolve_shape_for_project(project_id: str, selected_shape_key: str = None, shape_id: str = None):
    """
    Returns the effective shape for calculation.

    For global shapes:
    - load global shape
    - check project-specific overrides
    - replace only overridden formulas

    For custom shapes:
    - return project-specific custom shape directly
    """

    if selected_shape_key:
        source, selected_id = selected_shape_key.split(":",1)
    else:
        source = "global"
        selected_id = shape_id

    if source == "custom":
        custom_shape = custom_shape_library_collection.find_one({
            "_id": ObjectId(selected_id),
            "project_id": project_id,
            "type":"custom_shape",
            "is_active": True
        })

        if not custom_shape:
            return None

        resolved_shape = deepcopy(custom_shape)

        resolved_shape["shape_source"] = "custom"
        resolved_shape["shape_id"] = str(custom_shape["_id"])
        resolved_shape["custom_shape_id"] = str(custom_shape["_id"])
        resolved_shape["base_shape_id"] = None

        for output in resolved_shape.get("outputs",[]):
            output["formula_source"] = "project_custom_shape"

        return resolved_shape

    global_shape = shape_library_collection.find_one({
        "_id": ObjectId(selected_id)
    })

    if not global_shape:
        return None

    resolved_shape = deepcopy(global_shape)

    resolved_shape["shape_source"] = "global"
    resolved_shape["shape_id"] = str(global_shape["_id"])
    resolved_shape["base_shape_id"] = str(global_shape["_id"])
    resolved_shape["custom_shape_id"] = None

    override_doc = custom_shape_library_collection.find_one({
        "project_id": project_id,
        "type": "formula_override",
        "base_shape_id": str(global_shape["_id"]),
        "is_active": True
    })

    override_outputs = {}

    if override_doc:
        for output in override_doc.get("override_outputs", []):
            output_name = output.get("output_name", "").lower()
            override_outputs[output_name] = output

    merged_outputs = []

    for output in global_shape.get("outputs", []):
        merged_output = deepcopy(output)
        output_name = output.get("output_name", "").lower()

        if output_name in override_outputs:
            override = override_outputs[output_name]

            merged_output["formula"] = override.get("formula")
            merged_output["unit"] = override.get("unit", output.get("unit", "m"))
            merged_output["formula_source"] = "project_custom"
            merged_output["ai_request_id"] = override.get("ai_request_id")
        else:
            merged_output["formula_source"] = "global"

        merged_outputs.append(merged_output)

    resolved_shape["outputs"] = merged_outputs

    return resolved_shape


def upsert_project_formula_override(
        project_id: str,
        project_name: str,
        category: str,
        base_shape_id: str,
        base_shape_name: str,
        output_name: str,
        formula: str,
        unit: str,
        ai_request_id: str,
        admin_email: str
):
    """
    Creates or updates one project-specific formula override.
    Only the changed output formula is stored.
    """

    existing_doc = custom_shape_library_collection.find_one({
        "project_id": project_id,
        "type": "formula_override",
        "base_shape_id": base_shape_id,
        "is_active": True
    })

    new_override = {
        "output_name": output_name,
        "formula": formula,
        "unit": unit or "m",
        "source": "ai_request",
        "ai_request_id": ai_request_id,
        "updated_by": admin_email,
        "updated_at": datetime.now()
    }

    if existing_doc:
        override_outputs = existing_doc.get("override_outputs", [])
        found = False

        for output in override_outputs:
            if output.get("output_name", "").lower() == output_name.lower():
                output.update(new_override)
                found = True
                break

        if not found:
            override_outputs.append(new_override)

        custom_shape_library_collection.update_one(
            {"_id": existing_doc["_id"]},
            {
                "$set": {
                    "override_outputs": override_outputs,
                    "updated_by": admin_email,
                    "updated_at": datetime.now()
                }
            }
        )

        return str(existing_doc["_id"])

    document = {
        "project_id": project_id,
        "project_name": project_name,

        "type": "formula_override",

        "category": category,

        "base_shape_id": base_shape_id,
        "base_shape_name": base_shape_name,

        "override_outputs": [new_override],

        "is_active": True,

        "created_by": admin_email,
        "updated_by": admin_email,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    result = custom_shape_library_collection.insert_one(document)

    return str(result.inserted_id)
