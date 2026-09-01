from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from pymongo.database import Database


class ReviewRepository:
    def __init__(self, db: Database):
        self.db = db

    def create(self, data: dict) -> dict:
        now = datetime.now(timezone.utc)
        data.setdefault("created_at", now)
        data.setdefault("updated_at", now)
        data.setdefault("status", "pending")
        result = self.db.reviews.insert_one(data)
        data["_id"] = result.inserted_id
        return data

    def find_by_id(self, review_id: str) -> Optional[dict]:
        try:
            oid = ObjectId(review_id)
        except Exception:
            return None
        return self.db.reviews.find_one({"_id": oid})

    def find_approved_for_product(self, product_id: str, limit: int = 20) -> list:
        try:
            oid = ObjectId(product_id)
        except Exception:
            return []
        return list(
            self.db.reviews.find({"product_id": oid, "status": "approved"})
            .sort("created_at", -1)
            .limit(limit)
        )

    def find_by_user_and_product(self, user_id: str, product_id: str) -> Optional[dict]:
        try:
            return self.db.reviews.find_one({
                "user_id": ObjectId(user_id),
                "product_id": ObjectId(product_id),
            })
        except Exception:
            return None

    def find_all(self, status: str = None, page: int = 1, limit: int = 20) -> tuple:
        query = {}
        if status:
            query["status"] = status
        total = self.db.reviews.count_documents(query)
        items = list(
            self.db.reviews.find(query)
            .sort("created_at", -1)
            .skip((page - 1) * limit)
            .limit(limit)
        )
        return items, total

    def update_status(self, review_id: str, status: str) -> bool:
        try:
            oid = ObjectId(review_id)
        except Exception:
            return False
        result = self.db.reviews.update_one(
            {"_id": oid},
            {"$set": {"status": status, "updated_at": datetime.now(timezone.utc)}},
        )
        return result.modified_count > 0 or result.matched_count > 0

    def aggregate_product_rating(self, product_id: str) -> dict:
        try:
            oid = ObjectId(product_id)
        except Exception:
            return {"avg_rating": 0.0, "review_count": 0}
        pipeline = [
            {"$match": {"product_id": oid, "status": "approved"}},
            {"$group": {"_id": None, "avg": {"$avg": "$rating"}, "n": {"$sum": 1}}},
        ]
        result = list(self.db.reviews.aggregate(pipeline))
        if not result:
            return {"avg_rating": 0.0, "review_count": 0}
        return {
            "avg_rating": round(float(result[0].get("avg") or 0), 2),
            "review_count": int(result[0].get("n") or 0),
        }

    def user_purchased_product(self, user_id: str, product_id: str) -> bool:
        """Return True if the user has at least one order containing this product."""
        try:
            uid = ObjectId(user_id)
            pid = ObjectId(product_id)
        except Exception:
            return False
        return self.db.orders.count_documents({
            "customer_id": uid,
            "items.product_id": pid,
        }) > 0
