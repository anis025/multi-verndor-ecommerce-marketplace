from pymongo.database import Database
from bson import ObjectId


class OrderRepository:
    def __init__(self, db: Database):
        self.collection = db.orders

    def create(self, data: dict) -> dict:
        result = self.collection.insert_one(data)
        data["_id"] = result.inserted_id
        return data

    def find_by_id(self, order_id: str) -> dict:
        return self.collection.find_one({"_id": ObjectId(order_id)})

    def find_by_customer(self, customer_id: str, page: int = 1, limit: int = 20, status: str = None) -> tuple:
        query = {"customer_id": ObjectId(customer_id)}
        if status:
            query["status"] = status
        total = self.collection.count_documents(query)
        skip = (page - 1) * limit
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        orders = list(cursor)
        return orders, total

    def find_by_seller(self, seller_id: str, page: int = 1, limit: int = 20, status: str = None) -> tuple:
        query = {"items.seller_id": ObjectId(seller_id)}
        if status:
            query["status"] = status
        total = self.collection.count_documents(query)
        skip = (page - 1) * limit
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        orders = list(cursor)
        return orders, total

    def find_all(self, page: int = 1, limit: int = 20, status: str = None) -> tuple:
        query = {}
        if status:
            query["status"] = status
        total = self.collection.count_documents(query)
        skip = (page - 1) * limit
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        orders = list(cursor)
        return orders, total

    def update(self, order_id: str, data: dict) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": data},
        )
        return result.modified_count > 0
