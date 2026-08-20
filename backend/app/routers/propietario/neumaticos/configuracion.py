"""
Endpoints de configuración de neumáticos
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.dependencies import get_propietario_context
from app.schemas.propietario_schemas import ConfiguracionNeumaticosUpdate
from app.routers.propietario.utils import verificar_vehiculo_propietario

router = APIRouter()


@router.get("/configuracion/neumaticos")
async def obtener_configuracion_neumaticos(
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener configuración de neumáticos del propietario.
    """
    from sqlalchemy import text
    
    control_base_id = UUID(ctx["control_base_id"])
    
    query = text("""
        SELECT 
            control_base_id,
            COALESCE(vida_util_neumaticos_km, 50000) as vida_util,
            COALESCE(umbral_rotacion_neumaticos_km, 10000) as umbral_rotacion,
            COALESCE(umbral_cambio_neumaticos_km, 45000) as umbral_cambio,
            COALESCE(profundidad_minima_neumaticos_mm, 2.0) as profundidad_minima,
            COALESCE(factor_desgaste_delantero, 1.5) as factor_desgaste,
            updated_at
        FROM tenant.configuracion_tenant
        WHERE control_base_id = :control_base_id
    """)
    result = await db.execute(query, {"control_base_id": control_base_id})
    row = result.first()
    
    if not row:
        return {
            "control_base_id": str(control_base_id),
            "vida_util_km": 50000,
            "umbral_rotacion_km": 10000,
            "umbral_cambio_km": 45000,
            "profundidad_minima_mm": 2.0,
            "factor_desgaste_delantero": 1.5,
            "colores": {
                "verde": {"desde_mm": 4.1, "estado": "BUENO"},
                "amarillo": {"desde_mm": 2.0, "hasta_mm": 4.0, "estado": "ATENCION"},
                "rojo": {"hasta_mm": 1.9, "estado": "CRITICO"}
            },
            "ultima_actualizacion": datetime.now()
        }
    
    return {
        "control_base_id": str(row[0]),
        "vida_util_km": int(row[1]),
        "umbral_rotacion_km": int(row[2]),
        "umbral_cambio_km": int(row[3]),
        "profundidad_minima_mm": float(row[4]),
        "factor_desgaste_delantero": float(row[5]),
        "colores": {
            "verde": {"desde_mm": 4.1, "estado": "BUENO"},
            "amarillo": {"desde_mm": 2.0, "hasta_mm": 4.0, "estado": "ATENCION"},
            "rojo": {"hasta_mm": 1.9, "estado": "CRITICO"}
        },
        "ultima_actualizacion": row[6]
    }


@router.put("/configuracion/neumaticos")
async def actualizar_configuracion_neumaticos(
    data: ConfiguracionNeumaticosUpdate,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar configuración de neumáticos.
    """
    from sqlalchemy import text
    
    control_base_id = UUID(ctx["control_base_id"])
    
    updates = []
    params = {"control_base_id": control_base_id}
    
    if data.vida_util_km is not None:
        updates.append("vida_util_neumaticos_km = :vida_util")
        params["vida_util"] = data.vida_util_km
    
    if data.umbral_rotacion_km is not None:
        updates.append("umbral_rotacion_neumaticos_km = :umbral_rotacion")
        params["umbral_rotacion"] = data.umbral_rotacion_km
    
    if data.umbral_cambio_km is not None:
        updates.append("umbral_cambio_neumaticos_km = :umbral_cambio")
        params["umbral_cambio"] = data.umbral_cambio_km
    
    if data.profundidad_minima_mm is not None:
        updates.append("profundidad_minima_neumaticos_mm = :profundidad_minima")
        params["profundidad_minima"] = data.profundidad_minima_mm
    
    if data.factor_desgaste_delantero is not None:
        updates.append("factor_desgaste_delantero = :factor_desgaste")
        params["factor_desgaste"] = data.factor_desgaste_delantero
    
    if updates:
        query_check = text("""
            SELECT id FROM tenant.configuracion_tenant
            WHERE control_base_id = :control_base_id
        """)
        result = await db.execute(query_check, {"control_base_id": control_base_id})
        
        if result.first():
            query_update = text(f"""
                UPDATE tenant.configuracion_tenant
                SET {', '.join(updates)}, updated_at = NOW()
                WHERE control_base_id = :control_base_id
            """)
        else:
            columns = ["control_base_id"] + [u.split('=')[0].strip() for u in updates]
            placeholders = [f":{c.strip()}" for c in columns]
            query_update = text(f"""
                INSERT INTO tenant.configuracion_tenant (control_base_id, {', '.join(columns)})
                VALUES (:control_base_id, {', '.join(placeholders)})
            """)
        
        await db.execute(query_update, params)
        await db.commit()
    
    return {
        "mensaje": "Configuración actualizada correctamente",
        "configuracion": {
            "vida_util_km": data.vida_util_km,
            "umbral_rotacion_km": data.umbral_rotacion_km,
            "umbral_cambio_km": data.umbral_cambio_km,
            "profundidad_minima_mm": data.profundidad_minima_mm,
            "factor_desgaste_delantero": data.factor_desgaste_delantero
        }
    }