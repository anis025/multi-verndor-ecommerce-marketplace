from pymongo import MongoClient
from pymongo.database import Database
from app.core.config import settings

client: MongoClient = None
db: Database = None


def connect_to_mongo() -> Database:
    global client, db
    client = MongoClient(settings.MONGODB_URL, tz_aware=True)
    db = client[settings.DATABASE_NAME]
    client.admin.command("ping")
    return db


def close_mongo_connection():
    global client
    if client:
        client.close()


def get_database() -> Database:
    global db
    if db is None:
        connect_to_mongo()
    return db


def check_mongo_connection() -> dict:
    try:
        client.admin.command("ping")
        return {"status": "connected", "database": settings.DATABASE_NAME}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}
