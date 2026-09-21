from __future__ import annotations
from sqlalchemy import String, Numeric, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Product(Base):
    __tablename__ = "product"
    product_id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(20), unique=True)   # validated by the DFA
    name: Mapped[str] = mapped_column(String(150))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("category.category_id"))
    price: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    reorder_level: Mapped[int] = mapped_column(Integer, default=0)
    category = relationship("Category", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False)
