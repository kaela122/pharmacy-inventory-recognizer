from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import require_roles
from app.models import User
from app.schemas.order import OrderRead, OrderStats, OrderStatusUpdate
from app.services.order_service import OrderService, OrderStatusError

router = APIRouter(prefix="/orders", tags=["orders"])
# admins and inventory managers can move orders through their workflow
manager = require_roles("admin", "inventory_manager")


@router.get("", response_model=list[OrderRead])
def list_orders(db: Session = Depends(get_db)):
    return OrderService(db).list()


@router.get("/stats", response_model=OrderStats)
def order_stats(db: Session = Depends(get_db)):
    return OrderService(db).stats()


@router.patch("/{order_id}/status", response_model=OrderRead)
def update_order_status(order_id: int, payload: OrderStatusUpdate,
                        db: Session = Depends(get_db), user: User = Depends(manager)):
    try:
        r = OrderService(db).set_status(order_id, payload.status, user.employee_id)
    except OrderStatusError as e:
        raise HTTPException(409, str(e))
    if not r:
        raise HTTPException(404, "Order not found")
    return r
