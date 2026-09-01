from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.cart import AddToCartRequest, UpdateCartItemRequest
from app.services.cart_service import CartService
from app.core.dependencies import require_customer
from app.utils.helpers import to_object_id

router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.get("")
def get_cart(current_user: dict = Depends(require_customer)):
    cart_service = CartService()
    return cart_service.get_cart(current_user["user_id"])


@router.post("/items", status_code=status.HTTP_200_OK)
def add_to_cart(data: AddToCartRequest, current_user: dict = Depends(require_customer)):
    to_object_id(data.product_id)

    cart_service = CartService()
    cart, error = cart_service.add_to_cart(
        user_id=current_user["user_id"],
        product_id=data.product_id,
        quantity=data.quantity,
    )
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return cart


@router.put("/items/{product_id}")
def update_cart_item(product_id: str, data: UpdateCartItemRequest, current_user: dict = Depends(require_customer)):
    to_object_id(product_id)

    cart_service = CartService()
    cart, error = cart_service.update_item(
        user_id=current_user["user_id"],
        product_id=product_id,
        quantity=data.quantity,
    )
    if error:
        status_code = status.HTTP_404_NOT_FOUND if "not in cart" in error or "empty" in error else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error)
    return cart


@router.delete("/items/{product_id}")
def remove_from_cart(product_id: str, current_user: dict = Depends(require_customer)):
    to_object_id(product_id)

    cart_service = CartService()
    cart, error = cart_service.remove_from_cart(
        user_id=current_user["user_id"],
        product_id=product_id,
    )
    if error:
        status_code = status.HTTP_404_NOT_FOUND if "not in cart" in error or "empty" in error else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error)
    return cart


@router.delete("")
def clear_cart(current_user: dict = Depends(require_customer)):
    cart_service = CartService()
    cart, error = cart_service.clear_cart(current_user["user_id"])
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    return cart
