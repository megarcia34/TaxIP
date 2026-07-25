"""
Geographic routes (cities, provinces, countries)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/geo", tags=["Geographic"])


# ============================================================
# CIUDADES OPERATIVAS (con tenant activo)
# ============================================================

@router.get("/ciudades-operativas")
async def get_ciudades_operativas(
    db: AsyncSession = Depends(get_db)
):
    """
    Lista de ciudades que tienen un tenant activo asociado.
    Estas son las ciudades donde TaxIP opera y donde los propietarios pueden registrarse.
    """
    
    query = text("""
        SELECT DISTINCT
            c.id,
            c.nombre,
            c.codigo_postal,
            cb.id as tenant_id,
            cb.nombre as tenant_nombre
        FROM geo.ciudad c
        INNER JOIN tenant.control_base cb ON cb.ciudad_id = c.id
        WHERE cb.activo = true
        ORDER BY c.nombre ASC
    """)
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        {
            "id": str(row[0]),
            "nombre": row[1],
            "codigo_postal": row[2],
            "tenant_id": str(row[3]) if row[3] else None,
            "tenant_nombre": row[4]
        }
        for row in rows
    ]