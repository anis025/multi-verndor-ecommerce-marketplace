from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.services.notification_service import NotificationService
from app.core.dependencies import get_current_user
from app.utils.helpers import to_object_id

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("")
def list_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    notif_service = NotificationService()
    return notif_service.get_notifications(
        user_id=current_user["user_id"],
        page=page,
        limit=limit,
    )


@router.put("/{notification_id}/read")
def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    to_object_id(notification_id)
    notif_service = NotificationService()
    result, error = notif_service.mark_read(notification_id, current_user["user_id"])
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    return {"message": "Notification marked as read"}


@router.put("/read-all")
def mark_all_notifications_read(current_user: dict = Depends(get_current_user)):
    notif_service = NotificationService()
    result = notif_service.mark_all_read(current_user["user_id"])
    return {"message": f"Marked {result['marked']} notifications as read"}
