"""
Admin Dashboard - Punto de entrada del panel administrativo
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, date
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user, get_current_admin_user, get_admin_tenant_user
from app.services.rentabilidad import obtener_configuracion_tenant


# ============================================
# FUNCIONES DE FORMATEO
# ============================================

def format_number(value: float, decimals: int = 2) -> str:
    """
    Formatea un número con separador de miles (.) y decimales (,)
    Ejemplo: 1234567.89 → "1.234.567,89"
    """
    if value is None:
        return "0,00"
    
    if decimals == 0:
        return f"{int(value):,}".replace(",", ".")
    
    parte_entera = int(abs(value))
    parte_decimal = round(abs(value) - parte_entera, decimals)
    
    entera_formateada = f"{parte_entera:,}".replace(",", ".")
    decimal_str = f"{parte_decimal:.{decimals}f}"[2:]
    
    signo = "-" if value < 0 else ""
    return f"{signo}{entera_formateada},{decimal_str}"


def format_currency(value: float) -> str:
    """Formatea un número como moneda (ARS)"""
    if value is None:
        return "$ 0,00"
    return f"$ {format_number(value)}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Formatea un número como porcentaje"""
    if value is None:
        return "0,00%"
    return f"{format_number(value, decimals)}%"


router = APIRouter(prefix="/admin", tags=["Admin"])


# ============================================
# ENDPOINTS EXISTENTES (MANTENIDOS)
# ============================================

@router.get("/")
async def admin_root(
    current_user: tuple = Depends(get_current_user),
):
    """Punto de entrada del panel administrativo"""
    user_id, control_base_id, email, tipo_usuario = current_user
    
    if tipo_usuario.lower() not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren permisos de administrador."
        )
    
    return {
        "success": True,
        "message": "TaxIP Admin API",
        "version": "2.0.0",
        "user": {
            "id": str(user_id),
            "email": email,
            "tipo": tipo_usuario,
            "control_base_id": str(control_base_id) if control_base_id else None
        },
        "endpoints": {
            "dashboard": "/admin/dashboard",
            "propietarios": "/api/admin/propietarios",
            "empresas": "/api/admin/empresas",
            "tenants": "/api/admin/tenants",
            "tarifas": "/api/admin/tarifas",
            "comercios": "/admin/comercios",
            "viajes": "/api/viajes/dashboard",
            "tenant_resumen": "/admin/tenant/resumen",
            "tenant_vehiculos": "/admin/tenant/vehiculos",
            "tenant_vehiculo": "/admin/tenant/vehiculo/{id}",
            "tenant_medios_pago": "/admin/tenant/medios-pago",
            "tenant_gastos": "/admin/tenant/gastos"
        }
    }


