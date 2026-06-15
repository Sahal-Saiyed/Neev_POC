from datetime import datetime
from bson.objectid import ObjectId

from db import ai_requests_collection


def create_ai_request_document(request_data: dict):
    request_data["created_at"] = datetime.now()
    request_data["updated_at"] = datetime.now()

    result = ai_requests_collection.insert_one(request_data)

    request_id = str(result.inserted_id)
    request_code = f"AIR-{request_id[-6:].upper()}"

    ai_requests_collection.update_one(
        {"_id": result.inserted_id},
        {"$set": {"request_code": request_code}}
    )

    return request_id


def list_user_ai_requests(user_email: str, status_filter: str = "All", search_text: str = ""):
    query = {
        "requested_by": user_email
    }

    if status_filter != "All":
        query["status"] = status_filter.lower()

    if search_text:
        query["$or"] = [
            {"request_code": {"$regex": search_text, "$options": "i"}},
            {"project_name": {"$regex": search_text, "$options": "i"}},
            {"shape_name": {"$regex": search_text, "$options": "i"}},
            {"output_name": {"$regex": search_text, "$options": "i"}}
        ]

    return list(ai_requests_collection.find(query).sort("created_at", -1))


def list_admin_ai_requests(status_filter: str = "All", request_type_filter: str = "All", search_text: str = ""):
    query = {}

    if status_filter != "All":
        query["status"] = status_filter.lower()

    if request_type_filter != "All":
        query["request_type"] = request_type_filter

    if search_text:
        query["$or"] = [
            {"request_code": {"$regex": search_text, "$options": "i"}},
            {"project_name": {"$regex": search_text, "$options": "i"}},
            {"shape_name": {"$regex": search_text, "$options": "i"}},
            {"output_name": {"$regex": search_text, "$options": "i"}},
            {"requested_by": {"$regex": search_text, "$options": "i"}}
        ]

    return list(ai_requests_collection.find(query).sort("created_at", -1))


def get_ai_request_by_id(request_id: str):
    if not request_id:
        return None

    try:
        return ai_requests_collection.find_one({"_id": ObjectId(request_id)})
    except Exception:
        return None


def mark_ai_request_applied(
    request_id,
    admin_email: str,
    admin_comment: str = "",
    custom_shape_library_id: str = None
):
    return ai_requests_collection.update_one(
        {"_id": ObjectId(str(request_id))},
        {"$set": {
            "status": "applied",
            "scope": "project",
            "custom_shape_library_id": custom_shape_library_id,
            "admin_comment": admin_comment,
            "applied_by": admin_email,
            "applied_at": datetime.now(),
            "updated_at": datetime.now()
        }}
    )


def reject_ai_request(request_id, admin_email: str, admin_comment: str = ""):
    return ai_requests_collection.update_one(
        {"_id": ObjectId(str(request_id))},
        {"$set": {
            "status": "rejected",
            "admin_comment": admin_comment,
            "rejected_by": admin_email,
            "rejected_at": datetime.now(),
            "updated_at": datetime.now()
        }}
    )


def count_ai_requests(query=None):
    return ai_requests_collection.count_documents(query or {})


def create_new_shape_request(
    requested_by: str,
    requested_by_name: str,
    project_id: str,
    project_name: str,
    category: str,
    shape_name: str,
    description: str,
    outputs: list,
    reason: str,
    image_path: str = None,
    image_file_id: str = None,
    image_filename: str = None,
    image_mime_type: str = None,
    image_storage: str = None
):
    request_data = {
        "request_type": "new_shape",
        "requested_by": requested_by,
        "requested_by_name": requested_by_name,

        "project_id": project_id,
        "project_name": project_name,

        "category": category,
        "shape_name": shape_name,
        "reason": reason,

        # Old local-path support
        "new_shape_image_path": image_path,

        # New MongoDB GridFS support
        "new_shape_image_file_id": image_file_id,
        "new_shape_image_filename": image_filename,
        "new_shape_image_mime_type": image_mime_type,
        "new_shape_image_storage": image_storage,

        "new_shape_payload": {
            "shape_name": shape_name,
            "description": description,

            # Old local-path support
            "image_path": image_path,

            # New MongoDB GridFS support
            "image_file_id": image_file_id,
            "image_filename": image_filename,
            "image_mime_type": image_mime_type,
            "image_storage": image_storage,

            "outputs": outputs
        },
        "status": "pending"
    }

    return create_ai_request_document(request_data)

def mark_ai_request_applied_new_shape(
    request_id,
    admin_email: str,
    admin_comment: str = "",
    custom_shape_library_id: str = None
):
    return ai_requests_collection.update_one(
        {"_id": ObjectId(str(request_id))},
        {"$set": {
            "status": "applied",
            "scope": "project",
            "custom_shape_library_id": custom_shape_library_id,
            "admin_comment": admin_comment,
            "applied_by": admin_email,
            "applied_at": datetime.now(),
            "updated_at": datetime.now()
        }}
    )