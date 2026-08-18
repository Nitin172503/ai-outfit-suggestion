from datetime import datetime

from pydantic import BaseModel

from app.schemas.wardrobe import WardrobeItemOut


class SuggestionRequest(BaseModel):
    occasion: str = "casual"
    notes: str = ""
    item_ids: list[int] | None = None  # restrict suggestion pool; None = whole wardrobe


class SuggestedOutfit(BaseModel):
    name: str
    item_ids: list[int]
    color_harmony: str
    harmony_score: float
    rationale: str


class SuggestionResponse(BaseModel):
    suggestions: list[SuggestedOutfit]


class OutfitCreate(BaseModel):
    name: str = "Untitled outfit"
    occasion: str = ""
    item_ids: list[int]
    color_harmony: str = ""
    rationale: str = ""
    library_id: int | None = None


class OutfitOut(BaseModel):
    id: int
    name: str
    occasion: str
    color_harmony: str
    rationale: str
    library_id: int | None
    created_at: datetime
    items: list[WardrobeItemOut]

    class Config:
        from_attributes = True


class OutfitUpdate(BaseModel):
    name: str | None = None
    library_id: int | None = None
