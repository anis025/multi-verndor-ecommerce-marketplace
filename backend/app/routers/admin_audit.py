from fastapi import APIRouter, Depends, Query

from app.db.mongodb import get_database
from app.core.dependencies import require_admin

router = APIRouter(prefix="/api/admin/audit-logs", tags=["Admin Audit"])


@router.get("")
def list_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    action: str = Query(None),
    target_type: str = Query(None),
    current_user: dict = Depends(require_admin),
):
    db = get_database()
    query = {}
    if action:
        query["action"] = action
    if target_type:
        query["target_type"] = target_type

    total = db.admin_audit_log.count_documents(query)
    skip = (page - 1) * limit
    cursor = db.admin_audit_log.find(query).sort("created_at", -1).skip(skip).limit(limit)

    items = []
    for log in cursor:
        items.append({
            "id": str(log["_id"]),
            "admin_id": str(log.get("admin_id", "")),
            "action": log.get("action"),
            "target_type": log.get("target_type"),
            "target_id": str(log["target_id"]) if log.get("target_id") else None,
            "details": log.get("details", {}),
            "created_at": str(log.get("created_at", "")),
        })
    return {"items": items, "page": page, "limit": limit, "total": total}
