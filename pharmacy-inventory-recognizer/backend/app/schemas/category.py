from __future__ import annotations
from pydantic import BaseModel
from app.schemas.product import ProductRead


class CategoryInput(BaseModel):
    name: str
    description: str = ""


class CategoryRead(BaseModel):
    category_id: int
    name: str
    description: str
    sku_count: int
    units: int
    value: float
    alerts: int              # products at/below reorder level
    products: list[ProductRead] = []
