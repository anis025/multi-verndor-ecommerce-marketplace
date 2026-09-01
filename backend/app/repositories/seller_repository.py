from pymongo.database import Database
from bson import ObjectId


class SellerRepository:
    def __init__(self, db: Database):
        self.collection = db.sellers

    def find_by_user_id(self, user_id: str) -> dict:
        return self.collection.find_one({"user_id": ObjectId(user_id)})

    def find_by_id(self, seller_id: str) -> dict:
        return self.collection.find_one({"_id": ObjectId(seller_id)})

    def create(self, data: dict) -> dict:
        result = self.collection.insert_one(data)
        data["_id"] = result.inserted_id
        return data

    def update(self, seller_id: str, data: dict) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(seller_id)},
            {"$set": data},
        )
        return result.modified_count > 0

    def find_all(self, page: int = 1, limit: int = 20, status: str = None, search: str = None) -> tuple:
        query = {}
        if status:
            query["status"] = status
        if search:
            query["company_name"] = {"$regex": search, "$options": "i"}

        total = self.collection.count_documents(query)
        skip = (page - 1) * limit
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        sellers = list(cursor)
        return sellers, total

    def count(self, query: dict = None) -> int:
        return self.collection.count_documents(query or {})
