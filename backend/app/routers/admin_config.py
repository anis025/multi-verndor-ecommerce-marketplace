from fastapi import APIRouter, Depends

from app.schemas.management import SystemConfigUpdateRequest, SystemConfigResponse
from app.services.config_service import ConfigService
from app.core.dependencies import require_admin
from app.core.audit import log_admin_action

router = APIRouter(prefix="/api/admin/config", tags=["Admin Config"])


@router.get("", response_model=SystemConfigResponse)
def get_config(current_user: dict = Depends(require_admin)):
    return ConfigService().get_config()


@router.put("", response_model=SystemConfigResponse)
def update_config(data: SystemConfigUpdateRequest, current_user: dict = Depends(require_admin)):
    changes = data.model_dump(exclude_unset=True)
    config = ConfigService().update_config(changes, current_user["user_id"])
    log_admin_action(
        current_user["user_id"], "config.update", "system_config",
        target_id="global", details=changes,
    )
    return config
