from pymongo.database import Database
from bson import ObjectId


class ProductRepository:
    def __init__(self, db: Database):
        self.collection = db.products

    def find_by_id(self, product_id: str) -> dict:
        return self.collection.find_one({"_id": ObjectId(product_id)})

    def create(self, data: dict) -> dict:
        result = self.collection.insert_one(data)
        data["_id"] = result.inserted_id
        return data

    def update(self, product_id: str, data: dict) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": data},
        )
        return result.modified_count > 0

    def delete(self, product_id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(product_id)})
        return result.deleted_count > 0

    def find_all(self, page: int = 1, limit: int = 20, query: dict = None,
                 sort_by: str = "created_at", sort_order: int = -1) -> tuple:
        q = query or {}
        total = self.collection.count_documents(q)
        skip = (page - 1) * limit
        cursor = self.collection.find(q).skip(skip).limit(limit).sort(sort_by, sort_order)
        products = list(cursor)
        return products, total

    def find_by_seller(self, seller_id: str, page: int = 1, limit: int = 20) -> tuple:
        q = {"seller_id": ObjectId(seller_id)}
        total = self.collection.count_documents(q)
        skip = (page - 1) * limit
        cursor = self.collection.find(q).skip(skip).limit(limit).sort("created_at", -1)
        products = list(cursor)
        return products, total

    def count_by_seller(self, seller_id: str) -> int:
        return self.collection.count_documents({"seller_id": ObjectId(seller_id)})

    def count_by_category(self, category_id: str) -> int:
        return self.collection.count_documents({"category_id": ObjectId(category_id)})
