from datetime import datetime, timezone

from pymongo.database import Database
from bson import ObjectId


class UserRepository:
    def __init__(self, db: Database):
        self.collection = db.users

    def find_by_email(self, email: str) -> dict:
        return self.collection.find_one({"email": email.lower()})

    def find_by_id(self, user_id: str) -> dict:
        return self.collection.find_one({"_id": ObjectId(user_id)})

    def create(self, data: dict) -> dict:
        data["email"] = data["email"].lower()
        result = self.collection.insert_one(data)
        data["_id"] = result.inserted_id
        return data

    def update(self, user_id: str, data: dict) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": data},
        )
        return result.modified_count > 0

    def email_exists(self, email: str) -> bool:
        return self.collection.find_one({"email": email.lower()}) is not None

    def set_otp(self, user_id: str, otp_hash: str, expiry, now) -> bool:
        return self.update(user_id, {
            "email_otp_hash": otp_hash,
            "email_otp_expiry": expiry,
            "email_otp_attempts": 0,
            "otp_locked_until": None,
            "last_otp_sent_at": now,
            "updated_at": now,
        })

    def mark_verified(self, user_id: str) -> bool:
        now = datetime.now(timezone.utc)
        return self.update(user_id, {
            "email_verified": True,
            "is_active": True,
            "email_otp_hash": None,
            "email_otp_expiry": None,
            "email_otp_attempts": 0,
            "otp_locked_until": None,
            "updated_at": now,
        })

    def clear_otp(self, user_id: str) -> bool:
        """Clear OTP fields without touching is_active/email_verified.

        Used by the admin login flow where a successful OTP must not
        auto-reactivate a deactivated account.
        """
        return self.update(user_id, {
            "email_otp_hash": None,
            "email_otp_expiry": None,
            "email_otp_attempts": 0,
            "otp_locked_until": None,
            "updated_at": datetime.now(timezone.utc),
        })

    def record_failed_otp(self, user_id: str, locked_until=None) -> None:
        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": {"email_otp_attempts": 1}, "$set": {"otp_locked_until": locked_until}},
        )

    def find_all(self, page: int = 1, limit: int = 20, role: str = None, is_active: bool = None) -> tuple:
        query = {}
        if role:
            query["role"] = role
        if is_active is not None:
            query["is_active"] = is_active

        total = self.collection.count_documents(query)
        skip = (page - 1) * limit
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        users = list(cursor)
        return users, total

    def count(self, query: dict = None) -> int:
        return self.collection.count_documents(query or {})
