from datetime import datetime, timezone
import math
from bson import ObjectId

from app.db.mongodb import get_database
from app.repositories.order_repository import OrderRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.seller_repository import SellerRepository
from app.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService
from app.services.email_service import EmailService
from app.core.config import settings

VALID_STATUSES = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]


class OrderService:
    def __init__(self):
        db = get_database()
        self.order_repo = OrderRepository(db)
        self.cart_repo = CartRepository(db)
        self.product_repo = ProductRepository(db)
        self.seller_repo = SellerRepository(db)
        self.user_repo = UserRepository(db)

    def checkout(self, user_id: str, shipping_address: dict) -> tuple:
        cart = self.cart_repo.find_by_user(user_id)
        if not cart or not cart.get("items"):
            return None, "Cart is empty"

        raw_items = cart["items"]
        order_items = []
        total_amount = 0

        for raw in raw_items:
            product_id = str(raw["product_id"])
            quantity = raw["quantity"]

            product = self.product_repo.find_by_id(product_id)
            if not product:
                return None, f"Product {product_id} not found"

            if not product.get("is_active", True):
                return None, f"Product '{product.get('name', '')}' is no longer available"

            stock = product.get("stock", 0)
            if stock < quantity:
                return None, f"Insufficient stock for '{product.get('name', '')}' (available: {stock})"

            price = product.get("price", 0)
            subtotal = round(price * quantity, 2)
            total_amount += subtotal

            order_items.append({
                "product_id": ObjectId(product_id),
                "seller_id": product["seller_id"],
                "product_name": product.get("name", ""),
                "quantity": quantity,
                "unit_price": price,
                "subtotal": subtotal,
                "seller_status": "pending",
            })

        now = datetime.now(timezone.utc)
        order_data = {
            "customer_id": ObjectId(user_id),
            "items": order_items,
            "total_amount": round(total_amount, 2),
            "shipping_address": shipping_address,
            "status": "pending",
            "created_at": now,
            "updated_at": now,
        }

        order = self.order_repo.create(order_data)

        for raw in raw_items:
            product_id = str(raw["product_id"])
            quantity = raw["quantity"]
            product = self.product_repo.find_by_id(product_id)
            if product:
                new_stock = product.get("stock", 0) - quantity
                self.product_repo.update(product_id, {"stock": max(0, new_stock), "updated_at": now})

        self.cart_repo.delete(user_id)

        try:
            notif_service = NotificationService()
            notif_service.create_order_notifications(order)
        except Exception:
            pass

        # Send confirmation + seller emails. Never block the order on email failure.
        try:
            customer = self.user_repo.find_by_id(user_id)
            if customer and customer.get("email"):
                EmailService().send_order_confirmation_email(
                    customer["email"], self._to_response(order), customer.get("name", "Customer")
                )

            seller_map = {}
            for item in order.get("items", []):
                seller = self.seller_repo.find_by_id(str(item["seller_id"]))
                if not seller:
                    continue
                suser = self.user_repo.find_by_id(str(seller["user_id"]))
                if not suser or not suser.get("email"):
                    continue
                semail = suser["email"]
                seller_map.setdefault(semail, {"company_name": seller.get("company_name", "Seller"), "items": []})
                seller_map[semail]["items"].append(item)

            order_resp = self._to_response(order)
            for semail, data in seller_map.items():
                EmailService().send_seller_order_notification(
                    semail, data["company_name"], order_resp, data["items"]
                )
        except Exception as e:
            print(f"[email:error] order confirmation emails failed: {e}")

        return self._to_response(order), None

    def get_order(self, order_id: str, user_id: str) -> tuple:
        order = self.order_repo.find_by_id(order_id)
        if not order:
            return None, "Order not found"

        if str(order["customer_id"]) != user_id:
            return None, "Not authorized to view this order"

        return self._to_response(order), None

    def get_customer_orders(self, user_id: str, page: int = 1, limit: int = 20, status: str = None) -> dict:
        orders, total = self.order_repo.find_by_customer(user_id, page=page, limit=limit, status=status)
        items = [self._to_response(o) for o in orders]
        total_pages = math.ceil(total / limit) if limit > 0 else 1
        return {"items": items, "page": page, "limit": limit, "total": total, "total_pages": total_pages}

    def get_seller_orders(self, seller_id: str, page: int = 1, limit: int = 20, status: str = None) -> dict:
        orders, total = self.order_repo.find_by_seller(seller_id, page=page, limit=limit, status=status)
        items = [self._to_seller_response(o, seller_id) for o in orders]
        total_pages = math.ceil(total / limit) if limit > 0 else 1
        return {"items": items, "page": page, "limit": limit, "total": total, "total_pages": total_pages}

    def get_all_orders(self, page: int = 1, limit: int = 20, status: str = None) -> dict:
        orders, total = self.order_repo.find_all(page=page, limit=limit, status=status)
        items = [self._to_response(o) for o in orders]
        total_pages = math.ceil(total / limit) if limit > 0 else 1
        return {"items": items, "page": page, "limit": limit, "total": total, "total_pages": total_pages}

    def update_order_status(self, order_id: str, status: str) -> tuple:
        if status not in VALID_STATUSES:
            return None, "Invalid status"

        order = self.order_repo.find_by_id(order_id)
        if not order:
            return None, "Order not found"

        now = datetime.now(timezone.utc)
        self.order_repo.update(order_id, {"status": status, "updated_at": now})
        return self._to_response(self.order_repo.find_by_id(order_id)), None

    def cancel_order(self, order_id: str, user_id: str) -> tuple:
        order = self.order_repo.find_by_id(order_id)
        if not order:
            return None, "Order not found"
        if str(order["customer_id"]) != user_id:
            return None, "Not authorized to cancel this order"
        if order.get("status") != "pending":
            return None, "Only pending orders can be cancelled"

        now = datetime.now(timezone.utc)
        self.order_repo.update(order_id, {"status": "cancelled", "updated_at": now})
        return self._to_response(self.order_repo.find_by_id(order_id)), None

    def update_seller_item_status(self, order_id: str, product_id: str, seller_id: str, status: str) -> tuple:
        if status not in VALID_STATUSES:
            return None, "Invalid status"

        order = self.order_repo.find_by_id(order_id)
        if not order:
            return None, "Order not found"

        items = order.get("items", [])
        updated = False
        for item in items:
            if str(item["product_id"]) == product_id and str(item["seller_id"]) == seller_id:
                item["seller_status"] = status
                updated = True
                break

        if not updated:
            return None, "Order item not found"

        now = datetime.now(timezone.utc)
        self.order_repo.update(order_id, {"items": items, "updated_at": now})
        return self._to_seller_response(self.order_repo.find_by_id(order_id), seller_id), None

    def _to_response(self, order: dict) -> dict:
        items = []
        for item in order.get("items", []):
            seller = self.seller_repo.find_by_id(str(item["seller_id"]))
            seller_name = ""
            if seller:
                user = self.user_repo.find_by_id(str(seller["user_id"]))
                if user:
                    seller_name = user.get("name", "")

            items.append({
                "product_id": str(item["product_id"]),
                "seller_id": str(item["seller_id"]),
                "seller_name": seller_name,
                "product_name": item.get("product_name", ""),
                "quantity": item.get("quantity", 0),
                "unit_price": item.get("unit_price", 0),
                "subtotal": item.get("subtotal", 0),
                "seller_status": item.get("seller_status", "pending"),
            })

        return {
            "id": str(order["_id"]),
            "customer_id": str(order["customer_id"]),
            "items": items,
            "total_amount": order.get("total_amount", 0),
            "shipping_address": order.get("shipping_address", {}),
            "status": order.get("status", "pending"),
            "created_at": str(order.get("created_at", "")),
            "updated_at": str(order.get("updated_at", "")),
        }

    def _to_seller_response(self, order: dict, seller_id: str) -> dict:
        seller_items = []
        for item in order.get("items", []):
            if str(item["seller_id"]) != seller_id:
                continue

            seller = self.seller_repo.find_by_id(str(item["seller_id"]))
            seller_name = ""
            if seller:
                user = self.user_repo.find_by_id(str(seller["user_id"]))
                if user:
                    seller_name = user.get("name", "")

            seller_items.append({
                "product_id": str(item["product_id"]),
                "seller_id": str(item["seller_id"]),
                "seller_name": seller_name,
                "product_name": item.get("product_name", ""),
                "quantity": item.get("quantity", 0),
                "unit_price": item.get("unit_price", 0),
                "subtotal": item.get("subtotal", 0),
                "seller_status": item.get("seller_status", "pending"),
            })

        seller_total = sum(i["subtotal"] for i in seller_items)

        return {
            "id": str(order["_id"]),
            "customer_id": str(order["customer_id"]),
            "items": seller_items,
            "total_amount": seller_total,
            "shipping_address": order.get("shipping_address", {}),
            "status": order.get("status", "pending"),
            "created_at": str(order.get("created_at", "")),
            "updated_at": str(order.get("updated_at", "")),
        }
