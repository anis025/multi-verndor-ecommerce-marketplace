from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.services.order_service import OrderService
from app.services.seller_service import SellerService
from app.core.dependencies import require_seller
from app.utils.helpers import to_object_id

router = APIRouter(prefix="/api/seller/orders", tags=["Seller Orders"])


def _get_seller_id(current_user: dict) -> str:
    seller_service = SellerService()
    seller = seller_service.get_seller_profile(current_user["user_id"])
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller profile not found")
    return seller["id"]


@router.get("")
def list_seller_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(require_seller),
):
    seller_id = _get_seller_id(current_user)
    order_service = OrderService()
    return order_service.get_seller_orders(seller_id=seller_id, page=page, limit=limit)


@router.get("/{order_id}")
def get_seller_order(order_id: str, current_user: dict = Depends(require_seller)):
    to_object_id(order_id)
    seller_id = _get_seller_id(current_user)
    order_service = OrderService()

    order = order_service.order_repo.find_by_id(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    has_seller_item = any(str(item["seller_id"]) == seller_id for item in order.get("items", []))
    if not has_seller_item:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this order")

    return order_service._to_seller_response(order, seller_id)


@router.put("/{order_id}/items/{product_id}/status")
def update_order_item_status(
    order_id: str,
    product_id: str,
    body: dict,
    current_user: dict = Depends(require_seller),
):
    to_object_id(order_id)
    to_object_id(product_id)
    seller_id = _get_seller_id(current_user)

    new_status = body.get("status")
    if not new_status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status is required")

    order_service = OrderService()
    order, error = order_service.update_seller_item_status(order_id, product_id, seller_id, new_status)
    if error:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in error.lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error)
    return order
