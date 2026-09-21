"""All API routes."""
from fastapi import APIRouter
from app.api.routes import (auth, recognizer, dashboard, categories,
                            products, suppliers, orders, movements, users)

api_router = APIRouter()
for m in (auth, recognizer, dashboard, categories, products,
          suppliers, orders, movements, users):
    api_router.include_router(m.router)
