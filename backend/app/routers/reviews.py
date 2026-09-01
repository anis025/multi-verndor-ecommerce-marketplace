from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.review import ReviewCreateRequest, ReviewModerateRequest
from app.services.review_service import ReviewService
from app.core.dependencies import get_current_user, require_admin
from app.core.audit import log_admin_action
from app.utils.helpers import to_object_id


router = APIRouter(prefix="/api", tags=["Reviews"])


@router.post("/products/{product_id}/reviews", status_code=status.HTTP_201_CREATED)
def create_review(
    product_id: str,
    data: ReviewCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    to_object_id(product_id)
    if current_user.get("role") != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can review products.",
        )
    service = ReviewService()
    review, error = service.create_review(
        user_id=current_user["user_id"],
        product_id=product_id,
        rating=data.rating,
        title=data.title or "",
        body=data.body or "",
    )
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return review


@router.get("/products/{product_id}/reviews")
def list_product_reviews(
    product_id: str,
    limit: int = Query(20, ge=1, le=100),
):
    to_object_id(product_id)
    return ReviewService().list_for_product(product_id, limit=limit)


@router.get("/products/{product_id}/rating")
def get_product_rating(product_id: str):
    to_object_id(product_id)
    return ReviewService().aggregate_product_rating(product_id)


@router.post("/admin/reviews/{review_id}/moderate")
def moderate_review(
    review_id: str,
    data: ReviewModerateRequest,
    current_user: dict = Depends(require_admin),
):
    to_object_id(review_id)
    service = ReviewService()
    review, error = service.moderate(review_id, data.status)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    log_admin_action(
        current_user["user_id"],
        f"review.{data.status}",
        "review",
        target_id=review_id,
    )
    return review
