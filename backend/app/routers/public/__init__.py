# app/routers/public/__init__.py

from fastapi import APIRouter
from app.routers.public import qr

router = APIRouter(prefix="/public", tags=["Public"])

router.include_router(qr.router)