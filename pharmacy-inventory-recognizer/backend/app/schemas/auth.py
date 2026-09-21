from __future__ import annotations
from pydantic import BaseModel


class LoginRequest(BaseModel):
    employee_id: str
    password: str


class LoginResponse(BaseModel):
    token: str
    employee_id: str
    full_name: str
    role: str
