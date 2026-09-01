from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.category import CategoryCreateRequest, CategoryUpdateRequest
from app.services.category_service import CategoryService
from app.core.dependencies import require_admin
from app.utils.helpers import to_object_id

router = APIRouter(prefix="/api/admin/categories", tags=["Admin Categories"])


@router.get("")
def list_categories(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(require_admin),
):
    category_service = CategoryService()
    return category_service.get_categories(page=page, limit=limit, active_only=False)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreateRequest, current_user: dict = Depends(require_admin)):
    category_service = CategoryService()
    category, error = category_service.create_category(
        name=data.name,
        description=data.description,
        is_active=data.is_active,
    )
    if error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error)
    return category


@router.patch("/{category_id}")
def update_category(category_id: str, data: CategoryUpdateRequest, current_user: dict = Depends(require_admin)):
    to_object_id(category_id)
    category_service = CategoryService()
    category, error = category_service.update_category(
        category_id=category_id,
        name=data.name,
        description=data.description,
        is_active=data.is_active,
    )
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return category


@router.delete("/{category_id}")
def delete_category(category_id: str, current_user: dict = Depends(require_admin)):
    to_object_id(category_id)
    category_service = CategoryService()
    result, error = category_service.delete_category(category_id)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return {"message": "Category deleted successfully"}
