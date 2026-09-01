import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from pymongo import MongoClient
from app.core.config import settings

PRODUCTS = [
    {"id": "v800", "vendor": "vault", "name": "Darth Vader", "cat": "Star Wars", "price": 260, "badge": "NEW"},
    {"id": "v18", "vendor": "vault", "name": "Iron Man (Gold)", "cat": "Marvel · Avengers", "price": 260, "badge": "NEW"},
    {"id": "v54", "vendor": "vault", "name": "Batman (Keaton)", "cat": "DC · Batman", "price": 280, "badge": "NEW"},
    {"id": "v210", "vendor": "vault", "name": "Madara Uchiha", "cat": "Naruto", "price": 240, "badge": "NEW"},
    {"id": "v311", "vendor": "vault", "name": "Vecna", "cat": "Stranger Things", "price": 180, "badge": "NEW"},
    {"id": "v406", "vendor": "vault", "name": "Homelander", "cat": "The Boys", "price": 220, "badge": "NEW"},
    {"id": "v105", "vendor": "vault", "name": "Messi (FC Barcelona)", "cat": "FIFA", "price": 220, "badge": "NEW"},
    {"id": "v701", "vendor": "vault", "name": "Omni-Man", "cat": "Invincible", "price": 220, "badge": "NEW"},
    {"id": "v3", "vendor": "vault", "name": "Spider-Man (Tom)", "cat": "Marvel · Spider-Man", "price": 200, "badge": "NEW"},
    {"id": "v64", "vendor": "vault", "name": "Wonder Woman", "cat": "DC", "price": 200, "badge": "NEW"},
    {"id": "v108", "vendor": "vault", "name": "Ronaldo (Real Madrid)", "cat": "FIFA", "price": 220, "badge": "NEW"},
    {"id": "v504", "vendor": "vault", "name": "Makima", "cat": "Chainsaw Man", "price": 240, "badge": "NEW"},
    {"id": "v600", "vendor": "vault", "name": "DBZ Set (Goku · Vegeta · Vegito · Son Goku)", "cat": "Dragon Ball Z", "price": 880, "badge": "NEW"},
    {"id": "v803", "vendor": "vault", "name": "The Mandalorian", "cat": "Star Wars", "price": 240, "badge": "NEW"},
    {"id": "v44", "vendor": "vault", "name": "Venom", "cat": "Marvel · Spider-Man Villains", "price": 200, "badge": "NEW"},
    {"id": "v52", "vendor": "vault", "name": "Batman (Pattinson)", "cat": "DC · Batman", "price": 240, "badge": "NEW"},
    {"id": "v202", "vendor": "vault", "name": "Naruto Baryon Mode", "cat": "Naruto", "price": 250, "badge": "NEW"},
    {"id": "v401", "vendor": "vault", "name": "Soldier Boy", "cat": "The Boys", "price": 200, "badge": "NEW"},
    {"id": "v502", "vendor": "vault", "name": "Denji (Bloody Shirt)", "cat": "Chainsaw Man", "price": 280, "badge": "NEW"},
    {"id": "v806", "vendor": "vault", "name": "Baby Yoda (Grogu)", "cat": "Star Wars", "price": 220, "badge": "NEW"},
    # Odysse4u products
    {"id": "o1", "vendor": "odysse", "name": "PVC Butterfly Shoe", "cat": "Shoes", "price": 850, "badge": None},
    {"id": "o2", "vendor": "odysse", "name": "High Heel", "cat": "Heels", "price": 2350, "badge": None},
    {"id": "o3", "vendor": "odysse", "name": "Hand Purse", "cat": "Bags", "price": 799, "badge": None},
    {"id": "o4", "vendor": "odysse", "name": "Mini Hand Purse", "cat": "Mini Bags", "price": 750, "badge": None},
    {"id": "o5", "vendor": "odysse", "name": "PU Leather Backpack", "cat": "Backpacks", "price": 1400, "badge": None},
    {"id": "o6", "vendor": "odysse", "name": "Luxury Loafers", "cat": "Shoes", "price": 2500, "badge": None},
    {"id": "o7", "vendor": "odysse", "name": "Sliper", "cat": "Flip Flop & Slides", "price": 750, "badge": None},
    {"id": "o8", "vendor": "odysse", "name": "Hair Band", "cat": "Accessories", "price": 250, "badge": None},
    {"id": "o9", "vendor": "odysse", "name": "Hair Crown", "cat": "Accessories", "price": 250, "badge": None},
    {"id": "o10", "vendor": "odysse", "name": "Foot Peeling Mask", "cat": "Foot Care", "price": 350, "badge": None},
    {"id": "o11", "vendor": "odysse", "name": "Flower Vase", "cat": "Home", "price": 600, "badge": None},
    # Knot Fashion products
    {"id": "k1", "vendor": "knot", "name": "Black Drop Shoulder T-Shirt", "cat": "T-Shirts", "price": 290, "badge": None},
    {"id": "k2", "vendor": "knot", "name": "Bottle Green Drop Shoulder T-Shirt", "cat": "T-Shirts", "price": 290, "badge": None},
    {"id": "k3", "vendor": "knot", "name": "Coffee Drop Shoulder T-Shirt", "cat": "T-Shirts", "price": 290, "badge": None},
    {"id": "k4", "vendor": "knot", "name": "Maroon Drop Shoulder T-Shirt", "cat": "T-Shirts", "price": 290, "badge": None},
    {"id": "k5", "vendor": "knot", "name": "Sky Blue Drop Shoulder T-Shirt", "cat": "T-Shirts", "price": 290, "badge": None},
    {"id": "k6", "vendor": "knot", "name": "White Drop Shoulder T-Shirt", "cat": "T-Shirts", "price": 290, "badge": None},
    {"id": "k7", "vendor": "knot", "name": "Varsity Jacket", "cat": "Jackets", "price": 950, "badge": None},
]

