"""
Router para chofer - Gestión de turnos.
Flujo: Validar código → Check-in → Operación → Check-out
También soporta Check-in directo para propietario-chofer (auto-gestión).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user
from app.services.turno_service import TurnoService
from app.services.turno_authorization import TurnoAuthorizationService
from app.schemas.turno_schemas import (
    # Requests
    CheckInRequest,
    CheckInDirectoRequest,
    CheckOutRequest,
    ValidarCodigoRequest,
    # G67 - forzar cierre de viajes huerfanos
    CerrarViajeHuerfanoRequest,
    
    # Responses
    CheckInResponse,
    CheckOutResponse,
    TurnoActivoResponse,
    EstadoTurnoResponse,
    ValidarCodigoResponse,
    ModoInicioResponse,
    ResumenResponse,
    VehiculoInfo,
    VehiculoDisponibleInfo,
    # G67 - forzar cierre de viajes huerfanos
    ViajesHuerfanosResponse,
    CerrarViajeHuerfanoResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chofer/turno", tags=["Chofer - Turnos"])

# ==========================================
# CONSTANTES
# ==========================================
COMBUSTIBLES_VALIDOS = ['RESERVA', '1/4', '1/2', '3/4', 'LLENO']


# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def calcular_duracion(inicio_turno: Optional[datetime]) -> tuple[int, str]:
    """
    Calcula la duración desde el inicio del turno hasta ahora.
    Devuelve (minutos, formateada como HH:MM:SS).
    """
    if not inicio_turno:
        return 0, "00:00:00"

    ahora = datetime.now()
    diff = ahora - inicio_turno
    total_segundos = int(diff.total_seconds())

    if total_segundos < 0:
        return 0, "00:00:00"

    minutos = total_segundos // 60
    horas = minutos // 60
    mins = minutos % 60
    segs = total_segundos % 60
    formateada = f"{horas:02d}:{mins:02d}:{segs:02d}"

    return minutos, formateada




class BannerInfo(BaseModel):
    titulo: str
    subtitulo: str
    color_estado: str
    tipo_contrato: Optional[str] = None
    porcentaje_chofer: Optional[float] = None
    monto_diario: Optional[float] = None
    tratamiento_gastos: Optional[str] = None

class ResumenResponse(BaseModel):
    fecha_inicio: str
    fecha_fin: str
    dias: int
    viajes: int
    recaudado: float
    km_recorridos: float
    duracion_minutos: int
    viaje_mas_caro: float
    viaje_mas_bajo: float
    promedio_viaje: float
    desglose_por_origen: Optional[Dict[str, Dict[str, float]]] = None
    
    # Nuevos campos Fase 1
    banner_info: BannerInfo
    recaudacion_efectivo: float = 0.0
    recaudacion_electronico: float = 0.0
    gastos_turno: float = 0.0



# ==========================================
# ENDPOINTS
# ==========================================

@router.get("/estado", response_model=EstadoTurnoResponse)
async def obtener_estado_turno(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el estado completo del chofer para operar.
    Verifica: aprobación, vehículo, contrato, turno activo.
    """
    user_id, control_base_id, email, tipo = current_user

    # 1. Verificar chofer
    query_chofer = text("""
        SELECT
            cv.estado_aprobacion,
            cv.estado_laboral,
            cv.vehiculo_id IS NOT NULL as tiene_vehiculo,
            cv.vehiculo_id
        FROM fleet.chofer_vehiculo cv
        WHERE cv.usuario_id = :user_id
    """)
    result = await db.execute(query_chofer, {"user_id": user_id})
    row = result.first()

    if not row:
        return EstadoTurnoResponse(
            puede_operar=False,
            motivo="Chofer no registrado en el sistema",
            estado_aprobacion="pendiente",
            estado_laboral="fuera_servicio",
            tiene_turno_activo=False,
            tiene_vehiculo=False,
            tiene_contrato_activo=False
        )

    estado_aprobacion, estado_laboral, tiene_vehiculo, vehiculo_id = row

    # 2. Verificar contrato activo
    tiene_contrato = False
    if tiene_vehiculo and vehiculo_id:
        query_contrato = text("""
            SELECT id FROM fleet.contrato_vehiculo
            WHERE chofer_id = :user_id
              AND vehiculo_id = :vehiculo_id
              AND estado_contrato = 'ACTIVO'
              AND activo = true
            LIMIT 1
        """)
        result = await db.execute(query_contrato, {
            "user_id": user_id,
            "vehiculo_id": vehiculo_id
        })
        tiene_contrato = result.first() is not None

    # 3. Verificar turno activo
    query_turno = text("""
        SELECT id FROM fleet.turno_chofer
        WHERE chofer_id = :user_id AND estado = 'ACTIVO'
        LIMIT 1
    """)
    result = await db.execute(query_turno, {"user_id": user_id})
    tiene_turno_activo = result.first() is not None

    # 4. Determinar si puede operar
    puede_operar = (
        estado_aprobacion == 'aprobado' and
        tiene_vehiculo and
        tiene_contrato and
        tiene_turno_activo and
        estado_laboral in ['libre', 'ocupado']
    )

    motivo = None
    if not puede_operar:
        if estado_aprobacion != 'aprobado':
            motivo = f"Chofer no aprobado. Estado: {estado_aprobacion}"
        elif not tiene_vehiculo:
            motivo = "Chofer sin vehículo asignado"
        elif not tiene_contrato:
            motivo = "Chofer sin contrato activo"
        elif not tiene_turno_activo:
            motivo = "Chofer sin turno activo"
        elif estado_laboral not in ['libre', 'ocupado']:
            motivo = f"Estado laboral incorrecto: {estado_laboral}"

    return EstadoTurnoResponse(
        puede_operar=puede_operar,
        motivo=motivo,
        estado_aprobacion=estado_aprobacion,
        estado_laboral=estado_laboral,
        tiene_turno_activo=tiene_turno_activo,
        tiene_vehiculo=tiene_vehiculo,
        tiene_contrato_activo=tiene_contrato
    )


