from datetime import datetime, timezone
import math
from bson import ObjectId

from app.db.mongodb import get_database
from app.repositories.notification_repository import NotificationRepository
from app.repositories.seller_repository import SellerRepository
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService


class NotificationService:
    def __init__(self):
        db = get_database()
        self.notif_repo = NotificationRepository(db)
        self.seller_repo = SellerRepository(db)
        self.user_repo = UserRepository(db)
        self.email_service = EmailService()

    def create_notification(self, user_id: str, notif_type: str, title: str,
                            message: str, order_id: str = None) -> dict:
        now = datetime.now(timezone.utc)
        data = {
            "user_id": ObjectId(user_id),
            "type": notif_type,
            "title": title,
            "message": message,
            "order_id": ObjectId(order_id) if order_id else None,
            "is_read": False,
            "created_at": now,
        }
        return self.notif_repo.create(data)

    def get_notifications(self, user_id: str, page: int = 1, limit: int = 20) -> dict:
        notifications, total = self.notif_repo.find_by_user(user_id, page=page, limit=limit)
        items = [self._to_response(n) for n in notifications]
        unread_count = self.notif_repo.count_unread(user_id)
        total_pages = math.ceil(total / limit) if limit > 0 else 1
        return {
            "items": items,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "unread_count": unread_count,
        }

    def mark_read(self, notification_id: str, user_id: str) -> tuple:
        result = self.notif_repo.mark_read(notification_id, user_id)
        if not result:
            return None, "Notification not found"
        return True, None

    def mark_all_read(self, user_id: str) -> dict:
        count = self.notif_repo.mark_all_read(user_id)
        return {"marked": count}

    def create_order_notifications(self, order: dict):
        """Fire notifications when a customer order is placed:
         - In-app + email to EACH seller (new-order alert).
         - In-app + email confirmation to the CUSTOMER with full order
           details and the seller shop names."""
        order_id = str(order["_id"])
        customer_id = str(order["customer_id"])
        customer = self.user_repo.find_by_id(customer_id)
        customer_email = customer.get("email") if customer else None
        customer_name = customer.get("name", "Customer") if customer else "Customer"

        # group order items by seller
        sellers_map = {}
        for item in order.get("items", []):
            sid = str(item["seller_id"])
            sellers_map.setdefault(sid, []).append(item)

        # --- Seller: in-app + email ---
        for seller_id, items in sellers_map.items():
            seller = self.seller_repo.find_by_id(seller_id)
            if not seller:
                continue
            user_id = str(seller["user_id"])
            shop_name = seller.get("company_name", "Your store")
            seller_user = self.user_repo.find_by_id(user_id)
            seller_email = seller_user.get("email") if seller_user else None

            product_lines = ", ".join(
                f"{i.get('product_name', '?')} x{i.get('quantity', 0)}" for i in items
            )
            total = sum(i.get("subtotal", 0) for i in items)

            self.create_notification(
                user_id=user_id,
                notif_type="new_order",
                title="New Order Received",
                message=f"New order from {customer_name} for {product_lines}. Total: ${total:.2f}",
                order_id=order_id,
            )
            if seller_email:
                self.email_service.send_email(
                    to=seller_email,
                    subject=f"New order received - {shop_name}",
                    html=self._seller_email_html(shop_name, customer_name, order_id, items, total),
                )

        # --- Customer: in-app + email confirmation ---
        if customer_email:
            self.create_notification(
                user_id=customer_id,
                notif_type="order_confirmation",
                title="Order Confirmed",
                message=f"Your order #{order_id[-8:].upper()} has been placed. Total: ${order.get('total_amount', 0):.2f}",
                order_id=order_id,
            )
            self.email_service.send_email(
                to=customer_email,
                subject=f"Your Hatify Order Confirmation (#{order_id[-8:].upper()})",
                html=self._customer_email_html(
                    customer_name, order_id, sellers_map, order.get("total_amount", 0), order.get("created_at")
                ),
            )

    # ----------------------------- email templates -----------------------------
    def _customer_email_html(self, customer_name, order_id, sellers_map, total, created_at) -> str:
        sections = []
        for sid, items in sellers_map.items():
            seller = self.seller_repo.find_by_id(sid)
            shop = seller.get("company_name", "Store") if seller else "Store"
            rows = "".join(
                f"<tr><td style='padding:4px 8px'>{i.get('product_name', '')}</td>"
                f"<td style='padding:4px 8px'>x{i.get('quantity', 0)}</td>"
                f"<td style='padding:4px 8px'>${i.get('unit_price', 0):.2f}</td>"
                f"<td style='padding:4px 8px'>${i.get('subtotal', 0):.2f}</td></tr>"
                for i in items
            )
            sections.append(
                f"<h3 style='margin:16px 0 4px'>From {shop}</h3>"
                "<table cellpadding='6' style='border-collapse:collapse;width:100%;font-size:14px'>"
                "<thead><tr style='text-align:left;color:#6b7280'>"
                "<th>Product</th><th>Qty</th><th>Price</th><th>Subtotal</th></tr></thead>"
                f"<tbody>{rows}</tbody></table>"
            )
        date_str = str(created_at)
        return f"""
        <div style="font-family:Arial,Helvetica,sans-serif;max-width:600px;margin:auto;color:#111827">
          <h2>Thank you for your order, {customer_name}!</h2>
          <p>Order <strong>#{order_id[-8:].upper()}</strong> placed on {date_str}.</p>
          {''.join(sections)}
          <hr style="margin:20px 0;border:none;border-top:1px solid #e5e7eb"/>
          <h3>Order Total: ${total:.2f}</h3>
          <p style="color:#6b7280">We'll notify you as each seller ships your items.</p>
        </div>
        """

    def _seller_email_html(self, shop_name, customer_name, order_id, items, total) -> str:
        rows = "".join(
            f"<tr><td style='padding:4px 8px'>{i.get('product_name', '')}</td>"
            f"<td style='padding:4px 8px'>x{i.get('quantity', 0)}</td>"
            f"<td style='padding:4px 8px'>${i.get('subtotal', 0):.2f}</td></tr>"
            for i in items
        )
        return f"""
        <div style="font-family:Arial,Helvetica,sans-serif;max-width:600px;margin:auto;color:#111827">
          <h2>New order for {shop_name}</h2>
          <p>Customer: {customer_name}</p>
          <p>Order <strong>#{order_id[-8:].upper()}</strong></p>
          <table cellpadding='6' style='border-collapse:collapse;width:100%;font-size:14px'>
            <thead><tr style='text-align:left;color:#6b7280'>
            <th>Product</th><th>Qty</th><th>Subtotal</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
          <h3>Order Total: ${total:.2f}</h3>
        </div>
        """

    def _to_response(self, notif: dict) -> dict:
        return {
            "id": str(notif["_id"]),
            "user_id": str(notif["user_id"]),
            "type": notif.get("type", ""),
            "title": notif.get("title", ""),
            "message": notif.get("message", ""),
            "order_id": str(notif["order_id"]) if notif.get("order_id") else None,
            "is_read": notif.get("is_read", False),
            "created_at": str(notif.get("created_at", "")),
        }
