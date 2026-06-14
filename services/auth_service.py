from datetime import datetime

from db import users_collection
from auth import hash_password, check_password


def count_admin_users():
    return users_collection.count_documents({"role": "admin"})


def count_normal_users():
    return users_collection.count_documents({"role": "user"})


def find_user_by_email(email: str):
    if not email:
        return None

    return users_collection.find_one({"email": email})


def register_user(name: str, email: str, password: str, role: str):
    user_data = {
        "name": name,
        "email": email,
        "password": hash_password(password),
        "role": role,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "status": "active"
    }

    result = users_collection.insert_one(user_data)
    return str(result.inserted_id)


def authenticate_user(email: str, password: str):
    user = find_user_by_email(email)

    if not user:
        return None

    if not check_password(password, user.get("password")):
        return None

    return user