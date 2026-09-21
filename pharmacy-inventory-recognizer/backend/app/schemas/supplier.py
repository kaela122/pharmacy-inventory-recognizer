from __future__ import annotations
from pydantic import BaseModel, ConfigDict


class SupplierInput(BaseModel):
    name: str
    contact_person: str = ""
    phone: str = ""
    email: str = ""


class SupplierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    supplier_id: int
    name: str
    contact_person: str = ""
    phone: str = ""
    email: str = ""
    order_count: int = 0
