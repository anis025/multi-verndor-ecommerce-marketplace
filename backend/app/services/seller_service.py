from datetime import datetime, timezone

from app.db.mongodb import get_database
from app.repositories.seller_repository import SellerRepository
from app.repositories.user_repository import UserRepository


class SellerService:
    def __init__(self):
        db = get_database()
        self.seller_repo = SellerRepository(db)
        self.user_repo = UserRepository(db)

    def get_seller_profile(self, user_id: str) -> dict:
        seller = self.seller_repo.find_by_user_id(user_id)
        if not seller:
            return None
        return self._to_response(seller)

    def update_seller_profile(self, user_id: str, company_name: str = None,
                               description: str = None, phone: str = None,
                               address: str = None) -> tuple:
        seller = self.seller_repo.find_by_user_id(user_id)
        if not seller:
            return None, "Seller profile not found"

        update_data = {"updated_at": datetime.now(timezone.utc)}
        if company_name is not None:
            update_data["company_name"] = company_name
        if description is not None:
            update_data["description"] = description
        if phone is not None:
            update_data["phone"] = phone
        if address is not None:
            update_data["address"] = address

        self.seller_repo.update(str(seller["_id"]), update_data)
        return self.get_seller_profile(user_id), None

    def get_sellers_paginated(self, page: int = 1, limit: int = 20, status: str = None, search: str = None) -> dict:
        sellers, total = self.seller_repo.find_all(page=page, limit=limit, status=status, search=search)
        items = []
        for s in sellers:
            user = self.user_repo.find_by_id(str(s["user_id"]))
            item = self._to_admin_response(s)
            if user:
                item["user_email"] = user["email"]
                item["user_name"] = user["name"]
            items.append(item)
        return {"items": items, "page": page, "limit": limit, "total": total}

    def get_seller_admin(self, seller_id: str) -> dict:
        seller = self.seller_repo.find_by_id(seller_id)
        if not seller:
            return None
        item = self._to_admin_response(seller)
        user = self.user_repo.find_by_id(str(seller["user_id"]))
        if user:
            item["user_email"] = user["email"]
            item["user_name"] = user["name"]
        return item

    def update_seller_status(self, seller_id: str, status: str, reviewed_by: str,
                             reason: str = None, notes: str = None) -> tuple:
        seller = self.seller_repo.find_by_id(seller_id)
        if not seller:
            return None, "Seller not found"

        now = datetime.now(timezone.utc)
        update_data = {
            "status": status,
            "is_approved": status == "approved",
            "reviewed_by": reviewed_by,
            "reviewed_at": now,
            "updated_at": now,
        }
        if status == "rejected":
            update_data["rejection_reason"] = reason
        elif status == "suspended":
            update_data["suspension_reason"] = reason
        if notes is not None:
            update_data["admin_notes"] = notes

        self.seller_repo.update(seller_id, update_data)
        return self.get_seller_admin(seller_id), None

    def _to_response(self, seller: dict) -> dict:
        return {
            "id": str(seller["_id"]),
            "user_id": str(seller["user_id"]),
            "company_name": seller["company_name"],
            "description": seller.get("description", ""),
            "phone": seller.get("phone", ""),
            "address": seller.get("address", ""),
            "is_approved": seller.get("is_approved", False),
            "created_at": str(seller.get("created_at", "")),
            "updated_at": str(seller.get("updated_at", "")),
        }

    def _to_admin_response(self, seller: dict) -> dict:
        status = seller.get("status")
        if not status:
            status = "approved" if seller.get("is_approved", False) else "pending"
        return {
            "id": str(seller["_id"]),
            "user_id": str(seller["user_id"]),
            "company_name": seller["company_name"],
            "description": seller.get("description", ""),
            "phone": seller.get("phone", ""),
            "address": seller.get("address", ""),
            "status": status,
            "rejection_reason": seller.get("rejection_reason"),
            "suspension_reason": seller.get("suspension_reason"),
            "admin_notes": seller.get("admin_notes"),
            "reviewed_by": str(seller["reviewed_by"]) if seller.get("reviewed_by") else None,
            "reviewed_at": str(seller.get("reviewed_at", "")),
            "created_at": str(seller.get("created_at", "")),
            "updated_at": str(seller.get("updated_at", "")),
        }
