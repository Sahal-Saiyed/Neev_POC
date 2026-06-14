from datetime import datetime
from bson.objectid import ObjectId

from db import autocad_imports_collection


def create_autocad_import(
    project_id: str,
    project_code: str,
    import_name: str,
    block_id: str,
    block_name: str,
    floor_id: str,
    floor_name: str,
    drawing_number: str,
    structure_name: str,
    imported_by: str,
    imported_by_name: str
):
    import_data = {
        "project_id": project_id,
        "project_code": project_code,
        "name": import_name,
        "block_id": block_id,
        "block_name": block_name,
        "floor_id": floor_id,
        "floor_name": floor_name,
        "drawing_number": drawing_number,
        "structure_name": structure_name,
        "imported_by": imported_by,
        "imported_by_name": imported_by_name,
        "imported_at": datetime.now(),
        "updated_at": datetime.now(),
        "status": "Pending"
    }

    result = autocad_imports_collection.insert_one(import_data)
    return str(result.inserted_id)


def list_autocad_imports(project_id: str, search_text: str = "", status_filter: str = "All"):
    query = {
        "project_id": project_id
    }

    if search_text:
        query["name"] = {
            "$regex": search_text,
            "$options": "i"
        }

    if status_filter != "All":
        query["status"] = status_filter

    return list(autocad_imports_collection.find(query).sort("imported_at", -1))


def list_autocad_imports_by_project(project_id: str):
    return list(
        autocad_imports_collection.find({"project_id": project_id})
        .sort("imported_at", -1)
    )


def get_autocad_import_by_id(autocad_import_id: str):
    if not autocad_import_id:
        return None

    try:
        return autocad_imports_collection.find_one(
            {"_id": ObjectId(autocad_import_id)}
        )
    except Exception:
        return None


def count_autocad_imports_by_project(project_id: str):
    return autocad_imports_collection.count_documents({"project_id": project_id})