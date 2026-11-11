"""
Driver document management endpoints
Handles upload of documents: dni, licencia, buena_conducta, antecedentes, sanidad

Storage: Cloudinary (folder: choferes/{usuario_id}/{tipo_documento}/)
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from datetime import date
from pydantic import BaseModel
import logging

from app.database import get_db
from app.dependencies import get_current_user
from app.services.cloudinary_storage import cloudinary_storage

router = APIRouter(prefix="/api/chofer", tags=["Chofer Documentos"])
logger = logging.getLogger(__name__)


# ============================================
# Schemas
# ============================================

class DocumentoResponse(BaseModel):
    success: bool
    tipo_documento: str
    url: str
    message: str


class EstadoAprobacionResponse(BaseModel):
    estado_aprobacion: Optional[str] = None
    mensaje: Optional[str] = None
    documentos_subidos: int
    documentos_requeridos: int = 5
    puede_manejar: bool


# ============================================
# Constantes
# ============================================

DOCS_CON_VENCIMIENTO = ["licencia", "sanidad", "buena_conducta", "antecedentes"]
DOCS_CON_NUMERO_OBLIGATORIO = ["licencia", "buena_conducta", "antecedentes"]


# ============================================
# Endpoints
# ============================================

@router.post("/subir-documento", response_model=DocumentoResponse)
async def subir_documento(
    tipo_documento: str = Query(..., description="dni, licencia, buena_conducta, antecedentes, sanidad"),
    fecha_vencimiento: Optional[date] = Query(None, description="Fecha de vencimiento"),
    numero: Optional[str] = Query(None, description="Numero del documento"),
    file: UploadFile = File(...),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a driver document."""
    user_id = current_user[0]

    # 1. Validar tipo de documento
    tipos_validos = ["dni", "licencia", "buena_conducta", "antecedentes", "sanidad"]
    if tipo_documento not in tipos_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de documento invalido. Permitidos: {tipos_validos}"
        )

    # 2. Validar fecha de vencimiento para documentos que vencen
    if tipo_documento in DOCS_CON_VENCIMIENTO:
        if not fecha_vencimiento:
            raise HTTPException(
                status_code=400,
                detail=f"Fecha de vencimiento obligatoria para {tipo_documento}"
            )
        if fecha_vencimiento < date.today():
            raise HTTPException(
                status_code=400,
                detail="El documento esta vencido y no puede ser aceptado"
            )

    # 3. Validar numero segun tipo
    if tipo_documento == "dni":
        if not numero:
            perfil_query = text("""
                SELECT documento FROM auth.perfil_general
                WHERE usuario_id = :user_id
            """)
            perfil_result = await db.execute(perfil_query, {"user_id": user_id})
            perfil_row = perfil_result.first()
            if perfil_row and perfil_row[0]:
                numero = perfil_row[0]
                logger.info(f"DNI: numero tomado del perfil: {numero}")
            else:
                logger.warning(f"DNI: perfil sin documento para usuario {user_id}, numero queda null")
    elif tipo_documento in DOCS_CON_NUMERO_OBLIGATORIO:
        if not numero:
            raise HTTPException(
                status_code=400,
                detail=f"Numero obligatorio para {tipo_documento}"
            )
    # 4. Verificar/crear postulación del usuario
    check_query = text("""
        SELECT cv.id, cv.estado_aprobacion
        FROM fleet.chofer_vehiculo cv
        WHERE cv.usuario_id = :user_id
    """)
    result = await db.execute(check_query, {"user_id": user_id})
    row = result.first()

    if row:
        estado_actual = row[1]
        if estado_actual == "aprobado":
            raise HTTPException(
                status_code=400,
                detail="El chofer ya esta aprobado. No se pueden subir mas documentos."
            )
    else:
        # Si no existe la postulación, la creamos automáticamente
        logger.info(f"Creando postulación automática para el usuario {user_id}")
        try:
            # 1. Obtener el control_base_id del perfil del usuario
            perfil_query = text("""
                SELECT control_base_id FROM auth.usuario
                WHERE id = :user_id
            """)
            perfil_result = await db.execute(perfil_query, {"user_id": user_id})
            perfil_row = perfil_result.first()
            
            if perfil_row and perfil_row[0]:
                control_base_id = perfil_row[0]
            else:
                # Si no tiene perfil, buscamos una control_base activa por defecto
                default_cb = text("SELECT id FROM auth.control_base LIMIT 1")
                cb_result = await db.execute(default_cb)
                cb_row = cb_result.first()
                if not cb_row:
                    raise Exception("No hay control_base registrada en el sistema")
                control_base_id = cb_row[0]

            # 2. Insertar la postulación con el control_base_id
            insert_postulacion = text("""
                INSERT INTO fleet.chofer_vehiculo 
                    (id, usuario_id, control_base_id, estado_aprobacion, estado_laboral, activo, created_at)
                VALUES 
                    (gen_random_uuid(), :user_id, :control_base_id, 'pendiente', 'inactivo', true, NOW())
            """)
            await db.execute(insert_postulacion, {
                "user_id": user_id,
                "control_base_id": control_base_id
            })
            await db.commit()
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error al crear postulación automática: {str(e)}")
            # Lanzamos un error con el mensaje real para debug
            raise HTTPException(
                status_code=500,
                detail=f"Error interno al crear la postulación: {str(e)}"
            )

    # 5. Validar tamano del archivo (maximo 10MB)
    content = await file.read()
    file_size = len(content)
    if file_size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="El archivo no puede superar los 10MB"
        )

    await file.seek(0)

    # 6. Guardar el archivo en Cloudinary
    try:
        url = await cloudinary_storage.upload_documento_chofer(
            file=file,
            usuario_id=str(user_id),
            tipo_documento=tipo_documento
        )
    except Exception as e:
        import traceback
        logger.error(f"Error en upload a Cloudinary: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar documento: {str(e)}"
        )

    # 7. Registrar en la base de datos
    insert_doc = text("""
        INSERT INTO fleet.documentos_chofer
            (id, usuario_id, tipo_documento, url, numero, fecha_vencimiento, subido_en, activo, notificar_dias)
        VALUES
            (gen_random_uuid(), :user_id, :tipo_documento, :url, :numero, :fecha_vencimiento, NOW(), true, :notificar_dias)
        ON CONFLICT (usuario_id, tipo_documento)
        DO UPDATE SET
            url = :url,
            numero = :numero,
            fecha_vencimiento = :fecha_vencimiento,
            subido_en = NOW(),
            activo = true,
            notificar_dias = :notificar_dias
    """)

    await db.execute(insert_doc, {
        "user_id": user_id,
        "tipo_documento": tipo_documento,
        "url": url,
        "numero": numero,
        "fecha_vencimiento": fecha_vencimiento,
        "notificar_dias": 30
    })

    await db.commit()

    return DocumentoResponse(
        success=True,
        tipo_documento=tipo_documento,
        url=url,
        message=f"Documento {tipo_documento} subido correctamente"
    )


