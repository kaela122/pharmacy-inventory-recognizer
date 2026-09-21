from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Product, Category
from app.services.product_service import to_read


class DashboardService:
    def __init__(self, db: Session): self.db = db

    def _products(self):
        return [to_read(self.db, p) for p in self.db.scalars(select(Product)).all()]

    def stats(self):
        prods = self._products()
        alerts = [p for p in prods if p["status"] != "In Stock"]
        cats = self.db.scalars(select(Category).order_by(Category.category_id)).all()
        dist = [{"label": c.name, "value": sum(1 for p in prods if p["category_id"] == c.category_id)}
                for c in cats]
        dist = [d for d in dist if d["value"] > 0]
        return {
            "total_units": sum(p["stock"] for p in prods),
            "medicine_skus": len(prods),
            "low_stock": sum(1 for p in prods if p["status"] == "Low Stock"),
            "out_of_stock": sum(1 for p in prods if p["status"] == "Out of Stock"),
            "alerts": [self._alert(p) for p in alerts],
            "category_distribution": dist,
        }

    def analytics(self):
        prods = self._products()
        cats = self.db.scalars(select(Category).order_by(Category.category_id)).all()
        by = lambda c: [p for p in prods if p["category_id"] == c.category_id]
        stock_by = [{"label": c.name, "value": sum(p["stock"] for p in by(c))} for c in cats if by(c)]
        value_by = [{"label": c.name, "value": round(sum(p["stock"]*p["price"] for p in by(c)), 2)}
                    for c in cats if by(c)]
        status = [{"label": s, "value": sum(1 for p in prods if p["status"] == s)}
                  for s in ("In Stock", "Low Stock", "Out of Stock")]
        restock = [self._alert(p) for p in prods if p["status"] != "In Stock"]
        return {"stock_by_category": stock_by, "value_by_category": value_by,
                "status_distribution": status, "restocking": restock}

    @staticmethod
    def _alert(p):
        return {"sku": p["sku"], "name": p["name"], "stock": p["stock"],
                "reorder_level": p["reorder_level"], "status": p["status"]}
