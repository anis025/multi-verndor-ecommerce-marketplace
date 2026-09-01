from pymongo.database import Database
from bson import ObjectId


class NotificationRepository:
    def __init__(self, db: Database):
        self.collection = db.notifications

    def create(self, data: dict) -> dict:
        result = self.collection.insert_one(data)
        data["_id"] = result.inserted_id
        return data

    def find_by_user(self, user_id: str, page: int = 1, limit: int = 20) -> tuple:
        query = {"user_id": ObjectId(user_id)}
        total = self.collection.count_documents(query)
        skip = (page - 1) * limit
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        notifications = list(cursor)
        return notifications, total

    def count_unread(self, user_id: str) -> int:
        return self.collection.count_documents({
            "user_id": ObjectId(user_id),
            "is_read": False,
        })

    def mark_read(self, notification_id: str, user_id: str) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(notification_id), "user_id": ObjectId(user_id)},
            {"$set": {"is_read": True}},
        )
        return result.modified_count > 0

    def mark_all_read(self, user_id: str) -> int:
        result = self.collection.update_many(
            {"user_id": ObjectId(user_id), "is_read": False},
            {"$set": {"is_read": True}},
        )
        return result.modified_count

    def find_by_id(self, notification_id: str) -> dict:
        return self.collection.find_one({"_id": ObjectId(notification_id)})
