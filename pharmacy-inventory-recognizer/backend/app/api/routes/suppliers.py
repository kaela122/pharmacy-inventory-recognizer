from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import require_roles
from app.models import User
from app.schemas.supplier import SupplierInput, SupplierRead
from app.services.supplier_service import SupplierService, SupplierInUseError

router = APIRouter(prefix="/suppliers", tags=["suppliers"])
manager = require_roles("admin", "inventory_manager")


@router.get("", response_model=list[SupplierRead])
def list_suppliers(db: Session = Depends(get_db)):
    return SupplierService(db).list()


@router.post("", response_model=SupplierRead, status_code=201)
def create_supplier(payload: SupplierInput, db: Session = Depends(get_db), _: User = Depends(manager)):
    return SupplierService(db).create(payload)


@router.put("/{sid}", response_model=SupplierRead)
def update_supplier(sid: int, payload: SupplierInput, db: Session = Depends(get_db), _: User = Depends(manager)):
    r = SupplierService(db).update(sid, payload)
    if not r:
        raise HTTPException(404, "Supplier not found")
    return r


@router.delete("/{sid}", status_code=204)
def delete_supplier(sid: int, db: Session = Depends(get_db), _: User = Depends(manager)):
    try:
        ok = SupplierService(db).delete(sid)
    except SupplierInUseError:
        raise HTTPException(409, "Supplier has orders - can't delete.")
    if not ok:
        raise HTTPException(404, "Supplier not found")
