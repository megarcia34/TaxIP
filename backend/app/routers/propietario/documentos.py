"""
Documentación del propietario - Fase 7
CRUD completo con alertas de vencimiento y destinatario dinámico
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func, text
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import Optional, List
from datetime import datetime, date, timedelta

from app.database import get_db
from app.dependencies import get_current_user, get_propietario_id
from app.models.fleet import (
    DocumentoVehiculo,
    DocumentoPropietario,
    Vehiculo,
    PropietarioVehiculo,
    ContratoVehiculo
)
from app.models.auth import Usuario
from app.schemas.propietario_schemas import (
    DocumentoVehiculoCreate,
    DocumentoVehiculoUpdate,
    DocumentoVehiculoResponse,
    DocumentoPropietarioCreate,
    DocumentoPropietarioUpdate,
    DocumentoPropietarioResponse,
    AlertaVencimientoResponse,
)
from app.services.cloudinary_storage import cloudinary_storage

router = APIRouter()

# ============================================================
# TIPOS DE DOCUMENTOS PREDEFINIDOS
# ============================================================

TIPOS_DOCUMENTO_VEHICULO = {
    "SEGURO": {
        "nombre": "Seguro",
        "periodicidad_dias": 365,
        "alerta_a": "dueno",
        "descripcion": "Póliza de seguro del vehículo"
    },
    "VTV": {
        "nombre": "VTV / ITV",
        "periodicidad_dias": 365,
        "alerta_a": "chofer",
        "descripcion": "Verificación Técnica Vehicular"
    },
    "PATENTE": {
        "nombre": "Patente",
        "periodicidad_dias": 365,
        "alerta_a": "dueno",
        "descripcion": "Pago de patente anual"
    },
    "CEDULA_VERDE": {
        "nombre": "Cédula Verde",
        "periodicidad_dias": 365,
        "alerta_a": "chofer",
        "descripcion": "Cédula de identificación del vehículo"
    },
    "LICENCIA_CHOFER": {
        "nombre": "Licencia de Chofer",
        "periodicidad_dias": 1825,
        "alerta_a": "chofer",
        "descripcion": "Licencia de conducir del chofer"
    },
    "HABILITACION": {
        "nombre": "Habilitación Municipal",
        "periodicidad_dias": 365,
        "alerta_a": "dueno",
        "descripcion": "Habilitación municipal para operar"
    },
    "OTRO": {
        "nombre": "Otro",
        "periodicidad_dias": None,
        "alerta_a": "dueno",
        "descripcion": "Otro tipo de documento"
    }
}

TIPOS_DOCUMENTO_PROPIETARIO = {
    "DNI": {
        "nombre": "DNI",
        "periodicidad_dias": 5475,
        "alerta_a": "dueno",
        "descripcion": "Documento Nacional de Identidad"
    },
    "LICENCIA": {
        "nombre": "Licencia de Conducir",
        "periodicidad_dias": 1825,
        "alerta_a": "dueno",
        "descripcion": "Licencia de conducir del propietario"
    },
    "CUIT": {
        "nombre": "CUIT",
        "periodicidad_dias": None,
        "alerta_a": "dueno",
        "descripcion": "Clave Única de Identificación Tributaria"
    },
    "OTRO": {
        "nombre": "Otro",
        "periodicidad_dias": None,
        "alerta_a": "dueno",
        "descripcion": "Otro tipo de documento"
    }
}


# ============================================================
# DOCUMENTOS DE VEHÍCULO
# ============================================================

@router.post("/vehiculos/{vehiculo_id}/documentos", response_model=DocumentoVehiculoResponse)
async def crear_documento_vehiculo(
    vehiculo_id: UUID,
    data: DocumentoVehiculoCreate,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Subir un documento para un vehículo.
    """
    if data.tipo_documento not in TIPOS_DOCUMENTO_VEHICULO:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de documento inválido. Permitidos: {list(TIPOS_DOCUMENTO_VEHICULO.keys())}"
        )

    prop_vehiculo = await db.execute(
        select(PropietarioVehiculo).where(
            PropietarioVehiculo.vehiculo_id == vehiculo_id,
            PropietarioVehiculo.propietario_id == propietario_id,
            PropietarioVehiculo.activo == True
        )
    )
    if not prop_vehiculo.scalar_one_or_none():
        raise HTTPException(
            status_code=403,
            detail="Vehículo no pertenece al propietario"
        )

    documento = DocumentoVehiculo(
        vehiculo_id=vehiculo_id,
        tipo_documento=data.tipo_documento,
        numero=data.numero,
        fecha_emision=data.fecha_emision,
        fecha_vencimiento=data.fecha_vencimiento,
        observaciones=data.observaciones,
        url_archivo=data.url_archivo
    )

    db.add(documento)
    await db.commit()
    await db.refresh(documento)

    vehiculo = await db.get(Vehiculo, vehiculo_id)

    return DocumentoVehiculoResponse(
        id=documento.id,
        vehiculo_id=documento.vehiculo_id,
        patente=vehiculo.patente if vehiculo else "",
        tipo_documento=documento.tipo_documento,
        tipo_nombre=TIPOS_DOCUMENTO_VEHICULO.get(documento.tipo_documento, {}).get("nombre", documento.tipo_documento),
        numero=documento.numero,
        fecha_emision=documento.fecha_emision,
        fecha_vencimiento=documento.fecha_vencimiento,
        observaciones=documento.observaciones,
        url_archivo=documento.url_archivo,
        created_at=documento.created_at,
        updated_at=documento.updated_at
    )


