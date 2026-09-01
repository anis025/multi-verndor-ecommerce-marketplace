from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.order import CreateOrderRequest
from app.services.order_service import OrderService
from app.core.dependencies import require_customer
from app.utils.helpers import to_object_id

router = APIRouter(prefix="/api/orders", tags=["Customer Orders"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_order(data: CreateOrderRequest, current_user: dict = Depends(require_customer)):
    order_service = OrderService()
    order, error = order_service.checkout(
        user_id=current_user["user_id"],
        shipping_address=data.shipping_address.model_dump(),
    )
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return order


@router.get("")
def list_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    current_user: dict = Depends(require_customer),
):
    order_service = OrderService()
    return order_service.get_customer_orders(
        user_id=current_user["user_id"],
        page=page,
        limit=limit,
        status=status_filter,
    )


@router.get("/{order_id}")
def get_order(order_id: str, current_user: dict = Depends(require_customer)):
    to_object_id(order_id)
    order_service = OrderService()
    order, error = order_service.get_order(order_id, current_user["user_id"])
    if error:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in error.lower() else status.HTTP_403_FORBIDDEN
        raise HTTPException(status_code=status_code, detail=error)
    return order


@router.patch("/{order_id}/cancel")
def cancel_order(order_id: str, current_user: dict = Depends(require_customer)):
    to_object_id(order_id)
    order_service = OrderService()
    order, error = order_service.cancel_order(order_id, current_user["user_id"])
    if error:
        code = status.HTTP_404_NOT_FOUND if "not found" in error.lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=error)
    return order
