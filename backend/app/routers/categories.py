from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.category import CategoryCreateRequest
from app.services.category_service import CategoryService
from app.core.dependencies import get_current_user
from app.utils.helpers import to_object_id

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("")
def list_categories(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    category_service = CategoryService()
    return category_service.get_categories(page=page, limit=limit, active_only=False)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreateRequest, current_user: dict = Depends(get_current_user)):
    category_service = CategoryService()
    category, error = category_service.create_category(
        name=data.name,
        description=data.description,
        is_active=data.is_active,
    )
    if error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error)
    return category


@router.get("/active")
def list_active_categories():
    category_service = CategoryService()
    return {"items": category_service.get_active_categories()}


@router.get("/{category_id}")
def get_category(category_id: str):
    to_object_id(category_id)
    category_service = CategoryService()
    category = category_service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category
