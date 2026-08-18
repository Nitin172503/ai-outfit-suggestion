from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.library import Library
from app.models.outfit import Outfit, OutfitItem
from app.models.user import User
from app.models.wardrobe import WardrobeItem
from app.schemas.outfit import OutfitCreate, OutfitOut, OutfitUpdate, SuggestionRequest, SuggestionResponse
from app.schemas.wardrobe import WardrobeItemOut
from app.services import suggestion_engine

router = APIRouter(prefix="/outfits", tags=["outfits"])


def _to_public_path(disk_path: str) -> str:
    return "/" + str(Path(disk_path)).replace("\\", "/")


def _outfit_out(outfit: Outfit) -> OutfitOut:
    items = [link.wardrobe_item for link in outfit.item_links]
    item_outs = [WardrobeItemOut.model_validate(i) for i in items]
    for o in item_outs:
        o.image_path = _to_public_path(o.image_path)
    return OutfitOut(
        id=outfit.id,
        name=outfit.name,
        occasion=outfit.occasion,
        color_harmony=outfit.color_harmony,
        rationale=outfit.rationale,
        library_id=outfit.library_id,
        created_at=outfit.created_at,
        items=item_outs,
    )


@router.post("/suggest", response_model=SuggestionResponse)
def suggest(payload: SuggestionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(WardrobeItem).filter(WardrobeItem.user_id == current_user.id)
    if payload.item_ids:
        query = query.filter(WardrobeItem.id.in_(payload.item_ids))
    items = query.all()
    if len(items) < 2:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Add at least 2 wardrobe items before requesting suggestions")

    wardrobe_dicts = [
        {
            "id": i.id,
            "category": i.category,
            "primary_color": i.primary_color or "#808080",
            "description": i.description,
        }
        for i in items
    ]

    suggestions = suggestion_engine.generate_suggestions(wardrobe_dicts)
    return SuggestionResponse(suggestions=suggestions)


@router.post("/", response_model=OutfitOut, status_code=status.HTTP_201_CREATED)
def create_outfit(payload: OutfitCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = (
        db.query(WardrobeItem)
        .filter(WardrobeItem.id.in_(payload.item_ids), WardrobeItem.user_id == current_user.id)
        .all()
    )
    if len(items) != len(set(payload.item_ids)):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "One or more wardrobe items are invalid")

    if payload.library_id is not None:
        library = db.query(Library).filter(Library.id == payload.library_id, Library.user_id == current_user.id).first()
        if not library:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Library not found")

    outfit = Outfit(
        user_id=current_user.id,
        name=payload.name,
        occasion=payload.occasion,
        color_harmony=payload.color_harmony,
        rationale=payload.rationale,
        library_id=payload.library_id,
    )
    db.add(outfit)
    db.flush()
    for item in items:
        db.add(OutfitItem(outfit_id=outfit.id, wardrobe_item_id=item.id))
    db.commit()
    db.refresh(outfit)
    return _outfit_out(outfit)


@router.get("/", response_model=list[OutfitOut])
def list_outfits(
    library_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Outfit).filter(Outfit.user_id == current_user.id)
    if library_id is not None:
        query = query.filter(Outfit.library_id == library_id)
    outfits = query.order_by(Outfit.created_at.desc()).all()
    return [_outfit_out(o) for o in outfits]


@router.patch("/{outfit_id}", response_model=OutfitOut)
def update_outfit(
    outfit_id: int,
    payload: OutfitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id, Outfit.user_id == current_user.id).first()
    if not outfit:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Outfit not found")

    if payload.library_id is not None:
        library = db.query(Library).filter(Library.id == payload.library_id, Library.user_id == current_user.id).first()
        if not library:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Library not found")

    if payload.name is not None:
        outfit.name = payload.name
    if payload.library_id is not None:
        outfit.library_id = payload.library_id

    db.commit()
    db.refresh(outfit)
    return _outfit_out(outfit)


@router.delete("/{outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_outfit(outfit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id, Outfit.user_id == current_user.id).first()
    if not outfit:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Outfit not found")
    db.delete(outfit)
    db.commit()
