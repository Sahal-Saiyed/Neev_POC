from bson.objectid import ObjectId

from db import (
    users_collection,
    projects_collection,
    autocad_imports_collection,
    beams_collection,
    ai_requests_collection
)


def list_users(search_text: str = "", role_filter: str = "user"):
    query = {}

    if role_filter and role_filter != "All":
        query["role"] = role_filter.lower()

    if search_text:
        query["$or"] = [
            {"name": {"$regex": search_text, "$options": "i"}},
            {"email": {"$regex": search_text, "$options": "i"}},
            {"role": {"$regex": search_text, "$options": "i"}}
        ]

    return list(users_collection.find(query).sort("created_at", -1))


def get_user_by_id(user_id: str):
    if not user_id:
        return None

    try:
        return users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


def list_projects_by_user_email(user_email: str):
    return list(
        projects_collection.find({"created_by": user_email})
        .sort("created_at", -1)
    )


def count_projects_by_user_email(user_email: str):
    return projects_collection.count_documents({"created_by": user_email})


def count_autocad_imports_by_user_email(user_email: str):
    return autocad_imports_collection.count_documents({
        "imported_by": user_email
    })


def count_beams_by_user_email(user_email: str):
    return beams_collection.count_documents({
        "created_by": user_email
    })


def count_filled_beams_by_user_email(user_email: str):
    return beams_collection.count_documents({
        "created_by": user_email,
        "status": "Filled"
    })


def count_ai_requests_by_user_email(user_email: str):
    return ai_requests_collection.count_documents({
        "requested_by": user_email
    })