from datetime import datetime, timezone

from app.db.mongodb import get_database
from app.repositories.review_repository import ReviewRepository


class ReviewService:
    def __init__(self):
        self.db = get_database()
        self.review_repo = ReviewRepository(self.db)

    def create_review(self, user_id: str, product_id: str, rating: int, title: str, body: str):
        if not (1 <= rating <= 5):
            return None, "Rating must be between 1 and 5."

        if self.review_repo.find_by_user_and_product(user_id, product_id):
            return None, "You have already reviewed this product."

        if not self.review_repo.user_purchased_product(user_id, product_id):
            return None, "You can only review products you have purchased."

        now = datetime.now(timezone.utc)
        data = {
            "user_id": self._oid(user_id),
            "product_id": self._oid(product_id),
            "rating": rating,
            "title": (title or "").strip()[:120],
            "body": (body or "").strip()[:2000],
            "status": "approved",  # auto-approve; admins can moderate later if needed
            "created_at": now,
            "updated_at": now,
        }
        review = self.review_repo.create(data)
        return self._to_response(review), None

    def list_for_product(self, product_id: str, limit: int = 20):
        reviews = self.review_repo.find_approved_for_product(product_id, limit=limit)
        return [self._to_response(r) for r in reviews]

    def aggregate_product_rating(self, product_id: str):
        return self.review_repo.aggregate_product_rating(product_id)

    def moderate(self, review_id: str, status: str):
        if status not in ("approved", "rejected", "pending"):
            return None, "Invalid status."
        if not self.review_repo.update_status(review_id, status):
            return None, "Review not found."
        review = self.review_repo.find_by_id(review_id)
        if not review:
            return None, "Review not found."
        return self._to_response(review), None

    def list_all(self, status: str = None, page: int = 1, limit: int = 20):
        items, total = self.review_repo.find_all(status=status, page=page, limit=limit)
        return {
            "items": [self._to_response(r) for r in items],
            "page": page,
            "limit": limit,
            "total": total,
        }

    @staticmethod
    def _oid(value):
        from bson import ObjectId
        try:
            return ObjectId(value)
        except Exception:
            return None

    def _to_response(self, review: dict) -> dict:
        user = None
        if review.get("user_id"):
            user = self.db.users.find_one({"_id": review["user_id"]}, {"name": 1})
        return {
            "id": str(review["_id"]),
            "product_id": str(review["product_id"]),
            "user_id": str(review["user_id"]),
            "user_name": user["name"] if user else "Customer",
            "rating": review.get("rating", 0),
            "title": review.get("title", ""),
            "body": review.get("body", ""),
            "status": review.get("status", "pending"),
            "created_at": str(review.get("created_at", "")),
        }
