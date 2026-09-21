from __future__ import annotations
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Inventory(Base):
    __tablename__ = "inventory"
    inventory_id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.product_id"), unique=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    product = relationship("Product", back_populates="inventory")
