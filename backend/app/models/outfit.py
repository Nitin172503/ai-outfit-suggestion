from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Outfit(Base):
    __tablename__ = "outfits"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    library_id: Mapped[int | None] = mapped_column(ForeignKey("libraries.id"), nullable=True, index=True)

    name: Mapped[str] = mapped_column(String(255), default="Untitled outfit")
    occasion: Mapped[str] = mapped_column(String(100), default="")
    color_harmony: Mapped[str] = mapped_column(String(50), default="")
    rationale: Mapped[str] = mapped_column(String(2000), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner: Mapped["User"] = relationship(back_populates="outfits")
    library: Mapped["Library | None"] = relationship(back_populates="outfits")
    item_links: Mapped[list["OutfitItem"]] = relationship(back_populates="outfit", cascade="all, delete-orphan")


class OutfitItem(Base):
    __tablename__ = "outfit_items"

    outfit_id: Mapped[int] = mapped_column(ForeignKey("outfits.id"), primary_key=True)
    wardrobe_item_id: Mapped[int] = mapped_column(ForeignKey("wardrobe_items.id"), primary_key=True)

    outfit: Mapped["Outfit"] = relationship(back_populates="item_links")
    wardrobe_item: Mapped["WardrobeItem"] = relationship(back_populates="outfit_links")
