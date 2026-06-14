from bson.objectid import ObjectId
from db import(
    projects_collection,
    shape_library_collection
)

def find_user_projects(user_email: str):
    return list(
        projects_collection.find(
            {"created_by": user_email},
            {
                "project_name":1,
                "project_code":1,
                "created_by":1,
                "created_at":1
            }
        ).sort("created_at",-1)
    )

def find_project_by_name(user_email:str, project_name:str):
    return projects_collection.find_one(
        {
            "created_by": user_email,
            "project_name":{
                "$regex":f"^{project_name}$",
                "$options": "i"
            }
        }
    )


def find_shape_by_name(category:str, shape_name:str):
    return shape_library_collection.find_one({
            "category":category,
            "shape_name":{
                "$regex":f"^{shape_name}$",
                "$options":"i"
            },
            "is_active": True
    })

def get_shape_by_id(shape_id: str):
    try:
        return shape_library_collection.find_one({
            "_id": ObjectId(shape_id)
        })
    except Exception:
        return None

def get_current_formula(shape: dict, output_name: str):
    if not shape:
        return None

    outputs = shape.get("outputs", [])

    for output in outputs:
        if output.get("output_name", "").lower() == output_name.lower():
            return output.get("formula")

    return None

def get_shape_output_names(shape: dict):
    if not shape:
        return []

    return [
        output.get("output_name")
        for output in shape.get("outputs", [])
        if output.get("output_name")
    ]

def list_active_shapes(category: str = "beam"):
    return list(
        shape_library_collection.find(
            {
                "category": category,
                "is_active": True
            },
            {
                "shape_name": 1,
                "category": 1,
                "outputs": 1
            }
        ).sort("shape_name", 1)
    )