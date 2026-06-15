import argparse
import os
import sys
from datetime import datetime


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from db import (
    shape_library_collection,
    custom_shape_library_collection,
    ai_requests_collection
)

from services.image_service import save_local_image_to_mongodb

def resolve_local_path(image_path: str):
    if not image_path:
        return None

    if os.path.isabs(image_path):
        return image_path

    return os.path.join(PROJECT_ROOT, image_path)


def has_mongodb_image(document: dict):
    return bool(document.get("image_file_id"))


def migrate_shape_library(dry_run: bool = True):
    print("\nMigrating shape_library images...")

    scanned = 0
    migrated = 0
    skipped = 0

    shapes = shape_library_collection.find({
        "image_path": {"$exists": True, "$nin": [None, ""]}
    })

    for shape in shapes:
        scanned += 1

        if has_mongodb_image(shape):
            skipped += 1
            continue

        image_path = shape.get("image_path")
        local_path = resolve_local_path(image_path)

        if not local_path or not os.path.exists(local_path):
            skipped += 1
            print(f"SKIP missing file: {image_path}")
            continue

        shape_name = shape.get("shape_name", "shape")
        category = shape.get("category", "beam")

        if dry_run:
            print(f"DRY RUN shape_library: {shape_name} -> {image_path}")
            migrated += 1
            continue

        image_metadata = save_local_image_to_mongodb(
            image_path=local_path,
            category=category,
            shape_name=shape_name,
            uploaded_by="migration_script",
            source="shape_library_image_migration"
        )

        shape_library_collection.update_one(
            {"_id": shape["_id"]},
            {
                "$set": {
                    "image_file_id": image_metadata.get("image_file_id"),
                    "image_filename": image_metadata.get("image_filename"),
                    "image_mime_type": image_metadata.get("image_mime_type"),
                    "image_storage": image_metadata.get("image_storage"),
                    "image_migrated_at": datetime.now()
                }
            }
        )

        migrated += 1
        print(f"MIGRATED shape_library: {shape_name}")

    return scanned, migrated, skipped


def migrate_custom_shape_library(dry_run: bool = True):
    print("\nMigrating custom_shape_library images...")

    scanned = 0
    migrated = 0
    skipped = 0

    custom_shapes = custom_shape_library_collection.find({
        "type": "custom_shape",
        "image_path": {"$exists": True, "$nin": [None, ""]}
    })

    for custom_shape in custom_shapes:
        scanned += 1

        if has_mongodb_image(custom_shape):
            skipped += 1
            continue

        image_path = custom_shape.get("image_path")
        local_path = resolve_local_path(image_path)

        if not local_path or not os.path.exists(local_path):
            skipped += 1
            print(f"SKIP missing file: {image_path}")
            continue

        shape_name = custom_shape.get("shape_name", "custom_shape")
        category = custom_shape.get("category", "beam")

        if dry_run:
            print(f"DRY RUN custom_shape_library: {shape_name} -> {image_path}")
            migrated += 1
            continue

        image_metadata = save_local_image_to_mongodb(
            image_path=local_path,
            category=category,
            shape_name=shape_name,
            uploaded_by="migration_script",
            source="custom_shape_library_image_migration"
        )

        custom_shape_library_collection.update_one(
            {"_id": custom_shape["_id"]},
            {
                "$set": {
                    "image_file_id": image_metadata.get("image_file_id"),
                    "image_filename": image_metadata.get("image_filename"),
                    "image_mime_type": image_metadata.get("image_mime_type"),
                    "image_storage": image_metadata.get("image_storage"),
                    "image_migrated_at": datetime.now()
                }
            }
        )

        migrated += 1
        print(f"MIGRATED custom_shape_library: {shape_name}")

    return scanned, migrated, skipped


def migrate_ai_requests(dry_run: bool = True):
    print("\nMigrating ai_requests new-shape images...")

    scanned = 0
    migrated = 0
    skipped = 0

    requests = ai_requests_collection.find({
        "request_type": "new_shape"
    })

    for request in requests:
        scanned += 1

        payload = request.get("new_shape_payload", {}) or {}

        existing_file_id = (
            payload.get("image_file_id")
            or request.get("new_shape_image_file_id")
            or request.get("image_file_id")
        )

        if existing_file_id:
            skipped += 1
            continue

        image_path = (
            payload.get("image_path")
            or request.get("new_shape_image_path")
            or request.get("image_path")
        )

        local_path = resolve_local_path(image_path)

        if not local_path or not os.path.exists(local_path):
            skipped += 1
            print(f"SKIP missing file: {image_path}")
            continue

        shape_name = (
            payload.get("shape_name")
            or request.get("shape_name")
            or "new_shape"
        )

        category = request.get("category", "beam")

        if dry_run:
            print(f"DRY RUN ai_requests: {shape_name} -> {image_path}")
            migrated += 1
            continue

        image_metadata = save_local_image_to_mongodb(
            image_path=local_path,
            category=category,
            shape_name=shape_name,
            uploaded_by="migration_script",
            source="ai_request_image_migration"
        )

        ai_requests_collection.update_one(
            {"_id": request["_id"]},
            {
                "$set": {
                    "new_shape_image_file_id": image_metadata.get("image_file_id"),
                    "new_shape_image_filename": image_metadata.get("image_filename"),
                    "new_shape_image_mime_type": image_metadata.get("image_mime_type"),
                    "new_shape_image_storage": image_metadata.get("image_storage"),

                    "new_shape_payload.image_file_id": image_metadata.get("image_file_id"),
                    "new_shape_payload.image_filename": image_metadata.get("image_filename"),
                    "new_shape_payload.image_mime_type": image_metadata.get("image_mime_type"),
                    "new_shape_payload.image_storage": image_metadata.get("image_storage"),

                    "image_migrated_at": datetime.now()
                }
            }
        )

        migrated += 1
        print(f"MIGRATED ai_requests: {shape_name}")

    return scanned, migrated, skipped


def print_summary(name: str, result):
    scanned, migrated, skipped = result

    print(f"\n{name} summary:")
    print(f"  Scanned : {scanned}")
    print(f"  Migrated: {migrated}")
    print(f"  Skipped : {skipped}")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate local image_path images to MongoDB GridFS."
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually migrate images. Without this, script runs in dry-run mode."
    )

    args = parser.parse_args()

    dry_run = not args.apply

    if dry_run:
        print("Running in DRY RUN mode. No MongoDB records will be changed.")
        print("Use --apply to migrate images.")
    else:
        print("Running in APPLY mode. MongoDB records will be updated.")

    shape_result = migrate_shape_library(dry_run=dry_run)
    custom_result = migrate_custom_shape_library(dry_run=dry_run)
    ai_request_result = migrate_ai_requests(dry_run=dry_run)

    print_summary("shape_library", shape_result)
    print_summary("custom_shape_library", custom_result)
    print_summary("ai_requests", ai_request_result)

    print("\nDone.")


if __name__ == "__main__":
    main()