from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import require_roles
from app.models import User
from app.schemas.user import UserInput, UserRead
from app.services.user_service import UserService, UserError

router = APIRouter(prefix="/users", tags=["users"])
admin_only = require_roles("admin")


@router.get("", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), _: User = Depends(admin_only)):
    return UserService(db).list()


@router.post("", response_model=UserRead, status_code=201)
def create_user(payload: UserInput, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    try:
        return UserService(db).create(payload)
    except UserError as e:
        raise HTTPException(422, str(e))


@router.put("/{uid}", response_model=UserRead)
def update_user(uid: int, payload: UserInput, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    try:
        r = UserService(db).update(uid, payload)
    except UserError as e:
        raise HTTPException(422, str(e))
    if not r:
        raise HTTPException(404, "User not found")
    return r


@router.delete("/{uid}", status_code=204)
def delete_user(uid: int, db: Session = Depends(get_db), me: User = Depends(admin_only)):
    try:
        ok = UserService(db).delete(uid, me.user_id)
    except UserError as e:
        raise HTTPException(422, str(e))
    if not ok:
        raise HTTPException(404, "User not found")
