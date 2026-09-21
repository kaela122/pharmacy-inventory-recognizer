from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import require_roles
from app.models import User
from app.schemas.product import ProductInput, ProductRead
from app.services.product_service import (ProductService, InvalidSKUError, DuplicateSKUError)

router = APIRouter(prefix="/products", tags=["products"])
# admins and inventory managers can edit the catalog
manager = require_roles("admin", "inventory_manager")


@router.get("", response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db)):
    return ProductService(db).list()


@router.post("", response_model=ProductRead, status_code=201)
def create_product(payload: ProductInput, db: Session = Depends(get_db), _: User = Depends(manager)):
    try:
        return ProductService(db).create(payload)
    except InvalidSKUError as e: raise HTTPException(422, str(e))
    except DuplicateSKUError as e: raise HTTPException(409, str(e))


@router.put("/{pid}", response_model=ProductRead)
def update_product(pid: int, payload: ProductInput, db: Session = Depends(get_db), _: User = Depends(manager)):
    try:
        r = ProductService(db).update(pid, payload)
    except InvalidSKUError as e: raise HTTPException(422, str(e))
    except DuplicateSKUError as e: raise HTTPException(409, str(e))
    if not r: raise HTTPException(404, "Product not found")
    return r


@router.delete("/{pid}", status_code=204)
def delete_product(pid: int, db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    if not ProductService(db).delete(pid): raise HTTPException(404, "Product not found")
