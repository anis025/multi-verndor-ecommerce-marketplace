from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os

from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection, check_mongo_connection
from app.db.indexes import create_indexes
from app.services.email_service import validate_email_config
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.sellers import router as sellers_router
from app.routers.admin import router as admin_router
from app.routers.categories import router as categories_router
from app.routers.products import router as products_router
from app.routers.seller_products import router as seller_products_router
from app.routers.admin_categories import router as admin_categories_router
from app.routers.admin_products import router as admin_products_router
from app.routers.cart import router as cart_router
from app.routers.orders import router as orders_router
from app.routers.seller_orders import router as seller_orders_router
from app.routers.notifications import router as notifications_router
from app.routers.admin_orders import router as admin_orders_router
from app.routers.admin_dashboard import router as admin_dashboard_router
from app.routers.admin_config import router as admin_config_router
from app.routers.admin_audit import router as admin_audit_router
from app.routers.admin_auth import router as admin_auth_router
from app.routers.reviews import router as reviews_router

app = FastAPI(title=settings.APP_NAME, env=settings.APP_ENV)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:80",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(sellers_router)
app.include_router(admin_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(seller_products_router)
app.include_router(admin_categories_router)
app.include_router(admin_products_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(seller_orders_router)
app.include_router(notifications_router)
app.include_router(admin_orders_router)
app.include_router(admin_dashboard_router)
app.include_router(admin_config_router)
app.include_router(admin_audit_router)
app.include_router(admin_auth_router)
app.include_router(reviews_router)


@app.on_event("startup")
def startup_db():
    connect_to_mongo()
    create_indexes()
    validate_email_config()
    if settings.SMTP_USERNAME and settings.SMTP_PASSWORD and settings.EMAIL_FROM:
        print(f"[email:ok] SMTP configured: {settings.SMTP_HOST}:{settings.SMTP_PORT} "
              f"from {settings.EMAIL_FROM}")
    else:
        print(f"[email:warn] SMTP NOT configured (APP_ENV={settings.APP_ENV}). "
              f"Verification/notification emails will NOT be sent. "
              f"Set SMTP_USERNAME, SMTP_PASSWORD and EMAIL_FROM in backend/.env "
              f"and restart the server.")
    if settings.ADMIN_ALLOWED_EMAIL:
        print(f"[admin] login restricted to: {settings.ADMIN_ALLOWED_EMAIL}")
    else:
        print("[admin:warn] ADMIN_ALLOWED_EMAIL is empty — no one can log in as admin.")


@app.on_event("shutdown")
def shutdown_db():
    close_mongo_connection()


# Serve uploaded product images (the upload endpoint writes to backend/uploads/).
# Wrap StaticFiles with a small middleware that adds CORS headers so the
# browser can load <img src="/uploads/..."> cross-origin (frontend on :3000,
# uploads served by the API on :8000).
_upload_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads"
)
os.makedirs(_upload_dir, exist_ok=True)

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import Response


class _StaticCorsMiddleware:
    """Add permissive CORS headers to /uploads/* responses."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope.get("path", "").startswith("/uploads/"):
            origin = ""
            for k, v in scope.get("headers", []):
                if k == b"origin":
                    origin = v.decode("latin-1")
                    break
            send = self._wrap_send(send, origin)
        await self.app(scope, receive, send)

    def _wrap_send(self, send, origin):
        async def wrapped(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"access-control-allow-origin", origin.encode("latin-1") if origin else b"*"))
                headers.append((b"cross-origin-resource-policy", b"cross-origin"))
                message["headers"] = headers
            await send(message)

        return wrapped


app.mount(
    "/uploads",
    _StaticCorsMiddleware(StaticFiles(directory=_upload_dir)),
    name="uploads",
)


@app.get("/api/health")
def health_check():
    mongo_status = check_mongo_connection()
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "mongodb": mongo_status["status"],
    }
