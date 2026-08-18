"""Seed a demo account with a sample wardrobe and a couple of saved outfits.

Run once after migrations (locally or in deployment):

    python seed_demo.py

Safe to re-run — it wipes and recreates the demo user's data each time so
deploys stay in sync with this file. Demo garment photos are generated
locally via app.services.placeholder_art (flat icon silhouettes), never
downloaded from anywhere.
"""

from pathlib import Path

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.library import Library
from app.models.outfit import Outfit, OutfitItem
from app.models.user import User
from app.models.wardrobe import WardrobeItem
from app.services import color_engine, placeholder_art

DEMO_EMAIL = "demo@outfitai.app"
DEMO_PASSWORD = "OutfitDemo123!"
DEMO_NAME = "Demo User"

WARDROBE_SEED = [
    ("top", "Navy crewneck tee", "#1B2A4A"),
    ("top", "White oxford shirt", "#F2EFE9"),
    ("top", "Charcoal knit sweater", "#3A3A3A"),
    ("bottom", "Camel chinos", "#C19A6B"),
    ("bottom", "Indigo denim jeans", "#3B5B77"),
    ("bottom", "Black tailored trousers", "#202020"),
    ("dress", "Burgundy wrap dress", "#6E1F2A"),
    ("outerwear", "Forest green field jacket", "#2F4F3A"),
    ("outerwear", "Camel wool coat", "#B08D57"),
    ("shoes", "White leather sneakers", "#F0F0EC"),
    ("shoes", "Black leather derbies", "#141414"),
    ("bag", "Sage canvas tote", "#8A9B6E"),
    ("accessory", "Mustard wool beanie", "#D9A441"),
]

OUTFIT_SEED = [
    ("Office Ready", "work", ["White oxford shirt", "Black tailored trousers", "Black leather derbies"], "Work Capsule"),
    ("Weekend Errand", "casual", ["Navy crewneck tee", "Indigo denim jeans", "White leather sneakers"], "Weekend Casual"),
    (
        "Layered Chill",
        "casual",
        ["Charcoal knit sweater", "Camel chinos", "White leather sneakers", "Camel wool coat"],
        "Weekend Casual",
    ),
]


def main():
    settings = get_settings()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        existing = db.query(User).filter(User.email == DEMO_EMAIL).first()
        if existing:
            print(f"Removing existing demo user #{existing.id} to reseed…")
            db.delete(existing)
            db.commit()

        user = User(email=DEMO_EMAIL, hashed_password=hash_password(DEMO_PASSWORD), full_name=DEMO_NAME)
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created demo user #{user.id} ({DEMO_EMAIL})")

        user_dir = Path(settings.storage_dir) / str(user.id)
        user_dir.mkdir(parents=True, exist_ok=True)

        items_by_desc: dict[str, WardrobeItem] = {}
        for category, description, hexcolor in WARDROBE_SEED:
            icon = placeholder_art.render_garment_icon(category, hexcolor)
            filename = f"{description.lower().replace(' ', '_')}.jpg"
            dest = user_dir / filename
            icon.convert("RGB").save(dest, "JPEG", quality=90)

            item = WardrobeItem(
                user_id=user.id,
                image_path=str(dest),
                category=category,
                primary_color=hexcolor,
                secondary_colors=[],
                pattern="solid",
                description=description,
                classified=True,
                upload_source="jpg",
            )
            db.add(item)
            items_by_desc[description] = item
        db.commit()
        for item in items_by_desc.values():
            db.refresh(item)
        print(f"Seeded {len(items_by_desc)} wardrobe items")

        libraries_by_name: dict[str, Library] = {}
        for _, _, _, lib_name in OUTFIT_SEED:
            if lib_name in libraries_by_name:
                continue
            lib = Library(user_id=user.id, name=lib_name, description="")
            db.add(lib)
            libraries_by_name[lib_name] = lib
        db.commit()
        for lib in libraries_by_name.values():
            db.refresh(lib)
        print(f"Seeded {len(libraries_by_name)} libraries")

        for name, occasion, item_descs, lib_name in OUTFIT_SEED:
            outfit_items = [items_by_desc[d] for d in item_descs]
            hexes = [i.primary_color for i in outfit_items]
            scheme_key, score, _ = color_engine.score_combination(hexes)
            outfit = Outfit(
                user_id=user.id,
                name=name,
                occasion=occasion,
                color_harmony=scheme_key,
                rationale=color_engine.describe_combination(scheme_key, score),
                library_id=libraries_by_name[lib_name].id,
            )
            db.add(outfit)
            db.flush()
            for item in outfit_items:
                db.add(OutfitItem(outfit_id=outfit.id, wardrobe_item_id=item.id))
        db.commit()
        print(f"Seeded {len(OUTFIT_SEED)} saved outfits")

        print("\nDemo login:")
        print(f"  email:    {DEMO_EMAIL}")
        print(f"  password: {DEMO_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
