from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.services.product_service import ProductService
from app.core.dependencies import get_current_user
from app.utils.helpers import to_object_id

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("")
def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    category_id: str = Query(None),
    min_price: float = Query(None, ge=0),
    max_price: float = Query(None, ge=0),
    sort: str = Query("newest"),
):
    to_object_id(category_id) if category_id else None
    product_service = ProductService()
    return product_service.get_products(
        page=page, limit=limit, search=search,
        category_id=category_id, min_price=min_price,
        max_price=max_price, sort=sort,
    )


@router.get("/{product_id}")
def get_product(product_id: str):
    to_object_id(product_id)
    product_service = ProductService()
    product = product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product
