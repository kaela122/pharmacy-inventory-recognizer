from __future__ import annotations
from pydantic import BaseModel


class UserInput(BaseModel):
    employee_id: str
    full_name: str
    role: str                   # admin | inventory_manager | pharmacist
    password: str = ""          # required on create; optional on edit (blank = keep)


class UserRead(BaseModel):
    user_id: int
    employee_id: str
    full_name: str
    role: str
