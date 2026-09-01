from fastapi import APIRouter, Depends

from app.db.mongodb import get_database
from app.core.dependencies import require_admin

router = APIRouter(prefix="/api/admin/dashboard", tags=["Admin Dashboard"])


@router.get("")
def get_dashboard_stats(current_user: dict = Depends(require_admin)):
    db = get_database()

    total_users = db.users.count_documents({"role": "customer"})
    total_sellers = db.sellers.count_documents({})
    pending_sellers = db.sellers.count_documents({"status": "pending"})
    total_products = db.products.count_documents({})
    active_products = db.products.count_documents({"is_active": True})
    total_orders = db.orders.count_documents({})

    pipeline = [{"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}]
    result = list(db.orders.aggregate(pipeline))
    total_revenue = result[0]["total"] if result else 0

    return {
        "total_users": total_users,
        "total_sellers": total_sellers,
        "pending_sellers": pending_sellers,
        "total_products": total_products,
        "active_products": active_products,
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
    }
