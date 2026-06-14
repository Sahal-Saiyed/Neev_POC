from datetime import datetime

from db import ai_requests_collection
from agent.schemas import AIRequestCreate


def create_ai_request(request_data: AIRequestCreate):
    document = request_data.model_dump()

    document["created_at"] = datetime.now()
    document["updated_at"] = datetime.now()

    result = ai_requests_collection.insert_one(document)

    request_id = str(result.inserted_id)
    request_code = f"AIR-{request_id[-6:].upper()}"

    ai_requests_collection.update_one(
        {"_id": result.inserted_id},
        {
            "$set": {
                "request_code": request_code
            }
        }
    )

    return request_id


def get_pending_ai_requests():
    return list(
        ai_requests_collection.find({
            "status": "pending"
        }).sort("created_at", -1)
    )