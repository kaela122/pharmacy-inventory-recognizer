"""Products. Every SKU is validated by the DFA recognizer before saving."""
from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.automata import recognize
from app.models import Product, Inventory, Category
from app.schemas.product import ProductInput
from app.services.util import stock_status


class InvalidSKUError(ValueError): ...
class DuplicateSKUError(ValueError): ...


def to_read(db: Session, p: Product) -> dict:
    stock = p.inventory.quantity if p.inventory else 0
    cat = db.get(Category, p.category_id) if p.category_id else None
    return {"product_id": p.product_id, "sku": p.sku, "name": p.name,
            "category_id": p.category_id, "category_name": cat.name if cat else None,
            "price": float(p.price or 0), "stock": stock,
            "reorder_level": p.reorder_level, "status": stock_status(stock, p.reorder_level)}


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def list(self):
        prods = self.db.scalars(select(Product).order_by(Product.sku)).all()
        return [to_read(self.db, p) for p in prods]

    def _check(self, sku, exclude=None):
        if not recognize(sku).accepted:
            raise InvalidSKUError(f"SKU '{sku}' rejected by recognizer: {recognize(sku).reason}")
        ex = self.db.scalars(select(Product).where(Product.sku == sku)).first()
        if ex and ex.product_id != exclude:
            raise DuplicateSKUError(f"SKU '{sku}' already exists.")

    def create(self, data: ProductInput):
        data.sku = data.sku.strip().upper(); self._check(data.sku)
        p = Product(sku=data.sku, name=data.name, category_id=data.category_id,
                    price=data.price, reorder_level=data.reorder_level)
        self.db.add(p); self.db.flush()
        self.db.add(Inventory(product_id=p.product_id, quantity=data.stock))
        self.db.commit(); self.db.refresh(p)
        return to_read(self.db, p)

    def update(self, pid, data: ProductInput):
        p = self.db.get(Product, pid)
        if not p: return None
        data.sku = data.sku.strip().upper(); self._check(data.sku, exclude=pid)
        p.sku, p.name, p.category_id = data.sku, data.name, data.category_id
        p.price, p.reorder_level = data.price, data.reorder_level
        if p.inventory: p.inventory.quantity = data.stock
        else: self.db.add(Inventory(product_id=p.product_id, quantity=data.stock))
        self.db.commit(); self.db.refresh(p)
        return to_read(self.db, p)

    def delete(self, pid):
        p = self.db.get(Product, pid)
        if not p: return False
        if p.inventory: self.db.delete(p.inventory)
        self.db.delete(p); self.db.commit(); return True
