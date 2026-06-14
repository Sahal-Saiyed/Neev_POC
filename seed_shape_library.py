from datetime import datetime
from db import shape_library_collection

def seed_shape_library():
    shapes = [
        {
            "shape_name": "BOTTOM BAR",
            "category": "beam",
            "image_path": "assets/shapes/bottom_bar.png",
            "outputs": [
                {
                    "output_name": "L1",
                    "formula": "(LD + (10 * D)) - CX - (1 * CO)",
                    "unit": "m"
                },
                {
                    "output_name": "L2",
                    "formula": "max(BX, BY) + (CX + CY) - (2 * CO)",
                    "unit": "m"
                },
                {
                    "output_name": "L3",
                    "formula": "(LD + (10 * D)) - CY - (1 * CO)",
                    "unit": "m"
                }
            ],
            "is_active": True,
            "created_at": datetime.now()
        },
        {
            "shape_name": "TOP EXTRA BAR-LEFT",
            "category": "beam",
            "image_path": "assets/shapes/top_extra_bar_left.png",
            "outputs": [
                {
                    "output_name": "L1",
                    "formula": "(LD + (10 * D)) - (CX - (1 * CO))",
                    "unit": "m"
                },
                {
                    "output_name": "L2",
                    "formula": "(max(BX, BY) / 4) + (CX - (1 * CO))",
                    "unit": "m"
                }
            ],
            "is_active": True,
            "created_at": datetime.now()
        },
        {
            "shape_name": "TOP BAR",
            "category": "beam",
            "image_path": "assets/shapes/top_bar.png",
            "outputs": [
                {
                    "output_name": "L1",
                    "formula": "(LD + (10 * D)) - CX - (1 * CO)",
                    "unit": "m"
                },
                {
                    "output_name": "L2",
                    "formula": "max(BX, BY) + (CX + CY) - (2 * CO)",
                    "unit": "m"
                },
                {
                    "output_name": "L3",
                    "formula": "(LD + (10 * D)) - CY - (1 * CO)",
                    "unit": "m"
                }
            ],
            "is_active": True,
            "created_at": datetime.now()
        },
        {
            "shape_name": "TOP EXTRA BAR-RIGHT",
            "category": "beam",
            "image_path": "assets/shapes/top_extra_bar_right.png",
            "outputs": [
                {
                    "output_name": "L1",
                    "formula": "(LD + (10 * D)) - (CY - (1 * CO))",
                    "unit": "m"
                },
                {
                    "output_name": "L2",
                    "formula": "(max(BX, BY) / 4) + (CY - (1 * CO))",
                    "unit": "m"
                }
            ],
            "is_active": True,
            "created_at": datetime.now()
        },
        {
            "shape_name": "BOTTOM EXTRA BAR",
            "category": "beam",
            "image_path": "assets/shapes/bottom_extra_bar.png",
            "outputs": [
                {
                    "output_name": "L1",
                    "formula": "max(BX, BY) * 0.60",
                    "unit": "m"
                }
            ],
            "is_active": True,
            "created_at": datetime.now()
        },
        {
            "shape_name": "OUTER RING STIRRUPS",
            "category": "beam",
            "image_path": "assets/shapes/outer_ring_stirrups.png",
            "outputs": [
                {
                    "output_name": "L1",
                    "formula": "10 * D",
                    "unit": "m"
                },
                {
                    "output_name": "L2",
                    "formula": "min(BX, BY) - (2 * CO)",
                    "unit": "m"
                },
                {
                    "output_name": "L3",
                    "formula": "BZ - (2 * CO)",
                    "unit": "m"
                },
                {
                    "output_name": "L4",
                    "formula": "min(BX, BY) - (2 * CO)",
                    "unit": "m"
                },
                {
                    "output_name": "L5",
                    "formula": "BZ - (2 * CO)",
                    "unit": "m"
                },
                {
                    "output_name": "L6",
                    "formula": "10 * D",
                    "unit": "m"
                }
            ],
            "is_active": True,
            "created_at": datetime.now()
        },
        {
            "shape_name": "INNER RING",
            "category": "beam",
            "image_path": "assets/shapes/inner_ring.png",
            "outputs": [
                {
                    "output_name": "L1",
                    "formula": "10 * D",
                    "unit": "m"
                },
                {
                    "output_name": "L2",
                    "formula": "((min(BX, BY) - (2 * CO) - (2 * SD) - (2 * (0.5 * D))) / LS) + D",
                    "unit": "m"
                },
                {
                    "output_name": "L3",
                    "formula": "BZ - (2 * CO)",
                    "unit": "m"
                },
                {
                    "output_name": "L4",
                    "formula": "((min(BX, BY) - (2 * CO) - (2 * SD) - (2 * (0.5 * D))) / LS) + D",
                    "unit": "m"
                },
                {
                    "output_name": "L5",
                    "formula": "BZ - (2 * CO)",
                    "unit": "m"
                },
                {
                    "output_name": "L6",
                    "formula": "10 * D",
                    "unit": "m"
                }
            ],
            "is_active": True,
            "created_at": datetime.now()
        },
        {
            "shape_name": "STIRRUPS - INNER RING",
            "category": "beam",
            "image_path": "assets/shapes/stirrups_inner_ring.png",
            "outputs": [
                {
                    "output_name": "L1",
                    "formula": "10 * D",
                    "unit": "m"
                },
                {
                    "output_name": "L2",
                    "formula": "2 * (min(BX, BY) - (2 * CO))",
                    "unit": "m"
                },
                {
                    "output_name": "L3",
                    "formula": "(BZ - (2 * CO) - (2 * D) - (2 * D) - ((2 * (0.5 * D)) / 3)) + D",
                    "unit": "m"
                },
                {
                    "output_name": "L4",
                    "formula": "2 * (min(BX, BY) - (2 * CO))",
                    "unit": "m"
                },
                {
                    "output_name": "L5",
                    "formula": "(BZ - (2 * CO) - (2 * D) - (2 * D) - ((2 * (0.5 * D)) / 3)) + D",
                    "unit": "m"
                },
                {
                    "output_name": "L6",
                    "formula": "10 * D",
                    "unit": "m"
                }
            ],
            "is_active": True,
            "created_at": datetime.now()
        }
    ]

    for shape in shapes:
        existing_shape = shape_library_collection.find_one({
            "shape_name": shape["shape_name"],
            "category": shape["category"]
        })

        if existing_shape:
            shape_library_collection.update_one(
                {
                    "shape_name": shape["shape_name"],
                    "category": shape["category"]
                },
                {
                    "$set": shape
                }
            )
            print(f"Updated: {shape['shape_name']}")
        else:
            shape_library_collection.insert_one(shape)
            print(f"Inserted: {shape['shape_name']}")

    print("Shape library seeding completed.")


if __name__ == "__main__":
    seed_shape_library()