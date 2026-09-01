from pymongo.database import Database
from bson import ObjectId


class CategoryRepository:
    def __init__(self, db: Database):
        self.collection = db.categories

    def find_by_id(self, category_id: str) -> dict:
        return self.collection.find_one({"_id": ObjectId(category_id)})

    def find_by_name(self, name: str) -> dict:
        return self.collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})

    def create(self, data: dict) -> dict:
        result = self.collection.insert_one(data)
        data["_id"] = result.inserted_id
        return data

    def update(self, category_id: str, data: dict) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(category_id)},
            {"$set": data},
        )
        return result.modified_count > 0

    def delete(self, category_id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(category_id)})
        return result.deleted_count > 0

    def find_all(self, page: int = 1, limit: int = 20, active_only: bool = False) -> tuple:
        query = {}
        if active_only:
            query["is_active"] = True

        total = self.collection.count_documents(query)
        skip = (page - 1) * limit
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("name", 1)
        categories = list(cursor)
        return categories, total

    def find_active(self) -> list:
        return list(self.collection.find({"is_active": True}).sort("name", 1))

    def count_products(self, category_id: str) -> int:
        db = self.collection.database
        return db.products.count_documents({"category_id": ObjectId(category_id)})

    def name_exists(self, name: str, exclude_id: str = None) -> bool:
        query = {"name": {"$regex": f"^{name}$", "$options": "i"}}
        if exclude_id:
            query["_id"] = {"$ne": ObjectId(exclude_id)}
        return self.collection.find_one(query) is not None
