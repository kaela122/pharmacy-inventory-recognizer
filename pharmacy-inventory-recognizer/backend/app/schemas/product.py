from __future__ import annotations
from pydantic import BaseModel


class ProductInput(BaseModel):
    sku: str                 # validated by the DFA
    name: str
    category_id: int | None = None
    price: float = 0
    reorder_level: int = 0
    stock: int = 0


class ProductRead(BaseModel):
    product_id: int
    sku: str
    name: str
    category_id: int | None = None
    category_name: str | None = None
    price: float
    stock: int
    reorder_level: int
    status: str              # In Stock | Low Stock | Out of Stock
