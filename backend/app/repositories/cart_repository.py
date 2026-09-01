from pymongo.database import Database
from bson import ObjectId


class CartRepository:
    def __init__(self, db: Database):
        self.collection = db.carts

    def find_by_user(self, user_id: str) -> dict:
        return self.collection.find_one({"user_id": ObjectId(user_id)})

    def create(self, data: dict) -> dict:
        result = self.collection.insert_one(data)
        data["_id"] = result.inserted_id
        return data

    def update(self, user_id: str, data: dict) -> bool:
        result = self.collection.update_one(
            {"user_id": ObjectId(user_id)},
            {"$set": data},
        )
        return result.modified_count > 0

    def delete(self, user_id: str) -> bool:
        result = self.collection.delete_one({"user_id": ObjectId(user_id)})
        return result.deleted_count > 0
