from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.management import UserUpdateRequest, PasswordChangeRequest
from app.services.user_service import UserService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me")
def get_my_profile(current_user: dict = Depends(get_current_user)):
    user_service = UserService()
    user = user_service.get_user(current_user["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/me")
def update_my_profile(data: UserUpdateRequest, current_user: dict = Depends(get_current_user)):
    user_service = UserService()
    user = user_service.update_user(
        user_id=current_user["user_id"],
        name=data.name,
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/me/password")
def change_password(data: PasswordChangeRequest, current_user: dict = Depends(get_current_user)):
    user_service = UserService()
    result, error = user_service.change_password(
        user_id=current_user["user_id"],
        current_password=data.current_password,
        new_password=data.new_password,
    )
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return {"message": "Password updated successfully"}
