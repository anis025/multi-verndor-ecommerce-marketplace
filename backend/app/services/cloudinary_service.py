"""Cloudinary helper.

Wraps the Cloudinary SDK so callers (e.g. the seller image-upload route)
don't need to know about the SDK details or how credentials are read.

Credentials can be provided in two equivalent ways:
  * CLOUDINARY_URL = "cloudinary://API_KEY:API_SECRET@CLOUD_NAME"
  * CLOUDINARY_CLOUD_NAME / CLOUDINARY_API_KEY / CLOUDINARY_API_SECRET

The SDK picks up CLOUDINARY_URL automatically from the environment, so we
only need to populate os.environ when the user supplied the three separate
variables. The module is import-safe: it never raises at import time even
if credentials are missing (so the rest of the app can start); helpers
raise at call time with a clear message.
"""
from __future__ import annotations

import os
from typing import Optional

try:
    import cloudinary
    import cloudinary.uploader
    _CLOUDINARY_AVAILABLE = True
except ImportError:  # pragma: no cover - the dependency is in requirements.txt
    _CLOUDINARY_AVAILABLE = False


def _configure_from_settings() -> None:
    """Push credentials into os.environ if the user supplied the three
    separate variables instead of a single CLOUDINARY_URL. The Cloudinary
    SDK reads CLOUDINARY_URL on its own.
    """
    if os.environ.get("CLOUDINARY_URL"):
        return
    name = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
    key = os.environ.get("CLOUDINARY_API_KEY", "")
    secret = os.environ.get("CLOUDINARY_API_SECRET", "")
    if name and key and secret:
        os.environ["CLOUDINARY_URL"] = f"cloudinary://{key}:{secret}@{name}"


def is_configured() -> bool:
    """Return True if the SDK is installed and credentials are present."""
    if not _CLOUDINARY_AVAILABLE:
        return False
    _configure_from_settings()
    url = os.environ.get("CLOUDINARY_URL", "")
    return bool(url) and "@" in url


def _require_configured() -> None:
    if not _CLOUDINARY_AVAILABLE:
        raise RuntimeError(
            "cloudinary package is not installed. Add cloudinary to requirements.txt."
        )
    if not is_configured():
        raise RuntimeError(
            "Cloudinary is not configured. Set CLOUDINARY_URL "
            "(or CLOUDINARY_CLOUD_NAME / CLOUDINARY_API_KEY / CLOUDINARY_API_SECRET) "
            "in the environment / .env before uploading product images."
        )


def upload_bytes(content: bytes, *, folder: str = "hatify/products",
                 public_id: Optional[str] = None,
                 resource_type: str = "image") -> dict:
    """Upload raw image bytes to Cloudinary. Returns the SDK's result dict
    which includes 'secure_url' (https URL suitable for <img src>).
    """
    _require_configured()
    _configure_from_settings()
    kwargs = {"folder": folder, "resource_type": resource_type}
    if public_id:
        kwargs["public_id"] = public_id
    return cloudinary.uploader.upload(content, **kwargs)
