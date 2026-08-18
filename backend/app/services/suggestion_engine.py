"""Outfit suggestion generator — fully local, no network calls or external models.

Pairs one wardrobe item per key category (top/bottom/shoes, optionally
outerwear) and ranks every resulting combination purely by how well its
colors score against the color-theory engine in color_engine.py.
"""

import itertools

from app.services import color_engine


def _outfit_name(items: list[dict]) -> str:
    labels = [i["description"] or i["category"] for i in items]
    shown, rest = labels[:3], labels[3:]
    name = " + ".join(shown)
    if rest:
        name += f" + {len(rest)} more"
    return name or "Suggested outfit"


def generate_suggestions(wardrobe_items: list[dict], max_results: int = 4) -> list[dict]:
    by_category: dict[str, list[dict]] = {}
    for item in wardrobe_items:
        by_category.setdefault(item["category"], []).append(item)

    tops = by_category.get("top", []) + by_category.get("dress", [])
    bottoms = by_category.get("bottom", [])
    shoes = by_category.get("shoes", [])
    outerwear = by_category.get("outerwear", [None])
    if not outerwear:
        outerwear = [None]

    candidates = []
    for top in tops:
        bottom_options = bottoms if top["category"] != "dress" else [None]
        for bottom, shoe, outer in itertools.product(bottom_options, shoes or [None], outerwear):
            items = [i for i in (top, bottom, shoe, outer) if i]
            if len(items) < 2:
                continue
            hexes = [i["primary_color"] for i in items]
            scheme_key, score, _ = color_engine.score_combination(hexes)
            candidates.append(
                {
                    "name": _outfit_name(items),
                    "item_ids": [i["id"] for i in items],
                    "color_harmony": scheme_key,
                    "harmony_score": score,
                    "rationale": color_engine.describe_combination(scheme_key),
                }
            )

    candidates.sort(key=lambda c: c["harmony_score"], reverse=True)
    seen = set()
    unique = []
    for c in candidates:
        key = frozenset(c["item_ids"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(c)
    return unique[:max_results]
