"""
Módulo de contratos para propietarios
Implementa los modelos ALQUILER y AUTO_GESTION con validaciones centralizadas
"""

import json
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional, List
from datetime import datetime, date, time

from app.database import get_db
from app.dependencies import get_propietario_context
from app.schemas.propietario_schemas import (
    ContratoCreate,
    ContratoResponse,
    ChoferDisponibleResponse,
    ConfigurarContratoRequest
)
from app.schemas.turno_schemas import (
    GenerarQrRequest,
    GenerarQrResponse
)

# IMPORTAR es_conductor DIRECTAMENTE DESDE CORE
from app.core.validaciones_compartidas import es_conductor

# IMPORTAR VALIDACIONES DE DOMINIO DE CONTRATOS
from .validaciones import (
    validar_parametros_alquiler,
    verificar_propiedad_vehiculo,
    verificar_chofer_valido,
    verificar_conflictos_contrato,
    verificar_contrato_existe,
    preparar_parametros_contrato,
    validar_dias_contractuales,
    verificar_autogestion,
    hay_conflicto_horario,
    calcular_duracion_horas
)

# IMPORTAR SERVICIO DE QR
from app.services.qr_service import QRService

router = APIRouter()


# ============================================
# 1. CREAR CONTRATO
# ============================================

