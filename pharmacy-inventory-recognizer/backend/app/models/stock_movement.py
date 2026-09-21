from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class StockMovement(Base):
    """One logged change to a product's stock (stock-in, stock-out, or adjustment)."""
    __tablename__ = "stock_movement"
    movement_id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.product_id"))
    movement_type: Mapped[str] = mapped_column(String(10))   # in | out | adjust
    change: Mapped[int] = mapped_column(Integer)             # + for in, - for out
    resulting_stock: Mapped[int] = mapped_column(Integer)    # stock after this change
    note: Mapped[str] = mapped_column(String(200), default="")
    employee_id: Mapped[str] = mapped_column(String(20), default="")  # who did it
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    product = relationship("Product")
