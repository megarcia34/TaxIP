# app/routers/propietario/turnos.py
"""
Propietario - Gestión de turnos de sus vehículos
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime, timedelta
import random
from app.database import get_db
from app.dependencies import get_propietario_context
from pydantic import BaseModel

router = APIRouter()


class ConfirmarLiquidacionRequest(BaseModel):
    observacion: Optional[str] = None


@router.get("/turnos")
async def listar_turnos(
    vehiculo_id: Optional[UUID] = None,
    estado: Optional[str] = None,
    desde: Optional[str] = None,
    hasta: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar turnos de los vehículos del propietario
    Los datos de recaudación se obtienen desde IngresoTurno (nueva fuente de verdad)
    """
    propietario_id = ctx["propietario_id"]
    
    filters = ["pv.propietario_id = :propietario_id"]
    params = {"propietario_id": propietario_id, "limit": limit, "offset": offset}
    
    if vehiculo_id:
        filters.append("t.vehiculo_id = :vehiculo_id")
        params["vehiculo_id"] = vehiculo_id
    
    if estado:
        filters.append("t.estado = :estado")
        params["estado"] = estado
    
    if desde:
        filters.append("t.inicio_turno >= :desde")
        params["desde"] = desde
    
    if hasta:
        filters.append("t.inicio_turno <= :hasta")
        params["hasta"] = hasta
    
    where_clause = " AND ".join(filters)
    
    # ============================================================
    # NUEVA CONSULTA: SIN CAMPOS LEGACY
    # Los datos de recaudación se obtienen desde IngresoTurno
    # ============================================================
    query = text(f"""
        SELECT 
            t.id,
            t.vehiculo_id,
            v.patente,
            v.marca,
            v.modelo,
            t.chofer_id,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre,
            t.estado,
            t.km_inicial,
            t.km_final,
            t.combustible_inicial,
            t.combustible_final,
            -- ✅ DATOS DESDE LIQUIDACION (fuente de verdad para montos)
            COALESCE(l.monto_bruto, 0) as monto_bruto,
            COALESCE(l.total_chofer, 0) as total_chofer,
            COALESCE(l.total_propietario, 0) as total_propietario,
            l.estado as estado_liquidacion,
            l.id as liquidacion_id,
            t.inicio_turno,
            t.fin_turno,
            c.tipo_contrato,
            c.porcentaje_chofer,
            c.monto_diario,
            -- ✅ RESUMEN DE INGRESOS DESDE INGRESO_TURNO
            COALESCE((
                SELECT SUM(it.monto) 
                FROM fleet.ingreso_turno it 
                WHERE it.turno_id = t.id AND it.estado = 'aprobado'
            ), 0) as total_ingresos_aprobados,
            COALESCE((
                SELECT SUM(it.monto) 
                FROM fleet.ingreso_turno it 
                WHERE it.turno_id = t.id AND it.estado = 'pendiente'
            ), 0) as total_ingresos_pendientes
        FROM fleet.turno_chofer t
        JOIN fleet.vehiculo v ON v.id = t.vehiculo_id
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        JOIN fleet.contrato_vehiculo c ON c.id = t.contrato_id
        JOIN auth.usuario u ON u.id = t.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN fleet.liquidacion l ON l.turno_id = t.id
        WHERE {where_clause}
        ORDER BY t.inicio_turno DESC
        LIMIT :limit OFFSET :offset
    """)
    
    result = await db.execute(query, params)
    rows = result.all()
    
    return [
        {
            "id": str(row[0]),
            "vehiculo_id": str(row[1]),
            "patente": row[2],
            "marca": row[3],
            "modelo": row[4],
            "chofer_id": str(row[5]),
            "chofer_nombre": row[6],
            "estado": row[7],
            "km_inicial": float(row[8]) if row[8] else None,
            "km_final": float(row[9]) if row[9] else None,
            "combustible_inicial": row[10],
            "combustible_final": row[11],
            # ✅ Datos desde liquidacion
            "monto_bruto": float(row[12]) if row[12] else 0,
            "total_chofer": float(row[13]) if row[13] else 0,
            "total_propietario": float(row[14]) if row[14] else 0,
            "estado_liquidacion": row[15],
            "liquidacion_id": str(row[16]) if row[16] else None,
            "inicio_turno": row[17],
            "fin_turno": row[18],
            "tipo_contrato": row[19],
            "porcentaje_chofer": float(row[20]) if row[20] else None,
            "monto_diario": float(row[21]) if row[21] else None,
            # ✅ Datos desde IngresoTurno
            "total_ingresos_aprobados": float(row[22]) if row[22] else 0,
            "total_ingresos_pendientes": float(row[23]) if row[23] else 0
        }
        for row in rows
    ]


