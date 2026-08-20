from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional, List
from datetime import datetime, timedelta

from app.database import get_db
from app.dependencies import get_current_user
from app.routers.propietario.utils import verificar_vehiculo_propietario

router = APIRouter(prefix="/alertas", tags=["Alertas"])




# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def obtener_nivel_alerta(dias: int) -> str:
    """Determina el nivel de alerta según los días restantes"""
    if dias < 0:
        return "vencido"
    elif dias <= 7:
        return "critico"
    elif dias <= 15:
        return "urgente"
    elif dias <= 30:
        return "preventivo"
    else:
        return "vigente"


async def obtener_propietario_id(current_user: tuple) -> UUID:
    """Obtiene el ID del propietario desde el usuario autenticado"""
    user_id, control_base_id, email, tipo = current_user
    return user_id


# ============================================================
# ENDPOINT DE PRUEBA
# ============================================================

@router.get("/ping")
async def ping():
    return {"message": "Router de alertas funcionando"}


# ============================================================
# ENDPOINT: ALERTAS DE VENCIMIENTO DE DOCUMENTOS
# ============================================================

@router.get("/documentos/vencimientos")
async def alertas_vencimiento_documentos(
    propietario_id: Optional[UUID] = None,
    vehiculo_id: Optional[UUID] = None,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene alertas de vencimiento de documentos.
    Incluye documentos del propietario y de vehículos.
    """
    
    # Si no se pasa propietario_id, usar el del usuario autenticado
    if propietario_id is None:
        propietario_id = await obtener_propietario_id(current_user)
    
    hoy = datetime.now().date()
    alertas = []
    
    # 1. DOCUMENTOS DEL PROPIETARIO (DNI, Licencia)
    try:
        query_propietario = text("""
            SELECT 
                dp.id,
                dp.tipo_documento,
                dp.numero,
                dp.fecha_vencimiento,
                dp.observaciones,
                'propietario' as entidad_tipo,
                p.nombre as entidad_nombre,
                NULL as patente
            FROM fleet.documento_propietario dp
            JOIN auth.usuario u ON u.id = dp.propietario_id
            JOIN auth.perfil_general p ON p.usuario_id = u.id
            WHERE dp.propietario_id = :propietario_id
              AND dp.fecha_vencimiento IS NOT NULL
        """)
        result = await db.execute(query_propietario, {"propietario_id": propietario_id})
        rows = result.all()
        
        for row in rows:
            fecha_vence = row[3]
            if fecha_vence:
                dias = (fecha_vence - hoy).days
                alertas.append({
                    "id": str(row[0]),
                    "tipo_alerta": "documento",
                    "subtipo": row[1],
                    "numero": row[2],
                    "fecha_vencimiento": fecha_vence.isoformat(),
                    "dias_restantes": dias,
                    "entidad": row[5],
                    "entidad_nombre": row[6],
                    "patente": row[7],
                    "observaciones": row[4],
                    "nivel": obtener_nivel_alerta(dias)
                })
    except Exception as e:
        print(f"Error en documentos propietario: {e}")
    
    # 2. DOCUMENTOS DE VEHÍCULOS
    try:
        query_vehiculos = text("""
            SELECT 
                dv.id,
                dv.tipo_documento,
                dv.numero,
                dv.fecha_vencimiento,
                dv.observaciones,
                'vehiculo' as entidad_tipo,
                v.patente,
                v.marca,
                v.modelo,
                dv.vtv_fecha_vencimiento,
                dv.seguro_fecha_vencimiento
            FROM fleet.documento_vehiculo dv
            JOIN fleet.vehiculo v ON v.id = dv.vehiculo_id
            JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
            WHERE pv.propietario_id = :propietario_id
              AND dv.activo = true
        """)
        params = {"propietario_id": propietario_id}
        
        if vehiculo_id:
            query_vehiculos = text(query_vehiculos.text + " AND v.id = :vehiculo_id")
            params["vehiculo_id"] = vehiculo_id
        
        result = await db.execute(query_vehiculos, params)
        rows = result.all()
        
        for row in rows:
            fecha_vence = None
            subtipo = row[1]
            
            if subtipo == 'vtv':
                fecha_vence = row[9]
            elif subtipo == 'seguro':
                fecha_vence = row[10]
            else:
                fecha_vence = row[3]
            
            if fecha_vence:
                dias = (fecha_vence - hoy).days
                alertas.append({
                    "id": str(row[0]),
                    "tipo_alerta": "documento",
                    "subtipo": subtipo,
                    "numero": row[2],
                    "fecha_vencimiento": fecha_vence.isoformat(),
                    "dias_restantes": dias,
                    "entidad": row[5],
                    "entidad_nombre": f"{row[7]} {row[8]}",
                    "patente": row[6],
                    "observaciones": row[4],
                    "nivel": obtener_nivel_alerta(dias)
                })
    except Exception as e:
        print(f"Error en documentos vehículo: {e}")
    
    # Contar por nivel
    conteos = {
        "vencido": len([a for a in alertas if a["nivel"] == "vencido"]),
        "critico": len([a for a in alertas if a["nivel"] == "critico"]),
        "urgente": len([a for a in alertas if a["nivel"] == "urgente"]),
        "preventivo": len([a for a in alertas if a["nivel"] == "preventivo"]),
        "vigente": len([a for a in alertas if a["nivel"] == "vigente"]),
        "total": len(alertas)
    }
    
    # Ordenar por días restantes (más urgentes primero)
    alertas.sort(key=lambda x: x["dias_restantes"])
    
    # Solo devolver los que no están vigentes
    alertas_urgentes = [a for a in alertas if a["nivel"] != "vigente"]
    
    return {
        "conteos": conteos,
        "alertas": alertas_urgentes,
        "todas": alertas
    }


# ============================================================
# ENDPOINT: ALERTAS ACTIVAS (TODOS LOS TIPOS)
# ============================================================

@router.get("/activas")
async def alertas_activas(
    vehiculo_id: Optional[UUID] = None,
    tipo: Optional[str] = Query(None, description="velocidad, geocerca, desvio, mantenimiento, documento"),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener todas las alertas activas del propietario.
    Incluye: alertas de velocidad, geocercas, desvíos, mantenimiento y documentos.
    """
    
    propietario_id = await obtener_propietario_id(current_user)
    alertas = []
    
    # 1. ALERTAS DE DESVÍO
    try:
        query_desvio = text("""
            SELECT 
                ad.id,
                ad.viaje_id,
                ad.latitud,
                ad.longitud,
                ad.distancia_desvio_metros,
                ad.notificado,
                ad.resuelto,
                ad.created_at,
                'desvio_ruta' as tipo_alerta,
                v.patente,
                u.email as conductor_email,
                vs.direccion_origen,
                vs.direccion_destino
            FROM audit.alerta_desvio ad
            JOIN trip.viaje_solicitado vs ON ad.viaje_id = vs.id
            JOIN fleet.vehiculo v ON vs.vehiculo_id = v.id
            JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
            LEFT JOIN auth.usuario u ON vs.chofer_id = u.id
            WHERE pv.propietario_id = :propietario_id
              AND ad.resuelto = false
              AND ad.created_at > NOW() - INTERVAL '24 hours'
        """)
        params = {"propietario_id": propietario_id}
        
        if vehiculo_id:
            query_desvio = text(query_desvio.text + " AND v.id = :vehiculo_id")
            params["vehiculo_id"] = vehiculo_id
        
        result = await db.execute(query_desvio, params)
        rows = result.all()
        
        for row in rows:
            alertas.append({
                "id": str(row[0]),
                "tipo": row[8],
                "vehiculo_patente": row[9],
                "conductor": row[10],
                "mensaje": f"Desvío de ruta de {row[12]} a {row[13]}",
                "distancia_desvio": float(row[4]) if row[4] else None,
                "ubicacion": {
                    "latitud": float(row[2]) if row[2] else None,
                    "longitud": float(row[3]) if row[3] else None
                },
                "fecha": row[7].isoformat() if row[7] else None,
                "resuelto": row[6],
                "viaje_id": str(row[1]) if row[1] else None
            })
    except Exception as e:
        print(f"Error en alertas de desvío: {e}")
    
    # 2. ALERTAS DE DOCUMENTOS
    try:
        alertas_documentos = await alertas_vencimiento_documentos(
            propietario_id=propietario_id,
            vehiculo_id=vehiculo_id,
            current_user=current_user,
            db=db
        )
        
        for doc in alertas_documentos["alertas"]:
            alertas.append({
                "id": doc["id"],
                "tipo": "documento",
                "subtipo": doc["subtipo"],
                "vehiculo_patente": doc["patente"],
                "conductor": doc["entidad_nombre"],
                "mensaje": f"{doc['subtipo'].replace('_', ' ').title()} - {doc['numero']} vence en {doc['dias_restantes']} días",
                "dias_restantes": doc["dias_restantes"],
                "nivel": doc["nivel"],
                "fecha": doc["fecha_vencimiento"],
                "resuelto": False,
                "viaje_id": None
            })
    except Exception as e:
        print(f"Error en alertas de documentos: {e}")
    
    # Ordenar por fecha
    alertas.sort(key=lambda x: x.get("fecha") or "", reverse=True)
    
    return {
        "total_alertas": len(alertas),
        "alertas": alertas
    }


# ============================================================
# ENDPOINT: RESOLVER ALERTA
# ============================================================

@router.put("/{alerta_id}/resolver")
async def resolver_alerta(
    alerta_id: str,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Marcar una alerta como resuelta.
    """
    propietario_id = await obtener_propietario_id(current_user)
    
    try:
        alerta_uuid = UUID(alerta_id)
        query = text("""
            UPDATE audit.alerta_desvio 
            SET resuelto = true, notificado = true
            WHERE id = :alerta_id
            AND EXISTS (
                SELECT 1 FROM trip.viaje_solicitado vs
                JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = vs.vehiculo_id
                WHERE vs.id = alerta_desvio.viaje_id
                  AND pv.propietario_id = :propietario_id
            )
            RETURNING id
        """)
        result = await db.execute(query, {"alerta_id": alerta_uuid, "propietario_id": propietario_id})
        await db.commit()
        row = result.first()
        
        if row:
            return {"success": True, "message": "Alerta resuelta correctamente"}
    except ValueError:
        pass
    
    raise HTTPException(status_code=404, detail="Alerta no encontrada")

# ============================================================
# ENDPOINT: DISPARAR NOTIFICACIONES (MANUALMENTE)
# ============================================================

@router.post("/notificar")
async def disparar_notificaciones(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Dispara notificaciones de vencimiento para todos los documentos.
    """
    from app.services.notificacion_vencimiento import NotificacionVencimientoService
    
    service = NotificacionVencimientoService(db)
    resultado = await service.verificar_y_enviar_notificaciones()
    
    return {
        "success": True,
        "message": f"Notificaciones procesadas: {resultado['enviados']} enviadas, {resultado['errores']} errores",
        "detalle": resultado["detalles"],
        "estadisticas": {
            "enviados": resultado["enviados"],
            "errores": resultado["errores"]
        }
    }