@router.get("/activo", response_model=TurnoActivoResponse)
async def obtener_turno_activo(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el turno activo del chofer (si existe) con TODOS los datos.
    """
    user_id, control_base_id, email, tipo = current_user

    query = text("""
        SELECT
            t.id,
            t.estado,
            t.inicio_turno,
            t.vehiculo_id,
            t.km_inicial,
            t.combustible_inicial,
            v.patente,
            v.marca,
            v.modelo,
            v.anio,
            COALESCE(cv.estado_laboral, 'libre') as estado_laboral,
            t.contrato_id
        FROM fleet.turno_chofer t
        JOIN fleet.vehiculo v ON v.id = t.vehiculo_id
        LEFT JOIN fleet.chofer_vehiculo cv ON cv.usuario_id = t.chofer_id
        WHERE t.chofer_id = :user_id AND t.estado = 'ACTIVO'
        LIMIT 1
    """)
    result = await db.execute(query, {"user_id": user_id})
    row = result.first()

    if not row:
        return TurnoActivoResponse(tiene_turno_activo=False)

    duracion_minutos, duracion_formateada = calcular_duracion(row[2])

    return TurnoActivoResponse(
        tiene_turno_activo=True,
        turno_id=row[0],
        estado=row[1],
        inicio_turno=row[2],
        vehiculo_id=row[3],
        km_inicial=float(row[4]) if row[4] else None,
        combustible_inicial=row[5],
        patente=row[6],
        marca=row[7],
        modelo=row[8],
        anio=row[9],
        estado_laboral=row[10],
        contrato_id=row[11],
        duracion_minutos=duracion_minutos,
        duracion_formateada=duracion_formateada,
    )


@router.post("/validar-codigo", response_model=ValidarCodigoResponse)
async def validar_codigo_turno(
    request: ValidarCodigoRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Valida el código de 6 dígitos proporcionado por el propietario.
    Si es válido, genera una autorización temporal para iniciar el turno.
    """
    user_id, control_base_id, email, tipo = current_user

    # 1. Verificar que el chofer está aprobado
    query_chofer = text("""
        SELECT estado_aprobacion, vehiculo_id
        FROM fleet.chofer_vehiculo
        WHERE usuario_id = :user_id
    """)
    result = await db.execute(query_chofer, {"user_id": user_id})
    row = result.first()

    if not row:
        raise HTTPException(404, "Chofer no encontrado")

    estado_aprobacion, vehiculo_id = row

    if estado_aprobacion != 'aprobado':
        raise HTTPException(400, f"Chofer no aprobado. Estado: {estado_aprobacion}")

    if not vehiculo_id:
        raise HTTPException(400, "Chofer sin vehículo asignado. Contacta a tu propietario.")

    # 2. Verificar que no tenga turno activo
    query_turno = text("""
        SELECT id FROM fleet.turno_chofer
        WHERE chofer_id = :user_id AND estado = 'ACTIVO'
        LIMIT 1
    """)
    result = await db.execute(query_turno, {"user_id": user_id})
    if result.first():
        raise HTTPException(400, "Ya tienes un turno activo. Finalízalo antes de iniciar otro.")

    # 3. Buscar el código
    query_codigo = text("""
        SELECT
            cv.id,
            cv.codigo,
            cv.usado,
            cv.expira_en,
            cv.intentos
        FROM auth.codigo_verificacion cv
        WHERE cv.codigo = :codigo
          AND cv.tipo = 'INICIO_TURNO'
          AND cv.usado = false
          AND cv.expira_en > NOW()
    """)
    result = await db.execute(query_codigo, {"codigo": request.codigo})
    row = result.first()

    if not row:
        raise HTTPException(400, "Código inválido, expirado o ya utilizado")

    codigo_id, codigo, usado, expira_en, intentos = row

    # 4. Obtener metadatos del código (contrato, vehículo, propietario)
    query_metadata = text("""
        SELECT
            cm.contrato_id,
            cm.vehiculo_id,
            cm.propietario_id,
            cv.estado_contrato,
            cv.activo,
            v.patente,
            v.marca,
            v.modelo,
            v.anio
        FROM auth.codigo_metadatos cm
        JOIN fleet.contrato_vehiculo cv ON cv.id = cm.contrato_id
        JOIN fleet.vehiculo v ON v.id = cm.vehiculo_id
        WHERE cm.codigo_id = :codigo_id
    """)
    result = await db.execute(query_metadata, {"codigo_id": codigo_id})
    row = result.first()

    if not row:
        raise HTTPException(400, "Código no tiene contrato asociado")

    (contrato_id, vehiculo_codigo, propietario_id, estado_contrato, activo,
     patente, marca, modelo, anio) = row

    # 5. Validar contrato
    if estado_contrato != 'ACTIVO' or not activo:
        raise HTTPException(400, "El contrato asociado no está ACTIVO")

    # 6. Validar que el vehículo coincide con el chofer
    if vehiculo_codigo != vehiculo_id:
        raise HTTPException(400, "El código no corresponde a tu vehículo asignado")

    # 7. Obtener la licencia del chofer
    query_perfil = text("""
        SELECT documento
        FROM auth.perfil_general
        WHERE usuario_id = :user_id
    """)
    result = await db.execute(query_perfil, {"user_id": user_id})
    perfil_row = result.first()
    licencia_numero = perfil_row[0] if perfil_row and perfil_row[0] else "Sin licencia"

    # 8. Generar autorización temporal
    auth_token = str(uuid4())
    expires_at = datetime.now() + timedelta(minutes=5)

    # 9. Guardar autorización
    query_autorizacion = text("""
        INSERT INTO auth.autorizacion_inicio (
            id, token, contrato_id, chofer_id, vehiculo_id, control_base_id,
            created_at, expires_at, qr_referencia, created_by
        ) VALUES (
            gen_random_uuid(), :auth_token, :contrato_id, :user_id, :vehiculo_id, :control_base_id,
            NOW(), :expires_at, NULL, :propietario_id
        )
        RETURNING id
    """)
    result = await db.execute(query_autorizacion, {
        "auth_token": auth_token,
        "contrato_id": contrato_id,
        "user_id": user_id,
        "vehiculo_id": vehiculo_id,
        "control_base_id": control_base_id,
        "expires_at": expires_at,
        "propietario_id": propietario_id
    })
    autorizacion_id = result.scalar()

    # 10. Marcar código como usado
    await db.execute(
        text("UPDATE auth.codigo_verificacion SET usado = true WHERE id = :codigo_id"),
        {"codigo_id": codigo_id}
    )

    await db.commit()

    return ValidarCodigoResponse(
        success=True,
        message="Código validado. Ahora puedes iniciar tu turno.",
        auth_token=auth_token,
        expires_at=expires_at,
        contrato_id=contrato_id,
        vehiculo=VehiculoInfo(
            id=vehiculo_id,
            patente=patente,
            marca=marca,
            modelo=modelo,
            anio=anio
        ),
        licencia=licencia_numero
    )


@router.post("/check-in", response_model=CheckInResponse)
async def check_in_turno(
    request: CheckInRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Inicia el turno del chofer usando la autorización temporal.
    Requiere: auth_token, km_inicial, combustible_inicial.
    """
    user_id, control_base_id, email, tipo = current_user

    # 1. Validar combustible
    if request.combustible_inicial not in COMBUSTIBLES_VALIDOS:
        raise HTTPException(400, f"Combustible inválido. Permitidos: {COMBUSTIBLES_VALIDOS}")

    # 2. Validar autorización
    query_auth = text("""
        SELECT
            id, contrato_id, vehiculo_id, expires_at, used_at
        FROM auth.autorizacion_inicio
        WHERE token = :auth_token
          AND chofer_id = :user_id
    """)
    result = await db.execute(query_auth, {
        "auth_token": request.auth_token,
        "user_id": user_id
    })
    row = result.first()

    if not row:
        raise HTTPException(400, "Autorización no encontrada")

    auth_id, contrato_id, vehiculo_id, expires_at, used_at = row

    # 3. Validar expiración
    if expires_at and expires_at < datetime.now():
        raise HTTPException(400, "La autorización ha expirado. Solicita un nuevo código.")

    # 4. Validar que no esté usada
    if used_at:
        raise HTTPException(400, "Esta autorización ya fue utilizada")

    # 5. Verificar que no tenga turno activo
    query_turno = text("""
        SELECT id FROM fleet.turno_chofer
        WHERE chofer_id = :user_id AND estado = 'ACTIVO'
        LIMIT 1
    """)
    result = await db.execute(query_turno, {"user_id": user_id})
    if result.first():
        raise HTTPException(400, "Ya tienes un turno activo. Finalizalo antes de iniciar otro.")

    # 6. Verificar que el vehiculo no tenga un turno activo de otro chofer
    query_vehiculo_ocupado = text("""
        SELECT
            tc.id AS turno_id,
            tc.inicio_turno,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) AS chofer_nombre,
            u.email AS chofer_email
        FROM fleet.turno_chofer tc
        JOIN auth.usuario u ON u.id = tc.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE tc.vehiculo_id = :vehiculo_id
          AND tc.estado = 'ACTIVO'
        LIMIT 1
    """)
    result = await db.execute(query_vehiculo_ocupado, {"vehiculo_id": vehiculo_id})
    turno_ocupado = result.first()

    if turno_ocupado:
        turno_id_ocupado, inicio_ocupado, chofer_nombre, chofer_email = turno_ocupado
        raise HTTPException(
            status_code=400,
            detail=(
                f"El vehiculo ya tiene un turno ACTIVO iniciado por otro chofer "
                f"({chofer_nombre} - {chofer_email}) el {inicio_ocupado.strftime('%d/%m/%Y %H:%M')}. "
                f"Pedile que cierre su turno o contacta al administrador para liberarlo."
            ),
        )

    # 6.bis. Validar km
    if request.km_inicial < 0:
        raise HTTPException(400, "El kilometraje no puede ser negativo")

    # 7. Crear turno usando el servicio existente
    try:
        resultado = await TurnoService.check_in(
            db=db,
            chofer_id=user_id,
            vehiculo_id=vehiculo_id,
            km_inicial=request.km_inicial,
            combustible_inicial=request.combustible_inicial
        )

        # 8. Marcar autorización como usada
        await db.execute(
            text("UPDATE auth.autorizacion_inicio SET used_at = NOW() WHERE id = :auth_id"),
            {"auth_id": auth_id}
        )

        await db.commit()

        # 9. Obtener datos del vehículo
        query_vehiculo = text("""
            SELECT patente, marca, modelo, anio
            FROM fleet.vehiculo WHERE id = :vehiculo_id
        """)
        result = await db.execute(query_vehiculo, {"vehiculo_id": vehiculo_id})
        v_row = result.first()

        duracion_minutos, duracion_formateada = calcular_duracion(datetime.now())

        return CheckInResponse(
            success=True,
            message="Turno iniciado correctamente",
            turno_id=resultado["turno_id"],
            vehiculo_id=vehiculo_id,
            patente=v_row[0],
            marca=v_row[1],
            modelo=v_row[2],
            anio=v_row[3],
            inicio_turno=datetime.now(),
            estado_laboral="libre",
            km_inicial=request.km_inicial,
            combustible_inicial=request.combustible_inicial,
            duracion_minutos=duracion_minutos,
            duracion_formateada=duracion_formateada,
        )

    except HTTPException as e:
        await db.rollback()
        raise e
    except Exception as e:
        await db.rollback()
        logger.error(f"Error en check-in: {str(e)}")
        raise HTTPException(500, f"Error al iniciar turno: {str(e)}")


@router.post("/check-in-directo", response_model=CheckInResponse)
async def check_in_directo(
    request: CheckInDirectoRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Inicia turno directamente con un vehículo propio (sin código).
    Solo para propietarios que son dueños del vehículo.
    """
    user_id, control_base_id, email, tipo = current_user

    # 1. Validar combustible
    if request.combustible_inicial not in COMBUSTIBLES_VALIDOS:
        raise HTTPException(400, f"Combustible inválido. Permitidos: {COMBUSTIBLES_VALIDOS}")

    # 2. Verificar que el usuario es propietario de ese vehículo
    query_prop = text("""
        SELECT 1
        FROM fleet.propietario_vehiculo pv
        JOIN fleet.vehiculo v ON v.id = pv.vehiculo_id
        WHERE pv.propietario_id = :user_id
          AND pv.vehiculo_id = :vehiculo_id
          AND pv.activo = true
          AND v.activo = true
    """)
    result = await db.execute(query_prop, {
        "user_id": user_id,
        "vehiculo_id": request.vehiculo_id
    })
    if not result.first():
        raise HTTPException(403, "No sos propietario de este vehículo")

        # 3. Verificar que el vehículo no tenga turno activo
    query_turno = text("""
        SELECT
            tc.id AS turno_id,
            tc.inicio_turno,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) AS chofer_nombre,
            u.email AS chofer_email
        FROM fleet.turno_chofer tc
        JOIN auth.usuario u ON u.id = tc.chofer_id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE tc.vehiculo_id = :vehiculo_id
        AND tc.estado = 'ACTIVO'
        LIMIT 1
    """)
    result = await db.execute(query_turno, {"vehiculo_id": request.vehiculo_id})
    turno_ocupado = result.first()

    if turno_ocupado:
        turno_id_ocupado, inicio_ocupado, chofer_nombre, chofer_email = turno_ocupado
        raise HTTPException(
            status_code=400,
            detail=(
                f"El vehiculo ya tiene un turno ACTIVO iniciado por otro chofer "
                f"({chofer_nombre} - {chofer_email}) el {inicio_ocupado.strftime('%d/%m/%Y %H:%M')}. "
                f"Pedile que cierre su turno o contacta al administrador para liberarlo."
            ),
        )

    # 4. Verificar que el usuario no tenga turno activo
    query_turno_user = text("""
        SELECT id FROM fleet.turno_chofer
        WHERE chofer_id = :user_id AND estado = 'ACTIVO'
        LIMIT 1
    """)
    result = await db.execute(query_turno_user, {"user_id": user_id})
    if result.first():
        raise HTTPException(400, "Ya tenés un turno activo. Finalizalo antes de iniciar otro.")
    
    # 5. Verificar que el chofer está aprobado
    query_chofer = text("""
        SELECT estado_aprobacion
        FROM fleet.chofer_vehiculo
        WHERE usuario_id = :user_id
    """)
    result = await db.execute(query_chofer, {"user_id": user_id})
    chofer_row = result.first()

    if chofer_row and chofer_row[0] != 'aprobado':
        # Si es propietario, permitimos aunque no esté aprobado como chofer
        pass

    # 6. Buscar o crear contrato AUTO_GESTION
    query_contrato = text("""
        SELECT id FROM fleet.contrato_vehiculo
        WHERE propietario_id = :user_id
          AND vehiculo_id = :vehiculo_id
          AND chofer_id = :user_id
          AND tipo_contrato = 'AUTO_GESTION'
          AND activo = true
        LIMIT 1
    """)
    result = await db.execute(query_contrato, {
        "user_id": user_id,
        "vehiculo_id": request.vehiculo_id
    })
    contrato_row = result.first()

    if contrato_row:
        contrato_id = contrato_row[0]
    else:
        query_crear = text("""
            INSERT INTO fleet.contrato_vehiculo (
                id, control_base_id, propietario_id, vehiculo_id, chofer_id,
                tipo_contrato, estado_contrato, activo, fecha_inicio,
                hora_inicio, hora_fin, duracion_minima_horas, permite_extension,
                modalidad_computo, tratamiento_dia_no_trabajado, compensacion_km,
                created_at, updated_at
            ) VALUES (
                gen_random_uuid(), :control_base_id, :user_id, :vehiculo_id, :user_id,
                'AUTO_GESTION', 'ACTIVO', true, NOW(),
                '00:00', '23:59', 6, false,
                'DIARIO', 'POR_DISPONIBILIDAD', 'DIARIA',
                NOW(), NOW()
            )
            RETURNING id
        """)
        result = await db.execute(query_crear, {
            "control_base_id": control_base_id,
            "user_id": user_id,
            "vehiculo_id": request.vehiculo_id
        })
        contrato_id = result.scalar()
        await db.commit()

    # 7. Crear turno usando INSERT directo (no pasa por TurnoService.check_in
    #    porque este valida horarios contractuales que en AUTO_GESTION son flexibles)
    try:
        query_turno = text("""
            INSERT INTO fleet.turno_chofer (
                id, contrato_id, chofer_id, vehiculo_id, estado,
                km_inicial, combustible_inicial, inicio_turno,
                created_at, updated_at
            ) VALUES (
                gen_random_uuid(), :contrato_id, :chofer_id, :vehiculo_id, 'ACTIVO',
                :km_inicial, :combustible_inicial, NOW(),
                NOW(), NOW()
            )
            RETURNING id, inicio_turno
        """)
        result = await db.execute(query_turno, {
            "contrato_id": contrato_id,
            "chofer_id": user_id,
            "vehiculo_id": request.vehiculo_id,
            "km_inicial": request.km_inicial,
            "combustible_inicial": request.combustible_inicial
        })
        turno_row = result.first()
        turno_id = turno_row[0]
        inicio_turno = turno_row[1]

        # 8. Actualizar estado laboral del chofer
        await db.execute(text("""
            UPDATE fleet.chofer_vehiculo
            SET estado_laboral = 'libre', updated_at = NOW()
            WHERE usuario_id = :user_id
        """), {"user_id": user_id})

        await db.commit()

        # 9. Obtener datos del vehículo
        query_vehiculo = text("""
            SELECT patente, marca, modelo, anio
            FROM fleet.vehiculo WHERE id = :vehiculo_id
        """)
        result = await db.execute(query_vehiculo, {"vehiculo_id": request.vehiculo_id})
        v_row = result.first()

        duracion_minutos, duracion_formateada = calcular_duracion(inicio_turno)

        return CheckInResponse(
            success=True,
            message="Turno iniciado correctamente",
            turno_id=turno_id,
            vehiculo_id=request.vehiculo_id,
            patente=v_row[0],
            marca=v_row[1],
            modelo=v_row[2],
            anio=v_row[3],
            inicio_turno=inicio_turno,
            estado_laboral="libre",
            km_inicial=request.km_inicial,
            combustible_inicial=request.combustible_inicial,
            duracion_minutos=duracion_minutos,
            duracion_formateada=duracion_formateada,
        )

    except HTTPException as e:
        await db.rollback()
        raise e
    except Exception as e:
        await db.rollback()
        logger.error(f"Error en check-in-directo: {str(e)}")
        raise HTTPException(500, f"Error al iniciar turno: {str(e)}")


@router.post("/check-out", response_model=CheckOutResponse)
async def check_out_turno(
    request: CheckOutRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Finaliza el turno del chofer.
    Requiere: km_final, combustible_final, recaudacion_ticketera (opcional).

    Al cerrar el turno, el chofer pasa a estado_laboral = 'fuera_servicio'.
    """
    user_id, control_base_id, email, tipo = current_user

    # 1. Validar combustible
    if request.combustible_final not in COMBUSTIBLES_VALIDOS:
        raise HTTPException(400, f"Combustible inválido. Permitidos: {COMBUSTIBLES_VALIDOS}")

    # 2. Buscar turno activo
    query_turno = text("""
        SELECT id, km_inicial, vehiculo_id, inicio_turno
        FROM fleet.turno_chofer
        WHERE chofer_id = :user_id AND estado = 'ACTIVO'
        ORDER BY inicio_turno DESC
        LIMIT 1
    """)
    result = await db.execute(query_turno, {"user_id": user_id})
    row = result.first()

    if not row:
        raise HTTPException(400, "No tienes un turno activo")

    turno_id, km_inicial, vehiculo_id, inicio_turno = row

    # 3. Validar km_final
    if request.km_final < 0:
        raise HTTPException(400, "El kilometraje no puede ser negativo")

    if request.km_final < km_inicial:
        raise HTTPException(400, f"El kilometraje final ({request.km_final}) no puede ser menor al inicial ({km_inicial})")


    # 4. Verificar que no tenga viaje activo.
    # R17 - G67: si los hay, indicar al chofer como cerrarlos forzadamente.
    # NOTA: el estado real de un viaje en curso en TaxIP es 'en_curso'.
    query_viaje = text("""
        SELECT COUNT(*) FROM trip.viaje_solicitado
        WHERE chofer_id = :user_id
          AND estado IN ('aceptado', 'en_curso')
    """)
    result = await db.execute(query_viaje, {"user_id": user_id})
    huerfanos = result.scalar() or 0
    if huerfanos > 0:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Tenes {huerfanos} viaje(s) sin cerrar. "
                f"Cerralos forzadamente en "
                f"/api/chofer/turno/viajes-huerfanos antes de cerrar el turno."
            ),
        )

    # 5. Cerrar turno usando el servicio existente
    try:
        resultado = await TurnoService.check_out(
            db=db,
            turno_id=turno_id,
            chofer_id=user_id,
            km_final=request.km_final,
            combustible_final=request.combustible_final,
            recaudacion_ticketera=request.recaudacion_ticketera
        )

        # 6. J16: resetear estado_laboral del chofer a 'fuera_servicio'.
        # TurnoService.check_out hace su propio commit, por eso este UPDATE
        # va en una segunda transacción. Deuda: unificar en una sola.
        await db.execute(text("""
            UPDATE fleet.chofer_vehiculo
            SET estado_laboral = 'fuera_servicio',
                updated_at = NOW()
            WHERE usuario_id = :user_id
              AND control_base_id = :control_base_id
        """), {
            "user_id": user_id,
            "control_base_id": control_base_id,
        })
        await db.commit()

        km_recorridos = float(request.km_final) - float(km_inicial)
        duracion_minutos, _ = calcular_duracion(inicio_turno)
        duracion_horas = round(duracion_minutos / 60, 2)

        return CheckOutResponse(
            success=True,
            message=resultado["mensaje"],
            turno_id=turno_id,
            estado="PENDIENTE_CONFIRMACION",
            km_recorridos=km_recorridos,
            duracion_horas=duracion_horas,
            ingresos_registrados=resultado.get("ingresos_registrados", 0),
            liquidacion_id=None
        )

    except HTTPException as e:
        await db.rollback()
        raise e
    except Exception as e:
        await db.rollback()
        logger.error(f"Error en check-out: {str(e)}")
        raise HTTPException(500, f"Error al cerrar turno: {str(e)}")

# ==========================================
# R17 - G67: FORZAR CIERRE DE VIAJES HUERFANOS
# ==========================================

@router.get("/viajes-huerfanos", response_model=ViajesHuerfanosResponse)
async def listar_viajes_huerfanos(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista los viajes del chofer que bloquean el cierre de turno.

    R17 - G67.

    Devuelve los viajes en estado 'aceptado' o 'en_curso' del chofer.
    El chofer debe cerrarlos forzadamente antes de poder hacer check-out.
    """
    user_id, control_base_id, email, tipo = current_user

    query = text("""
        SELECT
            id, estado, created_at, iniciado_en,
            direccion_origen, direccion_destino,
            nombre_pasajero, precio_estimado, origen_tipo,
            EXTRACT(EPOCH FROM (NOW() - created_at)) / 60 AS antiguedad_min
        FROM trip.viaje_solicitado
        WHERE chofer_id = :user_id
          AND estado IN ('aceptado', 'en_curso')
        ORDER BY created_at ASC
    """)
    result = await db.execute(query, {"user_id": str(user_id)})
    rows = result.fetchall()

    viajes = []
    for row in rows:
        viajes.append({
            "viaje_id": row[0],
            "estado": row[1],
            "created_at": row[2],
            "iniciado_en": row[3],
            "direccion_origen": row[4],
            "direccion_destino": row[5],
            "pasajero_nombre": row[6],
            "precio_estimado": float(row[7]) if row[7] else None,
            "origen_tipo": row[8],
            "antiguedad_minutos": int(row[9]) if row[9] else 0,
        })

    return {
        "total": len(viajes),
        "puede_cerrar_turno": len(viajes) == 0,
        "viajes": viajes,
    }


@router.post(
    "/viajes-huerfanos/{viaje_id}/cerrar",
    response_model=CerrarViajeHuerfanoResponse,
)
async def cerrar_viaje_huerfano(
    viaje_id: UUID,
    request: CerrarViajeHuerfanoRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cierra forzadamente un viaje huerfano del turno activo.

    R17 - G67.

    Reglas:
    - Solo el chofer del turno puede cerrarlo.
    - Solo viajes en estado 'aceptado' o 'en_curso'.
    - 'aceptado' -> 'cancelado' (sin cobro).
    - 'en_curso' -> 'finalizado' (con precio_estimado).
    - Notifica al chofer y al propietario.
    """
    user_id, control_base_id, email, tipo = current_user

    # 1. Buscar turno activo del chofer
    turno_query = text("""
        SELECT id FROM fleet.turno_chofer
        WHERE chofer_id = :user_id AND estado = 'ACTIVO'
        ORDER BY inicio_turno DESC
        LIMIT 1
    """)
    turno_row = (await db.execute(turno_query, {"user_id": str(user_id)})).first()

    if not turno_row:
        raise HTTPException(400, "No tenes un turno activo")

    turno_id = turno_row[0]

    # 2. Llamar al servicio
    try:
        resultado = await TurnoService.forzar_cierre_viaje(
            db=db,
            turno_id=turno_id,
            chofer_id=user_id,
            viaje_id=viaje_id,
            motivo=request.motivo,
            notas=request.notas,
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error en forzar cierre viaje {viaje_id}: {e}")
        raise HTTPException(500, f"Error al cerrar viaje forzadamente: {str(e)}")

    return CerrarViajeHuerfanoResponse(
        success=True,
        viaje_id=resultado["viaje_id"],
        estado_previo=resultado["estado_previo"],
        estado_nuevo=resultado["estado_nuevo"],
        motivo=resultado["motivo"],
        motivo_label=resultado["motivo_label"],
        precio_final=resultado["precio_final"],
        puede_cerrar_turno=resultado["puede_cerrar_turno"],
        message="Viaje cerrado forzadamente",
    )



@router.get("/historial")
async def listar_historial_turnos(
    limit: int = 20,
    offset: int = 0,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista el historial de turnos del chofer.
    """
    user_id, control_base_id, email, tipo = current_user

    query = text("""
        SELECT
            t.id,
            t.estado,
            t.inicio_turno,
            t.fin_turno,
            t.km_inicial,
            t.km_final,
            t.combustible_inicial,
            t.combustible_final,
            v.patente,
            v.marca,
            v.modelo,
            COALESCE(l.monto_bruto, 0) as monto_bruto,
            COALESCE(l.total_chofer, 0) as total_chofer,
            l.estado as estado_liquidacion
        FROM fleet.turno_chofer t
        JOIN fleet.vehiculo v ON v.id = t.vehiculo_id
        LEFT JOIN fleet.liquidacion l ON l.turno_id = t.id
        WHERE t.chofer_id = :user_id
        ORDER BY t.inicio_turno DESC
        LIMIT :limit OFFSET :offset
    """)
    result = await db.execute(query, {
        "user_id": user_id,
        "limit": limit,
        "offset": offset
    })
    rows = result.all()

    return [
        {
            "id": str(row[0]),
            "estado": row[1],
            "inicioTurno": row[2],
            "finTurno": row[3],
            "kmInicial": float(row[4]) if row[4] else None,
            "kmFinal": float(row[5]) if row[5] else None,
            "combustibleInicial": row[6],
            "combustibleFinal": row[7],
            "patente": row[8],
            "marca": row[9],
            "modelo": row[10],
            "montoBruto": float(row[11]) if row[11] else 0,
            "totalChofer": float(row[12]) if row[12] else 0,
            "estadoLiquidacion": row[13]
        }
        for row in rows
    ]


# ==========================================
# MODO DE INICIO (detectar tipo de usuario)
# ==========================================
@router.get("/modo-inicio", response_model=ModoInicioResponse)
async def obtener_modo_inicio(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Detecta si el usuario es propietario-chofer (auto-gestión) o chofer normal.

    - Si es propietario con vehículos → requiere_codigo = False
    - Si NO es propietario o no tiene vehículos → requiere_codigo = True
    """
    user_id, control_base_id, email, tipo = current_user

    # 1. ¿Es propietario?
    query_prop = text("""
        SELECT 1 FROM auth.usuario u
        WHERE u.id = :user_id
          AND u.tipo_usuario_id = (
              SELECT id FROM auth.tipo_usuario WHERE nombre = 'propietario'
          )
        UNION
        SELECT 1 FROM auth.usuario_rol ur
        WHERE ur.usuario_id = :user_id
          AND ur.tipo_usuario_id = (
              SELECT id FROM auth.tipo_usuario WHERE nombre = 'propietario'
          )
          AND ur.activo = true
          AND (ur.fecha_fin IS NULL OR ur.fecha_fin > NOW())
        LIMIT 1
    """)
    result = await db.execute(query_prop, {"user_id": user_id})
    es_propietario = result.first() is not None

    # 2. Si es propietario, buscar sus vehículos disponibles
    vehiculos = []
    if es_propietario:
        query_veh = text("""
            SELECT
                v.id,
                v.patente,
                v.marca,
                v.modelo,
                v.anio
            FROM fleet.vehiculo v
            JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
            WHERE pv.propietario_id = :user_id
              AND v.activo = true
              AND pv.activo = true
              AND NOT EXISTS (
                  SELECT 1 FROM fleet.turno_chofer t
                  WHERE t.vehiculo_id = v.id
                    AND t.estado = 'ACTIVO'
              )
            ORDER BY v.patente
        """)
        result = await db.execute(query_veh, {"user_id": user_id})
        for row in result.all():
            vehiculos.append(VehiculoDisponibleInfo(
                id=row[0],
                patente=row[1],
                marca=row[2],
                modelo=row[3],
                anio=row[4]
            ))

    # 3. Determinar si requiere código
    requiere_codigo = not (es_propietario and len(vehiculos) > 0)

    return ModoInicioResponse(
        es_propietario=es_propietario,
        requiere_codigo=requiere_codigo,
        vehiculos_disponibles=vehiculos
    )
@router.get("/resumen", response_model=ResumenResponse)
async def obtener_resumen(
    dias: int = 0,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el resumen de actividad del chofer (Banner Home).
    - dias=0: hoy
    - dias=1: ayer
    - dias=7: ultima semana
    """
    user_id, control_base_id, email, tipo = current_user
    
    # DEBUG: Descomenta la siguiente linea, reinicia el backend y mira la consola 
    # para verificar que el user_id coincide con: 095a7189-36fe-47e5-889a-83f84ad6fa94
    # import logging
    # logging.info(f"=== DEBUG Banner Resumen === user_id recibido: {user_id}")

    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if dias == 0:
        fecha_inicio = hoy
        fecha_fin = hoy + timedelta(days=1)
    else:
        fecha_fin = hoy
        fecha_inicio = hoy - timedelta(days=dias)

    # 1. Obtener contrato activo del chofer
    query_contrato = text("""
        SELECT tipo_contrato, porcentaje_chofer, canon_diario, tratamiento_gastos
        FROM fleet.contrato_vehiculo
        WHERE chofer_id = :user_id
          AND estado_contrato = 'ACTIVO'
          AND activo = true
        LIMIT 1
    """)
    result_contrato = await db.execute(query_contrato, {"user_id": user_id})
    row_contrato = result_contrato.first()
    
    tipo_contrato = row_contrato[0] if row_contrato else None
    porcentaje_chofer = float(row_contrato[1]) if row_contrato and row_contrato[1] else None
    canon_diario = float(row_contrato[2]) if row_contrato and row_contrato[2] else None
    tratamiento_gastos = row_contrato[3] if row_contrato else 'DESPUES'

    # 2. Viajes finalizados y split de caja (Efectivo vs Electronico)
    # NOTA: Filtra por finalizado_en >= fecha_inicio. Si los viajes de prueba 
    # se hicieron ayer, no apareceran en dias=0.
    query_viajes = text("""
        SELECT
            COUNT(*) as viajes,
            COALESCE(SUM(precio_final), 0) as recaudado,
            COALESCE(MAX(precio_final), 0) as viaje_mas_caro,
            COALESCE(MIN(precio_final), 0) as viaje_mas_bajo,
            COALESCE(SUM(CASE WHEN COALESCE(metodo_pago, 'efectivo') = 'efectivo' THEN precio_final ELSE 0 END), 0) as efectivo,
            COALESCE(SUM(CASE WHEN COALESCE(metodo_pago, 'efectivo') != 'efectivo' THEN precio_final ELSE 0 END), 0) as electronico
        FROM trip.viaje_solicitado
        WHERE chofer_id = :user_id
          AND estado = 'finalizado'
          AND finalizado_en >= :fecha_inicio
          AND finalizado_en < :fecha_fin
    """)
    result_viajes = await db.execute(query_viajes, {
        "user_id": user_id,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin
    })
    row_viajes = result_viajes.first()
    
    viajes = row_viajes[0] or 0
    recaudado = float(row_viajes[1] or 0)
    viaje_mas_caro = float(row_viajes[2] or 0)
    viaje_mas_bajo = float(row_viajes[3] or 0)
    recaudacion_efectivo = float(row_viajes[4] or 0)
    recaudacion_electronico = float(row_viajes[5] or 0)

    # 3. Fix de KM y Duracion para turno ACTIVO
    query_turno_activo = text("""
        SELECT id, km_inicial, km_final, inicio_turno
        FROM fleet.turno_chofer
        WHERE chofer_id = :user_id AND estado = 'ACTIVO'
        ORDER BY inicio_turno DESC LIMIT 1
    """)
    result_turno = await db.execute(query_turno_activo, {"user_id": user_id})
    row_turno = result_turno.first()
    
    km_recorridos = 0.0
    duracion_minutos = 0
    turno_id_para_gastos = None

    if row_turno:
        turno_id_para_gastos = row_turno[0]
        km_inicial, km_final, inicio_turno = row_turno[1], row_turno[2], row_turno[3]
        
        # Fix KM: si no hay km_final, sumar distancia_metros de viajes finalizados
        if km_inicial is not None and km_final is not None:
            km_recorridos = float(km_final - km_inicial)
        elif km_inicial is not None and km_final is None:
            query_km_activo = text("""
                SELECT COALESCE(SUM(distancia_metros), 0)
                FROM trip.viaje_solicitado
                WHERE chofer_id = :user_id
                  AND turno_id = :turno_id
                  AND estado = 'finalizado'
            """)
            res_km = await db.execute(query_km_activo, {"user_id": user_id, "turno_id": row_turno[0]})
            km_recorridos = float(res_km.scalar() or 0) / 1000.0
            
        # FIX DURACION: si el turno esta activo, calcular desde inicio_turno hasta AHORA
        if inicio_turno is not None:
            diff = datetime.now() - inicio_turno
            duracion_minutos = int(diff.total_seconds() // 60)
    else:
        # Si no hay turno activo, sumar duracion de turnos cerrados en el periodo
        query_turnos_cerrados = text("""
            SELECT COALESCE(SUM(EXTRACT(EPOCH FROM (fin_turno - inicio_turno)) / 60), 0)
            FROM fleet.turno_chofer
            WHERE chofer_id = :user_id
              AND estado IN ('CERRADO', 'PENDIENTE_CONFIRMACION')
              AND inicio_turno >= :fecha_inicio
              AND inicio_turno < :fecha_fin
              AND km_final IS NOT NULL AND fin_turno IS NOT NULL
        """)
        result_dur = await db.execute(query_turnos_cerrados, {"user_id": user_id, "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin})
        duracion_minutos = int(result_dur.scalar() or 0)
        
        # Buscar el ultimo turno cerrado para los gastos
        query_last_turno = text("""
            SELECT id FROM fleet.turno_chofer
            WHERE chofer_id = :user_id AND estado IN ('CERRADO', 'PENDIENTE_CONFIRMACION')
            AND inicio_turno >= :fecha_inicio AND inicio_turno < :fecha_fin
            ORDER BY inicio_turno DESC LIMIT 1
        """)
        res_last = await db.execute(query_last_turno, {"user_id": user_id, "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin})
        last_row = res_last.first()
        if last_row:
            turno_id_para_gastos = last_row[0]

    # 4. Gastos del turno
    gastos_turno = 0.0
    if turno_id_para_gastos:
        query_gastos = text("SELECT COALESCE(SUM(monto), 0) FROM fleet.gasto_turno WHERE turno_id = :turno_id")
        res_gastos = await db.execute(query_gastos, {"turno_id": turno_id_para_gastos})
        gastos_turno = float(res_gastos.scalar() or 0)

    # 5. Desglose por origen
    query_desglose = text("""
        SELECT COALESCE(origen_tipo, 'desconocido') as origen, COUNT(*) as viajes, COALESCE(SUM(precio_final), 0) as recaudado
        FROM trip.viaje_solicitado
        WHERE chofer_id = :user_id AND estado = 'finalizado'
          AND finalizado_en >= :fecha_inicio AND finalizado_en < :fecha_fin
        GROUP BY COALESCE(origen_tipo, 'desconocido')
    """)
    result_desglose = await db.execute(query_desglose, {"user_id": user_id, "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin})
    desglose = {row[0]: {"viajes": int(row[1]), "recaudado": round(float(row[2]), 2)} for row in result_desglose.fetchall()}

    # 6. CALCULAR BANNER_INFO (Logica de Negocio)
    banner_info = BannerInfo(titulo="", subtitulo="", color_estado="gris")
    
    if not tipo_contrato:
        banner_info.titulo = "Sin contrato activo"
        banner_info.subtitulo = "Contacta a tu propietario"
        
    elif tipo_contrato == "PORCENTAJE":
        if tratamiento_gastos == "ANTES":
            base = max(0, recaudado - gastos_turno)
            tu_parte = base * (porcentaje_chofer / 100.0)
        else:
            tu_parte = (recaudado * (porcentaje_chofer / 100.0)) - gastos_turno
            
        banner_info.titulo = f"Tu parte: ${tu_parte:,.0f}"
        banner_info.subtitulo = f"{viajes} viajes - {porcentaje_chofer}% de ${recaudado:,.0f}"
        banner_info.color_estado = "primary"
        banner_info.tipo_contrato = "PORCENTAJE"
        banner_info.porcentaje_chofer = porcentaje_chofer
        banner_info.tratamiento_gastos = tratamiento_gastos
        
    elif tipo_contrato == "ALQUILER":
        if recaudado < canon_diario:
            falta = canon_diario - recaudado
            banner_info.titulo = f"Faltan ${falta:,.0f} para el canon"
            banner_info.subtitulo = f"Llevas ${recaudado:,.0f} de ${canon_diario:,.0f} - {viajes} viajes"
            banner_info.color_estado = "naranja"
        else:
            ganancia = recaudado - canon_diario
            banner_info.titulo = f"Canon cubierto! Ganancia: ${ganancia:,.0f}"
            banner_info.subtitulo = f"Recaudaste ${recaudado:,.0f} - {viajes} viajes"
            banner_info.color_estado = "verde"
            
        banner_info.tipo_contrato = "ALQUILER"
        banner_info.monto_diario = canon_diario
        
    elif tipo_contrato == "AUTO_GESTION":
        ganancia_neta = recaudado - gastos_turno
        banner_info.titulo = f"Ganancia neta: ${ganancia_neta:,.0f}"
        banner_info.subtitulo = f"{viajes} viajes realizados"
        banner_info.color_estado = "primary"
        banner_info.tipo_contrato = "AUTO_GESTION"
        banner_info.tratamiento_gastos = tratamiento_gastos

    # 7. Calcular promedio y retornar
    promedio_viaje = recaudado / viajes if viajes > 0 else 0

    return ResumenResponse(
        fecha_inicio=fecha_inicio.isoformat(),
        fecha_fin=fecha_fin.isoformat(),
        dias=dias,
        viajes=viajes,
        recaudado=round(recaudado, 2),
        km_recorridos=round(km_recorridos, 2),
        duracion_minutos=duracion_minutos,
        viaje_mas_caro=round(viaje_mas_caro, 2),
        viaje_mas_bajo=round(viaje_mas_bajo, 2),
        promedio_viaje=round(promedio_viaje, 2),
        desglose_por_origen=desglose,
        banner_info=banner_info,
        recaudacion_efectivo=round(recaudacion_efectivo, 2),
        recaudacion_electronico=round(recaudacion_electronico, 2),
        gastos_turno=round(gastos_turno, 2)
    )
@router.get("/{turno_id}")
async def obtener_detalle_turno(
    turno_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el detalle de un turno específico.
    """
    user_id, control_base_id, email, tipo = current_user

    query = text("""
        SELECT
            t.id,
            t.estado,
            t.inicio_turno,
            t.fin_turno,
            t.km_inicial,
            t.km_final,
            t.combustible_inicial,
            t.combustible_final,
            v.id as vehiculo_id,
            v.patente,
            v.marca,
            v.modelo,
            c.tipo_contrato,
            c.porcentaje_chofer,
            c.monto_diario,
            COALESCE(l.id, NULL) as liquidacion_id,
            COALESCE(l.monto_bruto, 0) as monto_bruto,
            COALESCE(l.total_chofer, 0) as total_chofer,
            COALESCE(l.total_propietario, 0) as total_propietario,
            l.estado as estado_liquidacion
        FROM fleet.turno_chofer t
        JOIN fleet.vehiculo v ON v.id = t.vehiculo_id
        JOIN fleet.contrato_vehiculo c ON c.id = t.contrato_id
        LEFT JOIN fleet.liquidacion l ON l.turno_id = t.id
        WHERE t.id = :turno_id AND t.chofer_id = :user_id
    """)
    result = await db.execute(query, {"turno_id": turno_id, "user_id": user_id})
    row = result.first()

    if not row:
        raise HTTPException(404, "Turno no encontrado")

    # Obtener gastos del turno
    query_gastos = text("""
        SELECT id, tipo_gasto, monto, km_registro, url_comprobante, created_at
        FROM fleet.gasto_turno
        WHERE turno_id = :turno_id
        ORDER BY created_at DESC
    """)
    result = await db.execute(query_gastos, {"turno_id": turno_id})
    gastos = result.all()

    # Obtener ingresos del turno
    query_ingresos = text("""
        SELECT id, tipo_ingreso, medio_pago, origen, monto, moneda, estado, created_at
        FROM fleet.ingreso_turno
        WHERE turno_id = :turno_id
        ORDER BY created_at DESC
    """)
    result = await db.execute(query_ingresos, {"turno_id": turno_id})
    ingresos = result.all()

    return {
        "id": str(row[0]),
        "estado": row[1],
        "inicioTurno": row[2],
        "finTurno": row[3],
        "kmInicial": float(row[4]) if row[4] else None,
        "kmFinal": float(row[5]) if row[5] else None,
        "kmRecorridos": float(row[5] - row[4]) if row[4] and row[5] else None,
        "combustibleInicial": row[6],
        "combustibleFinal": row[7],
        "vehiculo": {
            "id": str(row[8]),
            "patente": row[9],
            "marca": row[10],
            "modelo": row[11]
        },
        "contrato": {
            "tipo": row[12],
            "porcentajeChofer": float(row[13]) if row[13] else None,
            "montoDiario": float(row[14]) if row[14] else None
        },
        "liquidacion": {
            "id": str(row[15]) if row[15] else None,
            "montoBruto": float(row[16]) if row[16] else 0,
            "totalChofer": float(row[17]) if row[17] else 0,
            "totalPropietario": float(row[18]) if row[18] else 0,
            "estado": row[19]
        },
        "gastos": [
            {
                "id": str(g[0]),
                "tipoGasto": g[1],
                "monto": float(g[2]),
                "kmRegistro": float(g[3]) if g[3] else None,
                "urlComprobante": g[4],
                "createdAt": g[5]
            }
            for g in gastos
        ],
        "ingresos": [
            {
                "id": str(i[0]),
                "tipoIngreso": i[1],
                "medioPago": i[2],
                "origen": i[3],
                "monto": float(i[4]),
                "moneda": i[5],
                "estado": i[6],
                "createdAt": i[7]
            }
            for i in ingresos
        ]
    }