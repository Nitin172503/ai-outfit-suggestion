from pydantic import BaseModel


class ColorSchemeOut(BaseModel):
    key: str
    label: str
    description: str
    example_hexes: list[str]


class NamedPaletteOut(BaseModel):
    name: str
    hexes: list[str]
    mood: str
    best_for: list[str]


class ColorCheckRequest(BaseModel):
    hexes: list[str]


class ColorCheckResponse(BaseModel):
    best_match: str
    score: float
    breakdown: dict[str, float]
