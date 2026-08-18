import io
import uuid
import zipfile
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image

from app.core.config import get_settings

settings = get_settings()
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def _user_dir(user_id: int) -> Path:
    d = Path(settings.storage_dir) / str(user_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _save_image_bytes(user_id: int, raw: bytes, original_name: str) -> str:
    try:
        img = Image.open(io.BytesIO(raw))
        img.verify()
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        raise HTTPException(400, f"'{original_name}' is not a valid image")

    max_dim = 1600
    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim))

    filename = f"{uuid.uuid4().hex}.jpg"
    dest = _user_dir(user_id) / filename
    img.save(dest, "JPEG", quality=88)
    return str(dest)


def save_jpg_upload(user_id: int, file: UploadFile) -> str:
    raw = file.file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(raw) > max_bytes:
        raise HTTPException(400, f"'{file.filename}' exceeds {settings.max_upload_mb}MB limit")
    return _save_image_bytes(user_id, raw, file.filename or "upload.jpg")


def save_zip_upload(user_id: int, file: UploadFile) -> tuple[list[str], list[str]]:
    raw = file.file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(raw) > max_bytes:
        raise HTTPException(400, f"Zip exceeds {settings.max_upload_mb}MB limit")

    saved: list[str] = []
    skipped: list[str] = []

    try:
        zf = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile:
        raise HTTPException(400, "Uploaded file is not a valid zip archive")

    infos = [i for i in zf.infolist() if not i.is_dir()]
    if len(infos) > settings.max_zip_entries:
        raise HTTPException(400, f"Zip has more than {settings.max_zip_entries} files")

    for info in infos:
        name = Path(info.filename).name  # strip any path components (zip-slip guard)
        ext = Path(name).suffix.lower()
        if not name or ext not in ALLOWED_EXTENSIONS:
            skipped.append(info.filename)
            continue
        if info.file_size > max_bytes:
            skipped.append(info.filename)
            continue
        try:
            raw_img = zf.read(info)
            path = _save_image_bytes(user_id, raw_img, name)
            saved.append(path)
        except HTTPException:
            skipped.append(info.filename)

    return saved, skipped
