"""Stock movements: log every stock-in / stock-out / adjustment and keep inventory in sync."""
from __future__ import annotations
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from app.models import Product, Inventory, StockMovement
from app.schemas.movement import MovementInput


class MovementError(ValueError): ...


def _read(m: StockMovement) -> dict:
    return {"movement_id": m.movement_id, "product_id": m.product_id,
            "sku": m.product.sku, "product_name": m.product.name,
            "movement_type": m.movement_type, "change": m.change,
            "resulting_stock": m.resulting_stock, "note": m.note,
            "employee_id": m.employee_id, "created_at": m.created_at}


class MovementService:
    def __init__(self, db: Session):
        self.db = db

    def record(self, product_id: int, data: MovementInput, employee_id: str):
        p = self.db.get(Product, product_id)
        if not p:
            return None
        if data.quantity < 0:
            raise MovementError("Quantity cannot be negative.")
        inv = p.inventory or Inventory(product_id=p.product_id, quantity=0)
        if not p.inventory:
            self.db.add(inv)
        current = inv.quantity
        if data.movement_type == "in":
            change = data.quantity
        elif data.movement_type == "out":
            if data.quantity > current:
                raise MovementError(f"Cannot remove {data.quantity} - only {current} in stock.")
            change = -data.quantity
        elif data.movement_type == "adjust":
            change = data.quantity - current      # set stock to the given number
        else:
            raise MovementError("Type must be 'in', 'out' or 'adjust'.")
        inv.quantity = current + change
        m = StockMovement(product_id=p.product_id, movement_type=data.movement_type,
                          change=change, resulting_stock=inv.quantity,
                          note=data.note, employee_id=employee_id)
        self.db.add(m); self.db.commit(); self.db.refresh(m)
        return _read(m)

    def for_product(self, product_id: int):
        rows = self.db.scalars(select(StockMovement).where(StockMovement.product_id == product_id)
                               .order_by(desc(StockMovement.movement_id))).all()
        return [_read(m) for m in rows]

    def recent(self, limit: int = 50):
        rows = self.db.scalars(select(StockMovement)
                               .order_by(desc(StockMovement.movement_id)).limit(limit)).all()
        return [_read(m) for m in rows]