@router.get("/turnos/{turno_id}")
async def obtener_turno(
    turno_id: UUID,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalle de un turno específico con su liquidación e ingresos
    """
    propietario_id = ctx["propietario_id"]
    
    # ============================================================
    # NUEVA CONSULTA: SIN CAMPOS LEGACY
    # ============================================================
    query = text("""
        SELECT 
            t.id,
            t.vehiculo_id,
            v.patente,
            v.marca,
            v.modelo,
            t.chofer_id,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as chofer_nombre,
            t.estado,
            t.km_inicial,
            t.km_final,
            t.combustible_inicial,
            t.combustible_final,
            -- ✅ Datos desde liquidacion
            COALESCE(l.monto_bruto, 0) as monto_bruto,
            COALESCE(l.total_chofer, 0) as total_chofer,
            COALESCE(l.total_propietario, 0) as total_propietario,
            l.estado as estado_liquidacion,
            l.id as liquidacion_id,
            t.inicio_turno,
            t.fin_turno,
            c.tipo_contrato,
            c.porcentaje_chofer,
            c.monto_diario,
            -- ✅ RESUMEN DE INGRESOS DESDE INGRESO_TURNO
            COALESCE((
                SELECT SUM(it.monto) 
                FROM fleet.ingreso_turno it 
                WHERE it.turno_id = t.id AND it.estado = 'aprobado'
            ), 0) as total_ingresos_aprobados,
            COALESCE((
                SELECT SUM(it.monto) 
                FROM fleet.ingreso_turno it 
                WHERE it.turno_id = t.id AND it.estado = 'pendiente'
            ), 0) as total_ingresos_pendientes
        FROM fleet.turno_chofer t
        JOIN fleet.vehiculo v ON v.id = t.vehiculo_id
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        JOIN fleet.contrato_vehiculo c ON c.id = t.contrato_id
        JOIN auth.usuario u ON u.id = t.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN fleet.liquidacion l ON l.turno_id = t.id
        WHERE t.id = :turno_id AND pv.propietario_id = :propietario_id
    """)
    
    result = await db.execute(query, {"turno_id": turno_id, "propietario_id": propietario_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    # Obtener gastos del turno
    gastos_query = text("""
        SELECT id, tipo_gasto, monto, km_registro, url_comprobante, created_at
        FROM fleet.gasto_turno
        WHERE turno_id = :turno_id
        ORDER BY created_at DESC
    """)
    gastos_result = await db.execute(gastos_query, {"turno_id": turno_id})
    gastos_rows = gastos_result.all()
    
    gastos = [
        {
            "id": str(g[0]),
            "tipo_gasto": g[1],
            "monto": float(g[2]),
            "km_registro": float(g[3]) if g[3] else None,
            "url_comprobante": g[4],
            "created_at": g[5]
        }
        for g in gastos_rows
    ]

    # Obtener ingresos del turno desde IngresoTurno
    ingresos_query = text("""
        SELECT id, tipo_ingreso, medio_pago, origen, monto, moneda, estado, observaciones, created_at
        FROM fleet.ingreso_turno
        WHERE turno_id = :turno_id
        ORDER BY created_at DESC
    """)
    ingresos_result = await db.execute(ingresos_query, {"turno_id": turno_id})
    ingresos_rows = ingresos_result.all()
    
    ingresos = [
        {
            "id": str(i[0]),
            "tipo_ingreso": i[1],
            "medio_pago": i[2],
            "origen": i[3],
            "monto": float(i[4]),
            "moneda": i[5],
            "estado": i[6],
            "observaciones": i[7],
            "created_at": i[8]
        }
        for i in ingresos_rows
    ]
    
    return {
        "id": str(row[0]),
        "vehiculo_id": str(row[1]),
        "patente": row[2],
        "marca": row[3],
        "modelo": row[4],
        "chofer_id": str(row[5]),
        "chofer_nombre": row[6],
        "estado": row[7],
        "km_inicial": float(row[8]) if row[8] else None,
        "km_final": float(row[9]) if row[9] else None,
        "combustible_inicial": row[10],
        "combustible_final": row[11],
        # ✅ Datos desde liquidacion
        "monto_bruto": float(row[12]) if row[12] else 0,
        "total_chofer": float(row[13]) if row[13] else 0,
        "total_propietario": float(row[14]) if row[14] else 0,
        "estado_liquidacion": row[15],
        "liquidacion_id": str(row[16]) if row[16] else None,
        "inicio_turno": row[17],
        "fin_turno": row[18],
        "tipo_contrato": row[19],
        "porcentaje_chofer": float(row[20]) if row[20] else None,
        "monto_diario": float(row[21]) if row[21] else None,
        # ✅ Datos desde IngresoTurno
        "total_ingresos_aprobados": float(row[22]) if row[22] else 0,
        "total_ingresos_pendientes": float(row[23]) if row[23] else 0,
        "gastos": gastos,
        "ingresos": ingresos
    }


@router.post("/turnos/{turno_id}/confirmar")
async def confirmar_liquidacion(
    turno_id: UUID,
    request: Optional[ConfirmarLiquidacionRequest] = None,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Propietario confirma liquidación final del turno
    """
    propietario_id = ctx["propietario_id"]
    
    # Verificar que el turno existe y pertenece al propietario
    query = text("""
        SELECT t.id, t.estado, t.chofer_id, v.patente
        FROM fleet.turno_chofer t
        JOIN fleet.vehiculo v ON v.id = t.vehiculo_id
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE t.id = :turno_id AND pv.propietario_id = :propietario_id
    """)
    result = await db.execute(query, {"turno_id": turno_id, "propietario_id": propietario_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    if row[1] != 'PENDIENTE_CONFIRMACION':
        raise HTTPException(
            status_code=400,
            detail=f"El turno no está pendiente de confirmación. Estado actual: {row[1]}"
        )
    
    chofer_id = row[2]
    patente = row[3]
    
    # Actualizar turno a LIQUIDADO
    update_query = text("""
        UPDATE fleet.turno_chofer
        SET estado = 'LIQUIDADO', updated_at = NOW()
        WHERE id = :turno_id
    """)
    await db.execute(update_query, {"turno_id": turno_id})
    
    # Notificar al chofer
    insert_notificacion = text("""
        INSERT INTO notification.notificacion (id, usuario_id, titulo, mensaje, tipo, leida, created_at)
        VALUES (gen_random_uuid(), :chofer_id, 'Turno liquidado', 
                'El propietario ha confirmado la liquidación del turno del vehículo ' || :patente, 
                'turno_liquidado', false, NOW())
    """)
    await db.execute(insert_notificacion, {"chofer_id": chofer_id, "patente": patente})
    await db.commit()
    
    return {
        "success": True,
        "mensaje": "Liquidación confirmada correctamente"
    }

# ==========================================
# GENERAR CÓDIGO OPERATIVO (REEMPLAZA QR)
# ==========================================

class GenerarCodigoRequest(BaseModel):
    dias_validez: int = 30


class GenerarCodigoResponse(BaseModel):
    success: bool
    codigo: str
    contrato_id: UUID
    vehiculo_id: UUID
    patente: str
    expira_en: datetime
    mensaje: str


@router.post("/contratos/{contrato_id}/generar-codigo", response_model=GenerarCodigoResponse)
async def generar_codigo_operativo(
    contrato_id: UUID,
    request: GenerarCodigoRequest,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Genera un código de 6 dígitos para que el chofer inicie turno.
    Reemplaza al QR operativo.
    """
    propietario_id = UUID(ctx["propietario_id"])

    # 1. Verificar contrato
    query_contrato = text("""
        SELECT 
            cv.id,
            cv.estado_contrato,
            cv.activo,
            cv.vehiculo_id,
            cv.chofer_id,
            v.patente
        FROM fleet.contrato_vehiculo cv
        JOIN fleet.vehiculo v ON v.id = cv.vehiculo_id
        WHERE cv.id = :contrato_id 
          AND cv.propietario_id = :propietario_id
    """)
    result = await db.execute(query_contrato, {
        "contrato_id": contrato_id,
        "propietario_id": propietario_id
    })
    row = result.first()

    if not row:
        raise HTTPException(404, "Contrato no encontrado")

    if row[1] != "ACTIVO" or not row[2]:
        raise HTTPException(400, "El contrato no está ACTIVO")

    vehiculo_id = row[3]
    chofer_id = row[4]
    patente = row[5]

    # 2. Verificar que el chofer no tenga turno activo
    query_turno = text("""
        SELECT id FROM fleet.turno_chofer
        WHERE chofer_id = :chofer_id AND estado = 'ACTIVO'
        LIMIT 1
    """)
    result = await db.execute(query_turno, {"chofer_id": chofer_id})
    if result.first():
        raise HTTPException(400, "El chofer ya tiene un turno activo")

    # 3. Verificar que el vehículo no tenga turno activo
    query_turno = text("""
        SELECT id FROM fleet.turno_chofer
        WHERE vehiculo_id = :vehiculo_id AND estado = 'ACTIVO'
        LIMIT 1
    """)
    result = await db.execute(query_turno, {"vehiculo_id": vehiculo_id})
    if result.first():
        raise HTTPException(400, "El vehículo ya tiene un turno activo")

    # 4. Generar código de 6 dígitos
    codigo = f"{random.randint(100000, 999999)}"
    expira_en = datetime.now() + timedelta(days=request.dias_validez)

    # 5. Guardar código en auth.codigo_verificacion
    query_codigo = text("""
        INSERT INTO auth.codigo_verificacion (
            id, usuario_id, codigo, tipo, usado, intentos, creado_en, expira_en
        ) VALUES (
            gen_random_uuid(), :chofer_id, :codigo, 'INICIO_TURNO', false, 0, NOW(), :expira_en
        )
        RETURNING id
    """)
    result = await db.execute(query_codigo, {
        "chofer_id": chofer_id,
        "codigo": codigo,
        "expira_en": expira_en
    })
    codigo_id = result.scalar()

    # 6. Guardar metadatos del código
    query_metadata = text("""
        INSERT INTO auth.codigo_metadatos (
            id, codigo_id, contrato_id, vehiculo_id, propietario_id, created_at
        ) VALUES (
            gen_random_uuid(), :codigo_id, :contrato_id, :vehiculo_id, :propietario_id, NOW()
        )
    """)
    await db.execute(query_metadata, {
        "codigo_id": codigo_id,
        "contrato_id": contrato_id,
        "vehiculo_id": vehiculo_id,
        "propietario_id": propietario_id
    })

    await db.commit()

    return GenerarCodigoResponse(
        success=True,
        codigo=codigo,
        contrato_id=contrato_id,
        vehiculo_id=vehiculo_id,
        patente=patente,
        expira_en=expira_en,
        mensaje="Código generado correctamente. Compártelo con tu chofer."
    )