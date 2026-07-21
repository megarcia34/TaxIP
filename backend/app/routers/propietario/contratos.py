from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel
from app.database import get_db
from app.dependencies import get_propietario_context, get_propietario_id
from app.schemas.propietario_schemas import (
    ContratoCreate,
    ContratoResponse,
    ChoferDisponibleResponse
)

router = APIRouter()


@router.post("/contratos", response_model=ContratoResponse, status_code=201)
async def crear_contrato(
    data: ContratoCreate,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    propietario_id = UUID(ctx["propietario_id"])
    control_base_id = UUID(ctx["control_base_id"])
    user_id = UUID(ctx["user_id"])

    query_vehiculo = text("""
        SELECT v.id FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE v.id = :vehiculo_id 
          AND pv.propietario_id = :propietario_id 
          AND pv.activo = true 
          AND (pv.fecha_fin IS NULL OR pv.fecha_fin > NOW())
    """)
    result = await db.execute(query_vehiculo, {"vehiculo_id": data.vehiculo_id, "propietario_id": propietario_id})
    if not result.first():
        raise HTTPException(status_code=404, detail="Vehículo no pertenece al propietario o no está activo")

    query_chofer = text("""
        SELECT u.id FROM auth.usuario u
        JOIN auth.tipo_usuario tu ON tu.id = u.tipo_usuario_id
        WHERE u.id = :chofer_id 
          AND u.control_base_id = :control_base_id 
          AND u.activo = true 
          AND tu.nombre = 'chofer'
    """)
    result = await db.execute(query_chofer, {"chofer_id": data.chofer_id, "control_base_id": control_base_id})
    if not result.first():
        raise HTTPException(status_code=404, detail="Chofer no encontrado o no pertenece a su tenant")

    query_conflicto_vehiculo = text("""
        SELECT id FROM fleet.contrato_vehiculo
        WHERE vehiculo_id = :vehiculo_id 
          AND turno_asignado = :turno 
          AND activo = true 
          AND fecha_fin IS NULL
    """)
    result = await db.execute(query_conflicto_vehiculo, {"vehiculo_id": data.vehiculo_id, "turno": data.turno_asignado})
    if result.first():
        raise HTTPException(status_code=409, detail=f"El vehículo ya tiene un contrato activo en el turno {data.turno_asignado}")

    query_conflicto_chofer = text("""
        SELECT id FROM fleet.contrato_vehiculo
        WHERE chofer_id = :chofer_id 
          AND turno_asignado = :turno 
          AND activo = true 
          AND fecha_fin IS NULL
    """)
    result = await db.execute(query_conflicto_chofer, {"chofer_id": data.chofer_id, "turno": data.turno_asignado})
    if result.first():
        raise HTTPException(status_code=409, detail=f"El chofer ya tiene un contrato activo en el turno {data.turno_asignado}")

    if data.tipo_contrato == "PORCENTAJE" and data.porcentaje_chofer is None:
        raise HTTPException(status_code=400, detail="Porcentaje del chofer requerido")
    if data.tipo_contrato == "CANON_FIJO" and data.monto_diario is None:
        raise HTTPException(status_code=400, detail="Monto diario requerido")
    if data.tipo_contrato == "AUTO_GESTION" and data.chofer_id != propietario_id:
        raise HTTPException(status_code=400, detail="En auto-gestión, el chofer debe ser el mismo propietario")

    insert_contrato = text("""
        INSERT INTO fleet.contrato_vehiculo (
            id, control_base_id, propietario_id, vehiculo_id, chofer_id,
            tipo_contrato, turno_asignado, porcentaje_chofer, monto_diario,
            fecha_inicio, activo
        )
        VALUES (
            gen_random_uuid(), :control_base_id, :propietario_id, :vehiculo_id, :chofer_id,
            :tipo_contrato, :turno_asignado, :porcentaje_chofer, :monto_diario,
            NOW(), true
        )
        RETURNING id
    """)
    result = await db.execute(insert_contrato, {
        "control_base_id": control_base_id,
        "propietario_id": propietario_id,
        "vehiculo_id": data.vehiculo_id,
        "chofer_id": data.chofer_id,
        "tipo_contrato": data.tipo_contrato,
        "turno_asignado": data.turno_asignado,
        "porcentaje_chofer": data.porcentaje_chofer,
        "monto_diario": data.monto_diario
    })
    contrato_id = result.scalar()
    await db.commit()

    update_cv = text("""
        UPDATE fleet.chofer_vehiculo
        SET vehiculo_id = :vehiculo_id, updated_at = NOW()
        WHERE usuario_id = :chofer_id AND control_base_id = :control_base_id
    """)
    await db.execute(update_cv, {"vehiculo_id": data.vehiculo_id, "chofer_id": data.chofer_id, "control_base_id": control_base_id})
    await db.commit()

    query = text("""
        SELECT 
            c.id, c.vehiculo_id, v.patente, v.marca, v.modelo,
            c.chofer_id, p.nombre as chofer_nombre, p.apellido as chofer_apellido,
            c.tipo_contrato, c.turno_asignado, c.porcentaje_chofer, c.monto_diario,
            c.fecha_inicio, c.fecha_fin, c.activo
        FROM fleet.contrato_vehiculo c
        JOIN fleet.vehiculo v ON v.id = c.vehiculo_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = c.chofer_id
        WHERE c.id = :contrato_id
    """)
    result = await db.execute(query, {"contrato_id": contrato_id})
    row = result.first()
    
    return ContratoResponse(
        id=row[0], vehiculo_id=row[1], patente=row[2], marca=row[3], modelo=row[4],
        chofer_id=row[5], chofer_nombre=row[6], chofer_apellido=row[7],
        tipo_contrato=row[8], turno_asignado=row[9],
        porcentaje_chofer=float(row[10]) if row[10] else None,
        monto_diario=float(row[11]) if row[11] else None,
        fecha_inicio=row[12], fecha_fin=row[13], activo=row[14]
    )


@router.get("/contratos", response_model=List[ContratoResponse])
async def listar_contratos(
    activo: Optional[bool] = Query(None, description="Filtrar por activo"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    params = {"propietario_id": UUID(ctx["propietario_id"]), "limit": limit, "offset": offset}
    
    query = text("""
        SELECT 
            c.id, c.vehiculo_id, v.patente, v.marca, v.modelo,
            c.chofer_id, p.nombre as chofer_nombre, p.apellido as chofer_apellido,
            c.tipo_contrato, c.turno_asignado, c.porcentaje_chofer, c.monto_diario,
            c.fecha_inicio, c.fecha_fin, c.activo
        FROM fleet.contrato_vehiculo c
        JOIN fleet.vehiculo v ON v.id = c.vehiculo_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = c.chofer_id
        WHERE c.propietario_id = :propietario_id
    """)
    
    if activo is not None:
        if activo:
            query = text(query.text + " AND c.activo = true AND c.fecha_fin IS NULL")
        else:
            query = text(query.text + " AND (c.activo = false OR c.fecha_fin IS NOT NULL)")
    
    query = text(query.text + " ORDER BY c.created_at DESC LIMIT :limit OFFSET :offset")
    
    result = await db.execute(query, params)
    rows = result.all()
    
    return [
        ContratoResponse(
            id=row[0], vehiculo_id=row[1], patente=row[2], marca=row[3], modelo=row[4],
            chofer_id=row[5], chofer_nombre=row[6], chofer_apellido=row[7],
            tipo_contrato=row[8], turno_asignado=row[9],
            porcentaje_chofer=float(row[10]) if row[10] else None,
            monto_diario=float(row[11]) if row[11] else None,
            fecha_inicio=row[12], fecha_fin=row[13], activo=row[14]
        )
        for row in rows
    ]


@router.put("/contratos/{contrato_id}/finalizar")
async def finalizar_contrato(
    contrato_id: UUID,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    query_contrato = text("""
        SELECT chofer_id FROM fleet.contrato_vehiculo
        WHERE id = :contrato_id AND propietario_id = :propietario_id AND activo = true AND fecha_fin IS NULL
    """)
    result = await db.execute(query_contrato, {"contrato_id": contrato_id, "propietario_id": UUID(ctx["propietario_id"])})
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Contrato activo no encontrado")
    chofer_id = row[0]

    update_contrato = text("""
        UPDATE fleet.contrato_vehiculo
        SET activo = false, fecha_fin = NOW()
        WHERE id = :contrato_id
    """)
    await db.execute(update_contrato, {"contrato_id": contrato_id})

    update_cv = text("""
        UPDATE fleet.chofer_vehiculo
        SET vehiculo_id = NULL, updated_at = NOW()
        WHERE usuario_id = :chofer_id
    """)
    await db.execute(update_cv, {"chofer_id": chofer_id})
    await db.commit()
    
    return {"message": "Contrato finalizado correctamente"}


@router.get("/choferes/disponibles", response_model=List[ChoferDisponibleResponse])
async def choferes_disponibles(
    turno: str = Query(..., pattern="^(DIURNO|NOCTURNO|COMPLETO)$"),
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    control_base_id = UUID(ctx["control_base_id"])

    query = text("""
        SELECT 
            u.id, u.email, p.nombre, p.apellido, p.telefono,
            cv.calificacion_promedio, cv.total_calificaciones
        FROM auth.usuario u
        JOIN auth.tipo_usuario tu ON tu.id = u.tipo_usuario_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN fleet.chofer_vehiculo cv ON cv.usuario_id = u.id
        WHERE u.control_base_id = :control_base_id
          AND u.activo = true
          AND tu.nombre = 'chofer'
          AND NOT EXISTS (
              SELECT 1 FROM fleet.contrato_vehiculo cc
              WHERE cc.chofer_id = u.id
                AND cc.turno_asignado = :turno
                AND cc.activo = true
                AND cc.fecha_fin IS NULL
          )
        ORDER BY p.nombre, p.apellido
    """)
    result = await db.execute(query, {"control_base_id": control_base_id, "turno": turno})
    rows = result.all()
    
    return [
        ChoferDisponibleResponse(
            id=row[0], email=row[1], nombre=row[2], apellido=row[3],
            telefono=row[4], calificacion_promedio=float(row[5]) if row[5] else None,
            total_calificaciones=row[6]
        ) for row in rows
    ]


# ============================================
# SCHEMA PARA CONFIGURAR CONTRATO
# ============================================

class ConfigurarContratoRequest(BaseModel):
    tipo_contrato: str  # 'PORCENTAJE', 'MONTO_FIJO', 'AUTO_GESTION'
    turno_asignado: str  # 'mañana', 'tarde', 'noche'
    valor: float
    duracion_max_horas: int = 12


# ============================================
# CONFIGURAR CONTRATO (Propietario)
# ============================================

@router.post("/contratos/{contrato_id}/configurar")
async def configurar_contrato(
    contrato_id: UUID,
    data: ConfigurarContratoRequest,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Propietario configura las condiciones del contrato
    """
    propietario_id = ctx["propietario_id"]
    
    # Verificar que el contrato existe y está pendiente
    query = text("""
        SELECT c.id, c.vehiculo_id, c.chofer_id, c.estado_contrato, v.patente
        FROM fleet.contrato_vehiculo c
        JOIN fleet.vehiculo v ON v.id = c.vehiculo_id
        WHERE c.id = :contrato_id AND c.propietario_id = :propietario_id
    """)
    result = await db.execute(query, {"contrato_id": contrato_id, "propietario_id": propietario_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    
    if row[3] != 'PENDIENTE_CONFIGURACION':
        raise HTTPException(status_code=400, detail="El contrato ya fue configurado")
    
    vehiculo_id = row[1]
    chofer_id = row[2]
    patente = row[4]
    
    # Validar tipo de contrato
    tipos_validos = ['PORCENTAJE', 'MONTO_FIJO', 'AUTO_GESTION']
    if data.tipo_contrato not in tipos_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de contrato inválido. Permitidos: {tipos_validos}"
        )
    
    # Validar turno
    turnos_validos = ['mañana', 'tarde', 'noche']
    if data.turno_asignado not in turnos_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Turno inválido. Permitidos: {turnos_validos}"
        )
    
    # Validar valor según tipo
    if data.tipo_contrato == 'PORCENTAJE':
        if data.valor < 0 or data.valor > 100:
            raise HTTPException(status_code=400, detail="El porcentaje debe estar entre 0 y 100")
    elif data.tipo_contrato == 'MONTO_FIJO':
        if data.valor <= 0:
            raise HTTPException(status_code=400, detail="El monto fijo debe ser mayor a 0")
    # AUTO_GESTION no requiere valor
    
    # Verificar que el vehículo no tenga otro contrato activo en el mismo turno
    verificar_vehiculo = text("""
        SELECT id FROM fleet.contrato_vehiculo
        WHERE vehiculo_id = :vehiculo_id 
          AND turno_asignado = :turno
          AND estado_contrato = 'ACTIVO'
          AND id != :contrato_id
    """)
    result = await db.execute(verificar_vehiculo, {
        "vehiculo_id": vehiculo_id,
        "turno": data.turno_asignado,
        "contrato_id": contrato_id
    })
    if result.first():
        raise HTTPException(
            status_code=409,
            detail=f"El vehículo {patente} ya tiene un contrato activo en el turno {data.turno_asignado}"
        )
    
    # Verificar que el chofer no tenga otro contrato activo en el mismo turno
    verificar_chofer = text("""
        SELECT id FROM fleet.contrato_vehiculo
        WHERE chofer_id = :chofer_id 
          AND turno_asignado = :turno
          AND estado_contrato = 'ACTIVO'
          AND id != :contrato_id
    """)
    result = await db.execute(verificar_chofer, {
        "chofer_id": chofer_id,
        "turno": data.turno_asignado,
        "contrato_id": contrato_id
    })
    if result.first():
        raise HTTPException(
            status_code=409,
            detail=f"El chofer ya tiene un contrato activo en el turno {data.turno_asignado}"
        )
    
    # Actualizar contrato
    update_query = text("""
        UPDATE fleet.contrato_vehiculo
        SET tipo_contrato = :tipo_contrato,
            turno_asignado = :turno,
            porcentaje_chofer = :porcentaje,
            monto_diario = :monto,
            estado_contrato = 'ACTIVO',
            fecha_inicio = NOW()
        WHERE id = :contrato_id
        RETURNING id
    """)
    
    porcentaje = data.valor if data.tipo_contrato == 'PORCENTAJE' else None
    monto = data.valor if data.tipo_contrato == 'MONTO_FIJO' else None
    
    await db.execute(update_query, {
        "contrato_id": contrato_id,
        "tipo_contrato": data.tipo_contrato,
        "turno": data.turno_asignado,
        "porcentaje": porcentaje,
        "monto": monto
    })
    await db.commit()
    
    # Notificar al chofer
    insert_notificacion = text("""
        INSERT INTO notification.notificacion (id, usuario_id, titulo, mensaje, tipo, leida, created_at)
        VALUES (gen_random_uuid(), :chofer_id, 'Contrato activado', 
                'Tu contrato para el vehículo ' || :patente || ' ha sido activado', 
                'contrato_activado', false, NOW())
    """)
    await db.execute(insert_notificacion, {"chofer_id": chofer_id, "patente": patente})
    await db.commit()
    
    return {
        "success": True,
        "contrato_id": str(contrato_id),
        "estado": "ACTIVO",
        "mensaje": "Contrato configurado y activado exitosamente"
    }


@router.get("/contratos/pendientes")
async def contratos_pendientes(
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar contratos pendientes de configuración
    """
    propietario_id = ctx["propietario_id"]
    
    query = text("""
        SELECT c.id, c.vehiculo_id, v.patente, v.marca, v.modelo,
               c.chofer_id, p.nombre as chofer_nombre, p.apellido as chofer_apellido,
               c.created_at
        FROM fleet.contrato_vehiculo c
        JOIN fleet.vehiculo v ON v.id = c.vehiculo_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = c.chofer_id
        WHERE c.propietario_id = :propietario_id AND c.estado_contrato = 'PENDIENTE_CONFIGURACION'
        ORDER BY c.created_at DESC
    """)
    result = await db.execute(query, {"propietario_id": propietario_id})
    rows = result.all()
    
    return [
        {
            "contrato_id": str(row[0]),
            "vehiculo_id": str(row[1]),
            "patente": row[2],
            "marca": row[3],
            "modelo": row[4],
            "chofer_id": str(row[5]),
            "chofer_nombre": f"{row[6] or ''} {row[7] or ''}".strip(),
            "solicitado_en": row[8]
        }
        for row in rows
    ]