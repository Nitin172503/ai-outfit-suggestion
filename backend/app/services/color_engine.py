"""Deterministic color-theory engine: the "book of color combinations".

Classifies a set of garment colors against classic color-wheel schemes
(monochromatic, analogous, complementary, split-complementary, triadic)
and exposes a curated library of named palettes. Also does dominant-color
extraction straight from pixels (Pillow quantization, fully local, no
network calls or external models) so wardrobe photos can be auto-colored.
Used both to browse the color book directly and to score/validate the
suggestion engine's outfit groupings.
"""

import colorsys
from dataclasses import dataclass

from PIL import Image

NEUTRAL_SAT_THRESHOLD = 0.12
NEUTRAL_LOW_VALUE = 0.12
NEUTRAL_HIGH_VALUE = 0.92

SCHEMES = {
    "monochromatic": {
        "label": "Monochromatic",
        "description": "Different shades, tints, and tones of a single hue. Safe and cohesive.",
        "hue_offsets": [0],
        "tolerance": 15,
    },
    "analogous": {
        "label": "Analogous",
        "description": "Hues that sit next to each other on the color wheel (within ~60 degrees). Calm, harmonious.",
        "hue_offsets": [0, 30, 60],
        "tolerance": 25,
    },
    "complementary": {
        "label": "Complementary",
        "description": "Hues opposite each other on the wheel (180 degrees apart). High contrast, vibrant.",
        "hue_offsets": [0, 180],
        "tolerance": 20,
    },
    "split_complementary": {
        "label": "Split-complementary",
        "description": "A base hue plus the two hues adjacent to its complement. Contrast with less tension.",
        "hue_offsets": [0, 150, 210],
        "tolerance": 20,
    },
    "triadic": {
        "label": "Triadic",
        "description": "Three hues evenly spaced 120 degrees apart. Bold and balanced.",
        "hue_offsets": [0, 120, 240],
        "tolerance": 18,
    },
}

NAMED_PALETTES = [
    {"name": "Navy & Camel", "hexes": ["#1B2A4A", "#C19A6B", "#F5F0E6"], "mood": "classic, polished",
     "best_for": ["work", "smart casual"]},
    {"name": "Monochrome Black", "hexes": ["#0D0D0D", "#3A3A3A", "#8C8C8C", "#FFFFFF"], "mood": "sleek, minimal",
     "best_for": ["evening", "work", "date night"]},
    {"name": "Terracotta & Sage", "hexes": ["#C15A3C", "#8A9B6E", "#EDE3D0"], "mood": "earthy, warm",
     "best_for": ["casual", "brunch"]},
    {"name": "Burgundy & Forest", "hexes": ["#6E1F2A", "#2F4F3A", "#D8C9A3"], "mood": "rich, autumnal",
     "best_for": ["fall", "dinner"]},
    {"name": "Ocean Blues", "hexes": ["#0B3D5C", "#3E8EDE", "#BFDFF0"], "mood": "cool, calm",
     "best_for": ["summer", "casual"]},
    {"name": "Blush & Grey", "hexes": ["#E8C4C4", "#9A9A9A", "#F7F5F2"], "mood": "soft, modern",
     "best_for": ["date night", "spring"]},
    {"name": "Mustard & Denim", "hexes": ["#D9A441", "#3B5B77", "#EDEDED"], "mood": "playful, casual",
     "best_for": ["weekend", "casual"]},
    {"name": "All White", "hexes": ["#FFFFFF", "#F5F1EA", "#E3DFD6"], "mood": "crisp, clean",
     "best_for": ["summer", "resort"]},
]


@dataclass
class HueInfo:
    hex: str
    hue: float
    sat: float
    val: float
    is_neutral: bool


def hex_to_hsv(hex_str: str) -> tuple[float, float, float]:
    h = hex_str.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hue, sat, val = colorsys.rgb_to_hsv(r, g, b)
    return hue * 360, sat, val


def classify_color(hex_str: str) -> HueInfo:
    hue, sat, val = hex_to_hsv(hex_str)
    is_neutral = sat < NEUTRAL_SAT_THRESHOLD or val < NEUTRAL_LOW_VALUE or (
        val > NEUTRAL_HIGH_VALUE and sat < NEUTRAL_SAT_THRESHOLD + 0.05
    )
    return HueInfo(hex=hex_str, hue=hue, sat=sat, val=val, is_neutral=is_neutral)


def _circular_diff(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def _score_against_template(hues: list[float], offsets: list[float], tolerance: float) -> float:
    """Best-fit a set of hues against a rotated hue template; return 0..1."""
    if not hues:
        return 0.0
    best = 0.0
    for rotation in range(0, 360, 5):
        template = [(rotation + off) % 360 for off in offsets]
        total_dev = 0.0
        for hue in hues:
            nearest = min(_circular_diff(hue, t) for t in template)
            total_dev += nearest
        avg_dev = total_dev / len(hues)
        score = max(0.0, 1 - avg_dev / (tolerance * 2))
        best = max(best, score)
    return round(best, 3)


def score_combination(hexes: list[str]) -> tuple[str, float, dict[str, float]]:
    """Return (best_scheme_key, best_score, all_scheme_scores) for a list of hex colors."""
    infos = [classify_color(h) for h in hexes]
    chromatic_hues = [i.hue for i in infos if not i.is_neutral]

    if not chromatic_hues:
        return "monochromatic", 0.9, {"monochromatic": 0.9}

    if len(chromatic_hues) == 1:
        return "monochromatic", 1.0, {"monochromatic": 1.0}

    breakdown = {
        key: _score_against_template(chromatic_hues, cfg["hue_offsets"], cfg["tolerance"])
        for key, cfg in SCHEMES.items()
    }
    best_key = max(breakdown, key=breakdown.get)
    return best_key, breakdown[best_key], breakdown


def describe_combination(scheme_key: str, score: float | None = None) -> str:
    label = scheme_key.replace("_", " ")
    article = "an" if label[0] in "aeiou" else "a"
    if score is not None:
        return f"Colors form {article} {label} combination ({score * 100:.0f}% harmony match)."
    return f"Colors form {article} {label} combination."


def list_schemes() -> list[dict]:
    example_sets = {
        "monochromatic": ["#1B2A4A", "#3E5478", "#8FA3C4"],
        "analogous": ["#1B4A2A", "#1B2A4A", "#4A1B3A"],
        "complementary": ["#1B2A4A", "#4A3B1B"],
        "split_complementary": ["#1B2A4A", "#4A2E1B", "#3E1B4A"],
        "triadic": ["#4A1B1B", "#1B4A1B", "#1B1B4A"],
    }
    return [
        {
            "key": key,
            "label": cfg["label"],
            "description": cfg["description"],
            "example_hexes": example_sets[key],
        }
        for key, cfg in SCHEMES.items()
    ]


def extract_dominant_colors(image_path: str, num_colors: int = 2) -> list[str]:
    """Pull the most common colors out of an image via Pillow's own median-cut
    quantizer — pure local pixel math, no network calls, no pretrained model.
    """
    img = Image.open(image_path).convert("RGB")
    img = img.resize((120, 120))
    quantized = img.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette() or []
    counts = quantized.getcolors() or []
    counts.sort(key=lambda c: c[0], reverse=True)

    hexes = []
    for _, idx in counts:
        offset = idx * 3
        if offset + 2 >= len(palette):
            continue
        r, g, b = palette[offset], palette[offset + 1], palette[offset + 2]
        hexes.append(f"#{r:02X}{g:02X}{b:02X}")
        if len(hexes) >= num_colors:
            break
    return hexes or ["#808080"]
