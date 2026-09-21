from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class MovementInput(BaseModel):
    movement_type: str          # in | out | adjust
    quantity: int               # always positive; direction comes from movement_type
    note: str = ""


class MovementRead(BaseModel):
    movement_id: int
    product_id: int
    sku: str
    product_name: str
    movement_type: str
    change: int
    resulting_stock: int
    note: str
    employee_id: str
    created_at: datetime
