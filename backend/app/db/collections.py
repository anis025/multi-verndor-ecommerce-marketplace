from pymongo.database import Database


def get_users_collection(db: Database):
    return db.users


def get_sellers_collection(db: Database):
    return db.sellers


def get_categories_collection(db: Database):
    return db.categories


def get_products_collection(db: Database):
    return db.products


def get_carts_collection(db: Database):
    return db.carts


def get_orders_collection(db: Database):
    return db.orders


def get_notifications_collection(db: Database):
    return db.notifications
