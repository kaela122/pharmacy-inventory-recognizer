from __future__ import annotations
from pydantic import BaseModel


class AlertItem(BaseModel):
    sku: str
    name: str
    stock: int
    reorder_level: int
    status: str


class Slice(BaseModel):
    label: str
    value: float


class DashboardStats(BaseModel):
    total_units: int
    medicine_skus: int
    low_stock: int
    out_of_stock: int
    alerts: list[AlertItem]
    category_distribution: list[Slice]   # products per category


class Analytics(BaseModel):
    stock_by_category: list[Slice]
    value_by_category: list[Slice]
    status_distribution: list[Slice]     # In Stock / Low Stock / Out of Stock counts
    restocking: list[AlertItem]
