import os
from datetime import datetime
from bson.objectid import ObjectId
from db import (
    shape_library_collection,
    custom_shape_library_collection,
    ai_requests_collection
)
from shape_resolver import (
    get_available_shapes_for_project,
    resolve_shape_for_project,
    upsert_project_formula_override
)


def list_global_shapes(category: str = None, active_only: bool = False):
    query = {}

    if category:
        query["category"] = category

    if active_only:
        query["is_active"] = True

    return list(shape_library_collection.find(query).sort("shape_name", 1))


def get_global_shape_by_id(shape_id: str):
    if not shape_id:
        return None

    try:
        return shape_library_collection.find_one({"_id": ObjectId(shape_id)})
    except Exception:
        return None


def create_global_shape(shape_data: dict):
    shape_data["created_at"] = datetime.now()
    shape_data["updated_at"] = datetime.now()

    result = shape_library_collection.insert_one(shape_data)
    return str(result.inserted_id)


def update_global_shape(shape_id: str, update_data: dict):
    update_data["updated_at"] = datetime.now()

    return shape_library_collection.update_one(
        {"_id": ObjectId(shape_id)},
        {"$set": update_data}
    )


def deactivate_global_shape(shape_id: str):
    return update_global_shape(shape_id, {"is_active": False})


def reactivate_global_shape(shape_id: str):
    return update_global_shape(shape_id, {"is_active": True})


def list_available_shapes_for_project(project_id: str, category: str = "beam"):
    return get_available_shapes_for_project(
        project_id=project_id,
        category=category
    )


def resolve_project_shape(project_id: str, selected_shape_key: str = None, shape_id: str = None):
    return resolve_shape_for_project(
        project_id=project_id,
        selected_shape_key=selected_shape_key,
        shape_id=shape_id
    )


