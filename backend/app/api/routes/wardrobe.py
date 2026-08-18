from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.wardrobe import WardrobeItem
from app.schemas.wardrobe import WardrobeItemOut, WardrobeItemUpdate, WardrobeUploadResult
from app.services import color_engine, storage

router = APIRouter(prefix="/wardrobe", tags=["wardrobe"])


def _to_public_path(disk_path: str) -> str:
    return "/" + str(Path(disk_path)).replace("\\", "/")


def _detect_colors(item: WardrobeItem) -> None:
    try:
        hexes = color_engine.extract_dominant_colors(item.image_path, num_colors=3)
    except Exception:
        return
    if hexes:
        item.primary_color = hexes[0]
        item.secondary_colors = hexes[1:]


@router.post("/upload", response_model=WardrobeUploadResult, status_code=status.HTTP_201_CREATED)
def upload(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filename = (file.filename or "").lower()
    is_zip = filename.endswith(".zip") or file.content_type in (
        "application/zip",
        "application/x-zip-compressed",
    )

    created: list[WardrobeItem] = []
    skipped: list[str] = []

    if is_zip:
        paths, skipped = storage.save_zip_upload(current_user.id, file)
        for path in paths:
            item = WardrobeItem(user_id=current_user.id, image_path=path, upload_source="zip")
            _detect_colors(item)
            db.add(item)
            created.append(item)
    else:
        path = storage.save_jpg_upload(current_user.id, file)
        item = WardrobeItem(user_id=current_user.id, image_path=path, upload_source="jpg")
        _detect_colors(item)
        db.add(item)
        created.append(item)

    db.commit()
    for item in created:
        db.refresh(item)

    out = [WardrobeItemOut.model_validate(i) for i in created]
    for o in out:
        o.image_path = _to_public_path(o.image_path)
    return WardrobeUploadResult(created=out, skipped=skipped)


@router.get("/", response_model=list[WardrobeItemOut])
def list_items(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = (
        db.query(WardrobeItem)
        .filter(WardrobeItem.user_id == current_user.id)
        .order_by(WardrobeItem.created_at.desc())
        .all()
    )
    out = [WardrobeItemOut.model_validate(i) for i in items]
    for o in out:
        o.image_path = _to_public_path(o.image_path)
    return out


@router.patch("/{item_id}", response_model=WardrobeItemOut)
def update_item(
    item_id: int,
    payload: WardrobeItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(WardrobeItem)
        .filter(WardrobeItem.id == item_id, WardrobeItem.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Wardrobe item not found")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(item, field, value)
    if updates:
        item.classified = True  # a manual edit finalizes the classification

    db.commit()
    db.refresh(item)
    out = WardrobeItemOut.model_validate(item)
    out.image_path = _to_public_path(out.image_path)
    return out


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = (
        db.query(WardrobeItem)
        .filter(WardrobeItem.id == item_id, WardrobeItem.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Wardrobe item not found")
    Path(item.image_path).unlink(missing_ok=True)
    db.delete(item)
    db.commit()
