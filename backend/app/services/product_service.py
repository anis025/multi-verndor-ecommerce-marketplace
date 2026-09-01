from datetime import datetime, timezone
import math
from bson import ObjectId

from app.db.mongodb import get_database
from app.repositories.product_repository import ProductRepository
from app.repositories.seller_repository import SellerRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.user_repository import UserRepository


class ProductService:
    def __init__(self):
        db = get_database()
        self.db = db
        self.product_repo = ProductRepository(db)
        self.seller_repo = SellerRepository(db)
        self.category_repo = CategoryRepository(db)
        self.user_repo = UserRepository(db)

    def get_product(self, product_id: str) -> dict:
        product = self.product_repo.find_by_id(product_id)
        if not product:
            return None
        return self._to_response(product)

    def get_products(self, page: int = 1, limit: int = 20, search: str = None,
                     category_id: str = None, min_price: float = None,
                     max_price: float = None, sort: str = "newest") -> dict:
        query = {"is_active": True}

        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
            ]

        if category_id:
            query["category_id"] = ObjectId(category_id)

        if min_price is not None:
            query["price"] = query.get("price", {})
            query["price"]["$gte"] = min_price

        if max_price is not None:
            query["price"] = query.get("price", {})
            query["price"]["$lte"] = max_price

        sort_field = "created_at"
        sort_order = -1
        if sort == "price_asc":
            sort_field = "price"
            sort_order = 1
        elif sort == "price_desc":
            sort_field = "price"
            sort_order = -1
        elif sort == "newest":
            sort_field = "created_at"
            sort_order = -1

        products, total = self.product_repo.find_all(
            page=page, limit=limit, query=query,
            sort_by=sort_field, sort_order=sort_order,
        )
        items = [self._to_response(p) for p in products]
        total_pages = math.ceil(total / limit) if limit > 0 else 1
        return {"items": items, "page": page, "limit": limit, "total": total, "total_pages": total_pages}

    def get_all_products(self, page: int = 1, limit: int = 20, search: str = None,
                         category_id: str = None, seller_id: str = None,
                         is_active: bool = None) -> dict:
        query = {}
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
            ]
        if category_id:
            query["category_id"] = ObjectId(category_id)
        if seller_id:
            query["seller_id"] = ObjectId(seller_id)
        if is_active is not None:
            query["is_active"] = is_active

        products, total = self.product_repo.find_all(page=page, limit=limit, query=query)
        items = [self._to_response(p) for p in products]
        total_pages = math.ceil(total / limit) if limit > 0 else 1
        return {"items": items, "page": page, "limit": limit, "total": total, "total_pages": total_pages}

    def get_seller_products(self, seller_id: str, page: int = 1, limit: int = 20) -> dict:
        products, total = self.product_repo.find_by_seller(seller_id, page=page, limit=limit)
        items = [self._to_response(p) for p in products]
        total_pages = math.ceil(total / limit) if limit > 0 else 1
        return {"items": items, "page": page, "limit": limit, "total": total, "total_pages": total_pages}

    def create_product(self, seller_id: str, name: str, description: str, price: float,
                       stock: int, category_id: str, image_url: str = "",
                       is_active: bool = True) -> tuple:
        seller = self.seller_repo.find_by_id(seller_id)
        if not seller:
            return None, "Seller not found"

        if not seller.get("is_approved", False):
            return None, "Seller is not approved"

        category = self.category_repo.find_by_id(category_id)
        if not category:
            return None, "Category not found"

        if not category.get("is_active", True):
            return None, "Category is not active"

        now = datetime.now(timezone.utc)
        data = {
            "seller_id": ObjectId(seller_id),
            "category_id": ObjectId(category_id),
            "name": name,
            "description": description,
            "price": price,
            "stock": stock,
            "image_url": image_url,
            "is_active": is_active,
            "created_at": now,
            "updated_at": now,
        }
        product = self.product_repo.create(data)
        return self._to_response(product), None

    def update_product(self, product_id: str, seller_id: str, **kwargs) -> tuple:
        product = self.product_repo.find_by_id(product_id)
        if not product:
            return None, "Product not found"

        if str(product["seller_id"]) != seller_id:
            return None, "Not authorized to update this product"

        if "category_id" in kwargs and kwargs["category_id"] is not None:
            category = self.category_repo.find_by_id(kwargs["category_id"])
            if not category:
                return None, "Category not found"
            if not category.get("is_active", True):
                return None, "Category is not active"

        update_data = {"updated_at": datetime.now(timezone.utc)}
        for key in ["name", "description", "price", "stock", "image_url", "is_active"]:
            if key in kwargs and kwargs[key] is not None:
                if key == "category_id":
                    update_data["category_id"] = ObjectId(kwargs[key])
                else:
                    update_data[key] = kwargs[key]

        self.product_repo.update(product_id, update_data)
        return self.get_product(product_id), None

    def delete_product(self, product_id: str, seller_id: str) -> tuple:
        product = self.product_repo.find_by_id(product_id)
        if not product:
            return None, "Product not found"

        if str(product["seller_id"]) != seller_id:
            return None, "Not authorized to delete this product"

        self.product_repo.delete(product_id)
        return True, None

    def admin_update_product(self, product_id: str, **kwargs) -> tuple:
        product = self.product_repo.find_by_id(product_id)
        if not product:
            return None, "Product not found"

        update_data = {"updated_at": datetime.now(timezone.utc)}
        for key in ["name", "description", "price", "stock", "image_url", "is_active"]:
            if key in kwargs and kwargs[key] is not None:
                update_data[key] = kwargs[key]
        if "category_id" in kwargs and kwargs["category_id"] is not None:
            update_data["category_id"] = ObjectId(kwargs["category_id"])

        self.product_repo.update(product_id, update_data)
        return self.get_product(product_id), None

    def admin_delete_product(self, product_id: str) -> tuple:
        product = self.product_repo.find_by_id(product_id)
        if not product:
            return None, "Product not found"

        self.product_repo.delete(product_id)
        return True, None

    def _to_response(self, product: dict) -> dict:
        from app.repositories.review_repository import ReviewRepository

        seller = self.seller_repo.find_by_id(str(product["seller_id"]))
        category = self.category_repo.find_by_id(str(product["category_id"]))

        seller_name = ""
        company_name = ""
        if seller:
            user = self.user_repo.find_by_id(str(seller["user_id"]))
            if user:
                seller_name = user["name"]
            company_name = seller.get("company_name", "")

        category_name = category["name"] if category else ""

        rating = ReviewRepository(self.db).aggregate_product_rating(str(product["_id"]))

        return {
            "id": str(product["_id"]),
            "seller_id": str(product["seller_id"]),
            "category_id": str(product["category_id"]),
            "name": product["name"],
            "description": product.get("description", ""),
            "price": product["price"],
            "stock": product["stock"],
            "image_url": product.get("image_url", ""),
            "is_active": product.get("is_active", True),
            "seller_name": seller_name,
            "company_name": company_name,
            "category_name": category_name,
            "avg_rating": rating["avg_rating"],
            "review_count": rating["review_count"],
            "created_at": str(product.get("created_at", "")),
            "updated_at": str(product.get("updated_at", "")),
        }
