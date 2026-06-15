import os
import re
from datetime import datetime
from typing import Optional

import gridfs
from bson.objectid import ObjectId

from db import db


fs = gridfs.GridFS(db)


def _safe_filename_part(value: str):
    value = value or "image"
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = value.strip("_")
    return value or "image"


def _get_file_extension(filename: str, mime_type: str = ""):
    if filename:
        _, extension = os.path.splitext(filename)

        if extension:
            return extension.lower()

    mime_type = mime_type or ""

    if "png" in mime_type:
        return ".png"

    if "jpeg" in mime_type or "jpg" in mime_type:
        return ".jpg"

    if "webp" in mime_type:
        return ".webp"

    return ".png"


def save_uploaded_image_to_mongodb(
    uploaded_file,
    category: str = "beam",
    shape_name: str = "shape",
    uploaded_by: Optional[str] = None,
    source: str = "shape_upload"
):
    """
    Saves a Streamlit uploaded image to MongoDB GridFS.

    Returns metadata dict that can be stored in:
    - shape_library
    - custom_shape_library
    - ai_requests
    """

    if uploaded_file is None:
        return {
            "image_file_id": None,
            "image_filename": None,
            "image_mime_type": None,
            "image_storage": None
        }

    file_bytes = uploaded_file.getvalue()
    original_filename = uploaded_file.name or "shape_image.png"
    mime_type = uploaded_file.type or "image/png"

    safe_category = _safe_filename_part(category)
    safe_shape_name = _safe_filename_part(shape_name)
    extension = _get_file_extension(original_filename, mime_type)

    filename = (
        f"{safe_category}_{safe_shape_name}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        f"{extension}"
    )

    file_id = fs.put(
        file_bytes,
        filename=filename,
        content_type=mime_type,
        metadata={
            "category": category,
            "shape_name": shape_name,
            "uploaded_by": uploaded_by,
            "source": source,
            "original_filename": original_filename,
            "created_at": datetime.now()
        }
    )

    return {
        "image_file_id": str(file_id),
        "image_filename": filename,
        "image_mime_type": mime_type,
        "image_storage": "mongodb_gridfs"
    }


def get_mongodb_image_bytes(image_file_id: str):
    """
    Returns image bytes from GridFS.
    Returns None if file is missing or ID is invalid.
    """

    if not image_file_id:
        return None

    try:
        file_obj = fs.get(ObjectId(str(image_file_id)))
        return file_obj.read()
    except Exception:
        return None


def get_mongodb_image_info(image_file_id: str):
    """
    Returns GridFS file metadata.
    Returns None if missing.
    """

    if not image_file_id:
        return None

    try:
        file_obj = fs.get(ObjectId(str(image_file_id)))

        return {
            "image_file_id": str(file_obj._id),
            "image_filename": file_obj.filename,
            "image_mime_type": getattr(file_obj, "content_type", None),
            "metadata": getattr(file_obj, "metadata", {})
        }

    except Exception:
        return None


def delete_mongodb_image(image_file_id: str):
    """
    Deletes image from GridFS.
    Safe to call even if image does not exist.
    """

    if not image_file_id:
        return False

    try:
        fs.delete(ObjectId(str(image_file_id)))
        return True
    except Exception:
        return False


def has_mongodb_image(image_file_id: str):
    if not image_file_id:
        return False

    try:
        return fs.exists(ObjectId(str(image_file_id)))
    except Exception:
        return False


def extract_image_metadata_from_document(document: dict):
    """
    Normalizes image metadata from any DB document.
    """

    if not document:
        return {
            "image_file_id": None,
            "image_filename": None,
            "image_mime_type": None,
            "image_storage": None,
            "image_path": None
        }

    return {
        "image_file_id": document.get("image_file_id"),
        "image_filename": document.get("image_filename"),
        "image_mime_type": document.get("image_mime_type"),
        "image_storage": document.get("image_storage"),
        "image_path": document.get("image_path")
    }