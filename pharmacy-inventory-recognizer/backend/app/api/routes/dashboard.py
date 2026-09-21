from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.dashboard import DashboardStats, Analytics
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def stats(db: Session = Depends(get_db)):
    return DashboardService(db).stats()


@router.get("/analytics", response_model=Analytics)
def analytics(db: Session = Depends(get_db)):
    return DashboardService(db).analytics()
