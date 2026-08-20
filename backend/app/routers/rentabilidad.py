"""
Rentabilidad - Endpoints para cálculo de rentabilidad
CON SCHEMAS Y USO DE LIQUIDACIÓN
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date, timedelta

from app.database import get_db
from app.dependencies import get_current_user, get_propietario_id, get_filtros_reporte
from app.services.rentabilidad import (
    obtener_configuracion_tenant,
    calcular_rentabilidad_viaje,
    calcular_rentabilidad_periodo,
    recalcular_tablas_rentabilidad
)
from app.schemas.rentabilidad_schemas import (
    RentabilidadViajeResponse,
    RentabilidadPeriodoResponse,
    RentabilidadVehiculoDetalleResponse,
    RentabilidadTenantResponse,
    RecalcularRentabilidadResponse
)

router = APIRouter(prefix="/api/rentabilidad", tags=["Rentabilidad"])


# ============================================
# RENTABILIDAD DE UN VIAJE ESPECÍFICO
# ============================================

@router.get("/viaje/{viaje_id}", response_model=Dict[str, Any])
async def get_rentabilidad_viaje(
    viaje_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calcula la rentabilidad de un viaje específico
    """
    user_id, control_base_id, email, tipo_usuario = current_user
    
    # Verificar que el viaje existe
    query_verificar = text("""
        SELECT 
            vs.id, 
            vs.control_base_id,
            vs.vehiculo_id,
            vs.pasajero_id,
            vs.chofer_id
        FROM trip.viaje_solicitado vs
        WHERE vs.id = :viaje_id
    """)
    
    result = await db.execute(query_verificar, {"viaje_id": viaje_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    
    viaje_control_base_id = row[1]
    viaje_vehiculo_id = row[2]
    viaje_chofer_id = row[4]
    
    # Validar permisos
    if tipo_usuario.lower() not in ["super_admin", "admin", "admin_tenant"]:
        if tipo_usuario.lower() in ["propietario", "admin_propietario"]:
            query_prop = text("""
                SELECT id FROM fleet.propietario_vehiculo
                WHERE vehiculo_id = :vehiculo_id 
                  AND propietario_id = :user_id 
                  AND activo = true
            """)
            prop_result = await db.execute(query_prop, {
                "vehiculo_id": viaje_vehiculo_id,
                "user_id": user_id
            })
            if not prop_result.first():
                raise HTTPException(status_code=403, detail="No tienes permiso para ver este viaje")
        
        elif tipo_usuario.lower() == "chofer":
            if viaje_chofer_id != user_id:
                raise HTTPException(status_code=403, detail="No tienes permiso para ver este viaje")
    
    # Obtener configuración
    config = await obtener_configuracion_tenant(db, viaje_control_base_id)
    
    # Obtener tarifas
    tarifa_query = text("""
        SELECT tarifa_base, precio_por_km, precio_por_minuto, recargo_nocturno
        FROM payment.configuracion_tarifa
        WHERE control_base_id = :control_base_id AND activo = true
        ORDER BY created_at DESC
        LIMIT 1
    """)
    tarifa_result = await db.execute(tarifa_query, {"control_base_id": viaje_control_base_id})
    tarifa_row = tarifa_result.first()
    
    if not tarifa_row:
        tarifa_base, precio_km, precio_minuto, recargo_nocturno = 150, 50, 15, 1.2
    else:
        tarifa_base = float(tarifa_row[0])
        precio_km = float(tarifa_row[1])
        precio_minuto = float(tarifa_row[2])
        recargo_nocturno = float(tarifa_row[3])
    
    tarifa_config = {
        "tarifa_base": tarifa_base,
        "precio_km": precio_km,
        "precio_minuto": precio_minuto,
        "recargo_nocturno": recargo_nocturno
    }
    
    resultado = await calcular_rentabilidad_viaje(
        db, viaje_id, config, tarifa_config
    )
    
    if "error" in resultado:
        raise HTTPException(status_code=400, detail=resultado["error"])
    
    return {
        "success": True,
        "viaje_id": str(viaje_id),
        "datos": resultado,
        "configuracion_tenant": {
            "canon_mensual": config["canon_mensual_por_vehiculo"],
            "porcentaje_taxip": config["porcentaje_taxip_por_viaje"],
            "iva": config["iva"]
        }
    }


# ============================================
# RENTABILIDAD DE UN VEHÍCULO POR PERÍODO
# ============================================

@router.get("/vehiculo/{vehiculo_id}")
async def get_rentabilidad_vehiculo(
    vehiculo_id: UUID,
    fecha_desde: Optional[str] = Query(None, description="YYYY-MM-DD"),
    fecha_hasta: Optional[str] = Query(None, description="YYYY-MM-DD"),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calcula la rentabilidad de un vehículo en un período
    """
    user_id, control_base_id, email, tipo_usuario = current_user
    
    # Verificar vehículo
    query_vehiculo = text("""
        SELECT v.id, v.control_base_id, v.patente
        FROM fleet.vehiculo v
        WHERE v.id = :vehiculo_id AND v.activo = true
    """)
    result = await db.execute(query_vehiculo, {"vehiculo_id": vehiculo_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    vehiculo_control_base_id = row[1]
    patente = row[2]
    
    # Validar permisos
    if tipo_usuario.lower() not in ["super_admin", "admin", "admin_tenant"]:
        if tipo_usuario.lower() in ["propietario", "admin_propietario"]:
            query_prop = text("""
                SELECT id FROM fleet.propietario_vehiculo
                WHERE vehiculo_id = :vehiculo_id 
                  AND propietario_id = :user_id 
                  AND activo = true
            """)
            prop_result = await db.execute(query_prop, {
                "vehiculo_id": vehiculo_id,
                "user_id": user_id
            })
            if not prop_result.first():
                raise HTTPException(status_code=403, detail="No tienes permiso para ver este vehículo")
        else:
            raise HTTPException(status_code=403, detail="No tienes permiso para ver este vehículo")
    
    # Definir fechas
    hoy = date.today()
    
    if not fecha_desde and not fecha_hasta:
        fecha_desde = (hoy - timedelta(days=30)).isoformat()
        fecha_hasta = hoy.isoformat()
    
    try:
        fecha_desde_obj = date.fromisoformat(fecha_desde)
        fecha_hasta_obj = date.fromisoformat(fecha_hasta)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    resultado = await calcular_rentabilidad_periodo(
        db, vehiculo_id, fecha_desde_obj, fecha_hasta_obj, vehiculo_control_base_id
    )
    
    return {
        "success": True,
        "vehiculo": {
            "id": str(vehiculo_id),
            "patente": patente
        },
        "periodo": {
            "desde": fecha_desde_obj.isoformat(),
            "hasta": fecha_hasta_obj.isoformat(),
            "dias": (fecha_hasta_obj - fecha_desde_obj).days + 1
        },
        "resumen": {
            "total_viajes": resultado["total_viajes"],
            "ingresos_brutos": resultado["ingresos_brutos"],
            "gastos_totales": resultado.get("gastos_totales", 0),
            "utilidad_neta": resultado["utilidad_neta"],
            "canon_total": resultado.get("canon_total", 0),
            "km_excedentes_total": resultado.get("km_excedentes_total", 0),
            "margen": resultado["margen"]
        },
        "promedios": {
            "ingreso_por_viaje": round(resultado["ingresos_brutos"] / resultado["total_viajes"], 2) if resultado["total_viajes"] > 0 else 0,
            "utilidad_por_viaje": round(resultado["utilidad_neta"] / resultado["total_viajes"], 2) if resultado["total_viajes"] > 0 else 0,
            "viajes_por_dia": round(resultado["total_viajes"] / ((fecha_hasta_obj - fecha_desde_obj).days + 1), 2) if resultado["total_viajes"] > 0 else 0
        },
        "viajes": resultado["viajes"][:20]
    }


# ============================================
# RECALCULAR TABLAS PRECOMPUTADAS
# ============================================

@router.post("/recalcular/{vehiculo_id}", response_model=RecalcularRentabilidadResponse)
async def recalcular_rentabilidad(
    vehiculo_id: UUID,
    mes: int = Query(..., ge=1, le=12),
    anio: int = Query(..., ge=2020),
    current_user: tuple = Depends(get_propietario_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Recalcula las tablas de rentabilidad precomputadas para un vehículo
    """
    query_vehiculo = text("""
        SELECT v.id FROM fleet.vehiculo v
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE v.id = :vehiculo_id AND pv.propietario_id = :user_id AND pv.activo = true
    """)
    result = await db.execute(query_vehiculo, {
        "vehiculo_id": vehiculo_id,
        "user_id": current_user
    })
    
    if not result.first():
        raise HTTPException(status_code=403, detail="No tienes permiso para este vehículo")
    
    resultado = await recalcular_tablas_rentabilidad(db, vehiculo_id, mes, anio)
    
    if "error" in resultado:
        raise HTTPException(status_code=400, detail=resultado["error"])
    
    return RecalcularRentabilidadResponse(**resultado)