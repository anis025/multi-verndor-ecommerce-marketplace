from datetime import datetime, timezone
from bson import ObjectId

from app.db.mongodb import get_database
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository


class CartService:
    def __init__(self):
        db = get_database()
        self.cart_repo = CartRepository(db)
        self.product_repo = ProductRepository(db)

    def get_cart(self, user_id: str) -> dict:
        cart = self.cart_repo.find_by_user(user_id)
        if not cart:
            return {"id": None, "user_id": user_id, "items": [], "total": 0, "item_count": 0}

        items = self._build_items(cart.get("items", []))
        total = sum(item["subtotal"] for item in items)

        return {
            "id": str(cart["_id"]),
            "user_id": user_id,
            "items": items,
            "total": round(total, 2),
            "item_count": sum(item["quantity"] for item in items),
        }

    def add_to_cart(self, user_id: str, product_id: str, quantity: int = 1) -> tuple:
        product = self.product_repo.find_by_id(product_id)
        if not product:
            return None, "Product not found"

        if not product.get("is_active", True):
            return None, "Product is not available"

        stock = product.get("stock", 0)
        if stock < quantity:
            return None, "Insufficient stock"

        cart = self.cart_repo.find_by_user(user_id)
        now = datetime.now(timezone.utc)

        if not cart:
            cart_data = {
                "user_id": ObjectId(user_id),
                "items": [{"product_id": ObjectId(product_id), "quantity": quantity}],
                "created_at": now,
                "updated_at": now,
            }
            self.cart_repo.create(cart_data)
        else:
            items = cart.get("items", [])

            existing_index = None
            for i, item in enumerate(items):
                if str(item["product_id"]) == product_id:
                    existing_index = i
                    break

            if existing_index is not None:
                new_qty = items[existing_index]["quantity"] + quantity
                if new_qty > stock:
                    return None, "Insufficient stock"
                items[existing_index]["quantity"] = new_qty
            else:
                items.append({"product_id": ObjectId(product_id), "quantity": quantity})

            self.cart_repo.update(user_id, {"items": items, "updated_at": now})

        return self.get_cart(user_id), None

    def update_item(self, user_id: str, product_id: str, quantity: int) -> tuple:
        cart = self.cart_repo.find_by_user(user_id)
        if not cart:
            return None, "Cart is empty"

        product = self.product_repo.find_by_id(product_id)
        if not product:
            return None, "Product not found"

        if quantity > product.get("stock", 0):
            return None, "Insufficient stock"

        items = cart.get("items", [])
        updated = False
        for item in items:
            if str(item["product_id"]) == product_id:
                item["quantity"] = quantity
                updated = True
                break

        if not updated:
            return None, "Product not in cart"

        now = datetime.now(timezone.utc)
        self.cart_repo.update(user_id, {"items": items, "updated_at": now})
        return self.get_cart(user_id), None

    def remove_from_cart(self, user_id: str, product_id: str) -> tuple:
        cart = self.cart_repo.find_by_user(user_id)
        if not cart:
            return None, "Cart is empty"

        items = cart.get("items", [])
        new_items = [item for item in items if str(item["product_id"]) != product_id]

        if len(new_items) == len(items):
            return None, "Product not in cart"

        now = datetime.now(timezone.utc)
        self.cart_repo.update(user_id, {"items": new_items, "updated_at": now})
        return self.get_cart(user_id), None

    def clear_cart(self, user_id: str) -> tuple:
        cart = self.cart_repo.find_by_user(user_id)
        if not cart:
            return None, "Cart is empty"

        now = datetime.now(timezone.utc)
        self.cart_repo.update(user_id, {"items": [], "updated_at": now})
        return self.get_cart(user_id), None

    def get_cart_items_for_order(self, user_id: str) -> tuple:
        cart = self.cart_repo.find_by_user(user_id)
        if not cart or not cart.get("items"):
            return [], "Cart is empty"
        return cart.get("items", []), None

    def clear_cart_after_order(self, user_id: str):
        self.cart_repo.delete(user_id)

    def _build_items(self, raw_items: list) -> list:
        items = []
        for raw in raw_items:
            product = self.product_repo.find_by_id(str(raw["product_id"]))
            if not product:
                continue

            seller = product.get("seller_id")
            price = product.get("price", 0)
            quantity = raw.get("quantity", 1)
            subtotal = round(price * quantity, 2)

            items.append({
                "product_id": str(product["_id"]),
                "seller_id": str(seller),
                "product_name": product.get("name", ""),
                "price": price,
                "quantity": quantity,
                "stock": product.get("stock", 0),
                "image_url": product.get("image_url", ""),
                "subtotal": subtotal,
            })
        return items
