from db import (
    users_collection,
    projects_collection,
    shape_library_collection,
    autocad_imports_collection,
    beams_collection,
    ai_requests_collection
)


def get_admin_dashboard_stats():
    return {
        "total_users": users_collection.count_documents({"role": "user"}),
        "total_projects": projects_collection.count_documents({}),
        "total_shapes": shape_library_collection.count_documents({"is_active": True}),
        "total_imports": autocad_imports_collection.count_documents({}),
        "total_beams": beams_collection.count_documents({}),
        "filled_beams": beams_collection.count_documents({"status": "Filled"}),
        "pending_ai_requests": ai_requests_collection.count_documents({
            "status": "pending"
        })
    }


def get_recent_projects(limit: int = 5):
    return list(
        projects_collection.find({})
        .sort("created_at", -1)
        .limit(limit)
    )


def get_recent_shapes(limit: int = 5):
    return list(
        shape_library_collection.find({})
        .sort("created_at", -1)
        .limit(limit)
    )


def get_user_dashboard_stats(user_email: str):
    return {
        "total_projects": projects_collection.count_documents({
            "created_by": user_email
        }),
        "pending_ai_requests": ai_requests_collection.count_documents({
            "requested_by": user_email,
            "status": "pending"
        }),
        "applied_ai_requests": ai_requests_collection.count_documents({
            "requested_by": user_email,
            "status": "applied"
        })
    }