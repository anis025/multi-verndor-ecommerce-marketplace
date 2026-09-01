from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from typing import Optional

from app.schemas.product import ProductCreateRequest, ProductUpdateRequest
from app.services.product_service import ProductService
from app.services.seller_service import SellerService
from app.core.dependencies import get_current_user, require_seller
from app.utils.helpers import to_object_id

router = APIRouter(prefix="/api/sellers/me/products", tags=["Seller Products"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


@router.get("")
def list_my_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(require_seller),
):
    seller_service = SellerService()
    seller = seller_service.get_seller_profile(current_user["user_id"])
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller profile not found")

    product_service = ProductService()
    return product_service.get_seller_products(seller["id"], page=page, limit=limit)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreateRequest, current_user: dict = Depends(require_seller)):
    seller_service = SellerService()
    seller = seller_service.get_seller_profile(current_user["user_id"])
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller profile not found")

    if not seller.get("is_approved", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Seller is not approved")

    product_service = ProductService()
    product, error = product_service.create_product(
        seller_id=seller["id"],
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


@router.patch("/{product_id}")
def update_product(product_id: str, data: ProductUpdateRequest, current_user: dict = Depends(require_seller)):
    to_object_id(product_id)

    seller_service = SellerService()
    seller = seller_service.get_seller_profile(current_user["user_id"])
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller profile not found")

    product_service = ProductService()
    product, error = product_service.update_product(
        product_id=product_id,
        seller_id=seller["id"],
        name=data.name,
        description=data.description,
        price=data.price,
        stock=data.stock,
        category_id=data.category_id,
        image_url=data.image_url,
        is_active=data.is_active,
    )
    if error:
        status_code = status.HTTP_403_FORBIDDEN if "Not authorized" in error else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error)
    return product


@router.delete("/{product_id}")
def delete_product(product_id: str, current_user: dict = Depends(require_seller)):
    to_object_id(product_id)

    seller_service = SellerService()
    seller = seller_service.get_seller_profile(current_user["user_id"])
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller profile not found")

    product_service = ProductService()
    result, error = product_service.delete_product(product_id, seller["id"])
    if error:
        status_code = status.HTTP_403_FORBIDDEN if "Not authorized" in error else status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=status_code, detail=error)
    return {"message": "Product deleted successfully"}


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...), current_user: dict = Depends(require_seller)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}",
        )

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_IMAGE_SIZE // (1024*1024)}MB",
        )

    import os
    import uuid
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    return {"image_url": f"/uploads/{filename}", "filename": filename}
