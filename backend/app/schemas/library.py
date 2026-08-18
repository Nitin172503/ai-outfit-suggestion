from datetime import datetime

from pydantic import BaseModel, Field


class LibraryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ""


class LibraryOut(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    outfit_count: int = 0

    class Config:
        from_attributes = True
