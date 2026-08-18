from datetime import datetime

from pydantic import BaseModel


class WardrobeItemOut(BaseModel):
    id: int
    image_path: str
    category: str
    primary_color: str
    secondary_colors: list[str]
    pattern: str
    description: str
    classified: bool
    upload_source: str
    created_at: datetime

    class Config:
        from_attributes = True


class WardrobeUploadResult(BaseModel):
    created: list[WardrobeItemOut]
    skipped: list[str]


class WardrobeItemUpdate(BaseModel):
    category: str | None = None
    primary_color: str | None = None
    secondary_colors: list[str] | None = None
    pattern: str | None = None
    description: str | None = None
