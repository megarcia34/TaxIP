"""
Gastos del propietario - Fase 5.2
CRUD completo con categorías, filtros y subida de comprobantes a Cloudinary
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import Optional, List
from datetime import date, datetime

from app.database import get_db
from app.dependencies import get_current_user, get_propietario_id
from app.models.fleet import (
    GastoVehiculo,
    Vehiculo,
    CategoriaGasto,
    PropietarioVehiculo
)
from app.models.auth import Usuario
from app.schemas.propietario_schemas import (
    GastoVehiculoCreate,
    GastoVehiculoUpdate,
    GastoVehiculoDetailResponse,
    GastoVehiculoResponse,
    CategoriaGastoResponse,
    CategoriaGastoCreate,
    CategoriaGastoUpdate,
    ResumenGastosResponse,
)
from app.services.cloudinary_storage import cloudinary_storage

router = APIRouter()


# ============================================================
# CATEGORÍAS DE GASTOS (CRUD)
# ============================================================

@router.get("/categorias", response_model=List[CategoriaGastoResponse])
async def listar_categorias(
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar categorías de gasto del tenant del propietario.
    """
    # Obtener control_base_id del propietario
    user_result = await db.execute(
        select(Usuario).where(Usuario.id == propietario_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Propietario no encontrado")
    
    query = select(CategoriaGasto).where(
        CategoriaGasto.control_base_id == user.control_base_id,
        CategoriaGasto.activo == True
    ).order_by(CategoriaGasto.nombre)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/categorias", response_model=CategoriaGastoResponse)
async def crear_categoria(
    data: CategoriaGastoCreate,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crear una nueva categoría de gasto en el tenant del propietario.
    """
    # Obtener control_base_id del propietario
    user_result = await db.execute(
        select(Usuario).where(Usuario.id == propietario_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Propietario no encontrado")
    
    # Verificar que no exista una categoría con el mismo nombre
    existe = await db.execute(
        select(CategoriaGasto).where(
            CategoriaGasto.control_base_id == user.control_base_id,
            CategoriaGasto.nombre == data.nombre
        )
    )
    if existe.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una categoría con el nombre '{data.nombre}'"
        )
    
    categoria = CategoriaGasto(
        control_base_id=user.control_base_id,
        nombre=data.nombre,
        descripcion=data.descripcion,
        subcategorias=data.subcategorias or [],
        aplica_a=data.aplica_a or [],
        tratamiento_economico=data.tratamiento_economico
    )
    
    db.add(categoria)
    await db.commit()
    await db.refresh(categoria)
    return categoria


@router.put("/categorias/{categoria_id}", response_model=CategoriaGastoResponse)
async def actualizar_categoria(
    categoria_id: UUID,
    data: CategoriaGastoUpdate,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar una categoría de gasto.
    """
    # Obtener control_base_id del propietario
    user_result = await db.execute(
        select(Usuario).where(Usuario.id == propietario_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Propietario no encontrado")
    
    categoria = await db.get(CategoriaGasto, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    if categoria.control_base_id != user.control_base_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar esta categoría")
    
    # Actualizar campos
    if data.nombre is not None:
        # Verificar duplicado
        existe = await db.execute(
            select(CategoriaGasto).where(
                CategoriaGasto.control_base_id == user.control_base_id,
                CategoriaGasto.nombre == data.nombre,
                CategoriaGasto.id != categoria_id
            )
        )
        if existe.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe una categoría con el nombre '{data.nombre}'"
            )
        categoria.nombre = data.nombre
    
    if data.descripcion is not None:
        categoria.descripcion = data.descripcion
    if data.subcategorias is not None:
        categoria.subcategorias = data.subcategorias
    if data.aplica_a is not None:
        categoria.aplica_a = data.aplica_a
    if data.tratamiento_economico is not None:
        categoria.tratamiento_economico = data.tratamiento_economico
    if data.activo is not None:
        categoria.activo = data.activo
    
    await db.commit()
    await db.refresh(categoria)
    return categoria


@router.delete("/categorias/{categoria_id}")
async def eliminar_categoria(
    categoria_id: UUID,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar (desactivar) una categoría de gasto.
    """
    # Obtener control_base_id del propietario
    user_result = await db.execute(
        select(Usuario).where(Usuario.id == propietario_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Propietario no encontrado")
    
    categoria = await db.get(CategoriaGasto, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    if categoria.control_base_id != user.control_base_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta categoría")
    
    # Verificar que no tenga gastos asociados
    gastos = await db.execute(
        select(GastoVehiculo).where(GastoVehiculo.categoria_id == categoria_id).limit(1)
    )
    if gastos.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar la categoría porque tiene gastos asociados"
        )
    
    # Desactivar en lugar de eliminar
    categoria.activo = False
    await db.commit()
    
    return {"success": True, "message": "Categoría desactivada correctamente"}


# ============================================================
# GASTOS DE VEHÍCULO (CRUD)
# ============================================================

@router.post("/gasto", response_model=GastoVehiculoDetailResponse)
async def registrar_gasto(
    data: GastoVehiculoCreate,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Registrar un gasto de vehículo con categoría.
    """
    # 1. Verificar que el vehículo pertenece al propietario
    prop_vehiculo = await db.execute(
        select(PropietarioVehiculo).where(
            PropietarioVehiculo.vehiculo_id == data.vehiculo_id,
            PropietarioVehiculo.propietario_id == propietario_id,
            PropietarioVehiculo.activo == True
        )
    )
    if not prop_vehiculo.scalar_one_or_none():
        raise HTTPException(
            status_code=403,
            detail="Vehículo no pertenece al propietario"
        )
    
    # 2. Obtener el tenant del propietario
    user_result = await db.execute(
        select(Usuario).where(Usuario.id == propietario_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Propietario no encontrado")
    
    # 3. Verificar que la categoría existe y pertenece al tenant
    categoria = await db.get(CategoriaGasto, data.categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    if categoria.control_base_id != user.control_base_id:
        raise HTTPException(status_code=403, detail="Categoría no válida para este tenant")
    
    if not categoria.activo:
        raise HTTPException(status_code=400, detail="La categoría está desactivada")
    
    # 4. Verificar que la categoría aplica a vehículos
    if "vehiculo" not in categoria.aplica_a:
        raise HTTPException(
            status_code=400,
            detail=f"La categoría '{categoria.nombre}' no aplica a vehículos"
        )
    
    # 5. Validar subcategoría
    if data.subcategoria:
        if categoria.subcategorias and data.subcategoria not in categoria.subcategorias:
            raise HTTPException(
                status_code=400,
                detail=f"Subcategoría '{data.subcategoria}' no válida. Opciones: {', '.join(categoria.subcategorias)}"
            )
    
    # 6. Crear gasto
    gasto = GastoVehiculo(
        vehiculo_id=data.vehiculo_id,
        propietario_id=propietario_id,
        categoria_id=data.categoria_id,
        subcategoria=data.subcategoria,
        monto=data.monto,
        fecha_gasto=data.fecha_gasto,
        descripcion=data.descripcion,
        km_registro=data.km_registro,
        tipo_gasto=data.tipo_gasto or categoria.nombre  # Legacy
    )
    
    db.add(gasto)
    await db.commit()
    await db.refresh(gasto)
    
    # Obtener patente del vehículo para la respuesta
    vehiculo = await db.get(Vehiculo, data.vehiculo_id)
    
    return GastoVehiculoDetailResponse(
        id=gasto.id,
        vehiculo_id=gasto.vehiculo_id,
        vehiculo_patente=vehiculo.patente if vehiculo else "",
        categoria_id=gasto.categoria_id,
        categoria_nombre=categoria.nombre,
        subcategoria=gasto.subcategoria,
        tipo_gasto=gasto.tipo_gasto,
        monto=float(gasto.monto),
        descripcion=gasto.descripcion,
        km_registro=float(gasto.km_registro) if gasto.km_registro else None,
        comprobante_url=gasto.comprobante_url,
        fecha_gasto=gasto.fecha_gasto,
        created_at=gasto.created_at
    )


@router.get("/gastos", response_model=List[GastoVehiculoDetailResponse])
async def listar_gastos(
    vehiculo_id: Optional[UUID] = None,
    categoria_id: Optional[UUID] = None,
    subcategoria: Optional[str] = None,
    tipo_gasto: Optional[str] = None,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    monto_min: Optional[float] = None,
    monto_max: Optional[float] = None,
    limit: int = 100,
    offset: int = 0,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar gastos del propietario con filtros.
    """
    # Construir query base con joins
    query = select(GastoVehiculo).options(
        selectinload(GastoVehiculo.vehiculo),
        selectinload(GastoVehiculo.categoria)
    ).where(GastoVehiculo.propietario_id == propietario_id)
    
    # Aplicar filtros
    if vehiculo_id:
        query = query.where(GastoVehiculo.vehiculo_id == vehiculo_id)
    if categoria_id:
        query = query.where(GastoVehiculo.categoria_id == categoria_id)
    if subcategoria:
        query = query.where(GastoVehiculo.subcategoria == subcategoria)
    if tipo_gasto:
        query = query.where(GastoVehiculo.tipo_gasto == tipo_gasto)
    if desde:
        query = query.where(GastoVehiculo.fecha_gasto >= desde)
    if hasta:
        query = query.where(GastoVehiculo.fecha_gasto <= hasta)
    if monto_min is not None:
        query = query.where(GastoVehiculo.monto >= monto_min)
    if monto_max is not None:
        query = query.where(GastoVehiculo.monto <= monto_max)
    
    # Ordenar y paginar
    query = query.order_by(desc(GastoVehiculo.fecha_gasto), desc(GastoVehiculo.created_at))
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    gastos = result.scalars().all()
    
    # Construir respuesta
    response = []
    for gasto in gastos:
        response.append(GastoVehiculoDetailResponse(
            id=gasto.id,
            vehiculo_id=gasto.vehiculo_id,
            vehiculo_patente=gasto.vehiculo.patente if gasto.vehiculo else "",
            categoria_id=gasto.categoria_id,
            categoria_nombre=gasto.categoria.nombre if gasto.categoria else None,
            subcategoria=gasto.subcategoria,
            tipo_gasto=gasto.tipo_gasto,
            monto=float(gasto.monto),
            descripcion=gasto.descripcion,
            km_registro=float(gasto.km_registro) if gasto.km_registro else None,
            comprobante_url=gasto.comprobante_url,
            fecha_gasto=gasto.fecha_gasto,
            created_at=gasto.created_at
        ))
    
    return response


@router.get("/gasto/{gasto_id}", response_model=GastoVehiculoDetailResponse)
async def obtener_gasto(
    gasto_id: UUID,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener un gasto específico.
    """
    gasto = await db.get(GastoVehiculo, gasto_id)
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    
    if gasto.propietario_id != propietario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este gasto")
    
    # Cargar relaciones
    await db.refresh(gasto, attribute_names=["vehiculo", "categoria"])
    
    return GastoVehiculoDetailResponse(
        id=gasto.id,
        vehiculo_id=gasto.vehiculo_id,
        vehiculo_patente=gasto.vehiculo.patente if gasto.vehiculo else "",
        categoria_id=gasto.categoria_id,
        categoria_nombre=gasto.categoria.nombre if gasto.categoria else None,
        subcategoria=gasto.subcategoria,
        tipo_gasto=gasto.tipo_gasto,
        monto=float(gasto.monto),
        descripcion=gasto.descripcion,
        km_registro=float(gasto.km_registro) if gasto.km_registro else None,
        comprobante_url=gasto.comprobante_url,
        fecha_gasto=gasto.fecha_gasto,
        created_at=gasto.created_at
    )


@router.put("/gasto/{gasto_id}", response_model=GastoVehiculoDetailResponse)
async def actualizar_gasto(
    gasto_id: UUID,
    data: GastoVehiculoUpdate,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar un gasto existente.
    """
    # 1. Obtener gasto y verificar propiedad
    gasto = await db.get(GastoVehiculo, gasto_id)
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    
    if gasto.propietario_id != propietario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este gasto")
    
    # 2. Si se cambia la categoría, validar
    if data.categoria_id is not None and data.categoria_id != gasto.categoria_id:
        categoria = await db.get(CategoriaGasto, data.categoria_id)
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        
        user_result = await db.execute(
            select(Usuario).where(Usuario.id == propietario_id)
        )
        user = user_result.scalar_one_or_none()
        if categoria.control_base_id != user.control_base_id:
            raise HTTPException(status_code=403, detail="Categoría no válida para este tenant")
        
        if not categoria.activo:
            raise HTTPException(status_code=400, detail="La categoría está desactivada")
        
        if "vehiculo" not in categoria.aplica_a:
            raise HTTPException(
                status_code=400,
                detail=f"La categoría '{categoria.nombre}' no aplica a vehículos"
            )
        
        gasto.categoria_id = data.categoria_id
    
    # 3. Actualizar campos
    if data.subcategoria is not None:
        # Validar subcategoría si hay categoría
        if gasto.categoria_id:
            categoria = await db.get(CategoriaGasto, gasto.categoria_id)
            if categoria and categoria.subcategorias and data.subcategoria not in categoria.subcategorias:
                raise HTTPException(
                    status_code=400,
                    detail=f"Subcategoría '{data.subcategoria}' no válida. Opciones: {', '.join(categoria.subcategorias)}"
                )
        gasto.subcategoria = data.subcategoria
    
    if data.monto is not None:
        gasto.monto = data.monto
    if data.fecha_gasto is not None:
        gasto.fecha_gasto = data.fecha_gasto
    if data.descripcion is not None:
        gasto.descripcion = data.descripcion
    if data.km_registro is not None:
        gasto.km_registro = data.km_registro
    if data.tipo_gasto is not None:
        gasto.tipo_gasto = data.tipo_gasto
    
    await db.commit()
    await db.refresh(gasto)
    await db.refresh(gasto, attribute_names=["vehiculo", "categoria"])
    
    return GastoVehiculoDetailResponse(
        id=gasto.id,
        vehiculo_id=gasto.vehiculo_id,
        vehiculo_patente=gasto.vehiculo.patente if gasto.vehiculo else "",
        categoria_id=gasto.categoria_id,
        categoria_nombre=gasto.categoria.nombre if gasto.categoria else None,
        subcategoria=gasto.subcategoria,
        tipo_gasto=gasto.tipo_gasto,
        monto=float(gasto.monto),
        descripcion=gasto.descripcion,
        km_registro=float(gasto.km_registro) if gasto.km_registro else None,
        comprobante_url=gasto.comprobante_url,
        fecha_gasto=gasto.fecha_gasto,
        created_at=gasto.created_at
    )


@router.delete("/gasto/{gasto_id}")
async def eliminar_gasto(
    gasto_id: UUID,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar un gasto (baja física).
    """
    gasto = await db.get(GastoVehiculo, gasto_id)
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    
    if gasto.propietario_id != propietario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este gasto")
    
    await db.delete(gasto)
    await db.commit()
    
    return {"success": True, "message": "Gasto eliminado correctamente"}


# ============================================================
# SUBIR COMPROBANTES A CLOUDINARY
# ============================================================

@router.post("/gasto/{gasto_id}/comprobante")
async def subir_comprobante(
    gasto_id: UUID,
    file: UploadFile = File(...),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Subir un comprobante (PDF, imagen) a Cloudinary.
    """
    # Verificar que el gasto existe y pertenece al propietario
    gasto = await db.get(GastoVehiculo, gasto_id)
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    
    if gasto.propietario_id != propietario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este gasto")
    
    # Validar tipo de archivo
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no permitido. Use JPG, PNG o PDF"
        )
    
    try:
        # Subir a Cloudinary
        url = await cloudinary_storage.upload_comprobante(
            file=file,
            propietario_id=str(propietario_id),
            gasto_id=str(gasto_id),
            tipo="gasto_vehiculo"
        )
        
        # Actualizar el gasto con la URL
        gasto.comprobante_url = url
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


@router.delete("/gasto/{gasto_id}/comprobante")
async def eliminar_comprobante(
    gasto_id: UUID,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar un comprobante de Cloudinary.
    """
    gasto = await db.get(GastoVehiculo, gasto_id)
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    
    if gasto.propietario_id != propietario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este gasto")
    
    if not gasto.comprobante_url:
        raise HTTPException(status_code=404, detail="El gasto no tiene comprobante")
    
    # Extraer public_id y eliminar de Cloudinary
    public_id = cloudinary_storage.extract_public_id_from_url(gasto.comprobante_url)
    if public_id:
        await cloudinary_storage.delete_comprobante(public_id)
    
    # Eliminar URL de la base de datos
    gasto.comprobante_url = None
    await db.commit()
    
    return {"success": True, "message": "Comprobante eliminado correctamente"}


# ============================================================
# RESUMEN Y ESTADÍSTICAS
# ============================================================

@router.get("/gastos/resumen", response_model=ResumenGastosResponse)
async def resumen_gastos(
    desde: date,
    hasta: date,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Resumen de gastos por categoría y vehículo.
    """
    # Total de gastos
    total_result = await db.execute(
        select(func.coalesce(func.sum(GastoVehiculo.monto), 0))
        .where(
            GastoVehiculo.propietario_id == propietario_id,
            GastoVehiculo.fecha_gasto.between(desde, hasta)
        )
    )
    total = float(total_result.scalar() or 0)
    
    # Por categoría (usando LEFT JOIN para incluir gastos sin categoría)
    by_category_result = await db.execute(
        select(
            CategoriaGasto.nombre,
            func.coalesce(func.sum(GastoVehiculo.monto), 0).label("total")
        )
        .join(GastoVehiculo, GastoVehiculo.categoria_id == CategoriaGasto.id, isouter=True)
        .where(
            GastoVehiculo.propietario_id == propietario_id,
            GastoVehiculo.fecha_gasto.between(desde, hasta)
        )
        .group_by(CategoriaGasto.nombre)
        .order_by(func.sum(GastoVehiculo.monto).desc())
    )
    by_category = {row[0]: float(row[1]) for row in by_category_result.all() if row[0] is not None}
    
    # Incluir gastos sin categoría como "Sin categoría"
    sin_categoria_result = await db.execute(
        select(func.coalesce(func.sum(GastoVehiculo.monto), 0))
        .where(
            GastoVehiculo.propietario_id == propietario_id,
            GastoVehiculo.fecha_gasto.between(desde, hasta),
            GastoVehiculo.categoria_id.is_(None)
        )
    )
    sin_categoria = float(sin_categoria_result.scalar() or 0)
    if sin_categoria > 0:
        by_category["Sin categoría"] = sin_categoria
    
    # Por vehículo
    by_vehicle_result = await db.execute(
        select(
            Vehiculo.patente,
            func.coalesce(func.sum(GastoVehiculo.monto), 0).label("total")
        )
        .join(Vehiculo, Vehiculo.id == GastoVehiculo.vehiculo_id)
        .where(
            GastoVehiculo.propietario_id == propietario_id,
            GastoVehiculo.fecha_gasto.between(desde, hasta)
        )
        .group_by(Vehiculo.patente)
        .order_by(func.sum(GastoVehiculo.monto).desc())
    )
    by_vehicle = [{"patente": row[0], "total": float(row[1])} for row in by_vehicle_result.all()]
    
    return ResumenGastosResponse(
        total_gastos=total,
        por_tipo=by_category,
        por_vehiculo=by_vehicle,
        periodo_desde=desde,
        periodo_hasta=hasta
    )


@router.get("/gastos/evolucion")
async def evolucion_gastos(
    desde: date,
    hasta: date,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Evolución mensual de gastos para gráficos.
    """
    # Agrupar por mes
    result = await db.execute(
        select(
            func.date_trunc('month', GastoVehiculo.fecha_gasto).label("mes"),
            func.coalesce(func.sum(GastoVehiculo.monto), 0).label("total")
        )
        .where(
            GastoVehiculo.propietario_id == propietario_id,
            GastoVehiculo.fecha_gasto.between(desde, hasta)
        )
        .group_by(func.date_trunc('month', GastoVehiculo.fecha_gasto))
        .order_by(func.date_trunc('month', GastoVehiculo.fecha_gasto))
    )
    
    rows = result.all()
    return {
        "labels": [row[0].strftime("%b %Y") for row in rows],
        "values": [float(row[1]) for row in rows]
    }