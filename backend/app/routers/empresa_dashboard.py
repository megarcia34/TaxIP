"""
Dashboard para Empresas Corporativas
KPIs, estadísticas, viajes, facturación y gestión de empleados
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.dependencies import (
    get_current_empresa_user,
    get_current_empresa_admin_user,
    get_empresa_context
)

router = APIRouter(prefix="/api/empresa/dashboard", tags=["Empresa Dashboard"])





# ============================================
# 1. KPI - Resumen General
# ============================================

@router.get("/kpis")
async def get_empresa_kpis(
    empresa_context: dict = Depends(get_empresa_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener KPIs del dashboard de la empresa
    """
    empresa_id = UUID(empresa_context["empresa_id"])
    control_base_id = UUID(empresa_context["control_base_id"])
    
    query = text("""
        SELECT 
            -- Viajes totales
            COUNT(vs.id) as total_viajes,
            
            -- Viajes hoy
            COUNT(CASE WHEN DATE(vs.created_at) = CURRENT_DATE THEN 1 END) as viajes_hoy,
            
            -- Viajes este mes
            COUNT(CASE WHEN DATE_TRUNC('month', vs.created_at) = DATE_TRUNC('month', CURRENT_DATE) THEN 1 END) as viajes_mes,
            
            -- Viajes pendientes
            COUNT(CASE WHEN vs.estado IN ('pendiente', 'aceptado') THEN 1 END) as viajes_pendientes,
            
            -- Viajes en curso
            COUNT(CASE WHEN vs.estado = 'en_curso' THEN 1 END) as viajes_en_curso,
            
            -- Viajes completados
            COUNT(CASE WHEN vs.estado = 'finalizado' THEN 1 END) as viajes_completados,
            
            -- Viajes cancelados
            COUNT(CASE WHEN vs.estado = 'cancelado' THEN 1 END) as viajes_cancelados,
            
            -- Gasto total
            COALESCE(SUM(vs.precio_final), 0) as total_gastado,
            
            -- Gasto hoy
            COALESCE(SUM(CASE WHEN DATE(vs.created_at) = CURRENT_DATE THEN vs.precio_final END), 0) as gasto_hoy,
            
            -- Gasto este mes
            COALESCE(SUM(CASE WHEN DATE_TRUNC('month', vs.created_at) = DATE_TRUNC('month', CURRENT_DATE) THEN vs.precio_final END), 0) as gasto_mes,
            
            -- Empleados activos
            COUNT(DISTINCT ue.usuario_id) as empleados_activos,
            
            -- Promedio por viaje
            COALESCE(AVG(vs.precio_final), 0) as promedio_viaje
        FROM tenant.empresa e
        LEFT JOIN trip.viaje_solicitado vs ON vs.empresa_id = e.id
        LEFT JOIN auth.usuario_empresa ue ON ue.empresa_id = e.id AND ue.activo = true
        WHERE e.id = :empresa_id AND e.control_base_id = :control_base_id
        GROUP BY e.id
    """)
    
    result = await db.execute(query, {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id
    })
    row = result.first()
    
    if not row:
        return {
            "total_viajes": 0,
            "viajes_hoy": 0,
            "viajes_mes": 0,
            "viajes_pendientes": 0,
            "viajes_en_curso": 0,
            "viajes_completados": 0,
            "viajes_cancelados": 0,
            "total_gastado": 0.0,
            "gasto_hoy": 0.0,
            "gasto_mes": 0.0,
            "empleados_activos": 0,
            "promedio_viaje": 0.0
        }
    
    return {
        "total_viajes": row[0] or 0,
        "viajes_hoy": row[1] or 0,
        "viajes_mes": row[2] or 0,
        "viajes_pendientes": row[3] or 0,
        "viajes_en_curso": row[4] or 0,
        "viajes_completados": row[5] or 0,
        "viajes_cancelados": row[6] or 0,
        "total_gastado": float(row[7] or 0),
        "gasto_hoy": float(row[8] or 0),
        "gasto_mes": float(row[9] or 0),
        "empleados_activos": row[10] or 0,
        "promedio_viaje": float(row[11] or 0)
    }


# ============================================
# 2. Solicitar Viaje Corporativo
# ============================================

