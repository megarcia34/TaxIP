"""
Endpoints para imágenes de neumáticos
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional
import cloudinary.uploader
import logging
import traceback

from app.database import get_db
from app.dependencies import get_propietario_context
from app.routers.propietario.utils import (
    verificar_vehiculo_propietario,
    verificar_neumatico_propietario
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================
# SUBIR IMAGEN DE NEUMÁTICO
# ============================================================

@router.post("/neumaticos/{neumatico_id}/imagenes", status_code=status.HTTP_201_CREATED)
async def subir_imagen_neumatico(
    neumatico_id: UUID,
    file: UploadFile = File(..., description="Archivo de imagen (jpg, png, etc.)"),
    tipo_imagen: str = Form("FOTO_ESTADO", description="FOTO_ESTADO, GARANTIA, OTRO"),
    descripcion: Optional[str] = Form(None, description="Descripción de la imagen"),
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Subir una imagen asociada a un neumático.
    """
    logger.info("=" * 60)
    logger.info("📸 SUBIDA DE IMAGEN DE NEUMÁTICO - INICIO")
    logger.info("=" * 60)
    
    try:
        user_id = UUID(ctx["user_id"])
        control_base_id = UUID(ctx["control_base_id"])
        
        # Verificar que el neumático pertenece al propietario
        await verificar_neumatico_propietario(neumatico_id, UUID(ctx["propietario_id"]), db)
        
        # Validar archivo
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(400, "El archivo debe ser una imagen")
        
        # Leer archivo
        try:
            contents = await file.read()
            logger.info(f"📄 Tamaño: {len(contents)} bytes")
        except Exception as read_error:
            logger.error(f"❌ Error al leer archivo: {read_error}")
            raise HTTPException(500, f"Error al leer el archivo: {str(read_error)}")
        
        # Subir a Cloudinary
        try:
            logger.info("☁️ Subiendo a Cloudinary...")
            upload_result = cloudinary.uploader.upload(
                contents,
                folder=f"neumaticos/{neumatico_id}",
                transformation=[
                    {"width": 800, "height": 600, "crop": "limit"},
                    {"quality": "auto"}
                ]
            )
            logger.info(f"✅ Cloudinary OK: {upload_result['secure_url']}")
            
        except Exception as cloud_error:
            logger.error(f"❌ Error Cloudinary: {cloud_error}")
            logger.error(traceback.format_exc())
            raise HTTPException(500, f"Error en Cloudinary: {str(cloud_error)}")
        
        # Insertar en base de datos
        insert_query = text("""
            INSERT INTO fleet.neumatico_imagen (
                id, control_base_id, neumatico_vehiculo_id,
                cloudinary_public_id, cloudinary_url, cloudinary_secure_url,
                tipo_imagen, descripcion, peso_bytes, dimensiones,
                subido_por, fecha_subida
            ) VALUES (
                gen_random_uuid(), :control_base_id, :neumatico_id,
                :public_id, :url, :secure_url,
                :tipo_imagen, :descripcion, :peso_bytes, :dimensiones,
                :subido_por, NOW()
            ) RETURNING id, cloudinary_url, cloudinary_secure_url, tipo_imagen, descripcion
        """)
        
        result = await db.execute(insert_query, {
            "control_base_id": control_base_id,
            "neumatico_id": neumatico_id,
            "public_id": upload_result['public_id'],
            "url": upload_result['url'],
            "secure_url": upload_result['secure_url'],
            "tipo_imagen": tipo_imagen,
            "descripcion": descripcion,
            "peso_bytes": len(contents),
            "dimensiones": f"{upload_result.get('width', 0)}x{upload_result.get('height', 0)}",
            "subido_por": user_id
        })
        
        await db.commit()
        row = result.first()
        
        logger.info("✅ Imagen guardada en BD")
        logger.info("=" * 60)
        
        return {
            "id": str(row[0]),
            "url": row[1],
            "secure_url": row[2],
            "tipo_imagen": row[3],
            "descripcion": row[4],
            "mensaje": "Imagen subida correctamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("=" * 60)
        logger.error("❌ ERROR INESPERADO")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(500, f"Error interno: {str(e)}")


# ============================================================
# SUBIR IMAGEN DE OPERACIÓN DE NEUMÁTICO
# ============================================================

@router.post("/operaciones/{operacion_id}/imagenes", status_code=status.HTTP_201_CREATED)
async def subir_imagen_operacion(
    operacion_id: UUID,
    file: UploadFile = File(..., description="Archivo de imagen"),
    tipo_imagen: str = Form("FOTO_ESTADO", description="FOTO_ESTADO, GARANTIA, OTRO"),
    descripcion: Optional[str] = Form(None),
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Subir una imagen asociada a una operación de neumático.
    """
    logger.info("=" * 60)
    logger.info("📸 SUBIDA DE IMAGEN DE OPERACIÓN - INICIO")
    logger.info("=" * 60)
    
    try:
        user_id = UUID(ctx["user_id"])
        control_base_id = UUID(ctx["control_base_id"])
        propietario_id = UUID(ctx["propietario_id"])
        
        # Verificar que la operación existe y pertenece a un vehículo del propietario
        query_check = text("""
            SELECT o.id, o.vehiculo_id
            FROM fleet.neumatico_operacion o
            INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = o.vehiculo_id
            WHERE o.id = :operacion_id
              AND pv.propietario_id = :propietario_id
              AND pv.activo = true
        """)
        result = await db.execute(query_check, {
            "operacion_id": operacion_id,
            "propietario_id": propietario_id
        })
        row = result.first()
        
        if not row:
            raise HTTPException(404, "Operación no encontrada o no pertenece al propietario")
        
        # Validar archivo
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(400, "El archivo debe ser una imagen")
        
        # Leer archivo
        contents = await file.read()
        
        # Subir a Cloudinary
        try:
            logger.info("☁️ Subiendo a Cloudinary...")
            upload_result = cloudinary.uploader.upload(
                contents,
                folder=f"operaciones/{operacion_id}",
                transformation=[
                    {"width": 800, "height": 600, "crop": "limit"},
                    {"quality": "auto"}
                ]
            )
            logger.info(f"✅ Cloudinary OK: {upload_result['secure_url']}")
            
        except Exception as cloud_error:
            logger.error(f"❌ Error Cloudinary: {cloud_error}")
            raise HTTPException(500, f"Error en Cloudinary: {str(cloud_error)}")
        
        # Insertar en base de datos
        insert_query = text("""
            INSERT INTO fleet.neumatico_imagen (
                id, control_base_id, operacion_id,
                cloudinary_public_id, cloudinary_url, cloudinary_secure_url,
                tipo_imagen, descripcion, peso_bytes, dimensiones,
                subido_por, fecha_subida
            ) VALUES (
                gen_random_uuid(), :control_base_id, :operacion_id,
                :public_id, :url, :secure_url,
                :tipo_imagen, :descripcion, :peso_bytes, :dimensiones,
                :subido_por, NOW()
            ) RETURNING id, cloudinary_url, cloudinary_secure_url, tipo_imagen, descripcion
        """)
        
        result = await db.execute(insert_query, {
            "control_base_id": control_base_id,
            "operacion_id": operacion_id,
            "public_id": upload_result['public_id'],
            "url": upload_result['url'],
            "secure_url": upload_result['secure_url'],
            "tipo_imagen": tipo_imagen,
            "descripcion": descripcion,
            "peso_bytes": len(contents),
            "dimensiones": f"{upload_result.get('width', 0)}x{upload_result.get('height', 0)}",
            "subido_por": user_id
        })
        
        await db.commit()
        row = result.first()
        
        logger.info("✅ Imagen guardada en BD")
        logger.info("=" * 60)
        
        return {
            "id": str(row[0]),
            "url": row[1],
            "secure_url": row[2],
            "tipo_imagen": row[3],
            "descripcion": row[4],
            "mensaje": "Imagen subida correctamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(500, f"Error interno: {str(e)}")


# ============================================================
# LISTAR IMÁGENES DE UN NEUMÁTICO
# ============================================================

@router.get("/neumaticos/{neumatico_id}/imagenes")
async def listar_imagenes_neumatico(
    neumatico_id: UUID,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar todas las imágenes asociadas a un neumático.
    """
    try:
        propietario_id = UUID(ctx["propietario_id"])
        
        # Verificar que el neumático pertenece al propietario
        await verificar_neumatico_propietario(neumatico_id, propietario_id, db)
        
        query = text("""
            SELECT 
              ni.id, ni.cloudinary_url, ni.cloudinary_secure_url,
              ni.tipo_imagen, ni.descripcion, ni.peso_bytes, ni.dimensiones,
              ni.fecha_subida,
              CONCAT(p.nombre, ' ', p.apellido) as subido_por
            FROM fleet.neumatico_imagen ni
            LEFT JOIN auth.perfil_general p ON p.usuario_id = ni.subido_por
            WHERE ni.neumatico_vehiculo_id = :neumatico_id
             AND ni.activo = true
            ORDER BY ni.fecha_subida DESC
        """)
        
        result = await db.execute(query, {"neumatico_id": neumatico_id})
        rows = result.all()
        
        return [
            {
                "id": str(row[0]),
                "url": row[1],
                "secure_url": row[2],
                "tipo_imagen": row[3],
                "descripcion": row[4],
                "peso_bytes": row[5],
                "dimensiones": row[6],
                "fecha_subida": row[7],
                "subido_por": row[8]
            }
            for row in rows
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al listar imágenes: {e}")
        raise HTTPException(500, f"Error interno: {str(e)}")


# ============================================================
# LISTAR IMÁGENES DE UNA OPERACIÓN
# ============================================================

@router.get("/operaciones/{operacion_id}/imagenes")
async def listar_imagenes_operacion(
    operacion_id: UUID,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar todas las imágenes asociadas a una operación de neumático.
    """
    try:
        propietario_id = UUID(ctx["propietario_id"])
        
        # Verificar que la operación existe y pertenece al propietario
        query_check = text("""
            SELECT o.id
            FROM fleet.neumatico_operacion o
            INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = o.vehiculo_id
            WHERE o.id = :operacion_id
              AND pv.propietario_id = :propietario_id
              AND pv.activo = true
        """)
        result = await db.execute(query_check, {
            "operacion_id": operacion_id,
            "propietario_id": propietario_id
        })
        
        if not result.first():
            raise HTTPException(404, "Operación no encontrada o no pertenece al propietario")
        
        query = text("""
            SELECT 
                ni.id, ni.cloudinary_url, ni.cloudinary_secure_url,
                ni.tipo_imagen, ni.descripcion, ni.peso_bytes, ni.dimensiones,
                ni.fecha_subida,
            CONCAT(p.nombre, ' ', p.apellido) as subido_por
            FROM fleet.neumatico_imagen ni
            LEFT JOIN auth.perfil_general p ON p.usuario_id = ni.subido_por
            WHERE ni.operacion_id = :operacion_id
             AND ni.activo = true
            ORDER BY ni.fecha_subida DESC
      """)
        
        result = await db.execute(query, {"operacion_id": operacion_id})
        rows = result.all()
        
        return [
            {
                "id": str(row[0]),
                "url": row[1],
                "secure_url": row[2],
                "tipo_imagen": row[3],
                "descripcion": row[4],
                "peso_bytes": row[5],
                "dimensiones": row[6],
                "fecha_subida": row[7],
                "subido_por": row[8]
            }
            for row in rows
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al listar imágenes: {e}")
        raise HTTPException(500, f"Error interno: {str(e)}")


# ============================================================
# ELIMINAR IMAGEN
# ============================================================

@router.delete("/imagenes/{imagen_id}")
async def eliminar_imagen_neumatico(
    imagen_id: UUID,
    ctx: dict = Depends(get_propietario_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar una imagen de un neumático (también la elimina de Cloudinary).
    """
    logger.info(f"🗑️ Eliminando imagen: {imagen_id}")
    
    try:
        propietario_id = UUID(ctx["propietario_id"])
        user_id = UUID(ctx["user_id"])
        
        # Verificar que la imagen existe y pertenece al propietario
        query_check = text("""
            SELECT ni.id, ni.cloudinary_public_id, ni.neumatico_vehiculo_id
            FROM fleet.neumatico_imagen ni
            LEFT JOIN fleet.neumatico_vehiculo nv ON nv.id = ni.neumatico_vehiculo_id
            LEFT JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = nv.vehiculo_id
            WHERE ni.id = :imagen_id
              AND (pv.propietario_id = :propietario_id OR ni.subido_por = :user_id)
              AND ni.activo = true
        """)
        result = await db.execute(query_check, {
            "imagen_id": imagen_id,
            "propietario_id": propietario_id,
            "user_id": user_id
        })
        row = result.first()
        
        if not row:
            raise HTTPException(404, "Imagen no encontrada o no tienes permisos para eliminarla")
        
        public_id = row[1]
        
        # Eliminar de Cloudinary
        if public_id:
            try:
                cloudinary.uploader.destroy(public_id)
                logger.info(f"✅ Eliminado de Cloudinary: {public_id}")
            except Exception as cloud_error:
                logger.warning(f"⚠️ Error eliminando de Cloudinary: {cloud_error}")
        
        # Marcar como inactivo en base de datos (soft delete)
        update_query = text("""
            UPDATE fleet.neumatico_imagen
            SET activo = false
            WHERE id = :imagen_id
        """)
        await db.execute(update_query, {"imagen_id": imagen_id})
        await db.commit()
        
        logger.info(f"✅ Imagen eliminada: {imagen_id}")
        
        return {"mensaje": "Imagen eliminada correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al eliminar imagen: {e}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(500, f"Error interno: {str(e)}")