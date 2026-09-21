from __future__ import annotations
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models import Supplier, PurchaseOrder
from app.schemas.supplier import SupplierInput


class SupplierInUseError(Exception): ...


class SupplierService:
    def __init__(self, db: Session):
        self.db = db

    def _count(self, sid: int) -> int:
        return self.db.scalar(select(func.count()).select_from(PurchaseOrder)
                              .where(PurchaseOrder.supplier_id == sid)) or 0

    def _read(self, s: Supplier) -> dict:
        return {"supplier_id": s.supplier_id, "name": s.name,
                "contact_person": s.contact_person, "phone": s.phone,
                "email": s.email, "order_count": self._count(s.supplier_id)}

    def list(self):
        rows = self.db.scalars(select(Supplier).order_by(Supplier.name)).all()
        return [self._read(s) for s in rows]

    def create(self, data: SupplierInput):
        s = Supplier(name=data.name, contact_person=data.contact_person,
                     phone=data.phone, email=data.email)
        self.db.add(s); self.db.commit(); self.db.refresh(s)
        return self._read(s)

    def update(self, sid: int, data: SupplierInput):
        s = self.db.get(Supplier, sid)
        if not s:
            return None
        s.name, s.contact_person = data.name, data.contact_person
        s.phone, s.email = data.phone, data.email
        self.db.commit(); self.db.refresh(s)
        return self._read(s)

    def delete(self, sid: int):
        s = self.db.get(Supplier, sid)
        if not s:
            return False
        if self._count(sid) > 0:
            raise SupplierInUseError()
        self.db.delete(s); self.db.commit(); return True
