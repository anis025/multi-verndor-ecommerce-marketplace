from app.db.mongodb import get_database


def create_indexes():
    db = get_database()

    required_collections = [
        "users", "sellers", "categories",
        "products", "carts", "orders", "notifications",
        "reviews",
    ]
    existing = db.list_collection_names()
    for name in required_collections:
        if name not in existing:
            db.create_collection(name)

    db.users.create_index("email", unique=True)
    db.users.create_index("role")
    db.users.create_index("email_verified")

    db.sellers.create_index("user_id")

    db.products.create_index("seller_id")
    db.products.create_index("category_id")
    db.products.create_index("name")
    db.products.create_index("is_active")

    db.orders.create_index("customer_id")
    db.orders.create_index("created_at")

    db.notifications.create_index("user_id")
    db.notifications.create_index("is_read")

    db.reviews.create_index([("product_id", 1), ("status", 1)])
    db.reviews.create_index("user_id")