def create_project_custom_shape(
    project_id: str,
    project_name: str,
    category: str,
    shape_name: str,
    description: str,
    image_path: str,
    outputs: list,
    created_by: str,
    ai_request_id: str = None,
    image_file_id: str = None,
    image_filename: str = None,
    image_mime_type: str = None,
    image_storage: str = None
):
    custom_shape = {
        "project_id": project_id,
        "project_name": project_name,
        "type": "custom_shape",
        "category": category,
        "shape_name": shape_name,
        "description": description,

        "image_path": image_path,
        "image_file_id": image_file_id,
        "image_filename": image_filename,
        "image_mime_type": image_mime_type,
        "image_storage": image_storage,

        "outputs": outputs,
        "is_active": True,
        "created_by": created_by,
        "updated_by": created_by,
        "ai_request_id": ai_request_id,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    result = custom_shape_library_collection.insert_one(custom_shape)
    return str(result.inserted_id)


def apply_project_formula_override(
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
    return upsert_project_formula_override(
        project_id=project_id,
        project_name=project_name,
        category=category,
        base_shape_id=base_shape_id,
        base_shape_name=base_shape_name,
        output_name=output_name,
        formula=formula,
        unit=unit,
        ai_request_id=ai_request_id,
        admin_email=admin_email
    )


def save_uploaded_shape_image(uploaded_file, shape_name: str, category: str = "beam"):
    if uploaded_file is None:
        return None

    safe_shape_name = shape_name.lower().replace(" ", "_")
    file_extension = uploaded_file.name.split(".")[-1]

    folder_path = os.path.join("assets", "shapes", category)
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(
        folder_path,
        f"{safe_shape_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
    )

    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return file_path


def list_shapes(category: str = "beam", search_text: str = "", status_filter: str = "All"):
    query = {}

    if category:
        query["category"] = category

    if status_filter == "Active":
        query["is_active"] = True
    elif status_filter == "Inactive":
        query["is_active"] = False

    if search_text:
        query["shape_name"] = {
            "$regex": search_text,
            "$options": "i"
        }

    return list(shape_library_collection.find(query).sort("created_at", -1))


def get_shape_by_id(shape_id: str):
    return get_global_shape_by_id(shape_id)


def find_shape_by_name_and_category(shape_name: str, category: str):
    if not shape_name:
        return None

    return shape_library_collection.find_one({
        "shape_name": shape_name,
        "category": category
    })


def find_duplicate_shape(shape_id: str, shape_name: str, category: str):
    return shape_library_collection.find_one({
        "_id": {"$ne": ObjectId(shape_id)},
        "shape_name": shape_name,
        "category": category
    })


def create_shape(
    shape_name: str,
    category: str,
    description: str,
    image_path: str,
    outputs: list,
    created_by: str
):
    shape_data = {
        "shape_name": shape_name,
        "category": category,
        "description": description,
        "image_path": image_path,
        "outputs": outputs,
        "is_active": True,
        "created_by": created_by,
        "updated_by": created_by
    }

    return create_global_shape(shape_data)


def update_shape(
    shape_id: str,
    shape_name: str,
    description: str,
    image_path: str,
    outputs: list,
    is_active: bool,
    updated_by: str
):
    update_data = {
        "shape_name": shape_name,
        "description": description,
        "image_path": image_path,
        "outputs": outputs,
        "is_active": is_active,
        "updated_by": updated_by
    }

    return update_global_shape(shape_id, update_data)

def approve_new_shape_request_to_project(request: dict, admin_email: str):
    payload = request.get("new_shape_payload", {})

    project_id = request.get("project_id")
    project_name = request.get("project_name")
    category = request.get("category", "beam")

    shape_name = payload.get("shape_name") or request.get("shape_name")
    description = payload.get("description", "")
    image_path = payload.get("image_path") or request.get("new_shape_image_path")

    image_file_id = (
            payload.get("image_file_id")
            or request.get("new_shape_image_file_id")
            or request.get("image_file_id")
    )

    image_filename = (
            payload.get("image_filename")
            or request.get("new_shape_image_filename")
            or request.get("image_filename")
    )

    image_mime_type = (
            payload.get("image_mime_type")
            or request.get("new_shape_image_mime_type")
            or request.get("image_mime_type")
    )

    image_storage = (
            payload.get("image_storage")
            or request.get("new_shape_image_storage")
            or request.get("image_storage")
    )
    outputs = payload.get("outputs", [])

    if not project_id:
        raise ValueError("Request is missing project ID.")

    if not shape_name:
        raise ValueError("Request is missing shape name.")

    if not outputs:
        raise ValueError("Request is missing shape outputs.")

    return create_project_custom_shape(
        project_id=project_id,
        project_name=project_name,
        category=category,
        shape_name=shape_name,
        description=description,
        image_path=image_path,
        outputs=outputs,
        created_by=admin_email,
        ai_request_id=str(request["_id"]),
        image_file_id=image_file_id,
        image_filename=image_filename,
        image_mime_type=image_mime_type,
        image_storage=image_storage
    )


def get_customization_type_label(custom_type: str):
    labels = {
        "formula_override": "Custom Formula",
        "custom_shape": "Custom Shape"
    }

    return labels.get(custom_type, custom_type or "Customization")


def get_custom_item_outputs(custom_item: dict):
    if custom_item.get("type") == "formula_override":
        return custom_item.get("override_outputs", [])

    if custom_item.get("type") == "custom_shape":
        return custom_item.get("outputs", [])

    return []


def get_custom_item_shape_name(custom_item: dict):
    if custom_item.get("type") == "formula_override":
        return custom_item.get("base_shape_name", "N/A")

    if custom_item.get("type") == "custom_shape":
        return custom_item.get("shape_name", "N/A")

    return "N/A"


def get_custom_item_description(custom_item: dict):
    if custom_item.get("type") == "custom_shape":
        return custom_item.get("description", "")

    if custom_item.get("type") == "formula_override":
        return (
            f"Project-specific formula override for "
            f"{custom_item.get('base_shape_name', 'selected shape')}."
        )

    return ""


def _get_ai_request_for_custom_item(custom_item: dict):
    request_id = custom_item.get("ai_request_id")

    if not request_id and custom_item.get("type") == "formula_override":
        override_outputs = custom_item.get("override_outputs", [])

        for output in reversed(override_outputs):
            if output.get("ai_request_id"):
                request_id = output.get("ai_request_id")
                break

    if not request_id:
        return None

    try:
        return ai_requests_collection.find_one({"_id": ObjectId(str(request_id))})
    except Exception:
        return None


def _fallback_request_code(request_id):
    if not request_id:
        return "N/A"

    return f"AIR-{str(request_id)[-6:].upper()}"


def enrich_custom_item(custom_item: dict):
    enriched_item = dict(custom_item)

    request = _get_ai_request_for_custom_item(custom_item)

    request_id = None

    if custom_item.get("ai_request_id"):
        request_id = custom_item.get("ai_request_id")

    if not request_id and custom_item.get("type") == "formula_override":
        for output in reversed(custom_item.get("override_outputs", [])):
            if output.get("ai_request_id"):
                request_id = output.get("ai_request_id")
                break

    if request:
        enriched_item["request_code"] = request.get(
            "request_code",
            _fallback_request_code(request.get("_id"))
        )
        enriched_item["requested_by_name"] = request.get("requested_by_name", "N/A")
        enriched_item["requested_by"] = request.get("requested_by", "N/A")
        enriched_item["request_reason"] = request.get("reason", "N/A")
    else:
        enriched_item["request_code"] = _fallback_request_code(request_id)
        enriched_item["requested_by_name"] = "N/A"
        enriched_item["requested_by"] = "N/A"
        enriched_item["request_reason"] = "N/A"

    enriched_item["customization_type_label"] = get_customization_type_label(
        custom_item.get("type")
    )
    enriched_item["display_shape_name"] = get_custom_item_shape_name(custom_item)
    enriched_item["display_description"] = get_custom_item_description(custom_item)
    enriched_item["display_outputs"] = get_custom_item_outputs(custom_item)

    image_path = custom_item.get("image_path")
    image_file_id = custom_item.get("image_file_id")
    image_filename = custom_item.get("image_filename")
    image_mime_type = custom_item.get("image_mime_type")
    image_storage = custom_item.get("image_storage")

    if custom_item.get("type") == "formula_override":
        base_shape_id = custom_item.get("base_shape_id")

        if base_shape_id:
            try:
                base_shape = shape_library_collection.find_one({
                    "_id": ObjectId(str(base_shape_id))
                })

                if base_shape:
                    image_path = base_shape.get("image_path")
                    image_file_id = base_shape.get("image_file_id")
                    image_filename = base_shape.get("image_filename")
                    image_mime_type = base_shape.get("image_mime_type")
                    image_storage = base_shape.get("image_storage")
            except Exception:
                image_path = None
                image_file_id = None
                image_filename = None
                image_mime_type = None
                image_storage = None

    enriched_item["display_image_path"] = image_path
    enriched_item["display_image_file_id"] = image_file_id
    enriched_item["display_image_filename"] = image_filename
    enriched_item["display_image_mime_type"] = image_mime_type
    enriched_item["display_image_storage"] = image_storage

    return enriched_item


def list_custom_shape_library_items(
    category: str = "beam",
    search_text: str = "",
    status_filter: str = "All"
):
    query = {}

    if category:
        query["category"] = category

    if status_filter == "Active":
        query["is_active"] = True
    elif status_filter == "Inactive":
        query["is_active"] = False

    if search_text:
        query["$or"] = [
            {"project_name": {"$regex": search_text, "$options": "i"}},
            {"shape_name": {"$regex": search_text, "$options": "i"}},
            {"base_shape_name": {"$regex": search_text, "$options": "i"}}
        ]

    items = list(
        custom_shape_library_collection.find(query)
        .sort("updated_at", -1)
    )

    return [enrich_custom_item(item) for item in items]


def get_custom_shape_library_item_by_id(custom_item_id: str):
    if not custom_item_id:
        return None

    try:
        item = custom_shape_library_collection.find_one({
            "_id": ObjectId(custom_item_id)
        })

        if not item:
            return None

        return enrich_custom_item(item)

    except Exception:
        return None


def deactivate_custom_shape_library_item(custom_item_id: str, admin_email: str):
    return custom_shape_library_collection.update_one(
        {"_id": ObjectId(str(custom_item_id))},
        {
            "$set": {
                "is_active": False,
                "updated_by": admin_email,
                "updated_at": datetime.now()
            }
        }
    )


def reactivate_custom_shape_library_item(custom_item_id: str, admin_email: str):
    return custom_shape_library_collection.update_one(
        {"_id": ObjectId(str(custom_item_id))},
        {
            "$set": {
                "is_active": True,
                "updated_by": admin_email,
                "updated_at": datetime.now()
            }
        }
    )

def update_custom_formula_override(
    custom_item_id: str,
    override_outputs: list,
    is_active: bool,
    admin_email: str
):
    cleaned_outputs = []

    existing_item = custom_shape_library_collection.find_one({
        "_id": ObjectId(str(custom_item_id)),
        "type": "formula_override"
    })

    if not existing_item:
        raise ValueError("Custom formula override not found.")

    old_outputs_by_name = {}

    for old_output in existing_item.get("override_outputs", []):
        old_outputs_by_name[old_output.get("output_name", "").lower()] = old_output

    for output in override_outputs:
        output_name = output.get("output_name", "").strip()
        formula = output.get("formula", "").strip()
        unit = output.get("unit", "m").strip() or "m"

        if not output_name or not formula:
            raise ValueError("Each output must have output name and formula.")

        old_output = old_outputs_by_name.get(output_name.lower(), {})

        cleaned_outputs.append({
            "output_name": output_name,
            "formula": formula,
            "unit": unit,
            "source": "manual_admin_edit",
            "ai_request_id": old_output.get("ai_request_id"),
            "updated_by": admin_email,
            "updated_at": datetime.now()
        })

    return custom_shape_library_collection.update_one(
        {"_id": ObjectId(str(custom_item_id))},
        {
            "$set": {
                "override_outputs": cleaned_outputs,
                "is_active": is_active,
                "updated_by": admin_email,
                "updated_at": datetime.now()
            }
        }
    )


def find_duplicate_project_custom_shape(
    custom_item_id: str,
    project_id: str,
    shape_name: str,
    category: str
):
    return custom_shape_library_collection.find_one({
        "_id": {"$ne": ObjectId(str(custom_item_id))},
        "project_id": project_id,
        "category": category,
        "type": "custom_shape",
        "shape_name": shape_name
    })


def update_project_custom_shape(
    custom_item_id: str,
    shape_name: str,
    description: str,
    image_path: str,
    outputs: list,
    is_active: bool,
    admin_email: str
):
    cleaned_outputs = []

    for output in outputs:
        output_name = output.get("output_name", "").strip()
        formula = output.get("formula", "").strip()
        unit = output.get("unit", "m").strip() or "m"

        if not output_name or not formula:
            raise ValueError("Each output must have output name and formula.")

        cleaned_outputs.append({
            "output_name": output_name,
            "formula": formula,
            "unit": unit
        })

    return custom_shape_library_collection.update_one(
        {"_id": ObjectId(str(custom_item_id))},
        {
            "$set": {
                "shape_name": shape_name,
                "description": description,
                "image_path": image_path,
                "outputs": cleaned_outputs,
                "is_active": is_active,
                "updated_by": admin_email,
                "updated_at": datetime.now()
            }
        }
    )