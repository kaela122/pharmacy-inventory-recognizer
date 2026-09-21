from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models import User
from app.schemas.movement import MovementInput, MovementRead
from app.services.movement_service import MovementService, MovementError

router = APIRouter(tags=["stock"])


@router.post("/products/{pid}/movements", response_model=MovementRead, status_code=201)
def record_movement(pid: int, payload: MovementInput, db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    try:
        r = MovementService(db).record(pid, payload, user.employee_id)
    except MovementError as e:
        raise HTTPException(422, str(e))
    if not r:
        raise HTTPException(404, "Product not found")
    return r


@router.get("/products/{pid}/movements", response_model=list[MovementRead])
def product_history(pid: int, db: Session = Depends(get_db)):
    return MovementService(db).for_product(pid)


@router.get("/movements", response_model=list[MovementRead])
def recent_movements(db: Session = Depends(get_db)):
    return MovementService(db).recent()
