from datetime import datetime, timezone

from app.db.mongodb import get_database


def log_admin_action(admin_id, action, target_type, target_id=None, details=None):
    """Append-only record of an administrative action. Best-effort; never raises."""
    try:
        db = get_database()
        db.admin_audit_log.insert_one({
            "admin_id": admin_id,
            "action": action,
            "target_type": target_type,
            "target_id": target_id,
            "details": details or {},
            "created_at": datetime.now(timezone.utc),
        })
    except Exception:
        pass
