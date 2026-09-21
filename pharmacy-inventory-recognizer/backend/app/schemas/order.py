from __future__ import annotations
from datetime import date
from pydantic import BaseModel


class OrderItemRead(BaseModel):
    sku: str
    name: str
    quantity: int
    subtotal: float


class OrderRead(BaseModel):
    order_id: int
    order_number: str
    supplier_name: str
    status: str
    order_date: date
    item_count: int
    total: float
    items: list[OrderItemRead]


class OrderStats(BaseModel):
    total_orders: int
    pending: int
    fulfilled: int
    total_value: float       # excludes cancelled orders


class OrderStatusUpdate(BaseModel):
    status: str