@router.get("/estado-aprobacion", response_model=EstadoAprobacionResponse)
async def obtener_estado_aprobacion(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get driver approval status."""
    user_id = current_user[0]

    query = text("""
        SELECT
            cv.estado_aprobacion,
            COUNT(dc.id) as documentos_subidos,
            cv.estado_laboral
        FROM fleet.chofer_vehiculo cv
        LEFT JOIN fleet.documentos_chofer dc ON dc.usuario_id = cv.usuario_id
        WHERE cv.usuario_id = :user_id
        GROUP BY cv.estado_aprobacion, cv.estado_laboral
    """)

    result = await db.execute(query, {"user_id": user_id})
    row = result.first()

    if not row:
        return EstadoAprobacionResponse(
            estado_aprobacion=None,
            mensaje="No tenés una postulación activa como chofer. Hacé clic en 'Solicitar ser chofer' para empezar.",
            documentos_subidos=0,
            documentos_requeridos=5,
            puede_manejar=False
        )

    estado = row[0]
    documentos_subidos = row[1] or 0
    estado_laboral = row[2]

    mensajes = {
        "pendiente": "Falta subir documentos. Completa los 5 requeridos.",
        "en_revision": "Documentacion completa. Esperando revision municipal.",
        "aprobado": "Felicidades! Estas habilitado para manejar. Ya puedes aceptar viajes.",
        "rechazado": "Tu documentacion fue rechazada. Por favor, contacta al municipio para mas informacion."
    }

    mensaje = mensajes.get(estado, "Estado desconocido")
    puede_manejar = estado == "aprobado"

    return EstadoAprobacionResponse(
        estado_aprobacion=estado,
        mensaje=mensaje,
        documentos_subidos=documentos_subidos,
        documentos_requeridos=5,
        puede_manejar=puede_manejar
    )


@router.get("/mis-documentos")
async def listar_mis_documentos(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all documents uploaded by the current driver."""
    user_id = current_user[0]

    query = text("""
        SELECT id, tipo_documento, url, numero, fecha_vencimiento, subido_en
        FROM fleet.documentos_chofer
        WHERE usuario_id = :user_id
        ORDER BY subido_en DESC
    """)

    result = await db.execute(query, {"user_id": user_id})
    rows = result.all()

    return {
        "success": True,
        "documentos": [
            {
                "id": str(row[0]),
                "tipo_documento": row[1],
                "url": row[2],
                "numero": row[3],
                "fecha_vencimiento": row[4].isoformat() if row[4] else None,
                "subido_en": row[5].isoformat() if row[5] else None
            }
            for row in rows
        ]
    }