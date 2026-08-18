from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.library import Library
from app.models.outfit import Outfit
from app.models.user import User
from app.schemas.library import LibraryCreate, LibraryOut

router = APIRouter(prefix="/libraries", tags=["libraries"])


@router.post("/", response_model=LibraryOut, status_code=status.HTTP_201_CREATED)
def create_library(payload: LibraryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    library = Library(user_id=current_user.id, name=payload.name, description=payload.description)
    db.add(library)
    db.commit()
    db.refresh(library)
    out = LibraryOut.model_validate(library)
    out.outfit_count = 0
    return out


@router.get("/", response_model=list[LibraryOut])
def list_libraries(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    libraries = db.query(Library).filter(Library.user_id == current_user.id).order_by(Library.created_at.desc()).all()
    results = []
    for lib in libraries:
        count = db.query(Outfit).filter(Outfit.library_id == lib.id).count()
        out = LibraryOut.model_validate(lib)
        out.outfit_count = count
        results.append(out)
    return results


@router.delete("/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_library(library_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    library = db.query(Library).filter(Library.id == library_id, Library.user_id == current_user.id).first()
    if not library:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Library not found")
    db.query(Outfit).filter(Outfit.library_id == library.id).update({"library_id": None})
    db.delete(library)
    db.commit()
