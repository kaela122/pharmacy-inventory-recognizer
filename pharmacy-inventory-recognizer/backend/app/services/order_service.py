from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import PurchaseOrder, Inventory, StockMovement

# allowed forward moves for each current status (terminal states have none)
NEXT_STATUS = {
    "Pending": {"Processing", "Cancelled"},
    "Processing": {"Fulfilled", "Cancelled"},
}


class OrderStatusError(ValueError): ...


class OrderService:
    def __init__(self, db: Session): self.db = db

    def _read(self, o: PurchaseOrder) -> dict:
        items = [{"sku": i.product.sku, "name": i.product.name,
                  "quantity": i.quantity, "subtotal": float(i.subtotal)} for i in o.items]
        return {"order_id": o.order_id, "order_number": o.order_number,
                "supplier_name": o.supplier.name, "status": o.status,
                "order_date": o.order_date, "item_count": len(items),
                "total": float(o.total), "items": items}

    def list(self):
        orders = self.db.scalars(select(PurchaseOrder).order_by(PurchaseOrder.order_number)).all()
        return [self._read(o) for o in orders]

    def stats(self):
        orders = self.db.scalars(select(PurchaseOrder)).all()
        return {"total_orders": len(orders),
                "pending": sum(1 for o in orders if o.status == "Pending"),
                "fulfilled": sum(1 for o in orders if o.status == "Fulfilled"),
                "total_value": float(sum(o.total for o in orders if o.status != "Cancelled"))}

    def set_status(self, order_id: int, new_status: str, employee_id: str):
        o = self.db.get(PurchaseOrder, order_id)
        if not o:
            return None
        allowed = NEXT_STATUS.get(o.status, set())
        if new_status not in allowed:
            raise OrderStatusError(f"Can't move an order from {o.status} to {new_status}.")
        if new_status == "Fulfilled":
            # stock has arrived - add each item's quantity into inventory and log it
            for item in o.items:
                p = item.product
                inv = p.inventory or Inventory(product_id=p.product_id, quantity=0)
                if not p.inventory:
                    self.db.add(inv)
                inv.quantity = inv.quantity + item.quantity
                self.db.add(StockMovement(product_id=p.product_id, movement_type="in",
                                          change=item.quantity, resulting_stock=inv.quantity,
                                          note=f"Received - {o.order_number}", employee_id=employee_id))
        o.status = new_status
        self.db.commit()
        self.db.refresh(o)
        return self._read(o)
