"""
Driver document management endpoints
Handles upload of license, insurance, and background check documents
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user
from app.services.storage import storage_service

router = APIRouter(prefix="/api/chofer", tags=["Chofer Documentos"])


# ============================================
# Schemas
# ============================================

class DocumentoResponse(BaseModel):
    success: bool
    tipo_documento: str
    url: str
    message: str


class EstadoAprobacionResponse(BaseModel):
    estado_aprobacion: str  # pendiente, completo, aprobado, rechazado
    mensaje: Optional[str] = None
    documentos_subidos: int
    documentos_requeridos: int = 3
    puede_manejar: bool


# ============================================
# Endpoints
# ============================================

@router.post("/subir-documento", response_model=DocumentoResponse)
async def subir_documento(
    tipo_documento: str = Query(..., description="licencia, seguro, antecedentes"),
    file: UploadFile = File(...),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a driver document (license, insurance, background check)
    
    - tipo_documento: 'licencia', 'seguro', 'antecedentes'
    - The JWT token from registration is required in Authorization header
    - Documents are stored locally in ./uploads/documentos/
    """
    user_id = current_user[0]
    
    # Validar tipo de documento
    tipos_validos = ["licencia", "seguro", "antecedentes"]
    if tipo_documento not in tipos_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de documento inválido. Permitidos: {tipos_validos}"
        )
    
    # Verificar que el usuario es chofer y no está ya aprobado
    check_query = text("""
        SELECT cv.id, cv.estado_aprobacion
        FROM fleet.chofer_vehiculo cv
        WHERE cv.usuario_id = :user_id
    """)
    
    result = await db.execute(check_query, {"user_id": user_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Chofer no encontrado")
    
    estado_actual = row[1]
    if estado_actual == "aprobado":
        raise HTTPException(
            status_code=400,
            detail="El chofer ya está aprobado. No se pueden subir más documentos."
        )
    
    # Validar tamaño del archivo (máximo 10MB)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=400,
            detail="El archivo no puede superar los 10MB"
        )
    
    # Guardar el archivo
    try:
        url = await storage_service.save_document(
            file=file,
            usuario_id=str(user_id),
            tipo_documento=tipo_documento
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar documento: {str(e)}"
        )
    
    # Registrar en la base de datos
    insert_doc = text("""
        INSERT INTO fleet.documentos_chofer (id, usuario_id, tipo_documento, url, subido_en)
        VALUES (gen_random_uuid(), :user_id, :tipo_documento, :url, NOW())
        ON CONFLICT (usuario_id, tipo_documento) 
        DO UPDATE SET url = :url, subido_en = NOW()
    """)
    
    await db.execute(insert_doc, {
        "user_id": user_id,
        "tipo_documento": tipo_documento,
        "url": url
    })
    
    # Verificar si ya tiene los 3 documentos para cambiar estado a "completo"
    count_query = text("""
        SELECT COUNT(*) FROM fleet.documentos_chofer
        WHERE usuario_id = :user_id
    """)
    
    count_result = await db.execute(count_query, {"user_id": user_id})
    count = count_result.scalar()
    
    if count >= 3:
        update_query = text("""
            UPDATE fleet.chofer_vehiculo
            SET estado_aprobacion = 'completo', updated_at = NOW()
            WHERE usuario_id = :user_id
        """)
        await db.execute(update_query, {"user_id": user_id})
    
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
    """
    Get driver approval status
    
    Returns:
    - estado_aprobacion: 'pendiente', 'completo', 'aprobado', 'rechazado'
    - documentos_subidos: count of uploaded documents (0-3)
    - puede_manejar: boolean indicating if driver can accept trips
    """
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
        raise HTTPException(status_code=404, detail="Chofer no encontrado")
    
    estado = row[0]
    documentos_subidos = row[1] or 0
    estado_laboral = row[2]
    
    # Mensajes según estado
    mensajes = {
        "pendiente": "📄 Tu documentación está en revisión por el municipio. Te notificaremos cuando estés habilitado.",
        "completo": "📋 Documentación completa. Esperando revisión municipal.",
        "aprobado": "✅ ¡Felicidades! Estás habilitado para manejar. Ya puedes aceptar viajes.",
        "rechazado": "❌ Tu documentación fue rechazada. Por favor, contacta al municipio para más información."
    }
    
    mensaje = mensajes.get(estado, "Estado desconocido")
    
    # Determinar si puede manejar (solo si está aprobado)
    puede_manejar = estado == "aprobado"
    
    return EstadoAprobacionResponse(
        estado_aprobacion=estado,
        mensaje=mensaje,
        documentos_subidos=documentos_subidos,
        documentos_requeridos=3,
        puede_manejar=puede_manejar
    )


@router.get("/mis-documentos")
async def listar_mis_documentos(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all documents uploaded by the current driver
    """
    user_id = current_user[0]
    
    query = text("""
        SELECT id, tipo_documento, url, subido_en
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
                "subido_en": row[3]
            }
            for row in rows
        ]
    }