@router.get("/dashboard")
async def admin_dashboard(
    current_user: tuple = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Dashboard administrativo - Resumen de la plataforma"""
    user_id, control_base_id, email, tipo_usuario = current_user
    
    if not control_base_id:
        stats_query = text("""
            SELECT 
                (SELECT COUNT(*) FROM auth.usuario WHERE tipo_usuario_id IN (SELECT id FROM auth.tipo_usuario WHERE nombre = 'chofer')) as total_choferes,
                (SELECT COUNT(*) FROM auth.usuario WHERE tipo_usuario_id IN (SELECT id FROM auth.tipo_usuario WHERE nombre = 'pasajero')) as total_pasajeros,
                (SELECT COUNT(*) FROM fleet.vehiculo WHERE activo = true) as total_vehiculos,
                (SELECT COUNT(*) FROM tenant.control_base WHERE activo = true) as total_tenants,
                (SELECT COUNT(*) FROM trip.viaje_solicitado WHERE estado = 'pendiente') as viajes_pendientes,
                (SELECT COUNT(*) FROM trip.viaje_solicitado WHERE estado = 'en_curso') as viajes_en_curso,
                (SELECT COUNT(*) FROM trip.viaje_solicitado WHERE estado = 'finalizado' AND created_at::date = CURRENT_DATE) as viajes_hoy,
                (SELECT COALESCE(SUM(precio_final), 0) FROM trip.viaje_solicitado WHERE estado = 'finalizado' AND created_at::date = CURRENT_DATE) as recaudacion_hoy
        """)
        
        result = await db.execute(stats_query)
        row = result.first()
        
        viajes_query = text("""
            SELECT 
                vs.id,
                COALESCE(p.nombre || ' ' || p.apellido, u.email) as pasajero_nombre,
                COALESCE(p2.nombre || ' ' || p2.apellido, u2.email, 'Sin asignar') as chofer_nombre,
                vs.direccion_origen,
                vs.direccion_destino,
                vs.estado,
                vs.created_at,
                CASE 
                    WHEN vs.estado = 'finalizado' THEN vs.precio_final
                    ELSE vs.precio_estimado
                END as precio,
                cb.nombre as empresa
            FROM trip.viaje_solicitado vs
            JOIN auth.usuario u ON u.id = vs.pasajero_id
            LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
            LEFT JOIN auth.usuario u2 ON u2.id = vs.chofer_id
            LEFT JOIN auth.perfil_general p2 ON p2.usuario_id = u2.id
            LEFT JOIN tenant.control_base cb ON cb.id = vs.control_base_id
            ORDER BY vs.created_at DESC
            LIMIT 10
        """)
        
        result_viajes = await db.execute(viajes_query)
        viajes = result_viajes.all()
        
        return {
            "success": True,
            "tipo_usuario": "superadmin",
            "estadisticas": {
                "total_choferes": row[0] or 0,
                "total_pasajeros": row[1] or 0,
                "total_vehiculos": row[2] or 0,
                "total_tenants": row[3] or 0,
                "viajes_pendientes": row[4] or 0,
                "viajes_en_curso": row[5] or 0,
                "viajes_hoy": row[6] or 0,
                "recaudacion_hoy": float(row[7] or 0)
            },
            "viajes": [
                {
                    "id": str(v[0]),
                    "pasajero_nombre": v[1],
                    "chofer_nombre": v[2],
                    "direccion_origen": v[3],
                    "direccion_destino": v[4],
                    "estado": v[5],
                    "created_at": v[6],
                    "precio": float(v[7]) if v[7] else None,
                    "empresa": v[8]
                }
                for v in viajes
            ]
        }
    
    stats_query = text("""
        SELECT 
            (SELECT COUNT(*) FROM auth.usuario WHERE control_base_id = :control_base_id AND tipo_usuario_id IN (SELECT id FROM auth.tipo_usuario WHERE nombre = 'chofer')) as total_choferes,
            (SELECT COUNT(*) FROM auth.usuario WHERE control_base_id = :control_base_id AND tipo_usuario_id IN (SELECT id FROM auth.tipo_usuario WHERE nombre = 'pasajero')) as total_pasajeros,
            (SELECT COUNT(*) FROM fleet.vehiculo WHERE control_base_id = :control_base_id AND activo = true) as total_vehiculos,
            (SELECT COUNT(*) FROM trip.viaje_solicitado WHERE control_base_id = :control_base_id AND estado = 'pendiente') as viajes_pendientes,
            (SELECT COUNT(*) FROM trip.viaje_solicitado WHERE control_base_id = :control_base_id AND estado = 'en_curso') as viajes_en_curso,
            (SELECT COUNT(*) FROM trip.viaje_solicitado WHERE control_base_id = :control_base_id AND estado = 'finalizado' AND created_at::date = CURRENT_DATE) as viajes_hoy,
            (SELECT COALESCE(SUM(precio_final), 0) FROM trip.viaje_solicitado WHERE control_base_id = :control_base_id AND estado = 'finalizado' AND created_at::date = CURRENT_DATE) as recaudacion_hoy,
            (SELECT nombre FROM tenant.control_base WHERE id = :control_base_id) as tenant_nombre
    """)
    
    result = await db.execute(stats_query, {"control_base_id": control_base_id})
    row = result.first()
    
    viajes_query = text("""
        SELECT 
            vs.id,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as pasajero_nombre,
            COALESCE(p2.nombre || ' ' || p2.apellido, u2.email, 'Sin asignar') as chofer_nombre,
            vs.direccion_origen,
            vs.direccion_destino,
            vs.estado,
            vs.created_at,
            CASE 
                WHEN vs.estado = 'finalizado' THEN vs.precio_final
                ELSE vs.precio_estimado
            END as precio
        FROM trip.viaje_solicitado vs
        JOIN auth.usuario u ON u.id = vs.pasajero_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN auth.usuario u2 ON u2.id = vs.chofer_id
        LEFT JOIN auth.perfil_general p2 ON p2.usuario_id = u2.id
        WHERE vs.control_base_id = :control_base_id
        ORDER BY vs.created_at DESC
        LIMIT 10
    """)
    
    result_viajes = await db.execute(viajes_query, {"control_base_id": control_base_id})
    viajes = result_viajes.all()
    
    return {
        "success": True,
        "tipo_usuario": "admin",
        "tenant": row[7],
        "estadisticas": {
            "total_choferes": row[0] or 0,
            "total_pasajeros": row[1] or 0,
            "total_vehiculos": row[2] or 0,
            "viajes_pendientes": row[3] or 0,
            "viajes_en_curso": row[4] or 0,
            "viajes_hoy": row[5] or 0,
            "recaudacion_hoy": float(row[6] or 0)
        },
        "viajes": [
            {
                "id": str(v[0]),
                "pasajero_nombre": v[1],
                "chofer_nombre": v[2],
                "direccion_origen": v[3],
                "direccion_destino": v[4],
                "estado": v[5],
                "created_at": v[6],
                "precio": float(v[7]) if v[7] else None
            }
            for v in viajes
        ]
    }


# ============================================
# NUEVOS ENDPOINTS PARA ADMIN TENANT
# ============================================

@router.get("/tenant/resumen")
async def tenant_resumen(
    periodo: str = Query("mes", pattern="^(dia|semana|mes)$"),
    fecha_desde: Optional[str] = Query(None, description="YYYY-MM-DD"),
    fecha_hasta: Optional[str] = Query(None, description="YYYY-MM-DD"),
    current_user: tuple = Depends(get_admin_tenant_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Resumen general del tenant:
    - Total vehículos
    - Total viajes
    - Ingresos brutos
    - Ingresos netos
    - Total gastos
    - Utilidad neta
    - Margen
    """
    user_id, control_base_id, email, tipo_usuario = current_user
    
    hoy = date.today()
    if not fecha_desde and not fecha_hasta:
        if periodo == "dia":
            fecha_desde = hoy.isoformat()
            fecha_hasta = hoy.isoformat()
        elif periodo == "semana":
            fecha_desde = (hoy - timedelta(days=7)).isoformat()
            fecha_hasta = hoy.isoformat()
        else:
            fecha_desde = (hoy - timedelta(days=30)).isoformat()
            fecha_hasta = hoy.isoformat()
    
    try:
        fecha_desde_obj = date.fromisoformat(fecha_desde)
        fecha_hasta_obj = date.fromisoformat(fecha_hasta)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    config = await obtener_configuracion_tenant(db, control_base_id)
    
    query = text("""
        SELECT 
            (SELECT COUNT(*) FROM fleet.vehiculo WHERE control_base_id = :tenant_id AND activo = true) as total_vehiculos,
            COALESCE((
                SELECT COUNT(*) 
                FROM trip.viaje_solicitado 
                WHERE control_base_id = :tenant_id 
                  AND estado = 'finalizado'
                  AND created_at::date BETWEEN :fecha_desde AND :fecha_hasta
            ), 0) as total_viajes,
            COALESCE((
                SELECT COALESCE(SUM(precio_final), 0) 
                FROM trip.viaje_solicitado 
                WHERE control_base_id = :tenant_id 
                  AND estado = 'finalizado'
                  AND created_at::date BETWEEN :fecha_desde AND :fecha_hasta
            ), 0) as ingresos_brutos,
            COALESCE((
                SELECT COALESCE(SUM(g.monto), 0) 
                FROM fleet.gasto_vehiculo g
                JOIN fleet.vehiculo v ON v.id = g.vehiculo_id
                WHERE v.control_base_id = :tenant_id 
                  AND g.fecha_gasto BETWEEN :fecha_desde AND :fecha_hasta
            ), 0) as total_gastos
    """)
    
    result = await db.execute(query, {
        "tenant_id": control_base_id,
        "fecha_desde": fecha_desde_obj,
        "fecha_hasta": fecha_hasta_obj
    })
    row = result.first()
    
    total_vehiculos = row[0] or 0
    total_viajes = row[1] or 0
    ingresos_brutos = float(row[2] or 0)
    total_gastos = float(row[3] or 0)
    
    canon_mensual = config.get("canon_mensual_por_vehiculo", 10000)
    porcentaje_taxip = config.get("porcentaje_taxip_por_viaje", 1.5)
    
    dias_periodo = (fecha_hasta_obj - fecha_desde_obj).days + 1
    canon_proporcional = (canon_mensual / 30) * dias_periodo * total_vehiculos
    comision_porcentual = ingresos_brutos * (porcentaje_taxip / 100)
    total_comisiones = canon_proporcional + comision_porcentual
    
    ingresos_netos = ingresos_brutos - total_comisiones
    utilidad_neta = ingresos_netos - total_gastos
    margen = (utilidad_neta / ingresos_brutos * 100) if ingresos_brutos > 0 else 0
    
    return {
        "success": True,
        "periodo": {
            "tipo": periodo,
            "desde": fecha_desde_obj.isoformat(),
            "hasta": fecha_hasta_obj.isoformat(),
            "dias": dias_periodo
        },
        "resumen": {
            "total_vehiculos": total_vehiculos,
            "total_viajes": total_viajes,
            "ingresos_brutos": format_currency(ingresos_brutos),
            "comision_plataforma": format_currency(total_comisiones),
            "ingresos_netos": format_currency(ingresos_netos),
            "total_gastos": format_currency(total_gastos),
            "utilidad_neta": format_currency(utilidad_neta),
            "margen": format_percentage(margen)
        }
    }


@router.get("/tenant/vehiculos")
async def tenant_vehiculos(
    periodo: str = Query("mes", pattern="^(dia|semana|mes)$"),
    fecha_desde: Optional[str] = Query(None, description="YYYY-MM-DD"),
    fecha_hasta: Optional[str] = Query(None, description="YYYY-MM-DD"),
    current_user: tuple = Depends(get_admin_tenant_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista de vehículos del tenant con resumen de:
    - Conductor asignado
    - Viajes
    - Ingresos
    - Gastos
    - Utilidad
    - Margen
    """
    user_id, control_base_id, email, tipo_usuario = current_user
    
    hoy = date.today()
    if not fecha_desde and not fecha_hasta:
        if periodo == "dia":
            fecha_desde = hoy.isoformat()
            fecha_hasta = hoy.isoformat()
        elif periodo == "semana":
            fecha_desde = (hoy - timedelta(days=7)).isoformat()
            fecha_hasta = hoy.isoformat()
        else:
            fecha_desde = (hoy - timedelta(days=30)).isoformat()
            fecha_hasta = hoy.isoformat()
    
    try:
        fecha_desde_obj = date.fromisoformat(fecha_desde)
        fecha_hasta_obj = date.fromisoformat(fecha_hasta)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    query = text("""
        SELECT 
            v.id,
            v.patente,
            v.marca,
            v.modelo,
            v.anio,
            COALESCE(p.nombre || ' ' || p.apellido, u.email, 'Sin conductor') as conductor_nombre,
            COALESCE(COUNT(vs.id), 0) as total_viajes,
            COALESCE(SUM(vs.precio_final), 0) as total_ingresos,
            COALESCE(SUM(g.monto), 0) as total_gastos
        FROM fleet.vehiculo v
        LEFT JOIN fleet.chofer_vehiculo cv ON cv.vehiculo_id = v.id AND cv.activo = true
        LEFT JOIN auth.usuario u ON u.id = cv.usuario_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN trip.viaje_solicitado vs ON vs.vehiculo_id = v.id 
            AND vs.estado = 'finalizado'
            AND vs.created_at::date BETWEEN :fecha_desde AND :fecha_hasta
        LEFT JOIN fleet.gasto_vehiculo g ON g.vehiculo_id = v.id 
            AND g.fecha_gasto BETWEEN :fecha_desde AND :fecha_hasta
        WHERE v.control_base_id = :tenant_id AND v.activo = true
        GROUP BY v.id, v.patente, v.marca, v.modelo, v.anio, conductor_nombre
        ORDER BY total_ingresos DESC
    """)
    
    result = await db.execute(query, {
        "tenant_id": control_base_id,
        "fecha_desde": fecha_desde_obj,
        "fecha_hasta": fecha_hasta_obj
    })
    rows = result.all()
    
    return {
        "success": True,
        "periodo": {
            "desde": fecha_desde_obj.isoformat(),
            "hasta": fecha_hasta_obj.isoformat()
        },
        "vehiculos": [
            {
                "id": str(row[0]),
                "patente": row[1],
                "marca": row[2],
                "modelo": row[3],
                "anio": row[4],
                "conductor": row[5],
                "total_viajes": row[6] or 0,
                "total_ingresos": format_currency(float(row[7] or 0)),
                "total_gastos": format_currency(float(row[8] or 0)),
                "utilidad": format_currency(float(row[7] or 0) - float(row[8] or 0)),
                "margen": format_percentage(
                    ((float(row[7] or 0) - float(row[8] or 0)) / float(row[7] or 0) * 100) 
                    if float(row[7] or 0) > 0 else 0
                )
            }
            for row in rows
        ]
    }


@router.get("/tenant/vehiculo/{vehiculo_id}")
async def tenant_vehiculo_detalle(
    vehiculo_id: UUID,
    fecha_desde: Optional[str] = Query(None, description="YYYY-MM-DD"),
    fecha_hasta: Optional[str] = Query(None, description="YYYY-MM-DD"),
    current_user: tuple = Depends(get_admin_tenant_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reporte detallado por vehículo (formato imagen)
    """
    user_id, control_base_id, email, tipo_usuario = current_user
    
    hoy = date.today()
    if not fecha_desde and not fecha_hasta:
        fecha_desde = (hoy - timedelta(days=30)).isoformat()
        fecha_hasta = hoy.isoformat()
    
    try:
        fecha_desde_obj = date.fromisoformat(fecha_desde)
        fecha_hasta_obj = date.fromisoformat(fecha_hasta)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    check_query = text("""
        SELECT id, patente, marca, modelo, anio FROM fleet.vehiculo
        WHERE id = :vehiculo_id AND control_base_id = :tenant_id AND activo = true
    """)
    check_result = await db.execute(check_query, {
        "vehiculo_id": vehiculo_id,
        "tenant_id": control_base_id
    })
    vehiculo_row = check_result.first()
    
    if not vehiculo_row:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    conductor_query = text("""
        SELECT COALESCE(p.nombre || ' ' || p.apellido, u.email, 'Sin conductor') as conductor_nombre
        FROM fleet.chofer_vehiculo cv
        LEFT JOIN auth.usuario u ON u.id = cv.usuario_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE cv.vehiculo_id = :vehiculo_id AND cv.activo = true
        ORDER BY cv.updated_at DESC
        LIMIT 1
    """)
    conductor_result = await db.execute(conductor_query, {"vehiculo_id": vehiculo_id})
    conductor_row = conductor_result.first()
    conductor_nombre = conductor_row[0] if conductor_row else "Sin conductor"
    
    ingresos_query = text("""
        SELECT 
            COUNT(*) as total_viajes,
            COALESCE(SUM(precio_final), 0) as total_ingresos,
            COALESCE(AVG(precio_final), 0) as promedio_viaje
        FROM trip.viaje_solicitado
        WHERE vehiculo_id = :vehiculo_id 
          AND estado = 'finalizado'
          AND created_at::date BETWEEN :fecha_desde AND :fecha_hasta
    """)
    ingresos_result = await db.execute(ingresos_query, {
        "vehiculo_id": vehiculo_id,
        "fecha_desde": fecha_desde_obj,
        "fecha_hasta": fecha_hasta_obj
    })
    ingresos_row = ingresos_result.first()
    
    total_viajes = ingresos_row[0] or 0
    ingresos_brutos = float(ingresos_row[1] or 0)
    promedio_viaje = float(ingresos_row[2] or 0)
    
    gastos_query = text("""
        SELECT 
            tipo_gasto,
            COALESCE(SUM(monto), 0) as total
        FROM fleet.gasto_vehiculo
        WHERE vehiculo_id = :vehiculo_id 
          AND fecha_gasto BETWEEN :fecha_desde AND :fecha_hasta
        GROUP BY tipo_gasto
        ORDER BY total DESC
    """)
    gastos_result = await db.execute(gastos_query, {
        "vehiculo_id": vehiculo_id,
        "fecha_desde": fecha_desde_obj,
        "fecha_hasta": fecha_hasta_obj
    })
    gastos_rows = gastos_result.all()
    
    gastos = {}
    total_gastos = 0
    for row in gastos_rows:
        gastos[row[0]] = float(row[1] or 0)
        total_gastos += float(row[1] or 0)
    
    config = await obtener_configuracion_tenant(db, control_base_id)
    porcentaje_taxip = config.get("porcentaje_taxip_por_viaje", 1.5)
    
    comision_plataforma = ingresos_brutos * (porcentaje_taxip / 100)
    ingresos_netos = ingresos_brutos - comision_plataforma
    utilidad_neta = ingresos_netos - total_gastos
    margen = (utilidad_neta / ingresos_brutos * 100) if ingresos_brutos > 0 else 0
    
    benchmark_query = text("""
        SELECT 
            COALESCE(AVG(vs.precio_final), 0) as avg_ingreso,
            COUNT(vs.id) as total_viajes
        FROM fleet.vehiculo v
        JOIN trip.viaje_solicitado vs ON vs.vehiculo_id = v.id
        WHERE v.control_base_id = :tenant_id 
          AND v.id != :vehiculo_id
          AND vs.estado = 'finalizado'
          AND vs.created_at::date BETWEEN :fecha_desde AND :fecha_hasta
    """)
    benchmark_result = await db.execute(benchmark_query, {
        "tenant_id": control_base_id,
        "vehiculo_id": vehiculo_id,
        "fecha_desde": fecha_desde_obj,
        "fecha_hasta": fecha_hasta_obj
    })
    benchmark_row = benchmark_result.first()
    
    avg_flota = float(benchmark_row[0] or 0)
    viajes_flota = int(benchmark_row[1] or 0)
    
    comparacion = "similar"
    if avg_flota > 0 and viajes_flota > 0:
        if promedio_viaje > avg_flota * 1.1:
            comparacion = "superior"
        elif promedio_viaje < avg_flota * 0.9:
            comparacion = "inferior"
    
    return {
        "success": True,
        "vehiculo": {
            "id": str(vehiculo_row[0]),
            "patente": vehiculo_row[1],
            "marca": vehiculo_row[2],
            "modelo": vehiculo_row[3],
            "anio": vehiculo_row[4],
            "conductor": conductor_nombre
        },
        "periodo": {
            "mes": fecha_desde_obj.strftime("%B"),
            "anio": fecha_desde_obj.year,
            "desde": fecha_desde_obj.isoformat(),
            "hasta": fecha_hasta_obj.isoformat()
        },
        "ingresos": {
            "viajes": total_viajes,
            "brutos": format_currency(ingresos_brutos),
            "comision_plataforma": format_currency(comision_plataforma),
            "netos": format_currency(ingresos_netos)
        },
        "gastos": {
            "combustible": format_currency(gastos.get("combustible", 0)),
            "mantenimiento": format_currency(gastos.get("mantenimiento", 0) + gastos.get("reparacion", 0)),
            "seguro": format_currency(gastos.get("seguro", 0)),
            "impuestos": format_currency(gastos.get("impuesto", 0) + gastos.get("patente", 0)),
            "otros": format_currency(gastos.get("otros", 0)),
            "total": format_currency(total_gastos)
        },
        "rentabilidad": {
            "margen_neto": format_currency(utilidad_neta),
            "margen_porcentaje": format_percentage(margen)
        },
        "benchmarking": {
            "promedio_flota": format_currency(avg_flota),
            "viajes_flota": viajes_flota,
            "comparacion": comparacion
        }
    }


@router.get("/tenant/medios-pago")
async def tenant_medios_pago(
    fecha_desde: Optional[str] = Query(None, description="YYYY-MM-DD"),
    fecha_hasta: Optional[str] = Query(None, description="YYYY-MM-DD"),
    current_user: tuple = Depends(get_admin_tenant_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Distribución de medios de pago del tenant
    """
    user_id, control_base_id, email, tipo_usuario = current_user
    
    hoy = date.today()
    if not fecha_desde and not fecha_hasta:
        fecha_desde = (hoy - timedelta(days=30)).isoformat()
        fecha_hasta = hoy.isoformat()
    
    try:
        fecha_desde_obj = date.fromisoformat(fecha_desde)
        fecha_hasta_obj = date.fromisoformat(fecha_hasta)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    query = text("""
        WITH medios_base AS (
            SELECT unnest(ARRAY['efectivo', 'transferencia', 'qr', 'debito', 'credito']) as medio_pago
        )
        SELECT 
            mb.medio_pago,
            COALESCE(COUNT(vs.id), 0) as total_viajes,
            COALESCE(SUM(vs.precio_final), 0) as total_ingresos
        FROM medios_base mb
        LEFT JOIN trip.viaje_solicitado vs ON 
            COALESCE(
                (SELECT mp.nombre 
                 FROM payment.transaccion t 
                 JOIN payment.metodo_pago mp ON mp.id = t.metodo_pago_id 
                 WHERE t.viaje_id = vs.id 
                 LIMIT 1), 
                'efectivo'
            ) = mb.medio_pago
            AND vs.control_base_id = :tenant_id
            AND vs.estado = 'finalizado'
            AND vs.created_at::date BETWEEN :fecha_desde AND :fecha_hasta
        GROUP BY mb.medio_pago
        ORDER BY total_ingresos DESC
    """)
    
    result = await db.execute(query, {
        "tenant_id": control_base_id,
        "fecha_desde": fecha_desde_obj,
        "fecha_hasta": fecha_hasta_obj
    })
    rows = result.all()
    
    total_ingresos = sum(float(r[2] or 0) for r in rows)
    
    return {
        "success": True,
        "periodo": {
            "desde": fecha_desde_obj.isoformat(),
            "hasta": fecha_hasta_obj.isoformat()
        },
        "medios": [
            {
                "medio_pago": row[0],
                "total_viajes": row[1] or 0,
                "total_ingresos": format_currency(float(row[2] or 0)),
                "porcentaje": format_percentage(
                    (float(row[2] or 0) / total_ingresos * 100) 
                    if total_ingresos > 0 else 0
                )
            }
            for row in rows
        ]
    }


@router.get("/tenant/gastos")
async def tenant_gastos(
    fecha_desde: Optional[str] = Query(None, description="YYYY-MM-DD"),
    fecha_hasta: Optional[str] = Query(None, description="YYYY-MM-DD"),
    current_user: tuple = Depends(get_admin_tenant_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Gastos operativos por categoría del tenant
    """
    user_id, control_base_id, email, tipo_usuario = current_user
    
    hoy = date.today()
    if not fecha_desde and not fecha_hasta:
        fecha_desde = (hoy - timedelta(days=30)).isoformat()
        fecha_hasta = hoy.isoformat()
    
    try:
        fecha_desde_obj = date.fromisoformat(fecha_desde)
        fecha_hasta_obj = date.fromisoformat(fecha_hasta)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    query = text("""
        SELECT 
            g.tipo_gasto,
            COALESCE(SUM(g.monto), 0) as total
        FROM fleet.gasto_vehiculo g
        JOIN fleet.vehiculo v ON v.id = g.vehiculo_id
        WHERE v.control_base_id = :tenant_id 
          AND g.fecha_gasto BETWEEN :fecha_desde AND :fecha_hasta
        GROUP BY g.tipo_gasto
        ORDER BY total DESC
    """)
    
    result = await db.execute(query, {
        "tenant_id": control_base_id,
        "fecha_desde": fecha_desde_obj,
        "fecha_hasta": fecha_hasta_obj
    })
    rows = result.all()
    
    total_gastos = sum(float(r[1] or 0) for r in rows)
    
    return {
        "success": True,
        "periodo": {
            "desde": fecha_desde_obj.isoformat(),
            "hasta": fecha_hasta_obj.isoformat()
        },
        "gastos": [
            {
                "tipo_gasto": row[0] or "otros",
                "total": format_currency(float(row[1] or 0)),
                "porcentaje": format_percentage(
                    (float(row[1] or 0) / total_gastos * 100) 
                    if total_gastos > 0 else 0
                )
            }
            for row in rows
        ],
        "total_gastos": format_currency(total_gastos)
    }


@router.get("/health")
async def admin_health():
    """
    Health check del panel administrativo
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }