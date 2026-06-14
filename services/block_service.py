from datetime import datetime
from bson.objectid import ObjectId

from db import blocks_collection


def create_block(
    project_id: str,
    project_code: str,
    block_name: str,
    block_description: str,
    created_by: str,
    created_by_name: str
):
    block_data = {
        "project_id": project_id,
        "project_code": project_code,
        "block_name": block_name,
        "block_description": block_description,
        "created_by": created_by,
        "created_by_name": created_by_name,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "status": "active"
    }

    result = blocks_collection.insert_one(block_data)
    return str(result.inserted_id)


def list_blocks(project_id: str, search_text: str = ""):
    query = {
        "project_id": project_id
    }

    if search_text:
        query["block_name"] = {
            "$regex": search_text,
            "$options": "i"
        }

    return list(blocks_collection.find(query).sort("created_at", -1))


def list_blocks_by_project(project_id: str):
    return list(
        blocks_collection.find({"project_id": project_id})
        .sort("created_at", -1)
    )


def get_block_by_id(block_id: str):
    if not block_id:
        return None

    try:
        return blocks_collection.find_one({"_id": ObjectId(block_id)})
    except Exception:
        return None


def count_blocks_by_project(project_id: str):
    return blocks_collection.count_documents({"project_id": project_id})