@router.post("/viajes/solicitar")
async def solicitar_viaje_corporativo(
    data: dict,
    empresa_context: dict = Depends(get_empresa_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Solicitar un viaje para un pasajero de la empresa
    (Recepcionista o admin de empresa)
    """
    user_id = UUID(empresa_context["user_id"])
    empresa_id = UUID(empresa_context["empresa_id"])
    control_base_id = UUID(empresa_context["control_base_id"])
    empresa_nombre = empresa_context["empresa_nombre"]
    
    # Validar campos requeridos
    required_fields = ["direccion_origen", "direccion_destino", "origen_lat", "origen_lng", "destino_lat", "destino_lng"]
    for field in required_fields:
        if field not in data or data[field] is None:
            raise HTTPException(status_code=400, detail=f"Campo '{field}' es requerido")
    
    # Crear viaje
    insert_query = text("""
        INSERT INTO trip.viaje_solicitado (
            id, control_base_id, empresa_id, pasajero_id,
            direccion_origen, direccion_destino,
            origen, destino,
            nombre_pasajero, notas, estado, created_at
        )
        VALUES (
            gen_random_uuid(), :control_base_id, :empresa_id, :pasajero_id,
            :direccion_origen, :direccion_destino,
            ST_SetSRID(ST_MakePoint(:origen_lng, :origen_lat), 4326)::geography,
            ST_SetSRID(ST_MakePoint(:destino_lng, :destino_lat), 4326)::geography,
            :nombre_pasajero, :notas, 'pendiente', NOW()
        )
        RETURNING id
    """)
    
    result = await db.execute(insert_query, {
        "control_base_id": control_base_id,
        "empresa_id": empresa_id,
        "pasajero_id": user_id,
        "direccion_origen": data["direccion_origen"],
        "direccion_destino": data["direccion_destino"],
        "origen_lat": data["origen_lat"],
        "origen_lng": data["origen_lng"],
        "destino_lat": data["destino_lat"],
        "destino_lng": data["destino_lng"],
        "nombre_pasajero": data.get("nombre_pasajero", ""),
        "notas": data.get("notas", "")
    })
    
    await db.commit()
    viaje_id = result.first()[0]
    
    return {
        "success": True,
        "viaje_id": str(viaje_id),
        "mensaje": f"Viaje solicitado exitosamente para {empresa_nombre}",
        "estado": "pendiente"
    }


# ============================================
# 3. Listar Viajes de la Empresa
# ============================================

@router.get("/viajes")
async def listar_viajes_empresa_dashboard(
    estado: Optional[str] = None,
    desde: Optional[str] = None,
    hasta: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    empresa_context: dict = Depends(get_empresa_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar todos los viajes de la empresa con filtros
    """
    empresa_id = UUID(empresa_context["empresa_id"])
    control_base_id = UUID(empresa_context["control_base_id"])
    
    params = {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id,
        "limit": limit,
        "offset": offset
    }
    
    filters = ["vs.empresa_id = :empresa_id", "vs.control_base_id = :control_base_id"]
    
    if estado:
        filters.append("vs.estado = :estado")
        params["estado"] = estado
    
    if desde:
        filters.append("vs.created_at >= :desde")
        params["desde"] = desde
    
    if hasta:
        filters.append("vs.created_at <= :hasta")
        params["hasta"] = hasta
    
    where_clause = " AND ".join(filters)
    
    query = text(f"""
        SELECT 
            vs.id,
            vs.estado,
            vs.direccion_origen,
            vs.direccion_destino,
            vs.precio_final,
            vs.created_at,
            vs.finalizado_en,
            vs.nombre_pasajero,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre,
            v.patente,
            vs.distancia_metros,
            vs.tiempo_estimado_segundos
        FROM trip.viaje_solicitado vs
        LEFT JOIN auth.usuario u ON u.id = vs.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id
        WHERE {where_clause}
        ORDER BY vs.created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    
    result = await db.execute(query, params)
    rows = result.all()
    
    return [
        {
            "id": str(row[0]),
            "estado": row[1],
            "origen": row[2],
            "destino": row[3],
            "precio_final": float(row[4]) if row[4] else None,
            "created_at": row[5],
            "finalizado_en": row[6],
            "pasajero_nombre": row[7],
            "chofer_nombre": row[8],
            "patente": row[9],
            "distancia_metros": row[10],
            "tiempo_estimado": row[11]
        }
        for row in rows
    ]


# ============================================
# 4. Obtener Detalle de Viaje
# ============================================

@router.get("/viajes/{viaje_id}")
async def get_viaje_detalle(
    viaje_id: str,
    empresa_context: dict = Depends(get_empresa_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalle de un viaje específico de la empresa
    """
    empresa_id = UUID(empresa_context["empresa_id"])
    control_base_id = UUID(empresa_context["control_base_id"])
    
    query = text("""
        SELECT 
            vs.id,
            vs.estado,
            vs.direccion_origen,
            vs.direccion_destino,
            vs.precio_final,
            vs.precio_estimado,
            vs.created_at,
            vs.aceptado_en,
            vs.iniciado_en,
            vs.finalizado_en,
            vs.nombre_pasajero,
            vs.notas,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre,
            v.patente,
            v.marca,
            v.modelo,
            vs.distancia_metros,
            vs.tiempo_estimado_segundos,
            ST_Y(vs.origen::geometry) as origen_lat,
            ST_X(vs.origen::geometry) as origen_lng,
            ST_Y(vs.destino::geometry) as destino_lat,
            ST_X(vs.destino::geometry) as destino_lng
        FROM trip.viaje_solicitado vs
        LEFT JOIN auth.usuario u ON u.id = vs.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id
        WHERE vs.id = :viaje_id 
          AND vs.empresa_id = :empresa_id
          AND vs.control_base_id = :control_base_id
    """)
    
    result = await db.execute(query, {
        "viaje_id": UUID(viaje_id),
        "empresa_id": empresa_id,
        "control_base_id": control_base_id
    })
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    
    return {
        "id": str(row[0]),
        "estado": row[1],
        "origen": row[2],
        "destino": row[3],
        "precio_final": float(row[4]) if row[4] else None,
        "precio_estimado": float(row[5]) if row[5] else None,
        "created_at": row[6],
        "aceptado_en": row[7],
        "iniciado_en": row[8],
        "finalizado_en": row[9],
        "pasajero_nombre": row[10],
        "notas": row[11],
        "chofer_nombre": row[12],
        "vehiculo": {
            "patente": row[13],
            "marca": row[14],
            "modelo": row[15]
        } if row[13] else None,
        "distancia_metros": row[16],
        "tiempo_estimado_segundos": row[17],
        "ubicacion": {
            "origen_lat": float(row[18]) if row[18] else None,
            "origen_lng": float(row[19]) if row[19] else None,
            "destino_lat": float(row[20]) if row[20] else None,
            "destino_lng": float(row[21]) if row[21] else None
        }
    }


# ============================================
# 5. Estadísticas de Viajes por Mes
# ============================================

@router.get("/estadisticas/mensual")
async def get_estadisticas_mensuales(
    meses: int = 6,
    empresa_context: dict = Depends(get_empresa_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener estadísticas mensuales de viajes y gastos
    """
    empresa_id = UUID(empresa_context["empresa_id"])
    control_base_id = UUID(empresa_context["control_base_id"])
    
    fecha_limite = datetime.now() - timedelta(days=meses * 30)
    
    query = text("""
        SELECT 
            TO_CHAR(DATE_TRUNC('month', vs.created_at), 'YYYY-MM') as mes,
            DATE_TRUNC('month', vs.created_at) as fecha_mes,
            COUNT(vs.id) as total_viajes,
            COUNT(CASE WHEN vs.estado = 'finalizado' THEN 1 END) as viajes_completados,
            COUNT(CASE WHEN vs.estado = 'cancelado' THEN 1 END) as viajes_cancelados,
            COALESCE(SUM(vs.precio_final), 0) as gasto_total,
            COALESCE(AVG(vs.precio_final), 0) as promedio_gasto
        FROM trip.viaje_solicitado vs
        WHERE vs.empresa_id = :empresa_id
          AND vs.control_base_id = :control_base_id
          AND vs.created_at > :fecha_limite
        GROUP BY DATE_TRUNC('month', vs.created_at)
        ORDER BY fecha_mes DESC
    """)
    
    result = await db.execute(query, {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id,
        "fecha_limite": fecha_limite
    })
    rows = result.all()
    
    return [
        {
            "mes": row[0],
            "fecha": row[1],
            "total_viajes": row[2] or 0,
            "viajes_completados": row[3] or 0,
            "viajes_cancelados": row[4] or 0,
            "gasto_total": float(row[5] or 0),
            "promedio_gasto": float(row[6] or 0)
        }
        for row in rows
    ]


# ============================================
# 6. Top Viajes (Más frecuentes)
# ============================================

@router.get("/estadisticas/top-destinos")
async def get_top_destinos(
    limit: int = 10,
    empresa_context: dict = Depends(get_empresa_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener los destinos más frecuentes de la empresa
    """
    empresa_id = UUID(empresa_context["empresa_id"])
    control_base_id = UUID(empresa_context["control_base_id"])
    
    query = text("""
        SELECT 
            vs.direccion_destino as destino,
            COUNT(vs.id) as total_viajes,
            COALESCE(SUM(vs.precio_final), 0) as gasto_total,
            COALESCE(AVG(vs.precio_final), 0) as promedio_gasto
        FROM trip.viaje_solicitado vs
        WHERE vs.empresa_id = :empresa_id 
          AND vs.control_base_id = :control_base_id
          AND vs.estado = 'finalizado'
          AND vs.direccion_destino IS NOT NULL
        GROUP BY vs.direccion_destino
        ORDER BY total_viajes DESC
        LIMIT :limit
    """)
    
    result = await db.execute(query, {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id,
        "limit": limit
    })
    rows = result.all()
    
    return [
        {
            "destino": row[0],
            "total_viajes": row[1] or 0,
            "gasto_total": float(row[2] or 0),
            "promedio_gasto": float(row[3] or 0)
        }
        for row in rows
    ]


# ============================================
# 7. Empleados de la Empresa
# ============================================

@router.get("/empleados")
async def get_empleados_empresa_dashboard(
    activo: Optional[bool] = None,
    empresa_context: dict = Depends(get_empresa_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar empleados de la empresa
    """
    empresa_id = UUID(empresa_context["empresa_id"])
    control_base_id = UUID(empresa_context["control_base_id"])
    
    params = {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id
    }
    
    filtro_activo = ""
    if activo is not None:
        filtro_activo = "AND ue.activo = :activo"
        params["activo"] = activo
    
    query = text(f"""
        SELECT 
            u.id,
            u.email,
            p.nombre,
            p.apellido,
            p.telefono,
            ue.rol,
            ue.activo,
            u.created_at,
            COUNT(vs.id) as viajes_realizados,
            COALESCE(SUM(vs.precio_final), 0) as gasto_total
        FROM auth.usuario_empresa ue
        JOIN auth.usuario u ON u.id = ue.usuario_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN trip.viaje_solicitado vs ON vs.pasajero_id = u.id 
            AND vs.empresa_id = :empresa_id
        WHERE ue.empresa_id = :empresa_id
          AND u.control_base_id = :control_base_id
          {filtro_activo}
        GROUP BY u.id, u.email, p.nombre, p.apellido, p.telefono, ue.rol, ue.activo, u.created_at
        ORDER BY u.created_at DESC
    """)
    
    result = await db.execute(query, params)
    rows = result.all()
    
    return [
        {
            "id": str(row[0]),
            "email": row[1],
            "nombre": row[2] or "",
            "apellido": row[3] or "",
            "telefono": row[4],
            "rol": row[5] or "recepcionista",
            "activo": row[6],
            "created_at": row[7],
            "viajes_realizados": row[8] or 0,
            "gasto_total": float(row[9] or 0)
        }
        for row in rows
    ]


# ============================================
# 8. Crear Empleado (Admin de Empresa)
# ============================================

@router.post("/empleados")
async def crear_empleado_empresa(
    data: dict,
    empresa_context: dict = Depends(get_empresa_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Crear un nuevo empleado para la empresa
    (Solo admin de empresa)
    """
    from app.core.security import get_password_hash
    
    empresa_id = UUID(empresa_context["empresa_id"])
    control_base_id = UUID(empresa_context["control_base_id"])
    
    # Validar campos requeridos
    required_fields = ["email", "password", "nombre", "apellido"]
    for field in required_fields:
        if field not in data or not data[field]:
            raise HTTPException(status_code=400, detail=f"Campo '{field}' es requerido")
    
    # Verificar que el email no exista
    check_query = text("SELECT id FROM auth.usuario WHERE email = :email")
    result = await db.execute(check_query, {"email": data["email"]})
    if result.first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # Crear usuario
    usuario_id = UUID(int=0)  # Placeholder
    
    # Obtener tipo_usuario_id para 'empleado'
    tipo_query = text("SELECT id FROM auth.tipo_usuario WHERE nombre = 'empleado'")
    tipo_result = await db.execute(tipo_query)
    tipo_id = tipo_result.first()
    
    if not tipo_id:
        # Si no existe 'empleado', usar 'pasajero'
        tipo_query = text("SELECT id FROM auth.tipo_usuario WHERE nombre = 'pasajero'")
        tipo_result = await db.execute(tipo_query)
        tipo_id = tipo_result.first()
    
    insert_user = text("""
        INSERT INTO auth.usuario (id, tipo_usuario_id, control_base_id, email, password_hash, activo, created_at)
        VALUES (gen_random_uuid(), :tipo_id, :control_base_id, :email, :password_hash, true, NOW())
        RETURNING id
    """)
    
    result = await db.execute(insert_user, {
        "tipo_id": tipo_id[0],
        "control_base_id": control_base_id,
        "email": data["email"],
        "password_hash": get_password_hash(data["password"])
    })
    usuario_id = result.first()[0]
    
    # Crear perfil
    insert_perfil = text("""
        INSERT INTO auth.perfil_general (id, usuario_id, nombre, apellido, telefono, created_at)
        VALUES (gen_random_uuid(), :user_id, :nombre, :apellido, :telefono, NOW())
    """)
    
    await db.execute(insert_perfil, {
        "user_id": usuario_id,
        "nombre": data["nombre"],
        "apellido": data["apellido"],
        "telefono": data.get("telefono")
    })
    
    # Crear relación empresa-usuario
    insert_relacion = text("""
        INSERT INTO auth.usuario_empresa (id, empresa_id, usuario_id, rol, activo, created_at)
        VALUES (gen_random_uuid(), :empresa_id, :usuario_id, :rol, true, NOW())
    """)
    
    await db.execute(insert_relacion, {
        "empresa_id": empresa_id,
        "usuario_id": usuario_id,
        "rol": data.get("rol", "recepcionista")
    })
    
    await db.commit()
    
    return {
        "success": True,
        "mensaje": f"Empleado {data['nombre']} {data['apellido']} creado exitosamente",
        "usuario_id": str(usuario_id)
    }


# ============================================
# 9. Facturas de la Empresa
# ============================================

@router.get("/facturas")
async def get_facturas_empresa_dashboard(
    estado: Optional[str] = None,
    empresa_context: dict = Depends(get_empresa_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar facturas de la empresa
    """
    empresa_id = UUID(empresa_context["empresa_id"])
    control_base_id = UUID(empresa_context["control_base_id"])
    
    params = {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id
    }
    
    filtro_estado = ""
    if estado:
        filtro_estado = "AND f.estado = :estado"
        params["estado"] = estado
    
    query = text(f"""
        SELECT 
            f.id,
            f.periodo,
            f.total,
            f.descuento,
            f.total_final,
            f.estado,
            f.pdf_url,
            f.created_at,
            f.pagada_at
        FROM payment.factura_empresa f
        WHERE f.empresa_id = :empresa_id
        {filtro_estado}
        ORDER BY f.periodo DESC
    """)
    
    result = await db.execute(query, params)
    rows = result.all()
    
    return [
        {
            "id": str(row[0]),
            "periodo": row[1],
            "total": float(row[2] or 0),
            "descuento": float(row[3] or 0),
            "total_final": float(row[4] or 0),
            "estado": row[5] or "pendiente",
            "pdf_url": row[6],
            "created_at": row[7],
            "pagada_at": row[8]
        }
        for row in rows
    ]


# ============================================
# 10. Resumen de Cuenta Corriente
# ============================================

@router.get("/cuenta-corriente")
async def get_cuenta_corriente_empresa(
    empresa_context: dict = Depends(get_empresa_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener resumen de cuenta corriente de la empresa
    """
    empresa_id = UUID(empresa_context["empresa_id"])
    control_base_id = UUID(empresa_context["control_base_id"])
    
    query = text("""
        SELECT 
            e.id,
            e.nombre,
            e.limite_credito,
            COALESCE(SUM(vs.precio_final), 0) as deuda_total,
            COUNT(CASE WHEN vs.estado IN ('pendiente', 'aceptado', 'en_curso') THEN 1 END) as viajes_pendientes,
            COUNT(CASE WHEN f.estado = 'pendiente' THEN 1 END) as facturas_pendientes,
            COALESCE(SUM(CASE WHEN f.estado = 'pagada' THEN f.total_final END), 0) as total_pagado
        FROM tenant.empresa e
        LEFT JOIN trip.viaje_solicitado vs ON vs.empresa_id = e.id AND vs.estado != 'cancelado'
        LEFT JOIN payment.factura_empresa f ON f.empresa_id = e.id
        WHERE e.id = :empresa_id AND e.control_base_id = :control_base_id
        GROUP BY e.id, e.nombre, e.limite_credito
    """)
    
    result = await db.execute(query, {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id
    })
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    deuda_total = float(row[3] or 0)
    limite_credito = float(row[2] or 0)
    total_pagado = float(row[6] or 0)
    
    return {
        "empresa_id": str(row[0]),
        "empresa_nombre": row[1],
        "limite_credito": limite_credito,
        "saldo_disponible": limite_credito - deuda_total,
        "deuda_total": deuda_total,
        "total_pagado": total_pagado,
        "viajes_pendientes": row[4] or 0,
        "facturas_pendientes": row[5] or 0
    }

# ============================================
# 11. REGISTRAR PAGO (Admin Empresa)
# ============================================

@router.post("/cuenta-corriente/pagar")
async def registrar_pago_empresa(
    data: dict,
    empresa_context: dict = Depends(get_empresa_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Registrar un pago a cuenta corriente (Admin Empresa)
    """
    empresa_id = UUID(empresa_context["empresa_id"])
    control_base_id = UUID(empresa_context["control_base_id"])
    user_id = UUID(empresa_context["user_id"])
    empresa_nombre = empresa_context["empresa_nombre"]
    
    # Validar campos requeridos
    required_fields = ["monto", "metodo_pago"]
    for field in required_fields:
        if field not in data or data[field] is None:
            raise HTTPException(status_code=400, detail=f"Campo '{field}' es requerido")
    
    monto = float(data["monto"])
    metodo_pago = data["metodo_pago"]
    referencia = data.get("referencia")
    factura_id = data.get("factura_id")
    observaciones = data.get("observaciones")
    comprobante_url = data.get("comprobante_url")
    
    # Validar monto
    if monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")
    
    # Validar método de pago
    metodos_validos = ["transferencia", "efectivo", "tarjeta", "deposito", "otros"]
    if metodo_pago not in metodos_validos:
        raise HTTPException(status_code=400, detail=f"Método de pago inválido. Permitidos: {metodos_validos}")
    
    # Obtener deuda actual
    query_deuda = text("""
        SELECT 
            COALESCE(SUM(vs.precio_final), 0) as deuda_total
        FROM tenant.empresa e
        LEFT JOIN trip.viaje_solicitado vs ON vs.empresa_id = e.id AND vs.estado != 'cancelado'
        WHERE e.id = :empresa_id AND e.control_base_id = :control_base_id
        GROUP BY e.id
    """)
    result_deuda = await db.execute(query_deuda, {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id
    })
    deuda_row = result_deuda.first()
    deuda_total = float(deuda_row[0]) if deuda_row else 0
    
    # Validar que el monto no supere la deuda
    if monto > deuda_total:
        raise HTTPException(
            status_code=400, 
            detail=f"El monto a pagar (${monto:.2f}) supera la deuda total (${deuda_total:.2f})"
        )
    
    # Insertar pago
    insert_query = text("""
        INSERT INTO payment.pago_empresa (
            id, empresa_id, monto, metodo_pago, referencia, 
            estado, comprobante_url, factura_id, observaciones, 
            fecha_pago, created_at
        )
        VALUES (
            gen_random_uuid(), :empresa_id, :monto, :metodo_pago, :referencia,
            'pendiente', :comprobante_url, :factura_id, :observaciones,
            NOW(), NOW()
        )
        RETURNING id
    """)
    
    result = await db.execute(insert_query, {
        "empresa_id": empresa_id,
        "monto": monto,
        "metodo_pago": metodo_pago,
        "referencia": referencia,
        "comprobante_url": comprobante_url,
        "factura_id": UUID(factura_id) if factura_id else None,
        "observaciones": observaciones
    })
    pago_id = result.first()[0]
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Pago registrado correctamente. Pendiente de confirmación.",
        "pago_id": str(pago_id),
        "monto": monto,
        "metodo_pago": metodo_pago,
        "estado": "pendiente"
    }


# ============================================
# 12. HISTORIAL DE PAGOS (Admin Empresa)
# ============================================

@router.get("/cuenta-corriente/historial-pagos")
async def get_historial_pagos_empresa(
    limit: int = 50,
    offset: int = 0,
    estado: Optional[str] = None,
    empresa_context: dict = Depends(get_empresa_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener historial de pagos de la empresa (Admin Empresa)
    """
    empresa_id = UUID(empresa_context["empresa_id"])
    control_base_id = UUID(empresa_context["control_base_id"])
    
    params = {
        "empresa_id": empresa_id,
        "control_base_id": control_base_id,
        "limit": limit,
        "offset": offset
    }
    
    filtro_estado = ""
    if estado:
        filtro_estado = "AND p.estado = :estado"
        params["estado"] = estado
    
    query = text(f"""
        SELECT 
            p.id,
            p.monto,
            p.metodo_pago,
            p.referencia,
            p.estado,
            p.comprobante_url,
            p.observaciones,
            p.fecha_pago,
            p.confirmado_en,
            p.created_at,
            f.periodo as factura_periodo,
            f.total_final as factura_total
        FROM payment.pago_empresa p
        LEFT JOIN payment.factura_empresa f ON f.id = p.factura_id
        WHERE p.empresa_id = :empresa_id
        {filtro_estado}
        ORDER BY p.fecha_pago DESC
        LIMIT :limit OFFSET :offset
    """)
    
    result = await db.execute(query, params)
    rows = result.all()
    
    return [
        {
            "id": str(row[0]),
            "monto": float(row[1]),
            "metodo_pago": row[2],
            "referencia": row[3],
            "estado": row[4] or "pendiente",
            "comprobante_url": row[5],
            "observaciones": row[6],
            "fecha_pago": row[7],
            "confirmado_en": row[8],
            "created_at": row[9],
            "factura": {
                "periodo": row[10],
                "total": float(row[11]) if row[11] else None
            } if row[10] else None
        }
        for row in rows
    ]


# ============================================
# 13. DESCARGAR COMPROBANTE (Admin Empresa)
# ============================================

@router.get("/cuenta-corriente/comprobante/{pago_id}")
async def descargar_comprobante_pago(
    pago_id: UUID,
    empresa_context: dict = Depends(get_empresa_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener información del comprobante de pago (Admin Empresa)
    """
    empresa_id = UUID(empresa_context["empresa_id"])
    control_base_id = UUID(empresa_context["control_base_id"])
    
    query = text("""
        SELECT 
            p.id,
            p.monto,
            p.metodo_pago,
            p.referencia,
            p.estado,
            p.comprobante_url,
            p.fecha_pago,
            p.confirmado_en,
            e.nombre as empresa_nombre,
            COALESCE(p.confirmado_por, p.fecha_pago) as confirmado_por
        FROM payment.pago_empresa p
        JOIN tenant.empresa e ON e.id = p.empresa_id
        WHERE p.id = :pago_id 
          AND p.empresa_id = :empresa_id
          AND e.control_base_id = :control_base_id
    """)
    
    result = await db.execute(query, {
        "pago_id": pago_id,
        "empresa_id": empresa_id,
        "control_base_id": control_base_id
    })
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    
    return {
        "id": str(row[0]),
        "monto": float(row[1]),
        "metodo_pago": row[2],
        "referencia": row[3],
        "estado": row[4] or "pendiente",
        "comprobante_url": row[5],
        "fecha_pago": row[6],
        "confirmado_en": row[7],
        "empresa_nombre": row[8],
        "confirmado_por": row[9]
    }