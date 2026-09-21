from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import User
from app.core.security import hash_password
from app.schemas.user import UserInput

ROLES = {"admin", "inventory_manager", "pharmacist"}


class UserError(ValueError): ...


def _read(u: User) -> dict:
    return {"user_id": u.user_id, "employee_id": u.employee_id,
            "full_name": u.full_name, "role": u.role}


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def list(self):
        return [_read(u) for u in self.db.scalars(select(User).order_by(User.employee_id)).all()]

    def _validate(self, data: UserInput):
        if data.role not in ROLES:
            raise UserError(f"Role must be one of: {', '.join(sorted(ROLES))}.")

    def create(self, data: UserInput):
        self._validate(data)
        emp = data.employee_id.strip().upper()
        if not emp or not data.full_name.strip():
            raise UserError("Employee ID and full name are required.")
        if not data.password:
            raise UserError("Password is required for a new user.")
        if self.db.scalars(select(User).where(User.employee_id == emp)).first():
            raise UserError(f"Employee ID '{emp}' already exists.")
        u = User(employee_id=emp, full_name=data.full_name.strip(),
                 role=data.role, password_hash=hash_password(data.password))
        self.db.add(u); self.db.commit(); self.db.refresh(u)
        return _read(u)

    def update(self, uid: int, data: UserInput):
        self._validate(data)
        u = self.db.get(User, uid)
        if not u:
            return None
        u.full_name, u.role = data.full_name.strip(), data.role
        if data.password:                       # blank = keep current password
            u.password_hash = hash_password(data.password)
        self.db.commit(); self.db.refresh(u)
        return _read(u)

    def delete(self, uid: int, acting_user_id: int):
        u = self.db.get(User, uid)
        if not u:
            return False
        if u.user_id == acting_user_id:
            raise UserError("You can't delete your own account.")
        if u.role == "admin" and self.db.query(User).filter(User.role == "admin").count() <= 1:
            raise UserError("Can't delete the last admin account.")
        self.db.delete(u); self.db.commit(); return True
