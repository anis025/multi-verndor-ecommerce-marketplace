from datetime import datetime, timezone

from app.db.mongodb import get_database

DEFAULT_CONFIG = {
    "site_name": "Hatify",
    "maintenance_mode": False,
    "registration_open": True,
    "commission_rate": 0.0,
    "default_page_size": 20,
    "featured_category_ids": [],
    "support_email": "",
    "currency": "USD",
}


class ConfigService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.system_config

    def get_config(self) -> dict:
        doc = self.collection.find_one({"_id": "global"}) or {}
        config = dict(DEFAULT_CONFIG)
        for key in DEFAULT_CONFIG:
            if key in doc:
                config[key] = doc[key]
        config["updated_at"] = str(doc.get("updated_at", ""))
        config["updated_by"] = doc.get("updated_by")
        return config

    def update_config(self, data: dict, updated_by) -> dict:
        update = {"updated_at": datetime.now(timezone.utc), "updated_by": updated_by}
        for key, value in data.items():
            if key in DEFAULT_CONFIG:
                update[key] = value
        self.collection.update_one({"_id": "global"}, {"$set": update}, upsert=True)
        return self.get_config()
