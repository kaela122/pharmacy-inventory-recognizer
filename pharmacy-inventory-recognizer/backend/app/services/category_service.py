from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Category, Product
from app.schemas.category import CategoryInput
from app.services.product_service import to_read


class DuplicateCategoryError(Exception): ...
class CategoryInUseError(Exception): ...


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def list(self):
        out = []
        for c in self.db.scalars(select(Category).order_by(Category.category_id)).all():
            prods = [to_read(self.db, p) for p in c.products]
            out.append({
                "category_id": c.category_id, "name": c.name, "description": c.description,
                "sku_count": len(prods),
                "units": sum(p["stock"] for p in prods),
                "value": round(sum(p["stock"] * p["price"] for p in prods), 2),
                "alerts": sum(1 for p in prods if p["status"] != "In Stock"),
                "products": prods,
            })
        return out

    def create(self, data: CategoryInput):
        if self.db.scalars(select(Category).where(Category.name.ilike(data.name))).first():
            raise DuplicateCategoryError()
        c = Category(name=data.name, description=data.description)
        self.db.add(c); self.db.commit(); self.db.refresh(c)
        return {"category_id": c.category_id, "name": c.name, "description": c.description,
                "sku_count": 0, "units": 0, "value": 0, "alerts": 0, "products": []}

    def delete(self, cid):
        c = self.db.get(Category, cid)
        if not c: return False
        if c.products: raise CategoryInUseError()
        self.db.delete(c); self.db.commit(); return True
