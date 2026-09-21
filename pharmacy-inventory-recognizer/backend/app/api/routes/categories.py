from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import require_roles
from app.models import User
from app.schemas.category import CategoryInput, CategoryRead
from app.services.category_service import (CategoryService, DuplicateCategoryError, CategoryInUseError)

router = APIRouter(prefix="/categories", tags=["categories"])
manager = require_roles("admin", "inventory_manager")


@router.get("", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return CategoryService(db).list()


@router.post("", response_model=CategoryRead, status_code=201)
def create_category(payload: CategoryInput, db: Session = Depends(get_db), _: User = Depends(manager)):
    try:
        return CategoryService(db).create(payload)
    except DuplicateCategoryError:
        raise HTTPException(409, f"Category '{payload.name}' already exists.")


@router.delete("/{cid}", status_code=204)
def delete_category(cid: int, db: Session = Depends(get_db), _: User = Depends(manager)):
    try:
        ok = CategoryService(db).delete(cid)
    except CategoryInUseError:
        raise HTTPException(409, "Category has medicines - move them first.")
    if not ok: raise HTTPException(404, "Category not found")
