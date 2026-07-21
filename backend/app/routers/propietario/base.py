# app/routers/propietario/base.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Tuple
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_owner_user

# Re-exportar dependencias comunes
__all__ = [
    "APIRouter",
    "Depends",
    "AsyncSession",
    "Optional",
    "Tuple",
    "UUID",
    "get_db",
    "get_current_owner_user"
]