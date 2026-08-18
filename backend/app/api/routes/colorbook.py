from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.colorbook import ColorCheckRequest, ColorCheckResponse, ColorSchemeOut, NamedPaletteOut
from app.services import color_engine

router = APIRouter(prefix="/colorbook", tags=["colorbook"])


@router.get("/schemes", response_model=list[ColorSchemeOut])
def get_schemes():
    return color_engine.list_schemes()


@router.get("/palettes", response_model=list[NamedPaletteOut])
def get_palettes():
    return color_engine.NAMED_PALETTES


@router.post("/check", response_model=ColorCheckResponse)
def check_combination(payload: ColorCheckRequest, current_user: User = Depends(get_current_user)):
    if len(payload.hexes) < 2:
        return ColorCheckResponse(best_match="monochromatic", score=1.0, breakdown={"monochromatic": 1.0})
    best_key, score, breakdown = color_engine.score_combination(payload.hexes)
    return ColorCheckResponse(best_match=best_key, score=score, breakdown=breakdown)
