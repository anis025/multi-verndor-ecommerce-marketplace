from datetime import datetime, timezone

from bson import ObjectId

from app.core.security import hash_password, verify_password
from app.db.mongodb import get_database
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self):
        db = get_database()
        self.user_repo = UserRepository(db)
        self.db = db

    def get_user(self, user_id: str) -> dict:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return None
        return self._to_response(user)

    def update_user(self, user_id: str, name: str = None) -> dict:
        update_data = {"updated_at": datetime.now(timezone.utc)}
        if name is not None:
            update_data["name"] = name

        self.user_repo.update(user_id, update_data)
        return self.get_user(user_id)

    def change_password(self, user_id: str, current_password: str, new_password: str) -> tuple:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return None, "User not found"

        if not verify_password(current_password, user["password_hash"]):
            return None, "Current password is incorrect"

        self.user_repo.update(user_id, {
            "password_hash": hash_password(new_password),
            "updated_at": datetime.now(timezone.utc),
        })
        return True, None

    def get_users_paginated(self, page: int = 1, limit: int = 20, role: str = None, is_active: bool = None) -> dict:
        users, total = self.user_repo.find_all(page=page, limit=limit, role=role, is_active=is_active)
        items = [self._to_admin_response(u) for u in users]
        return {"items": items, "page": page, "limit": limit, "total": total}

    def get_user_admin(self, user_id: str) -> dict:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return None
        return self._to_admin_response(user)

    def get_user_admin_detail(self, user_id: str) -> dict:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return None
        detail = self._to_admin_response(user)

        # Attach a basic order summary (count + last 5) when the user is a
        # customer. Sellers see their product count instead.
        try:
            uid = ObjectId(user_id)
        except Exception:
            return detail

        if user.get("role") == "customer":
            order_count = self.db.orders.count_documents({"customer_id": uid})
            recent = list(
                self.db.orders.find({"customer_id": uid})
                .sort("created_at", -1)
                .limit(5)
            )
            detail["order_count"] = order_count
            detail["recent_orders"] = [
                {
                    "id": str(o["_id"]),
                    "status": o.get("status"),
                    "total_amount": o.get("total_amount", 0),
                    "item_count": len(o.get("items", [])),
                    "created_at": str(o.get("created_at", "")),
                }
                for o in recent
            ]
        elif user.get("role") == "seller":
            seller = self.db.sellers.find_one({"user_id": uid})
            if seller:
                detail["seller_id"] = str(seller["_id"])
                detail["company_name"] = seller.get("company_name", "")
                detail["seller_status"] = seller.get("status", "pending")
                detail["is_approved"] = seller.get("is_approved", False)
                detail["product_count"] = self.db.products.count_documents(
                    {"seller_id": seller["_id"]}
                )
        return detail

    def mark_email_verified(self, user_id: str) -> tuple:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return None, "User not found"
        self.user_repo.update(user_id, {
            "email_verified": True,
            "is_active": True,
            "email_otp_hash": None,
            "email_otp_expiry": None,
            "email_otp_attempts": 0,
            "otp_locked_until": None,
            "updated_at": datetime.now(timezone.utc),
        })
        return self.get_user_admin(user_id), None

    def reset_password(self, user_id: str, new_password: str) -> tuple:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return None, "User not found"
        self.user_repo.update(user_id, {
            "password_hash": hash_password(new_password),
            "updated_at": datetime.now(timezone.utc),
        })
        return True, None

    def change_role(self, user_id: str, role: str) -> tuple:
        if role not in ("customer", "seller", "admin"):
            return None, "Invalid role"
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return None, "User not found"
        self.user_repo.update(user_id, {"role": role, "updated_at": datetime.now(timezone.utc)})
        return self.get_user_admin(user_id), None

    def update_user_status(self, user_id: str, is_active: bool) -> tuple:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return None, "User not found"

        self.user_repo.update(user_id, {
            "is_active": is_active,
            "updated_at": datetime.now(timezone.utc),
        })
        return self.get_user_admin(user_id), None

    def _to_response(self, user: dict) -> dict:
        return {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "is_active": user.get("is_active", True),
            "email_verified": user.get("email_verified", True),
            "created_at": str(user.get("created_at", "")),
            "updated_at": str(user.get("updated_at", "")),
        }

    def _to_admin_response(self, user: dict) -> dict:
        return self._to_response(user)
