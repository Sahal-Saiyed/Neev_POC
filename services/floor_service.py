from datetime import datetime
from bson.objectid import ObjectId

from db import floors_collection


def create_floor(
    project_id: str,
    block_id: str,
    project_code: str,
    block_name: str,
    floor_name: str,
    floor_description: str,
    created_by: str,
    created_by_name: str
):
    floor_data = {
        "project_id": project_id,
        "block_id": block_id,
        "project_code": project_code,
        "block_name": block_name,
        "floor_name": floor_name,
        "floor_description": floor_description,
        "created_by": created_by,
        "created_by_name": created_by_name,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "status": "active"
    }

    result = floors_collection.insert_one(floor_data)
    return str(result.inserted_id)


def list_floors(project_id: str, block_id: str, search_text: str = ""):
    query = {
        "project_id": project_id,
        "block_id": block_id
    }

    if search_text:
        query["floor_name"] = {
            "$regex": search_text,
            "$options": "i"
        }

    return list(floors_collection.find(query).sort("created_at", -1))


def list_floors_by_block(block_id: str):
    return list(
        floors_collection.find({"block_id": block_id})
        .sort("created_at", -1)
    )


def get_floor_by_id(floor_id: str):
    if not floor_id:
        return None

    try:
        return floors_collection.find_one({"_id": ObjectId(floor_id)})
    except Exception:
        return None


def count_floors_by_block(block_id: str):
    return floors_collection.count_documents({"block_id": block_id})