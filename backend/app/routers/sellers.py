from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.management import SellerUpdateRequest
from app.services.seller_service import SellerService
from app.core.dependencies import get_current_user, require_seller

router = APIRouter(prefix="/api/sellers", tags=["Sellers"])


@router.get("/me")
def get_my_seller_profile(current_user: dict = Depends(require_seller)):
    seller_service = SellerService()
    seller = seller_service.get_seller_profile(current_user["user_id"])
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller profile not found")
    return seller


@router.patch("/me")
def update_my_seller_profile(data: SellerUpdateRequest, current_user: dict = Depends(require_seller)):
    seller_service = SellerService()
    seller, error = seller_service.update_seller_profile(
        user_id=current_user["user_id"],
        company_name=data.company_name,
        description=data.description,
        phone=data.phone,
        address=data.address,
    )
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    return seller
