from datetime import datetime
from bson.objectid import ObjectId

from db import projects_collection


def generate_project_code():
    project_count = projects_collection.count_documents({})
    next_number = project_count + 1
    return f"PROJ{next_number:04d}"


def create_project(
    project_name: str,
    description: str,
    start_date,
    end_date,
    created_by: str,
    created_by_name: str
):
    project_data = {
        "project_code": generate_project_code(),
        "project_name": project_name,
        "description": description,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "created_by": created_by,
        "created_by_name": created_by_name,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "status": "active"
    }

    result = projects_collection.insert_one(project_data)
    return str(result.inserted_id)


def list_projects(user_email: str, role: str, search_text: str = ""):
    query = {}

    if role != "admin":
        query["created_by"] = user_email

    if search_text:
        query["project_name"] = {
            "$regex": search_text,
            "$options": "i"
        }

    return list(projects_collection.find(query).sort("created_at", -1))


def list_user_projects(user_email: str):
    return list(
        projects_collection.find({"created_by": user_email})
        .sort("created_at", -1)
    )


def get_project_by_id(project_id: str):
    if not project_id:
        return None

    try:
        return projects_collection.find_one({"_id": ObjectId(project_id)})
    except Exception:
        return None


def find_user_project_by_name(user_email: str, project_name: str):
    if not project_name:
        return None

    return projects_collection.find_one({
        "created_by": user_email,
        "project_name": {
            "$regex": f"^{project_name}$",
            "$options": "i"
        }
    })


def update_project(project_id: str, update_data: dict):
    update_data["updated_at"] = datetime.now()

    return projects_collection.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": update_data}
    )