@router.get("/vehiculos/{vehiculo_id}/documentos", response_model=List[DocumentoVehiculoResponse])
async def listar_documentos_vehiculo(
    vehiculo_id: UUID,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar todos los documentos de un vehículo.
    """
    prop_vehiculo = await db.execute(
        select(PropietarioVehiculo).where(
            PropietarioVehiculo.vehiculo_id == vehiculo_id,
            PropietarioVehiculo.propietario_id == propietario_id,
            PropietarioVehiculo.activo == True
        )
    )
    if not prop_vehiculo.scalar_one_or_none():
        raise HTTPException(
            status_code=403,
            detail="Vehículo no pertenece al propietario"
        )

    query = select(DocumentoVehiculo).options(
        selectinload(DocumentoVehiculo.vehiculo)
    ).where(
        DocumentoVehiculo.vehiculo_id == vehiculo_id
    ).order_by(DocumentoVehiculo.fecha_vencimiento, desc(DocumentoVehiculo.created_at))

    result = await db.execute(query)
    documentos = result.scalars().all()

    return [
        DocumentoVehiculoResponse(
            id=d.id,
            vehiculo_id=d.vehiculo_id,
            patente=d.vehiculo.patente if d.vehiculo else "",
            tipo_documento=d.tipo_documento,
            tipo_nombre=TIPOS_DOCUMENTO_VEHICULO.get(d.tipo_documento, {}).get("nombre", d.tipo_documento),
            numero=d.numero,
            fecha_emision=d.fecha_emision,
            fecha_vencimiento=d.fecha_vencimiento,
            observaciones=d.observaciones,
            url_archivo=d.url_archivo,
            created_at=d.created_at,
            updated_at=d.updated_at
        )
        for d in documentos
    ]


@router.get("/vehiculos/documentos/{documento_id}", response_model=DocumentoVehiculoResponse)
async def obtener_documento_vehiculo(
    documento_id: UUID,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener un documento específico de vehículo.
    """
    documento = await db.get(DocumentoVehiculo, documento_id)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    prop_vehiculo = await db.execute(
        select(PropietarioVehiculo).where(
            PropietarioVehiculo.vehiculo_id == documento.vehiculo_id,
            PropietarioVehiculo.propietario_id == propietario_id,
            PropietarioVehiculo.activo == True
        )
    )
    if not prop_vehiculo.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este documento")

    await db.refresh(documento, attribute_names=["vehiculo"])

    return DocumentoVehiculoResponse(
        id=documento.id,
        vehiculo_id=documento.vehiculo_id,
        patente=documento.vehiculo.patente if documento.vehiculo else "",
        tipo_documento=documento.tipo_documento,
        tipo_nombre=TIPOS_DOCUMENTO_VEHICULO.get(documento.tipo_documento, {}).get("nombre", documento.tipo_documento),
        numero=documento.numero,
        fecha_emision=documento.fecha_emision,
        fecha_vencimiento=documento.fecha_vencimiento,
        observaciones=documento.observaciones,
        url_archivo=documento.url_archivo,
        created_at=documento.created_at,
        updated_at=documento.updated_at
    )


@router.put("/vehiculos/documentos/{documento_id}", response_model=DocumentoVehiculoResponse)
async def actualizar_documento_vehiculo(
    documento_id: UUID,
    data: DocumentoVehiculoUpdate,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar un documento de vehículo.
    """
    documento = await db.get(DocumentoVehiculo, documento_id)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    prop_vehiculo = await db.execute(
        select(PropietarioVehiculo).where(
            PropietarioVehiculo.vehiculo_id == documento.vehiculo_id,
            PropietarioVehiculo.propietario_id == propietario_id,
            PropietarioVehiculo.activo == True
        )
    )
    if not prop_vehiculo.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este documento")

    if data.tipo_documento is not None:
        if data.tipo_documento not in TIPOS_DOCUMENTO_VEHICULO:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de documento inválido. Permitidos: {list(TIPOS_DOCUMENTO_VEHICULO.keys())}"
            )
        documento.tipo_documento = data.tipo_documento
    if data.numero is not None:
        documento.numero = data.numero
    if data.fecha_emision is not None:
        documento.fecha_emision = data.fecha_emision
    if data.fecha_vencimiento is not None:
        documento.fecha_vencimiento = data.fecha_vencimiento
    if data.observaciones is not None:
        documento.observaciones = data.observaciones
    if data.url_archivo is not None:
        documento.url_archivo = data.url_archivo

    documento.updated_at = datetime.now()

    await db.commit()
    await db.refresh(documento)
    await db.refresh(documento, attribute_names=["vehiculo"])

    return DocumentoVehiculoResponse(
        id=documento.id,
        vehiculo_id=documento.vehiculo_id,
        patente=documento.vehiculo.patente if documento.vehiculo else "",
        tipo_documento=documento.tipo_documento,
        tipo_nombre=TIPOS_DOCUMENTO_VEHICULO.get(documento.tipo_documento, {}).get("nombre", documento.tipo_documento),
        numero=documento.numero,
        fecha_emision=documento.fecha_emision,
        fecha_vencimiento=documento.fecha_vencimiento,
        observaciones=documento.observaciones,
        url_archivo=documento.url_archivo,
        created_at=documento.created_at,
        updated_at=documento.updated_at
    )


@router.delete("/vehiculos/documentos/{documento_id}")
async def eliminar_documento_vehiculo(
    documento_id: UUID,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar un documento de vehículo.
    """
    documento = await db.get(DocumentoVehiculo, documento_id)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    prop_vehiculo = await db.execute(
        select(PropietarioVehiculo).where(
            PropietarioVehiculo.vehiculo_id == documento.vehiculo_id,
            PropietarioVehiculo.propietario_id == propietario_id,
            PropietarioVehiculo.activo == True
        )
    )
    if not prop_vehiculo.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este documento")

    await db.delete(documento)
    await db.commit()

    return {"success": True, "message": "Documento eliminado correctamente"}


@router.post("/vehiculos/documentos/{documento_id}/comprobante")
async def subir_comprobante_documento(
    documento_id: UUID,
    file: UploadFile = File(...),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Subir un archivo (PDF, imagen) como comprobante de un documento.
    """
    documento = await db.get(DocumentoVehiculo, documento_id)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    prop_vehiculo = await db.execute(
        select(PropietarioVehiculo).where(
            PropietarioVehiculo.vehiculo_id == documento.vehiculo_id,
            PropietarioVehiculo.propietario_id == propietario_id,
            PropietarioVehiculo.activo == True
        )
    )
    if not prop_vehiculo.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este documento")

    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no permitido. Use JPG, PNG o PDF"
        )

    try:
        url = await cloudinary_storage.upload_comprobante(
            file=file,
            propietario_id=str(propietario_id),
            gasto_id=str(documento_id),
            tipo="documento_vehiculo"
        )

        documento.url_archivo = url
        documento.updated_at = datetime.now()
        await db.commit()

        return {
            "success": True,
            "message": "Comprobante subido correctamente",
            "url": url
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al subir el comprobante: {str(e)}"
        )


# ============================================================
# DOCUMENTOS DEL PROPIETARIO
# ============================================================

@router.post("/documentos/propietario", response_model=DocumentoPropietarioResponse)
async def crear_documento_propietario(
    data: DocumentoPropietarioCreate,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Subir un documento personal del propietario (DNI, Licencia, etc.)
    """
    if data.tipo_documento not in TIPOS_DOCUMENTO_PROPIETARIO:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de documento inválido. Permitidos: {list(TIPOS_DOCUMENTO_PROPIETARIO.keys())}"
        )

    existe = await db.execute(
        select(DocumentoPropietario).where(
            DocumentoPropietario.propietario_id == propietario_id,
            DocumentoPropietario.tipo_documento == data.tipo_documento
        )
    )
    if existe.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un documento de tipo {data.tipo_documento} para este propietario"
        )

    documento = DocumentoPropietario(
        propietario_id=propietario_id,
        tipo_documento=data.tipo_documento,
        numero=data.numero,
        fecha_emision=data.fecha_emision,
        fecha_vencimiento=data.fecha_vencimiento,
        observaciones=data.observaciones,
        url_archivo=data.url_archivo
    )

    db.add(documento)
    await db.commit()
    await db.refresh(documento)

    return DocumentoPropietarioResponse(
        id=documento.id,
        propietario_id=documento.propietario_id,
        tipo_documento=documento.tipo_documento,
        tipo_nombre=TIPOS_DOCUMENTO_PROPIETARIO.get(documento.tipo_documento, {}).get("nombre", documento.tipo_documento),
        numero=documento.numero,
        fecha_emision=documento.fecha_emision,
        fecha_vencimiento=documento.fecha_vencimiento,
        observaciones=documento.observaciones,
        url_archivo=documento.url_archivo,
        created_at=documento.created_at,
        updated_at=documento.updated_at
    )


@router.get("/documentos/propietario", response_model=List[DocumentoPropietarioResponse])
async def listar_documentos_propietario(
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar todos los documentos personales del propietario.
    """
    query = select(DocumentoPropietario).where(
        DocumentoPropietario.propietario_id == propietario_id
    ).order_by(desc(DocumentoPropietario.created_at))

    result = await db.execute(query)
    documentos = result.scalars().all()

    return [
        DocumentoPropietarioResponse(
            id=d.id,
            propietario_id=d.propietario_id,
            tipo_documento=d.tipo_documento,
            tipo_nombre=TIPOS_DOCUMENTO_PROPIETARIO.get(d.tipo_documento, {}).get("nombre", d.tipo_documento),
            numero=d.numero,
            fecha_emision=d.fecha_emision,
            fecha_vencimiento=d.fecha_vencimiento,
            observaciones=d.observaciones,
            url_archivo=d.url_archivo,
            created_at=d.created_at,
            updated_at=d.updated_at
        )
        for d in documentos
    ]


@router.get("/documentos/propietario/{documento_id}", response_model=DocumentoPropietarioResponse)
async def obtener_documento_propietario(
    documento_id: UUID,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener un documento personal específico del propietario.
    """
    documento = await db.get(DocumentoPropietario, documento_id)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if documento.propietario_id != propietario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este documento")

    return DocumentoPropietarioResponse(
        id=documento.id,
        propietario_id=documento.propietario_id,
        tipo_documento=documento.tipo_documento,
        tipo_nombre=TIPOS_DOCUMENTO_PROPIETARIO.get(documento.tipo_documento, {}).get("nombre", documento.tipo_documento),
        numero=documento.numero,
        fecha_emision=documento.fecha_emision,
        fecha_vencimiento=documento.fecha_vencimiento,
        observaciones=documento.observaciones,
        url_archivo=documento.url_archivo,
        created_at=documento.created_at,
        updated_at=documento.updated_at
    )


@router.put("/documentos/propietario/{documento_id}", response_model=DocumentoPropietarioResponse)
async def actualizar_documento_propietario(
    documento_id: UUID,
    data: DocumentoPropietarioUpdate,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar un documento personal del propietario.
    """
    documento = await db.get(DocumentoPropietario, documento_id)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if documento.propietario_id != propietario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este documento")

    if data.tipo_documento is not None:
        if data.tipo_documento not in TIPOS_DOCUMENTO_PROPIETARIO:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de documento inválido. Permitidos: {list(TIPOS_DOCUMENTO_PROPIETARIO.keys())}"
            )
        documento.tipo_documento = data.tipo_documento
    if data.numero is not None:
        documento.numero = data.numero
    if data.fecha_emision is not None:
        documento.fecha_emision = data.fecha_emision
    if data.fecha_vencimiento is not None:
        documento.fecha_vencimiento = data.fecha_vencimiento
    if data.observaciones is not None:
        documento.observaciones = data.observaciones
    if data.url_archivo is not None:
        documento.url_archivo = data.url_archivo

    documento.updated_at = datetime.now()
    await db.commit()
    await db.refresh(documento)

    return DocumentoPropietarioResponse(
        id=documento.id,
        propietario_id=documento.propietario_id,
        tipo_documento=documento.tipo_documento,
        tipo_nombre=TIPOS_DOCUMENTO_PROPIETARIO.get(documento.tipo_documento, {}).get("nombre", documento.tipo_documento),
        numero=documento.numero,
        fecha_emision=documento.fecha_emision,
        fecha_vencimiento=documento.fecha_vencimiento,
        observaciones=documento.observaciones,
        url_archivo=documento.url_archivo,
        created_at=documento.created_at,
        updated_at=documento.updated_at
    )


@router.delete("/documentos/propietario/{documento_id}")
async def eliminar_documento_propietario(
    documento_id: UUID,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar un documento personal del propietario.
    """
    documento = await db.get(DocumentoPropietario, documento_id)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if documento.propietario_id != propietario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este documento")

    await db.delete(documento)
    await db.commit()

    return {"success": True, "message": "Documento eliminado correctamente"}


# ============================================================
# ALERTAS DE VENCIMIENTO
# ============================================================

@router.get("/documentos/vencimientos", response_model=List[AlertaVencimientoResponse])
async def alertas_vencimiento(
    dias_previos: int = Query(30, description="Días antes del vencimiento para alertar"),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener alertas de documentos próximos a vencer.
    """
    hoy = datetime.now().date()
    fecha_limite = hoy + timedelta(days=dias_previos)
    alertas = []

    # 1. Documentos de vehículos
    query_vehiculo = text("""
        SELECT 
            d.id,
            d.tipo_documento,
            d.numero,
            d.fecha_vencimiento,
            v.patente,
            d.fecha_vencimiento - NOW()::date as dias_restantes
        FROM fleet.documento_vehiculo d
        JOIN fleet.vehiculo v ON v.id = d.vehiculo_id
        JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND d.fecha_vencimiento IS NOT NULL
          AND d.fecha_vencimiento <= :fecha_limite
          AND d.fecha_vencimiento >= :hoy
        ORDER BY d.fecha_vencimiento ASC
    """)
    result = await db.execute(query_vehiculo, {
        "propietario_id": propietario_id,
        "fecha_limite": fecha_limite,
        "hoy": hoy
    })
    rows = result.all()

    for row in rows:
        dias_restantes = int(row[5] or 0)
        nivel = "critico" if dias_restantes <= 7 else "urgente" if dias_restantes <= 15 else "preventivo"
        
        alertas.append(AlertaVencimientoResponse(
            id=row[0],
            tipo_documento=row[1],
            numero=row[2],
            fecha_vencimiento=row[3],
            patente=row[4],
            entidad_tipo="vehiculo",
            dias_restantes=dias_restantes,
            alerta_a="dueno",
            nivel=nivel
        ))

    # 2. Documentos del propietario
    query_propietario = text("""
        SELECT 
            d.id,
            d.tipo_documento,
            d.numero,
            d.fecha_vencimiento,
            d.fecha_vencimiento - NOW()::date as dias_restantes
        FROM fleet.documento_propietario d
        WHERE d.propietario_id = :propietario_id
          AND d.fecha_vencimiento IS NOT NULL
          AND d.fecha_vencimiento <= :fecha_limite
          AND d.fecha_vencimiento >= :hoy
        ORDER BY d.fecha_vencimiento ASC
    """)
    result = await db.execute(query_propietario, {
        "propietario_id": propietario_id,
        "fecha_limite": fecha_limite,
        "hoy": hoy
    })
    rows = result.all()

    for row in rows:
        dias_restantes = int(row[4] or 0)
        nivel = "critico" if dias_restantes <= 7 else "urgente" if dias_restantes <= 15 else "preventivo"
        
        alertas.append(AlertaVencimientoResponse(
            id=row[0],
            tipo_documento=row[1],
            numero=row[2],
            fecha_vencimiento=row[3],
            patente=None,
            entidad_tipo="propietario",
            dias_restantes=dias_restantes,
            alerta_a="dueno",
            nivel=nivel
        ))

    alertas.sort(key=lambda x: x.dias_restantes or 999)
    return alertas


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

async def _obtener_contrato_activo(db: AsyncSession, vehiculo_id: UUID):
    """Obtiene el contrato activo para un vehículo."""
    query = select(ContratoVehiculo).where(
        ContratoVehiculo.vehiculo_id == vehiculo_id,
        ContratoVehiculo.estado_contrato == 'ACTIVO',
        ContratoVehiculo.activo == True
    ).order_by(desc(ContratoVehiculo.fecha_inicio)).limit(1)

    result = await db.execute(query)
    return result.scalar_one_or_none()