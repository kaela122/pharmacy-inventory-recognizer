from __future__ import annotations
from datetime import date
from sqlalchemy import String, Numeric, Integer, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_order"
    order_id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[str] = mapped_column(String(30), unique=True)   # ORD-2026-001
    supplier_id: Mapped[int] = mapped_column(ForeignKey("supplier.supplier_id"))
    status: Mapped[str] = mapped_column(String(20), default="Pending")   # Pending/Processing/Fulfilled/Cancelled
    order_date: Mapped[date] = mapped_column(Date)
    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    supplier = relationship("Supplier")
    items = relationship("PurchaseOrderItem", back_populates="order", cascade="all, delete-orphan")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_item"
    item_id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("purchase_order.order_id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("product.product_id"))
    quantity: Mapped[int] = mapped_column(Integer)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2))
    order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")
