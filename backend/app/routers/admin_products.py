from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.product import ProductUpdateRequest
from app.services.product_service import ProductService
from app.core.dependencies import require_admin
from app.utils.helpers import to_object_id

router = APIRouter(prefix="/api/admin/products", tags=["Admin Products"])


@router.get("")
def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    category_id: str = Query(None),
    seller_id: str = Query(None),
    is_active: bool = Query(None),
    current_user: dict = Depends(require_admin),
):
    if category_id:
        to_object_id(category_id)
    if seller_id:
        to_object_id(seller_id)

    product_service = ProductService()
    return product_service.get_all_products(
        page=page, limit=limit, search=search,
        category_id=category_id, seller_id=seller_id,
        is_active=is_active,
    )


@router.get("/{product_id}")
def get_product(product_id: str, current_user: dict = Depends(require_admin)):
    to_object_id(product_id)
    product_service = ProductService()
    product = product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.patch("/{product_id}")
def update_product(product_id: str, data: ProductUpdateRequest, current_user: dict = Depends(require_admin)):
    to_object_id(product_id)
    product_service = ProductService()
    product, error = product_service.admin_update_product(
        product_id=product_id,
        name=data.name,
        description=data.description,
        price=data.price,
        stock=data.stock,
        category_id=data.category_id,
        image_url=data.image_url,
        is_active=data.is_active,
    )
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return product


@router.delete("/{product_id}")
def delete_product(product_id: str, current_user: dict = Depends(require_admin)):
    to_object_id(product_id)
    product_service = ProductService()
    result, error = product_service.admin_delete_product(product_id)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    return {"message": "Product deleted successfully"}
