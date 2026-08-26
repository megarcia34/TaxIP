# app/core/validaciones_compartidas.py
"""
Validaciones compartidas entre módulos (sin dependencias circulares)
"""

from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def es_conductor(usuario_id: UUID, db: AsyncSession) -> bool:
    """
    Verifica si un usuario tiene capacidad CONDUCTOR activa.
    
    Busca en auth.usuario_rol (capacidades adicionales).
    También verifica si tipo_usuario_id = chofer (legacy).
    """
    # 1. Verificar rol principal (legacy)
    query_legacy = text("""
        SELECT 1 FROM auth.usuario u
        JOIN auth.tipo_usuario tu ON tu.id = u.tipo_usuario_id
        WHERE u.id = :usuario_id
          AND u.activo = true
          AND tu.nombre = 'chofer'
    """)
    result = await db.execute(query_legacy, {"usuario_id": usuario_id})
    if result.first():
        return True
    
    # 2. Verificar capacidad adicional (nuevo modelo)
    query_capacidad = text("""
        SELECT 1 FROM auth.usuario_rol ur
        JOIN auth.tipo_usuario tu ON tu.id = ur.tipo_usuario_id
        WHERE ur.usuario_id = :usuario_id
          AND ur.activo = true
          AND tu.nombre = 'chofer'
          AND (ur.fecha_fin IS NULL OR ur.fecha_fin > CURRENT_DATE)
    """)
    result = await db.execute(query_capacidad, {"usuario_id": usuario_id})
    return result.first() is not None


def calcular_duracion_horas(inicio: datetime, fin: Optional[datetime] = None) -> Decimal:
    """
    Calcula la duración en horas entre dos fechas.
    Si fin es None, usa datetime.now()
    """
    if inicio is None:
        return Decimal(0)
    
    if fin is None:
        fin = datetime.now()
    
    diff = fin - inicio
    return Decimal(str(diff.total_seconds() / 3600))