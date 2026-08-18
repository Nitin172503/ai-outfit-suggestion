from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="unknown")
    primary_color: Mapped[str] = mapped_column(String(20), default="")
    secondary_colors: Mapped[list] = mapped_column(JSON, default=list)
    pattern: Mapped[str] = mapped_column(String(50), default="solid")
    description: Mapped[str] = mapped_column(String(1000), default="")
    classified: Mapped[bool] = mapped_column(default=False)
    upload_source: Mapped[str] = mapped_column(String(10), default="jpg")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner: Mapped["User"] = relationship(back_populates="wardrobe_items")
    outfit_links: Mapped[list["OutfitItem"]] = relationship(back_populates="wardrobe_item", cascade="all, delete-orphan")
