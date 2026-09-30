"""
Router para el endpoint unificado del Splash Screen.
Combina información de expediente, turno y estado del chofer en una sola respuesta.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
import logging

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.chofer_splash_schemas import *

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chofer", tags=["Chofer - Splash"])

# Constantes
TIPOS_DOC_CHOFER = ['dni', 'licencia', 'sanidad', 'buena_conducta']


@router.get("/splash-estado", response_model=SplashEstadoResponse)
async def obtener_estado_splash(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint unificado para el Splash Screen.
    Devuelve todo el estado necesario para decidir la navegación inicial.
    
    Una sola llamada reemplaza a:
    - GET /api/auth/me
    - GET /api/chofer/turno/estado
    - GET /api/chofer/registro-progresivo/estado-expediente
    """
    user_id, control_base_id, email, tipo = current_user
    logger.info(f"📱 Splash - Consultando estado para usuario: {user_id}")
    
    # ============================================================
    # 1. OBTENER DATOS DEL CHOFER (fleet.chofer_vehiculo)
    # ============================================================
    query_chofer = text("""
        SELECT 
            cv.estado_aprobacion,
            cv.estado_laboral,
            cv.vehiculo_id,
            cv.control_base_id,
            cv.activo
        FROM fleet.chofer_vehiculo cv
        WHERE cv.usuario_id = :user_id
    """)
    result = await db.execute(query_chofer, {"user_id": user_id})
    row = result.first()
    
    if not row:
        logger.warning(f"⚠️ Chofer sin expediente: {user_id}")
        return SplashEstadoResponse(
            autenticado=True,
            estado_aprobacion="pendiente",
            estado_laboral="fuera_servicio",
            puede_operar=False,
            tiene_vehiculo=False,
            tiene_contrato_activo=False,
            tiene_turno_activo=False,
            etapa_actual="registro",
            documentos_faltantes=TIPOS_DOC_CHOFER + ["selfie"],
            progreso=ProgresoResponse(
                datos_personales=False,
                documentos_basicos=False,
                selfie=False
            ),
            motivo_bloqueo="Expediente de chofer no encontrado",
            tenant_nombre=None,
            vehiculo=None,
            turno=None,
            contrato=None
        )
    
    estado_aprobacion, estado_laboral, vehiculo_id, cb_id, activo = row
    
    # ============================================================
    # 2. OBTENER TENANT
    # ============================================================
    tenant_nombre = None
    query_tenant = text("""
        SELECT nombre FROM tenant.control_base WHERE id = :cb_id
    """)
    result = await db.execute(query_tenant, {"cb_id": cb_id or control_base_id})
    tenant_row = result.first()
    if tenant_row:
        tenant_nombre = tenant_row[0]
    
    # ============================================================
    # 3. OBTENER VEHÍCULO
    # ============================================================
    tiene_vehiculo = vehiculo_id is not None
    vehiculo_info = None
    patente = None
    
    if tiene_vehiculo:
        query_vehiculo = text("""
            SELECT id, patente FROM fleet.vehiculo WHERE id = :vehiculo_id AND activo = true
        """)
        result = await db.execute(query_vehiculo, {"vehiculo_id": vehiculo_id})
        veh_row = result.first()
        if veh_row:
            vehiculo_info = VehiculoInfoResponse(
                id=veh_row[0],
                patente=veh_row[1]
            )
            patente = veh_row[1]
        else:
            tiene_vehiculo = False
    
    # ============================================================
    # 4. OBTENER CONTRATO ACTIVO
    # ============================================================
    tiene_contrato_activo = False
    contrato_info = None
    
    if tiene_vehiculo and vehiculo_id:
        query_contrato = text("""
            SELECT 
                id,
                tipo_contrato,
                estado_contrato,
                fecha_inicio,
                fecha_fin
            FROM fleet.contrato_vehiculo
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
        contrato_row = result.first()
        if contrato_row:
            tiene_contrato_activo = True
            contrato_info = ContratoInfoResponse(
                id=contrato_row[0],
                tipo=contrato_row[1]
            )
    
    # ============================================================
    # 5. OBTENER TURNO ACTIVO
    # ============================================================
    tiene_turno_activo = False
    turno_info = None
    
    query_turno = text("""
        SELECT id, inicio_turno, estado
        FROM fleet.turno_chofer
        WHERE chofer_id = :user_id AND estado = 'ACTIVO'
        ORDER BY inicio_turno DESC
        LIMIT 1
    """)
    result = await db.execute(query_turno, {"user_id": user_id})
    turno_row = result.first()
    if turno_row:
        tiene_turno_activo = True
        turno_info = TurnoInfoResponse(
            id=turno_row[0],
            inicio_turno=turno_row[1]
        )
    
    # ============================================================
    # 6. OBTENER PROGRESO DEL EXPEDIENTE (M1)
    # ============================================================
    # 6a. Verificar datos personales
    query_perfil = text("""
        SELECT 
            nombre IS NOT NULL AND apellido IS NOT NULL AND documento IS NOT NULL
            AND telefono IS NOT NULL AND direccion IS NOT NULL AND ciudad_id IS NOT NULL
            AND codigo_postal IS NOT NULL
        FROM auth.perfil_general
        WHERE usuario_id = :user_id
    """)
    result = await db.execute(query_perfil, {"user_id": user_id})
    tiene_datos = result.scalar() or False
    
    # 6b. Verificar documentos
    query_docs = text("""
        SELECT tipo_documento FROM fleet.documentos_chofer
        WHERE usuario_id = :user_id AND activo = true
    """)
    result = await db.execute(query_docs, {"user_id": user_id})
    docs_subidos = {row[0] for row in result.all()}
    
    tiene_selfie = "selfie" in docs_subidos
    documentos_basicos = all(d in docs_subidos for d in TIPOS_DOC_CHOFER)
    documentos_faltantes = [d for d in TIPOS_DOC_CHOFER if d not in docs_subidos]
    if not tiene_selfie:
        documentos_faltantes.append("selfie")
    
    # ============================================================
    # 7. CALCULAR PUEDE_OPERAR
    # ============================================================
    puede_operar = (
        estado_aprobacion == 'aprobado' and
        tiene_vehiculo and
        tiene_contrato_activo and
        estado_laboral in ['libre', 'ocupado']
    )
    
    # ============================================================
    # 8. DETERMINAR ETAPA ACTUAL (para navegación)
    # ============================================================
    etapa_actual = await _determinar_etapa(
        estado_aprobacion=estado_aprobacion,
        tiene_datos=tiene_datos,
        documentos_basicos=documentos_basicos,
        tiene_selfie=tiene_selfie,
        tiene_vehiculo=tiene_vehiculo,
        tiene_contrato_activo=tiene_contrato_activo,
        tiene_turno_activo=tiene_turno_activo,
        puede_operar=puede_operar
    )
    
    # ============================================================
    # 9. DETERMINAR MOTIVO DE BLOQUEO (si corresponde)
    # ============================================================
    motivo_bloqueo = await _determinar_motivo_bloqueo(
        estado_aprobacion=estado_aprobacion,
        tiene_vehiculo=tiene_vehiculo,
        tiene_contrato_activo=tiene_contrato_activo,
        tiene_turno_activo=tiene_turno_activo,
        estado_laboral=estado_laboral
    )
    
    # ============================================================
    # 10. RESPUESTA CONSOLIDADA
    # ============================================================
    return SplashEstadoResponse(
        autenticado=True,
        estado_aprobacion=estado_aprobacion,
        estado_laboral=estado_laboral,
        puede_operar=puede_operar,
        tiene_vehiculo=tiene_vehiculo,
        tiene_contrato_activo=tiene_contrato_activo,
        tiene_turno_activo=tiene_turno_activo,
        etapa_actual=etapa_actual,
        documentos_faltantes=documentos_faltantes,
        progreso=ProgresoResponse(
            datos_personales=tiene_datos,
            documentos_basicos=documentos_basicos,
            selfie=tiene_selfie
        ),
        motivo_bloqueo=motivo_bloqueo,
        tenant_nombre=tenant_nombre,
        vehiculo=vehiculo_info,
        turno=turno_info,
        contrato=contrato_info
    )


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

async def _determinar_etapa(
    estado_aprobacion: str,
    tiene_datos: bool,
    documentos_basicos: bool,
    tiene_selfie: bool,
    tiene_vehiculo: bool,
    tiene_contrato_activo: bool,
    tiene_turno_activo: bool,
    puede_operar: bool
) -> str:
    """Determina la etapa actual del chofer para la navegación."""
    
    # Caso: Registro pendiente
    if estado_aprobacion == 'pendiente':
        if not tiene_datos:
            return "registro"  # No debería pasar, pero por seguridad
        if not documentos_basicos:
            return "documentos"
        if not tiene_selfie:
            return "selfie"
        return "revision"  # Todo completo, debería estar en en_revision
    
    # Caso: En revisión
    if estado_aprobacion == 'en_revision':
        return "revision"
    
    # Caso: Rechazado
    if estado_aprobacion == 'rechazado':
        return "revision"
    
    # Caso: Aprobado
    if estado_aprobacion == 'aprobado':
        if not tiene_vehiculo:
            return "esperando_vehiculo"
        if not tiene_contrato_activo:
            return "contrato_pendiente"
        if tiene_turno_activo:
            return "home"
        return "listo"
    
    # Fallback
    return "registro"


async def _determinar_motivo_bloqueo(
    estado_aprobacion: str,
    tiene_vehiculo: bool,
    tiene_contrato_activo: bool,
    tiene_turno_activo: bool,
    estado_laboral: str
) -> Optional[str]:
    """Determina el motivo de bloqueo si no puede operar."""
    
    if estado_aprobacion == 'pendiente':
        return "Tu registro está incompleto. Completá todos los pasos para ser aprobado."
    
    if estado_aprobacion == 'en_revision':
        return "Tu expediente está en revisión. Te notificaremos cuando sea aprobado."
    
    if estado_aprobacion == 'rechazado':
        return "Tu expediente fue rechazado. Contactá al administrador para más información."
    
    if estado_aprobacion == 'aprobado':
        if not tiene_vehiculo:
            return "Tu registro fue aprobado, pero todavía no tenés un vehículo asignado. Contactá a tu propietario."
        if not tiene_contrato_activo:
            return "Tenés un vehículo asignado, pero el contrato aún no está activo. Contactá a tu propietario."
        if not tiene_turno_activo:
            return None  # No hay bloqueo, está listo para iniciar turno
        if estado_laboral == 'fuera_servicio':
            return "Estás fuera de servicio. Activá tu estado para comenzar a recibir viajes."
    
    return None