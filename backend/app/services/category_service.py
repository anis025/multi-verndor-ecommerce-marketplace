from datetime import datetime, timezone

from app.db.mongodb import get_database
from app.repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self):
        db = get_database()
        self.category_repo = CategoryRepository(db)

    def get_category(self, category_id: str) -> dict:
        category = self.category_repo.find_by_id(category_id)
        if not category:
            return None
        return self._to_response(category)

    def get_categories(self, page: int = 1, limit: int = 20, active_only: bool = False) -> dict:
        categories, total = self.category_repo.find_all(page=page, limit=limit, active_only=active_only)
        items = [self._to_response(c) for c in categories]
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        return {"items": items, "page": page, "limit": limit, "total": total, "total_pages": total_pages}

    def get_active_categories(self) -> list:
        categories = self.category_repo.find_active()
        return [self._to_response(c) for c in categories]

    def create_category(self, name: str, description: str = "", is_active: bool = True) -> tuple:
        if self.category_repo.name_exists(name):
            return None, "Category name already exists"

        now = datetime.now(timezone.utc)
        data = {
            "name": name,
            "description": description,
            "is_active": is_active,
            "created_at": now,
            "updated_at": now,
        }
        category = self.category_repo.create(data)
        return self._to_response(category), None

    def update_category(self, category_id: str, name: str = None, description: str = None,
                        is_active: bool = None) -> tuple:
        category = self.category_repo.find_by_id(category_id)
        if not category:
            return None, "Category not found"

        update_data = {"updated_at": datetime.now(timezone.utc)}
        if name is not None:
            if self.category_repo.name_exists(name, exclude_id=category_id):
                return None, "Category name already exists"
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if is_active is not None:
            update_data["is_active"] = is_active

        self.category_repo.update(category_id, update_data)
        return self.get_category(category_id), None

    def delete_category(self, category_id: str) -> tuple:
        category = self.category_repo.find_by_id(category_id)
        if not category:
            return None, "Category not found"

        product_count = self.category_repo.count_products(category_id)
        if product_count > 0:
            return None, f"Cannot delete category with {product_count} product(s). Deactivate instead."

        self.category_repo.delete(category_id)
        return True, None

    def _to_response(self, category: dict) -> dict:
        return {
            "id": str(category["_id"]),
            "name": category["name"],
            "description": category.get("description", ""),
            "is_active": category.get("is_active", True),
            "created_at": str(category.get("created_at", "")),
            "updated_at": str(category.get("updated_at", "")),
        }
