"""Flat-icon garment renderer used only to seed demo wardrobe photos.

Draws simple, clearly-readable clothing silhouettes (t-shirt, trousers,
dress, jacket, shoe, bag, hat) purely with Pillow primitives — no external
images, models, or network calls. Real users never hit this path; it exists
so a freshly deployed instance has something to look at immediately.
"""

from PIL import Image, ImageDraw

CANVAS = 640
BG = (244, 241, 236)


def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _shade(rgb: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)  # type: ignore[return-value]


def render_garment_icon(category: str, primary_hex: str, size: int = CANVAS) -> Image.Image:
    img = Image.new("RGB", (size, size), BG)
    draw = ImageDraw.Draw(img)
    primary = _hex_to_rgb(primary_hex)
    outline = _shade(primary, 0.55)
    shadow = _shade(BG, 0.94)
    cx, cy = size // 2, size // 2

    draw.ellipse([cx - 160, size - 170, cx + 160, size - 100], fill=shadow)

    if category == "top":
        draw.polygon(
            [
                (cx - 200, cy - 90),
                (cx - 120, cy - 160),
                (cx - 60, cy - 190),
                (cx - 40, cy - 150),
                (cx + 40, cy - 150),
                (cx + 60, cy - 190),
                (cx + 120, cy - 160),
                (cx + 200, cy - 90),
                (cx + 150, cy - 30),
                (cx + 120, cy - 60),
                (cx + 120, cy + 180),
                (cx - 120, cy + 180),
                (cx - 120, cy - 60),
                (cx - 150, cy - 30),
            ],
            fill=primary,
            outline=outline,
            width=6,
        )
        draw.ellipse([cx - 42, cy - 195, cx + 42, cy - 145], fill=BG, outline=outline, width=4)

    elif category == "bottom":
        draw.rounded_rectangle([cx - 115, cy - 180, cx + 115, cy - 120], radius=18, fill=primary, outline=outline, width=6)
        draw.rounded_rectangle([cx - 115, cy - 135, cx - 12, cy + 200], radius=22, fill=primary, outline=outline, width=6)
        draw.rounded_rectangle([cx + 12, cy - 135, cx + 115, cy + 200], radius=22, fill=primary, outline=outline, width=6)
        draw.polygon([(cx - 14, cy - 140), (cx + 14, cy - 140), (cx, cy - 95)], fill=BG)

    elif category == "dress":
        draw.polygon(
            [
                (cx - 70, cy - 190),
                (cx + 70, cy - 190),
                (cx + 60, cy - 130),
                (cx + 150, cy + 200),
                (cx - 150, cy + 200),
                (cx - 60, cy - 130),
            ],
            fill=primary,
            outline=outline,
            width=6,
        )
        draw.ellipse([cx - 40, cy - 200, cx + 40, cy - 155], fill=BG, outline=outline, width=4)

    elif category == "outerwear":
        draw.polygon(
            [
                (cx - 220, cy - 80),
                (cx - 130, cy - 170),
                (cx - 70, cy - 130),
                (cx - 20, cy - 190),
                (cx + 20, cy - 190),
                (cx + 70, cy - 130),
                (cx + 130, cy - 170),
                (cx + 220, cy - 80),
                (cx + 165, cy - 15),
                (cx + 130, cy - 50),
                (cx + 130, cy + 190),
                (cx - 130, cy + 190),
                (cx - 130, cy - 50),
                (cx - 165, cy - 15),
            ],
            fill=primary,
            outline=outline,
            width=6,
        )
        draw.line([(cx, cy - 150), (cx, cy + 185)], fill=outline, width=5)

    elif category == "shoes":
        draw.polygon(
            [
                (cx - 150, cy + 35),
                (cx - 150, cy - 5),
                (cx - 115, cy - 45),
                (cx - 55, cy - 65),
                (cx - 10, cy - 60),
                (cx + 45, cy - 45),
                (cx + 110, cy - 15),
                (cx + 150, cy + 10),
                (cx + 150, cy + 35),
            ],
            fill=primary,
            outline=outline,
            width=6,
        )
        draw.rounded_rectangle([cx - 165, cy + 28, cx + 165, cy + 68], radius=18, fill=outline)
        for lx in (-40, -5, 30):
            draw.line([(cx + lx - 12, cy - 40), (cx + lx + 16, cy - 22)], fill=BG, width=6)

    elif category == "bag":
        draw.arc([cx - 75, cy - 175, cx + 75, cy - 25], start=195, end=345, fill=outline, width=14)
        draw.rounded_rectangle([cx - 130, cy - 40, cx + 130, cy + 170], radius=24, fill=primary, outline=outline, width=6)
        draw.rounded_rectangle([cx - 40, cy - 5, cx + 40, cy + 35], radius=8, fill=outline)

    elif category == "accessory":
        draw.ellipse([cx - 170, cy + 20, cx + 170, cy + 85], fill=primary, outline=outline, width=6)
        draw.ellipse([cx - 85, cy - 110, cx + 85, cy + 45], fill=primary, outline=outline, width=6)

    else:
        draw.rounded_rectangle([cx - 140, cy - 140, cx + 140, cy + 140], radius=36, fill=primary, outline=outline, width=6)

    return img
