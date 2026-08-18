from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    wardrobe_items: Mapped[list["WardrobeItem"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    outfits: Mapped[list["Outfit"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    libraries: Mapped[list["Library"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
