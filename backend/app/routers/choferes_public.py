"""
Router público para choferes (acceso desde empleados)
No requiere permisos de administrador
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user

# ✅ Crear el router con el prefijo correcto
router = APIRouter(prefix="/api/choferes", tags=["Choferes Públicos"])


@router.get("/disponibles")
async def choferes_disponibles(
    control_base_id: UUID = Query(..., description="ID de la base operativa"),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene choferes disponibles para EMPLEADOS (solo visualización).
    No requiere permisos de administrador.
    """
    query = text("""
        SELECT 
            cv.id,
            u.id as usuario_id,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as nombre,
            cv.estado_laboral,
            v.patente,
            v.marca,
            v.modelo,
            cv.latitud,
            cv.longitud,
            cv.calificacion_promedio,
            cv.total_viajes
        FROM fleet.chofer_vehiculo cv
        JOIN auth.usuario u ON u.id = cv.usuario_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN fleet.vehiculo v ON v.id = cv.vehiculo_id
        WHERE cv.control_base_id = :control_base_id
          AND cv.estado_laboral = 'libre'
          AND cv.activo = true
          AND u.activo = true
        ORDER BY p.nombre ASC
    """)
    
    result = await db.execute(query, {"control_base_id": control_base_id})
    rows = result.all()
    
    return [
        {
            "id": str(row[0]),
            "usuario_id": str(row[1]),
            "nombre": row[2] or "Sin nombre",
            "estado_laboral": row[3],
            "vehiculo": {
                "patente": row[4],
                "marca": row[5] or "Sin marca",
                "modelo": row[6] or "Sin modelo"
            },
            "ubicacion": {
                "latitud": float(row[7]) if row[7] else None,
                "longitud": float(row[8]) if row[8] else None
            },
            "calificacion": float(row[9]) if row[9] else 0,
            "total_viajes": row[10] or 0
        }
        for row in rows
    ]