@router.post("/contratos", response_model=ContratoResponse, status_code=201)
async def crear_contrato(
    data: ContratoCreate,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Crea un nuevo contrato con validación completa.
    
    - ALQUILER: con parámetros económicos y horarios flexibles
    - AUTO_GESTION: sin parámetros económicos, requiere capacidad CONDUCTOR
    - PORCENTAJE: con porcentaje para el chofer
    """
    propietario_id = UUID(ctx["propietario_id"])
    control_base_id = UUID(ctx["control_base_id"])
    
    # 1. Validar tenant
    query_propietario = text("""
        SELECT id FROM auth.usuario
        WHERE id = :propietario_id
          AND control_base_id = :control_base_id
          AND activo = true
    """)
    result = await db.execute(query_propietario, {
        "propietario_id": propietario_id,
        "control_base_id": control_base_id
    })
    if not result.first():
        raise HTTPException(status_code=404, detail="Propietario no encontrado o inactivo")
    
    # 2. Validar propiedad del vehículo
    es_valido, mensaje = await verificar_propiedad_vehiculo(
        data.vehiculo_id,
        propietario_id,
        control_base_id,
        db
    )
    if not es_valido:
        raise HTTPException(status_code=404, detail=mensaje)
    
    # 3. Validar chofer
    es_valido, mensaje = await verificar_chofer_valido(
        data.chofer_id,
        control_base_id,
        db
    )
    if not es_valido:
        raise HTTPException(status_code=404, detail=mensaje)
    
    # 4. Validar reglas según tipo de contrato
    if data.tipo_contrato == "ALQUILER":
        if data.chofer_id == propietario_id:
            raise HTTPException(
                status_code=400,
                detail="En ALQUILER, el propietario y el conductor deben ser personas diferentes"
            )
    
    elif data.tipo_contrato == "AUTO_GESTION":
        if data.chofer_id != propietario_id:
            raise HTTPException(
                status_code=400,
                detail="En AUTO_GESTION, el propietario y el conductor deben ser la misma persona"
            )
        tiene_capacidad = await es_conductor(propietario_id, db)
        if not tiene_capacidad:
            raise HTTPException(
                status_code=400,
                detail="El propietario no está habilitado como conductor. Debe registrar capacidad CONDUCTOR."
            )
    
    # 5. ✅ CORREGIDO: Validar fechas de vigencia
    fecha_inicio = data.fecha_inicio if data.fecha_inicio else date.today()
    fecha_fin = data.fecha_fin
    
    # ✅ PERMITE fecha_fin = None o fecha_fin >= fecha_inicio
    if fecha_fin and fecha_fin < fecha_inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha de finalización no puede ser anterior a la fecha de inicio"
        )
    # Si fecha_fin == fecha_inicio, es un contrato de 1 día (válido)
    
    # 6. Validar días contractuales según tipo
    try:
        validar_dias_contractuales(data.dias_contractuales, data.tipo_contrato)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 7. Validar conflictos (CON HORARIOS FLEXIBLES)
    hay_conflictos, mensajes = await verificar_conflictos_contrato(
        data.vehiculo_id,
        data.chofer_id,
        data.hora_inicio,
        data.hora_fin,
        control_base_id,
        db,
        contrato_excluido_id=None,
        dias_contractuales=data.dias_contractuales,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )
    if hay_conflictos:
        raise HTTPException(status_code=409, detail=" | ".join(mensajes))
    
    # 8. Preparar parámetros según tipo de contrato
    try:
        params = preparar_parametros_contrato(
            tipo_contrato=data.tipo_contrato,
            canon_diario=data.canon_diario if data.tipo_contrato == "ALQUILER" else None,
            km_incluidos_dia=data.km_incluidos_dia if data.tipo_contrato == "ALQUILER" else None,
            valor_km_excedente=data.valor_km_excedente if data.tipo_contrato == "ALQUILER" else None,
            modalidad_computo=data.modalidad_computo if data.tipo_contrato == "ALQUILER" else None,
            dias_contractuales=data.dias_contractuales,
            tratamiento_dia_no_trabajado=data.tratamiento_dia_no_trabajado if data.tipo_contrato == "ALQUILER" else None,
            porcentaje_chofer=data.porcentaje_chofer if data.tipo_contrato == "PORCENTAJE" else None,
            dia_inicio_semana=data.dia_inicio_semana if data.tipo_contrato == "ALQUILER" else None,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 9. Determinar estado según fecha_inicio
    fecha_hoy = date.today()
    if fecha_inicio > fecha_hoy:
        estado_inicial = "PROGRAMADO"
        activo_inicial = False
    else:
        estado_inicial = "ACTIVO"
        activo_inicial = True
    
    # 10. Serializar dias_contractuales a JSON
    dias_json = json.dumps(params.get("dias_contractuales")) if params.get("dias_contractuales") else None
    
    # 11. Convertir horarios a time
    hora_inicio_time = datetime.strptime(data.hora_inicio, "%H:%M").time()
    hora_fin_time = datetime.strptime(data.hora_fin, "%H:%M").time()
    hora_fin_extension_time = datetime.strptime(data.hora_fin_extension, "%H:%M").time() if data.hora_fin_extension else None
    
    # 12. Crear el contrato
    insert_contrato = text("""
        INSERT INTO fleet.contrato_vehiculo (
            id, control_base_id, propietario_id, vehiculo_id, chofer_id,
            tipo_contrato,
            hora_inicio, hora_fin, duracion_minima_horas, permite_extension, hora_fin_extension,
            porcentaje_chofer,
            canon_diario, km_incluidos_dia, valor_km_excedente,
            modalidad_computo, dias_contractuales, tratamiento_dia_no_trabajado,
            dia_inicio_semana,
            fecha_inicio, fecha_fin, estado_contrato, activo,
            created_at, updated_at
        )
        VALUES (
            gen_random_uuid(), :control_base_id, :propietario_id, :vehiculo_id, :chofer_id,
            :tipo_contrato,
            :hora_inicio, :hora_fin, :duracion_minima_horas, :permite_extension, :hora_fin_extension,
            :porcentaje_chofer,
            :canon_diario, :km_incluidos_dia, :valor_km_excedente,
            :modalidad_computo, :dias_contractuales, :tratamiento_dia_no_trabajado,
            :dia_inicio_semana,
            :fecha_inicio, :fecha_fin, :estado_contrato, :activo,
            NOW(), NOW()
        )
        RETURNING id
    """)
    
    result = await db.execute(insert_contrato, {
        "control_base_id": control_base_id,
        "propietario_id": propietario_id,
        "vehiculo_id": data.vehiculo_id,
        "chofer_id": data.chofer_id,
        "tipo_contrato": data.tipo_contrato,
        "hora_inicio": hora_inicio_time,
        "hora_fin": hora_fin_time,
        "duracion_minima_horas": data.duracion_minima_horas,
        "permite_extension": data.permite_extension,
        "hora_fin_extension": hora_fin_extension_time,
        "porcentaje_chofer": params.get("porcentaje_chofer"),
        "canon_diario": params.get("canon_diario"),
        "km_incluidos_dia": params.get("km_incluidos_dia"),
        "valor_km_excedente": params.get("valor_km_excedente"),
        "modalidad_computo": params.get("modalidad_computo"),
        "dias_contractuales": dias_json,
        "tratamiento_dia_no_trabajado": params.get("tratamiento_dia_no_trabajado"),
        "dia_inicio_semana": params.get("dia_inicio_semana"),
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "estado_contrato": estado_inicial,
        "activo": activo_inicial
    })
    contrato_id = result.scalar()
    
    # 13. Asignar vehículo al chofer en chofer_vehiculo
    update_cv = text("""
        UPDATE fleet.chofer_vehiculo
        SET vehiculo_id = :vehiculo_id, updated_at = NOW()
        WHERE usuario_id = :chofer_id AND control_base_id = :control_base_id
    """)
    await db.execute(update_cv, {
        "vehiculo_id": data.vehiculo_id,
        "chofer_id": data.chofer_id,
        "control_base_id": control_base_id
    })
    
    # 14. Confirmar transacción
    await db.commit()
    
    # 15. Devolver el contrato creado
    return await _get_contrato_by_id(contrato_id, db)


# ============================================
# 2. LISTAR CONTRATOS
# ============================================

@router.get("/contratos", response_model=List[ContratoResponse])
async def listar_contratos(
    activo: Optional[bool] = Query(None, description="Filtrar por activo"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Lista los contratos del propietario autenticado"""
    propietario_id = UUID(ctx["propietario_id"])
    control_base_id = UUID(ctx["control_base_id"])
    
    query = text("""
        SELECT 
            c.id, c.vehiculo_id, v.patente, v.marca, v.modelo,
            c.chofer_id, p.nombre as chofer_nombre, p.apellido as chofer_apellido,
            c.tipo_contrato,
            c.hora_inicio, c.hora_fin, c.duracion_minima_horas, c.permite_extension, c.hora_fin_extension,
            c.porcentaje_chofer, c.monto_diario,
            c.fecha_inicio, c.fecha_fin, c.activo, c.estado_contrato,
            c.canon_diario, c.km_incluidos_dia, c.valor_km_excedente,
            c.modalidad_computo, c.dias_contractuales, c.tratamiento_dia_no_trabajado,
            c.dia_inicio_semana
        FROM fleet.contrato_vehiculo c
        JOIN fleet.vehiculo v ON v.id = c.vehiculo_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = c.chofer_id
        WHERE c.propietario_id = :propietario_id
          AND c.control_base_id = :control_base_id
    """)
    
    if activo is not None:
        if activo:
            query = text(query.text + " AND c.estado_contrato = 'ACTIVO'")
        else:
            query = text(query.text + " AND c.estado_contrato != 'ACTIVO'")
    
    query = text(query.text + " ORDER BY c.created_at DESC LIMIT :limit OFFSET :offset")
    
    result = await db.execute(query, {
        "propietario_id": propietario_id,
        "control_base_id": control_base_id,
        "limit": limit,
        "offset": offset
    })
    rows = result.all()
    
    return [_map_row_to_contrato_response(row) for row in rows]


# ============================================
# 3. OBTENER CONTRATO POR ID
# ============================================

@router.get("/contratos/{contrato_id}", response_model=ContratoResponse)
async def obtener_contrato(
    contrato_id: UUID,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene un contrato específico del propietario autenticado"""
    propietario_id = UUID(ctx["propietario_id"])
    control_base_id = UUID(ctx["control_base_id"])
    
    query = text("""
        SELECT 
            c.id, c.vehiculo_id, v.patente, v.marca, v.modelo,
            c.chofer_id, p.nombre as chofer_nombre, p.apellido as chofer_apellido,
            c.tipo_contrato,
            c.hora_inicio, c.hora_fin, c.duracion_minima_horas, c.permite_extension, c.hora_fin_extension,
            c.porcentaje_chofer, c.monto_diario,
            c.fecha_inicio, c.fecha_fin, c.activo, c.estado_contrato,
            c.canon_diario, c.km_incluidos_dia, c.valor_km_excedente,
            c.modalidad_computo, c.dias_contractuales, c.tratamiento_dia_no_trabajado,
            c.dia_inicio_semana
        FROM fleet.contrato_vehiculo c
        JOIN fleet.vehiculo v ON v.id = c.vehiculo_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = c.chofer_id
        WHERE c.id = :contrato_id
          AND c.propietario_id = :propietario_id
          AND c.control_base_id = :control_base_id
    """)
    result = await db.execute(query, {
        "contrato_id": contrato_id,
        "propietario_id": propietario_id,
        "control_base_id": control_base_id
    })
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    
    return _map_row_to_contrato_response(row)


# ============================================
# 4. CONFIGURAR CONTRATO PENDIENTE
# ============================================

@router.post("/contratos/{contrato_id}/configurar")
async def configurar_contrato(
    contrato_id: UUID,
    data: ConfigurarContratoRequest,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Configura un contrato pendiente y lo activa.
    Revalida TODAS las condiciones antes de activar.
    """
    propietario_id = UUID(ctx["propietario_id"])
    control_base_id = UUID(ctx["control_base_id"])
    
    existe, estado = await verificar_contrato_existe(contrato_id, propietario_id, db)
    if not existe:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    
    if estado != 'PENDIENTE_CONFIGURACION':
        raise HTTPException(status_code=400, detail="El contrato ya fue configurado")
    
    query_datos = text("""
        SELECT vehiculo_id, chofer_id
        FROM fleet.contrato_vehiculo
        WHERE id = :contrato_id
    """)
    result = await db.execute(query_datos, {"contrato_id": contrato_id})
    row = result.first()
    vehiculo_id = row[0]
    chofer_id = row[1]
    
    # 3a. Validar propiedad del vehículo
    es_valido, mensaje = await verificar_propiedad_vehiculo(
        vehiculo_id,
        propietario_id,
        control_base_id,
        db
    )
    if not es_valido:
        raise HTTPException(status_code=404, detail=f"Vehículo ya no es válido: {mensaje}")
    
    # 3b. Validar chofer
    es_valido, mensaje = await verificar_chofer_valido(
        chofer_id,
        control_base_id,
        db
    )
    if not es_valido:
        raise HTTPException(status_code=404, detail=f"Chofer ya no es válido: {mensaje}")
    
    # 3c. Para ALQUILER, verificar que propietario y chofer sean personas diferentes
    if data.tipo_contrato == "ALQUILER" and chofer_id == propietario_id:
        raise HTTPException(
            status_code=400,
            detail="En ALQUILER, el propietario y el conductor deben ser personas diferentes"
        )
    
    # 3d. Para AUTO_GESTION, revalidar identidad y capacidad
    if data.tipo_contrato == "AUTO_GESTION":
        if chofer_id != propietario_id:
            raise HTTPException(
                status_code=400,
                detail="En AUTO_GESTION, el propietario y el conductor deben ser la misma persona"
            )
        tiene_capacidad = await es_conductor(propietario_id, db)
        if not tiene_capacidad:
            raise HTTPException(
                status_code=400,
                detail="El propietario no está habilitado como conductor. Debe registrar capacidad CONDUCTOR."
            )
    
    # 3e. ✅ CORREGIDO: Validar fechas de vigencia
    fecha_inicio = data.fecha_inicio if data.fecha_inicio else date.today()
    fecha_fin = data.fecha_fin
    
    if fecha_fin and fecha_fin < fecha_inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha de finalización no puede ser anterior a la fecha de inicio"
        )
    
    # 3f. Validar días contractuales según tipo
    try:
        validar_dias_contractuales(data.dias_contractuales, data.tipo_contrato)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 3g. Validar conflictos (CON HORARIOS FLEXIBLES)
    hay_conflictos, mensajes = await verificar_conflictos_contrato(
        vehiculo_id,
        chofer_id,
        data.hora_inicio,
        data.hora_fin,
        control_base_id,
        db,
        contrato_excluido_id=contrato_id,
        dias_contractuales=data.dias_contractuales,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )
    if hay_conflictos:
        raise HTTPException(status_code=409, detail=" | ".join(mensajes))
    
    # 4. Preparar parámetros según tipo
    try:
        params = preparar_parametros_contrato(
            tipo_contrato=data.tipo_contrato,
            canon_diario=data.canon_diario if data.tipo_contrato == "ALQUILER" else None,
            km_incluidos_dia=data.km_incluidos_dia if data.tipo_contrato == "ALQUILER" else None,
            valor_km_excedente=data.valor_km_excedente if data.tipo_contrato == "ALQUILER" else None,
            modalidad_computo=data.modalidad_computo if data.tipo_contrato == "ALQUILER" else None,
            dias_contractuales=data.dias_contractuales,
            tratamiento_dia_no_trabajado=data.tratamiento_dia_no_trabajado if data.tipo_contrato == "ALQUILER" else None,
            porcentaje_chofer=data.porcentaje_chofer if data.tipo_contrato == "PORCENTAJE" else None,
            dia_inicio_semana=data.dia_inicio_semana if data.tipo_contrato == "ALQUILER" else None,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 5. Determinar estado según fecha_inicio
    fecha_hoy = date.today()
    if fecha_inicio > fecha_hoy:
        nuevo_estado = "PROGRAMADO"
        nuevo_activo = False
    else:
        nuevo_estado = "ACTIVO"
        nuevo_activo = True
    
    # 6. Serializar dias_contractuales a JSON
    dias_json = json.dumps(params.get("dias_contractuales")) if params.get("dias_contractuales") else None
    
    # 7. Convertir horarios a time
    hora_inicio_time = datetime.strptime(data.hora_inicio, "%H:%M").time()
    hora_fin_time = datetime.strptime(data.hora_fin, "%H:%M").time()
    hora_fin_extension_time = datetime.strptime(data.hora_fin_extension, "%H:%M").time() if data.hora_fin_extension else None
    
    # 8. Iniciar transacción para actualizar contrato
    try:
        async with db.begin():
            update_query = text("""
                UPDATE fleet.contrato_vehiculo
                SET tipo_contrato = :tipo_contrato,
                    hora_inicio = :hora_inicio,
                    hora_fin = :hora_fin,
                    duracion_minima_horas = :duracion_minima_horas,
                    permite_extension = :permite_extension,
                    hora_fin_extension = :hora_fin_extension,
                    porcentaje_chofer = :porcentaje,
                    monto_diario = NULL,
                    canon_diario = :canon_diario,
                    km_incluidos_dia = :km_incluidos_dia,
                    valor_km_excedente = :valor_km_excedente,
                    modalidad_computo = :modalidad_computo,
                    dias_contractuales = :dias_contractuales,
                    tratamiento_dia_no_trabajado = :tratamiento_dia_no_trabajado,
                    dia_inicio_semana = :dia_inicio_semana,
                    estado_contrato = :estado_contrato,
                    fecha_inicio = :fecha_inicio,
                    fecha_fin = :fecha_fin,
                    activo = :activo,
                    updated_at = NOW()
                WHERE id = :contrato_id
                RETURNING id
            """)
            await db.execute(update_query, {
                "contrato_id": contrato_id,
                "tipo_contrato": data.tipo_contrato,
                "hora_inicio": hora_inicio_time,
                "hora_fin": hora_fin_time,
                "duracion_minima_horas": data.duracion_minima_horas,
                "permite_extension": data.permite_extension,
                "hora_fin_extension": hora_fin_extension_time,
                "porcentaje": params.get("porcentaje_chofer"),
                "canon_diario": params.get("canon_diario"),
                "km_incluidos_dia": params.get("km_incluidos_dia"),
                "valor_km_excedente": params.get("valor_km_excedente"),
                "modalidad_computo": params.get("modalidad_computo"),
                "dias_contractuales": dias_json,
                "tratamiento_dia_no_trabajado": params.get("tratamiento_dia_no_trabajado"),
                "dia_inicio_semana": params.get("dia_inicio_semana"),
                "estado_contrato": nuevo_estado,
                "activo": nuevo_activo,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin
            })
            
            update_cv = text("""
                UPDATE fleet.chofer_vehiculo
                SET vehiculo_id = :vehiculo_id, updated_at = NOW()
                WHERE usuario_id = :chofer_id AND control_base_id = :control_base_id
            """)
            await db.execute(update_cv, {
                "vehiculo_id": vehiculo_id,
                "chofer_id": chofer_id,
                "control_base_id": control_base_id
            })
            
            insert_notificacion = text("""
                INSERT INTO notification.notificacion (id, usuario_id, titulo, mensaje, tipo, leida, created_at)
                VALUES (gen_random_uuid(), :chofer_id, 'Contrato activado', 
                        'Tu contrato ha sido activado', 
                        'contrato_activado', false, NOW())
            """)
            await db.execute(insert_notificacion, {"chofer_id": chofer_id})
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al configurar contrato: {str(e)}"
        )
    
    return {
        "success": True,
        "contrato_id": str(contrato_id),
        "estado": nuevo_estado,
        "mensaje": "Contrato configurado y activado exitosamente"
    }


# ============================================
# 5. FINALIZAR CONTRATO
# ============================================

@router.put("/contratos/{contrato_id}/finalizar")
async def finalizar_contrato(
    contrato_id: UUID,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Finaliza un contrato activo.
    Verifica que el contrato existe, está activo, y pertenece al propietario.
    """
    propietario_id = UUID(ctx["propietario_id"])
    control_base_id = UUID(ctx["control_base_id"])
    
    query_contrato = text("""
        SELECT chofer_id FROM fleet.contrato_vehiculo
        WHERE id = :contrato_id 
          AND propietario_id = :propietario_id 
          AND control_base_id = :control_base_id
          AND estado_contrato = 'ACTIVO'
    """)
    result = await db.execute(query_contrato, {
        "contrato_id": contrato_id,
        "propietario_id": propietario_id,
        "control_base_id": control_base_id
    })
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Contrato activo no encontrado")
    
    chofer_id = row[0]
    
    update_contrato = text("""
        UPDATE fleet.contrato_vehiculo
        SET activo = false, 
            estado_contrato = 'FINALIZADO',
            fecha_fin = NOW(),
            updated_at = NOW()
        WHERE id = :contrato_id
    """)
    await db.execute(update_contrato, {"contrato_id": contrato_id})
    
    query_otros = text("""
        SELECT id FROM fleet.contrato_vehiculo
        WHERE chofer_id = :chofer_id
          AND estado_contrato = 'ACTIVO'
          AND id != :contrato_id
    """)
    result = await db.execute(query_otros, {
        "chofer_id": chofer_id,
        "contrato_id": contrato_id
    })
    
    if not result.first():
        update_cv = text("""
            UPDATE fleet.chofer_vehiculo
            SET vehiculo_id = NULL, updated_at = NOW()
            WHERE usuario_id = :chofer_id AND control_base_id = :control_base_id
        """)
        await db.execute(update_cv, {
            "chofer_id": chofer_id,
            "control_base_id": control_base_id
        })
    
    await db.commit()
    
    return {"message": "Contrato finalizado correctamente"}


# ============================================
# 6. CHOFERES DISPONIBLES
# ============================================
@router.get("/choferes/disponibles", response_model=List[ChoferDisponibleResponse])
async def choferes_disponibles(
    hora_inicio: str = Query(..., pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$"),
    hora_fin: str = Query(..., pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$"),
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista choferes disponibles para un horario específico.
    """
    control_base_id = UUID(ctx["control_base_id"])
    
    # ✅ Convertir strings a objetos time
    hora_inicio_time = datetime.strptime(hora_inicio, "%H:%M").time()
    hora_fin_time = datetime.strptime(hora_fin, "%H:%M").time()
    
    # ✅ Usar objetos time en la consulta
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
                AND cc.estado_contrato = 'ACTIVO'
                AND (
                    (:hora_inicio < cc.hora_fin AND cc.hora_inicio < :hora_fin)
                )
          )
        ORDER BY p.nombre, p.apellido
    """)
    
    result = await db.execute(query, {
        "control_base_id": control_base_id,
        "hora_inicio": hora_inicio_time,
        "hora_fin": hora_fin_time
    })
    rows = result.all()
    
    return [
        ChoferDisponibleResponse(
            id=row[0], email=row[1], nombre=row[2], apellido=row[3],
            telefono=row[4], calificacion_promedio=float(row[5]) if row[5] else None,
            total_calificaciones=row[6]
        ) for row in rows
    ]


# ============================================
# 7. CONTRATOS PENDIENTES
# ============================================

@router.get("/contratos/pendientes")
async def contratos_pendientes(
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """Lista contratos pendientes de configuración del propietario"""
    propietario_id = UUID(ctx["propietario_id"])
    control_base_id = UUID(ctx["control_base_id"])
    
    query = text("""
        SELECT c.id, c.vehiculo_id, v.patente, v.marca, v.modelo,
               c.chofer_id, p.nombre as chofer_nombre, p.apellido as chofer_apellido,
               c.created_at
        FROM fleet.contrato_vehiculo c
        JOIN fleet.vehiculo v ON v.id = c.vehiculo_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = c.chofer_id
        WHERE c.propietario_id = :propietario_id 
          AND c.control_base_id = :control_base_id
          AND c.estado_contrato = 'PENDIENTE_CONFIGURACION'
        ORDER BY c.created_at DESC
    """)
    result = await db.execute(query, {
        "propietario_id": propietario_id,
        "control_base_id": control_base_id
    })
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


# ============================================
# 8. OBTENER CAPACIDAD CONDUCTOR DE UN PROPIETARIO
# ============================================

@router.get("/capacidad-conductor")
async def obtener_capacidad_conductor(
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Verifica si el propietario autenticado tiene capacidad CONDUCTOR activa.
    """
    propietario_id = UUID(ctx["propietario_id"])
    
    tiene_capacidad = await es_conductor(propietario_id, db)
    
    return {
        "tiene_capacidad_conductor": tiene_capacidad,
        "mensaje": "El propietario está habilitado como conductor" if tiene_capacidad else "El propietario no está habilitado como conductor"
    }


# ============================================
# 9. C2 — GENERAR QR OPERATIVO
# ============================================

@router.post("/{contrato_id}/generar-qr", response_model=GenerarQrResponse)
async def generar_qr_operativo(
    contrato_id: UUID,
    request: GenerarQrRequest,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Genera un QR operativo para un contrato ACTIVO.
    El QR permite al conductor autorizado iniciar una jornada.
    """
    propietario_id = UUID(ctx["propietario_id"])
    
    query_contrato = text("""
        SELECT id, estado_contrato, activo
        FROM fleet.contrato_vehiculo
        WHERE id = :contrato_id AND propietario_id = :propietario_id
    """)
    result = await db.execute(query_contrato, {
        "contrato_id": contrato_id,
        "propietario_id": propietario_id
    })
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    
    if row[1] != "ACTIVO" or not row[2]:
        raise HTTPException(status_code=400, detail="El contrato no está ACTIVO")
    
    resultado = await QRService.generar_qr(
        propietario_id=propietario_id,
        contrato_id=contrato_id,
        db=db,
        dias_validez=request.dias_validez or 30
    )
    
    return GenerarQrResponse(
        token=resultado["token"],
        contrato_id=contrato_id,
        expires_at=resultado.get("fecha_expiracion"),
        mensaje="QR generado exitosamente"
    )


# ============================================
# 10. FUNCIONES AUXILIARES PRIVADAS
# ============================================

async def _get_contrato_by_id(contrato_id: UUID, db: AsyncSession) -> ContratoResponse:
    """
    Obtiene un contrato por ID sin validación de propietario (uso interno).
    PRECAUCIÓN: Esta función NO valida propietario ni tenant.
    Solo debe usarse internamente después de crear un contrato.
    """
    query = text("""
        SELECT 
            c.id, c.vehiculo_id, v.patente, v.marca, v.modelo,
            c.chofer_id, p.nombre as chofer_nombre, p.apellido as chofer_apellido,
            c.tipo_contrato,
            c.hora_inicio, c.hora_fin, c.duracion_minima_horas, c.permite_extension, c.hora_fin_extension,
            c.porcentaje_chofer, c.monto_diario,
            c.fecha_inicio, c.fecha_fin, c.activo, c.estado_contrato,
            c.canon_diario, c.km_incluidos_dia, c.valor_km_excedente,
            c.modalidad_computo, c.dias_contractuales, c.tratamiento_dia_no_trabajado,
            c.dia_inicio_semana
        FROM fleet.contrato_vehiculo c
        JOIN fleet.vehiculo v ON v.id = c.vehiculo_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = c.chofer_id
        WHERE c.id = :contrato_id
    """)
    result = await db.execute(query, {"contrato_id": contrato_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    
    return _map_row_to_contrato_response(row)

# ============================================
# 11. VERIFICAR DISPONIBILIDAD EN TIEMPO REAL
# ============================================

@router.get("/contratos/verificar-disponibilidad")
async def verificar_disponibilidad(
    vehiculo_id: Optional[UUID] = Query(None, description="ID del vehículo a verificar"),
    chofer_id: Optional[UUID] = Query(None, description="ID del chofer a verificar"),
    hora_inicio: Optional[str] = Query(None, pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$", description="Hora inicio HH:MM"),
    hora_fin: Optional[str] = Query(None, pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$", description="Hora fin HH:MM"),
    dias_contractuales: Optional[str] = Query(None, description="JSON array de días: ['lunes','martes']"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio del contrato"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin del contrato"),
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Verifica disponibilidad de vehículo y chofer en tiempo real.
    Útil para feedback inmediato en el formulario.
    
    Retorna:
    - vehiculo_disponible: bool
    - chofer_disponible: bool
    - conflictos: List[str] - mensajes descriptivos
    - vehiculo_detalle: dict - información del contrato actual del vehículo
    - chofer_detalle: dict - información del contrato actual del chofer
    """
    propietario_id = UUID(ctx["propietario_id"])
    control_base_id = UUID(ctx["control_base_id"])
    
    response = {
        "vehiculo_disponible": True,
        "chofer_disponible": True,
        "conflictos": [],
        "vehiculo_detalle": None,
        "chofer_detalle": None
    }
    
    # Parsear días
    dias = None
    if dias_contractuales:
        try:
            dias = json.loads(dias_contractuales)
            if not isinstance(dias, list):
                dias = None
        except:
            dias = None
    
    # Si no hay horario, usar valores por defecto
    hora_inicio_efectiva = hora_inicio or "00:00"
    hora_fin_efectiva = hora_fin or "23:59"
    
    # ============================================
    # 1. Verificar vehículo
    # ============================================
    if vehiculo_id:
        # 1a. Verificar propiedad
        es_valido, mensaje = await verificar_propiedad_vehiculo(
            vehiculo_id, propietario_id, control_base_id, db
        )
        if not es_valido:
            response["vehiculo_disponible"] = False
            response["conflictos"].append(f"🚫 Vehículo no válido: {mensaje}")
        else:
            # 1b. Buscar conflictos del vehículo
            # Usar un chofer_id dummy para la validación de vehículo
            dummy_chofer_id = UUID("00000000-0000-0000-0000-000000000000")
            hay_conflictos, conflictos = await verificar_conflictos_contrato(
                vehiculo_id,
                dummy_chofer_id,
                hora_inicio_efectiva,
                hora_fin_efectiva,
                control_base_id,
                db,
                contrato_excluido_id=None,
                dias_contractuales=dias,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            
            if hay_conflictos:
                response["vehiculo_disponible"] = False
                # Filtrar y formatear conflictos de vehículo
                for c in conflictos:
                    if "vehículo" in c.lower():
                        response["conflictos"].append(f"🚗 {c}")
                
                # Obtener detalle del contrato actual del vehículo
                query_detalle = text("""
                    SELECT 
                        c.id, v.patente, c.hora_inicio, c.hora_fin, 
                        c.dias_contractuales, c.estado_contrato,
                        u.nombre as chofer_nombre, u.apellido as chofer_apellido
                    FROM fleet.contrato_vehiculo c
                    JOIN fleet.vehiculo v ON v.id = c.vehiculo_id
                    LEFT JOIN auth.usuario u ON u.id = c.chofer_id
                    WHERE c.vehiculo_id = :vehiculo_id
                      AND c.control_base_id = :control_base_id
                      AND c.estado_contrato IN ('ACTIVO', 'PROGRAMADO')
                    ORDER BY c.created_at DESC
                    LIMIT 1
                """)
                result = await db.execute(query_detalle, {
                    "vehiculo_id": vehiculo_id,
                    "control_base_id": control_base_id
                })
                row = result.first()
                if row:
                    response["vehiculo_detalle"] = {
                        "contrato_id": str(row[0]),
                        "patente": row[1],
                        "hora_inicio": row[2].strftime("%H:%M") if row[2] else None,
                        "hora_fin": row[3].strftime("%H:%M") if row[3] else None,
                        "dias_contractuales": row[4] if row[4] else [],
                        "estado": row[5],
                        "chofer": f"{row[6] or ''} {row[7] or ''}".strip() if row[6] else None
                    }
    
    # ============================================
    # 2. Verificar chofer
    # ============================================
    if chofer_id:
        # 2a. Verificar que el chofer existe y es válido
        es_valido, mensaje = await verificar_chofer_valido(
            chofer_id, control_base_id, db
        )
        if not es_valido:
            response["chofer_disponible"] = False
            response["conflictos"].append(f"🚫 Chofer no válido: {mensaje}")
        else:
            # 2b. Buscar conflictos del chofer
            dummy_vehiculo_id = UUID("00000000-0000-0000-0000-000000000000")
            hay_conflictos, conflictos = await verificar_conflictos_contrato(
                dummy_vehiculo_id,
                chofer_id,
                hora_inicio_efectiva,
                hora_fin_efectiva,
                control_base_id,
                db,
                contrato_excluido_id=None,
                dias_contractuales=dias,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            
            if hay_conflictos:
                response["chofer_disponible"] = False
                for c in conflictos:
                    if "chofer" in c.lower():
                        response["conflictos"].append(f"👤 {c}")
                
                # Obtener detalle del contrato actual del chofer
                query_detalle = text("""
                    SELECT 
                        c.id, v.patente, c.hora_inicio, c.hora_fin,
                        c.dias_contractuales, c.estado_contrato,
                        c.vehiculo_id
                    FROM fleet.contrato_vehiculo c
                    JOIN fleet.vehiculo v ON v.id = c.vehiculo_id
                    WHERE c.chofer_id = :chofer_id
                      AND c.control_base_id = :control_base_id
                      AND c.estado_contrato IN ('ACTIVO', 'PROGRAMADO')
                    ORDER BY c.created_at DESC
                    LIMIT 1
                """)
                result = await db.execute(query_detalle, {
                    "chofer_id": chofer_id,
                    "control_base_id": control_base_id
                })
                row = result.first()
                if row:
                    response["chofer_detalle"] = {
                        "contrato_id": str(row[0]),
                        "patente": row[1],
                        "hora_inicio": row[2].strftime("%H:%M") if row[2] else None,
                        "hora_fin": row[3].strftime("%H:%M") if row[3] else None,
                        "dias_contractuales": row[4] if row[4] else [],
                        "estado": row[5],
                        "vehiculo_id": str(row[6]) if row[6] else None
                    }
    
    return response

def _map_row_to_contrato_response(row) -> ContratoResponse:
    """
    Mapea una fila de base de datos a ContratoResponse
    Índices CORREGIDOS para la nueva estructura de columnas
    """
    # El orden de las columnas en la consulta SELECT es:
    # 0: id
    # 1: vehiculo_id
    # 2: patente
    # 3: marca
    # 4: modelo
    # 5: chofer_id
    # 6: chofer_nombre
    # 7: chofer_apellido
    # 8: tipo_contrato
    # 9: hora_inicio
    # 10: hora_fin
    # 11: duracion_minima_horas
    # 12: permite_extension
    # 13: hora_fin_extension
    # 14: porcentaje_chofer
    # 15: monto_diario
    # 16: fecha_inicio
    # 17: fecha_fin
    # 18: activo
    # 19: estado_contrato
    # 20: canon_diario
    # 21: km_incluidos_dia
    # 22: valor_km_excedente
    # 23: modalidad_computo
    # 24: dias_contractuales
    # 25: tratamiento_dia_no_trabajado
    # 26: dia_inicio_semana
    
    # Procesar dias_contractuales (índice 24)
    dias = row[24]
    if isinstance(dias, str):
        try:
            dias = json.loads(dias)
        except:
            dias = []
    elif dias is None:
        dias = []
    
    # Procesar tratamiento_dia_no_trabajado (índice 25)
    tratamiento = row[25]
    if isinstance(tratamiento, list):
        tratamiento = None
    
    # Convertir time a string HH:MM
    hora_inicio_str = row[9].strftime("%H:%M") if row[9] else None
    hora_fin_str = row[10].strftime("%H:%M") if row[10] else None
    hora_fin_extension_str = row[13].strftime("%H:%M") if row[13] else None
    
    return ContratoResponse(
        id=row[0],
        vehiculo_id=row[1],
        patente=row[2],
        marca=row[3],
        modelo=row[4],
        chofer_id=row[5],
        chofer_nombre=row[6],
        chofer_apellido=row[7],
        tipo_contrato=row[8],
        hora_inicio=hora_inicio_str,
        hora_fin=hora_fin_str,
        duracion_minima_horas=row[11],
        permite_extension=row[12],
        hora_fin_extension=hora_fin_extension_str,
        porcentaje_chofer=float(row[14]) if row[14] is not None else None,
        monto_diario=float(row[15]) if row[15] is not None else None,
        fecha_inicio=row[16],
        fecha_fin=row[17],
        activo=row[18],
        estado_contrato=row[19],
        canon_diario=float(row[20]) if row[20] is not None else None,
        km_incluidos_dia=float(row[21]) if row[21] is not None else None,
        valor_km_excedente=float(row[22]) if row[22] is not None else None,
        modalidad_computo=row[23],
        dias_contractuales=dias if isinstance(dias, list) else [],
        tratamiento_dia_no_trabajado=tratamiento,
        dia_inicio_semana=row[26] if len(row) > 26 else None
    )