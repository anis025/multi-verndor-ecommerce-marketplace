from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.services.order_service import OrderService
from app.core.dependencies import require_admin
from app.utils.helpers import to_object_id

router = APIRouter(prefix="/api/admin/orders", tags=["Admin Orders"])


@router.get("")
def list_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(require_admin),
):
    order_service = OrderService()
    return order_service.get_all_orders(page=page, limit=limit)


@router.get("/{order_id}")
def get_order(order_id: str, current_user: dict = Depends(require_admin)):
    to_object_id(order_id)
    order_service = OrderService()
    order = order_service.order_repo.find_by_id(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order_service._to_response(order)


@router.put("/{order_id}/status")
def update_order_status(order_id: str, body: dict, current_user: dict = Depends(require_admin)):
    to_object_id(order_id)
    new_status = body.get("status")
    if not new_status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status is required")

    order_service = OrderService()
    order, error = order_service.update_order_status(order_id, new_status)
    if error:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in error.lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error)
    return order
