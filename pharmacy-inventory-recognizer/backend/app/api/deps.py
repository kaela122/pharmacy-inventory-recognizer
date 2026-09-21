"""Auth dependencies and role checks."""
from __future__ import annotations
from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.db.session import get_db
from app.models import User


def get_current_user(authorization: str | None = Header(default=None),
                     db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated")
    emp = decode_token(authorization.split(" ", 1)[1])
    if not emp:
        raise HTTPException(401, "Invalid token")
    user = db.scalars(select(User).where(User.employee_id == emp)).first()
    if not user:
        raise HTTPException(401, "User not found")
    return user


def require_roles(*roles: str):
    """Allow only the given roles."""
    def dep(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(403, "You don't have permission for this action")
        return user
    return dep
