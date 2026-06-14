import os
from datetime import datetime
from bson.objectid import ObjectId

from db import shape_library_collection, custom_shape_library_collection
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
    ai_request_id: str = None
):
    custom_shape = {
        "project_id": project_id,
        "project_name": project_name,
        "type": "custom_shape",
        "category": category,
        "shape_name": shape_name,
        "description": description,
        "image_path": image_path,
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
        ai_request_id=str(request["_id"])
    )