VENDOR_NAMES = {
    "vault": "Jumanji Vault",
    "odysse": "Odysse4u",
    "knot": "Knot Fashion",
}

PRODUCT_DESCRIPTIONS = {
    "vault": "Premium collectible figurine. Hand-painted with incredible detail. Perfect for collectors and fans.",
    "odysse": "High-quality fashion accessory. Premium materials and craftsmanship.",
    "knot": "Premium streetwear. Comfortable fit with modern design.",
}


def seed_products():
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    products_col = db["products"]
    users_col = db["users"]
    sellers_col = db["sellers"]
    categories_col = db["categories"]

    now = datetime.now(timezone.utc)

    for product in PRODUCTS:
        vendor = product["vendor"]
        vendor_name = VENDOR_NAMES.get(vendor, vendor)

        existing = products_col.find_one({"vendor_product_id": product["id"]})
        if existing:
            continue

        seller = sellers_col.find_one({"store_name": vendor_name})
        if not seller:
            user = users_col.find_one({"email": f"{vendor}@hatify.com"})
            if not user:
                user_doc = {
                    "email": f"{vendor}@hatify.com",
                    "name": vendor_name,
                    "role": "seller",
                    "created_at": now,
                    "updated_at": now,
                }
                result = users_col.insert_one(user_doc)
                user_id = result.inserted_id
            else:
                user_id = user["_id"]

            seller_doc = {
                "user_id": user_id,
                "store_name": vendor_name,
                "description": f"Official {vendor_name} store.",
                "status": "approved",
                "is_approved": True,
                "created_at": now,
                "updated_at": now,
            }
            result = sellers_col.insert_one(seller_doc)
            seller_id = result.inserted_id
        else:
            seller_id = seller["_id"]

        cat_name = product["cat"]
        category = categories_col.find_one({"name": cat_name})
        if not category:
            cat_doc = {
                "name": cat_name,
                "description": f"{cat_name} products",
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            }
            result = categories_col.insert_one(cat_doc)
            category_id = result.inserted_id
        else:
            category_id = category["_id"]

        product_doc = {
            "seller_id": seller_id,
            "category_id": category_id,
            "vendor_product_id": product["id"],
            "name": product["name"],
            "description": PRODUCT_DESCRIPTIONS.get(vendor, ""),
            "price": product["price"],
            "stock": 50,
            "image": "",
            "is_active": True,
            "badge": product.get("badge"),
            "created_at": now,
            "updated_at": now,
        }
        products_col.insert_one(product_doc)

    count = products_col.count_documents({})
    print(f"Seeded {count} products successfully.")
    client.close()


if __name__ == "__main__":
    seed_products()
