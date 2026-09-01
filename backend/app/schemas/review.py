from typing import Optional
from pydantic import BaseModel, Field


class ReviewCreateRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(default=None, max_length=120)
    body: Optional[str] = Field(default=None, max_length=2000)


class ReviewModerateRequest(BaseModel):
    status: str = Field(..., pattern=r"^(approved|rejected|pending)$")
