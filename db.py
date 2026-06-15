import os
from pymongo import MongoClient
from config import get_setting, require_setting

MONGO_URI = require_setting("MONGO_URI")
DB_NAME = get_setting("DB_NAME", "BuniyadBytePOC")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


if not MONGO_URI:
    raise Exception("MONGO_URI not found. Please add it in .env file.")

client = MongoClient(MONGO_URI)

db = client["ai_agent_poc"]

users_collection = db["users"]
projects_collection = db["projects"]
blocks_collection = db["blocks"]
floors_collection = db["floors"]
autocad_imports_collection = db["autocad_imports"]

shape_library_collection = db["shape_library"]
custom_shape_library_collection = db["custom_shape_library"]
beams_collection = db["beams"]

ai_requests_collection = db["ai_requests"]

def test_connection():
    try:
        client.admin.command("ping")
        return True
    except Exception as e:
        print("MongoDB connection error:", e)
        return False