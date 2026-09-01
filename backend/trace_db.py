"""Debug: verify which DB the test process actually connects to."""
import os

# Simulate conftest import-time setup
os.environ.setdefault("DATABASE_NAME", "hatify_test")

from app.core.config import settings
settings.DATABASE_NAME = os.environ["DATABASE_NAME"]
print("settings.DATABASE_NAME =", repr(settings.DATABASE_NAME))

# Now simulate the client fixture calling connect_to_mongo()
from app.db.mongodb import connect_to_mongo, get_database, db as global_db
print("global db before:", repr(global_db))
connected = connect_to_mongo()
print("connected db name =", connected.name)
print("global db after:", repr(global_db))
print("get_database().name =", get_database().name)

# Simulate what clean_db does
print("users count in connected db:", connected.users.count_documents({}))
connected.users.delete_many({})
print("after delete_many in connected db:", connected.users.count_documents({}))
