from datetime import datetime
from bson.objectid import ObjectId

from db import beams_collection


def create_beam(
    project_id: str,
    autocad_import_id: str,
    block_id: str,
    block_name: str,
    floor_id: str,
    floor_name: str,
    beam_name: str,
    beam_description: str,
    created_by: str,
    created_by_name: str
):
    beam_data = {
        "project_id": project_id,
        "autocad_import_id": autocad_import_id,
        "block_id": block_id,
        "block_name": block_name,
        "floor_id": floor_id,
        "floor_name": floor_name,
        "beam_name": beam_name,
        "beam_description": beam_description,
        "shape_id": None,
        "shape_name": None,
        "selected_shape_key": None,
        "shape_source": None,
        "base_shape_id": None,
        "custom_shape_id": None,
        "inputs": {},
        "outputs": [],
        "status": "Unfilled",
        "created_by": created_by,
        "created_by_name": created_by_name,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    result = beams_collection.insert_one(beam_data)
    return str(result.inserted_id)


def list_beams(
    project_id: str,
    autocad_import_id: str,
    search_text: str = "",
    status_filter: str = "All"
):
    query = {
        "project_id": project_id,
        "autocad_import_id": autocad_import_id
    }

    if search_text:
        query["beam_name"] = {
            "$regex": search_text,
            "$options": "i"
        }

    if status_filter != "All":
        query["status"] = status_filter

    return list(beams_collection.find(query).sort("created_at", -1))


def get_beam_by_id(beam_id: str):
    if not beam_id:
        return None

    try:
        return beams_collection.find_one({"_id": ObjectId(beam_id)})
    except Exception:
        return None


def update_beam_calculation(beam_id: str, beam_update: dict):
    beam_update["updated_at"] = datetime.now()

    return beams_collection.update_one(
        {"_id": ObjectId(str(beam_id))},
        {"$set": beam_update}
    )


def count_beams_by_autocad_import(autocad_import_id: str):
    return beams_collection.count_documents({
        "autocad_import_id": autocad_import_id
    })