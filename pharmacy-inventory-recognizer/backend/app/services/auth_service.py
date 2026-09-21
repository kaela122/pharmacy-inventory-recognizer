from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import verify_password, create_token
from app.models import User


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, employee_id: str, password: str) -> dict | None:
        user = self.db.scalars(select(User).where(User.employee_id == employee_id)).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        return {"token": create_token(user.employee_id), "employee_id": user.employee_id,
                "full_name": user.full_name, "role": user.role}
