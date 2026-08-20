from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from uuid import UUID
import cloudinary.uploader
import traceback
import logging
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user

# Configurar logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fotos", tags=["Fotos Vehículo"])


# ============================================================
# MODELOS PYDANTIC
# ============================================================

class DescripcionUpdate(BaseModel):
    descripcion: str


# ============================================================
# ENDPOINT DE PRUEBA
# ============================================================

@router.get("/ping")
async def ping():
    return {"message": "Router de fotos funcionando correctamente"}


# ============================================================
# OBTENER FOTOS DE UN VEHÍCULO
# ============================================================

@router.get("/vehiculos/{vehiculo_id}")
async def obtener_fotos_vehiculo(
    vehiculo_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene todas las fotos de un vehículo"""
    
    user_id, control_base_id, email, tipo = current_user
    
    query = text("""
        SELECT 
            id, url, public_id, descripcion, orden, es_principal, created_at
        FROM fleet.foto_vehiculo
        WHERE vehiculo_id = :vehiculo_id
        ORDER BY es_principal DESC, orden ASC, created_at DESC
    """)
    
    result = await db.execute(query, {"vehiculo_id": UUID(vehiculo_id)})
    rows = result.fetchall()
    
    return [
        {
            "id": str(row[0]),
            "url": row[1],
            "public_id": row[2],
            "descripcion": row[3],
            "orden": row[4],
            "es_principal": row[5],
            "created_at": row[6].isoformat() if row[6] else None
        }
        for row in rows
    ]


# ============================================================
# SUBIR NUEVA FOTO
# ============================================================

@router.post("/vehiculos/{vehiculo_id}")
async def subir_foto(
    vehiculo_id: str,
    file: UploadFile = File(...),
    descripcion: Optional[str] = Form(None),
    es_principal: bool = Form(False),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sube una nueva foto del vehículo a Cloudinary"""
    
    logger.info("=" * 60)
    logger.info("📸 SUBIDA DE FOTO - INICIO")
    logger.info("=" * 60)
    
    try:
        user_id, control_base_id, email, tipo = current_user
        logger.info(f"✅ 1. Usuario: {user_id}")
        
        # Verificar vehículo existe
        query_check = text("""
            SELECT id, patente FROM fleet.vehiculo 
            WHERE id = :vehiculo_id
        """)
        result = await db.execute(query_check, {"vehiculo_id": UUID(vehiculo_id)})
        vehiculo = result.first()
        
        if not vehiculo:
            logger.error("❌ Vehículo no encontrado")
            raise HTTPException(404, "Vehículo no encontrado")
        
        logger.info(f"✅ 2. Vehículo: {vehiculo[1]} (ID: {vehiculo[0]})")
        
        # Verificar propietario
        query_prop = text("""
            SELECT id FROM fleet.propietario_vehiculo
            WHERE propietario_id = :user_id AND vehiculo_id = :vehiculo_id AND activo = true
        """)
        result = await db.execute(query_prop, {
            "user_id": user_id,
            "vehiculo_id": UUID(vehiculo_id)
        })
        
        if not result.first():
            logger.error("❌ Usuario no es propietario")
            raise HTTPException(403, "No tienes permisos sobre este vehículo")
        
        logger.info("✅ 3. Propietario verificado")
        
        # Validar archivo
        logger.info(f"📄 File: {file.filename}")
        logger.info(f"📄 Content-Type: {file.content_type}")
        
        if not file.content_type or not file.content_type.startswith('image/'):
            logger.error(f"❌ Archivo no es imagen: {file.content_type}")
            raise HTTPException(400, "El archivo debe ser una imagen")
        
        logger.info("✅ 4. Archivo válido")
        
        # Leer archivo
        try:
            contents = await file.read()
            logger.info(f"✅ 5. Tamaño: {len(contents)} bytes")
        except Exception as read_error:
            logger.error(f"❌ Error al leer archivo: {read_error}")
            raise HTTPException(500, f"Error al leer el archivo: {str(read_error)}")
        
        # Subir a Cloudinary
        try:
            logger.info("☁️ Subiendo a Cloudinary...")
            upload_result = cloudinary.uploader.upload(
                contents,
                folder=f"vehiculos/{vehiculo_id}",
                transformation=[
                    {"width": 800, "height": 600, "crop": "limit"},
                    {"quality": "auto"}
                ]
            )
            logger.info(f"✅ 6. Cloudinary OK: {upload_result['secure_url']}")
            
        except Exception as cloud_error:
            logger.error(f"❌ Error Cloudinary: {cloud_error}")
            logger.error(traceback.format_exc())
            raise HTTPException(500, f"Error en Cloudinary: {str(cloud_error)}")
        
        # Contar fotos
        query_count = text("""
            SELECT COUNT(*) FROM fleet.foto_vehiculo
            WHERE vehiculo_id = :vehiculo_id
        """)
        result = await db.execute(query_count, {"vehiculo_id": UUID(vehiculo_id)})
        count = result.scalar() or 0
        logger.info(f"✅ 7. Fotos existentes: {count}")
        
        # Si es primera foto, marcar como principal
        if count == 0:
            es_principal = True
            logger.info("   → Primera foto, marcando como principal")
        
        # Insertar en base de datos
        try:
            query_insert = text("""
                INSERT INTO fleet.foto_vehiculo (
                    vehiculo_id, url, public_id, descripcion, orden, es_principal, subida_por
                ) VALUES (
                    :vehiculo_id, :url, :public_id, :descripcion, :orden, :es_principal, :subida_por
                )
                RETURNING id, url, public_id, descripcion, orden, es_principal, created_at
            """)
            
            result = await db.execute(query_insert, {
                "vehiculo_id": UUID(vehiculo_id),
                "url": upload_result['secure_url'],
                "public_id": upload_result['public_id'],
                "descripcion": descripcion,
                "orden": count,
                "es_principal": es_principal,
                "subida_por": user_id
            })
            
            await db.commit()
            row = result.first()
            
            logger.info("✅ 8. Foto guardada en BD")
            logger.info(f"   ID: {row[0]}")
            logger.info("=" * 60)
            logger.info("✅ SUBIDA COMPLETADA CON ÉXITO")
            logger.info("=" * 60)
            
            return {
                "id": str(row[0]),
                "url": row[1],
                "public_id": row[2],
                "descripcion": row[3],
                "orden": row[4],
                "es_principal": row[5],
                "created_at": row[6].isoformat() if row[6] else None,
                "message": "Foto subida correctamente"
            }
            
        except Exception as db_error:
            logger.error(f"❌ Error en base de datos: {db_error}")
            logger.error(traceback.format_exc())
            await db.rollback()
            raise HTTPException(500, f"Error al guardar en base de datos: {str(db_error)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("=" * 60)
        logger.error("❌ ERROR INESPERADO")
        logger.error("=" * 60)
        logger.error(traceback.format_exc())
        logger.error("=" * 60)
        await db.rollback()
        raise HTTPException(500, f"Error interno: {str(e)}")


# ============================================================
# ACTUALIZAR DESCRIPCIÓN DE FOTO (CORREGIDO - RECIBE JSON)
# ============================================================

@router.patch("/{foto_id}/descripcion")
async def actualizar_descripcion(
    foto_id: str,
    data: DescripcionUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualiza la descripción de una foto"""
    
    logger.info(f"📝 Actualizando descripción de foto: {foto_id}")
    logger.info(f"📝 Nueva descripción: {data.descripcion}")
    
    try:
        # Verificar que la foto existe
        query_check = text("""
            SELECT f.id, f.vehiculo_id, v.patente
            FROM fleet.foto_vehiculo f
            JOIN fleet.vehiculo v ON v.id = f.vehiculo_id
            WHERE f.id = :foto_id
        """)
        result = await db.execute(query_check, {"foto_id": UUID(foto_id)})
        foto = result.first()
        
        if not foto:
            logger.error(f"❌ Foto no encontrada: {foto_id}")
            raise HTTPException(404, "Foto no encontrada")
        
        logger.info(f"✅ Foto encontrada: Vehículo {foto[2]}")
        
        # Verificar que el usuario es propietario del vehículo
        user_id, control_base_id, email, tipo = current_user
        
        query_prop = text("""
            SELECT id FROM fleet.propietario_vehiculo
            WHERE propietario_id = :user_id AND vehiculo_id = :vehiculo_id AND activo = true
        """)
        result = await db.execute(query_prop, {
            "user_id": user_id,
            "vehiculo_id": foto[1]
        })
        
        if not result.first():
            logger.error(f"❌ Usuario no es propietario del vehículo")
            raise HTTPException(403, "No tienes permisos sobre este vehículo")
        
        logger.info("✅ Propietario verificado")
        
        # Actualizar descripción
        query_update = text("""
            UPDATE fleet.foto_vehiculo 
            SET descripcion = :descripcion
            WHERE id = :foto_id
            RETURNING id, descripcion
        """)
        
        result = await db.execute(query_update, {
            "foto_id": UUID(foto_id),
            "descripcion": data.descripcion
        })
        await db.commit()
        
        row = result.first()
        
        if not row:
            raise HTTPException(404, "Foto no encontrada")
        
        logger.info(f"✅ Descripción actualizada: {row[1]}")
        
        return {
            "message": "Descripción actualizada",
            "id": str(row[0]),
            "descripcion": row[1]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al actualizar descripción: {e}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(500, f"Error al actualizar descripción: {str(e)}")


# ============================================================
# MARCAR FOTO COMO PRINCIPAL
# ============================================================

@router.patch("/{foto_id}/principal")
async def marcar_principal(
    foto_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Marca una foto como principal (automáticamente desmarca las demás)"""
    
    logger.info(f"⭐ Marcando foto como principal: {foto_id}")
    
    try:
        # Verificar que la foto existe
        query_check = text("""
            SELECT f.id, f.vehiculo_id, v.patente
            FROM fleet.foto_vehiculo f
            JOIN fleet.vehiculo v ON v.id = f.vehiculo_id
            WHERE f.id = :foto_id
        """)
        result = await db.execute(query_check, {"foto_id": UUID(foto_id)})
        foto = result.first()
        
        if not foto:
            logger.error(f"❌ Foto no encontrada: {foto_id}")
            raise HTTPException(404, "Foto no encontrada")
        
        # Verificar propietario
        user_id, control_base_id, email, tipo = current_user
        
        query_prop = text("""
            SELECT id FROM fleet.propietario_vehiculo
            WHERE propietario_id = :user_id AND vehiculo_id = :vehiculo_id AND activo = true
        """)
        result = await db.execute(query_prop, {
            "user_id": user_id,
            "vehiculo_id": foto[1]
        })
        
        if not result.first():
            logger.error(f"❌ Usuario no es propietario")
            raise HTTPException(403, "No tienes permisos sobre este vehículo")
        
        # Desmarcar todas las fotos del vehículo
        query_desmarcar = text("""
            UPDATE fleet.foto_vehiculo 
            SET es_principal = FALSE
            WHERE vehiculo_id = :vehiculo_id
        """)
        await db.execute(query_desmarcar, {"vehiculo_id": foto[1]})
        
        # Marcar la foto seleccionada como principal
        query_marcar = text("""
            UPDATE fleet.foto_vehiculo 
            SET es_principal = TRUE
            WHERE id = :foto_id
            RETURNING id, es_principal
        """)
        result = await db.execute(query_marcar, {"foto_id": UUID(foto_id)})
        await db.commit()
        
        row = result.first()
        
        if not row:
            raise HTTPException(404, "Foto no encontrada")
        
        logger.info(f"✅ Foto marcada como principal: {row[0]}")
        
        return {
            "message": "Foto marcada como principal",
            "foto_id": str(row[0]),
            "es_principal": row[1]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al marcar como principal: {e}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(500, f"Error al marcar como principal: {str(e)}")


# ============================================================
# ELIMINAR FOTO
# ============================================================

@router.delete("/{foto_id}")
async def eliminar_foto(
    foto_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Elimina una foto del vehículo y de Cloudinary"""
    
    logger.info(f"🗑️ Eliminando foto: {foto_id}")
    
    try:
        # Verificar que la foto existe
        query_check = text("""
            SELECT f.id, f.vehiculo_id, f.public_id, v.patente
            FROM fleet.foto_vehiculo f
            JOIN fleet.vehiculo v ON v.id = f.vehiculo_id
            WHERE f.id = :foto_id
        """)
        result = await db.execute(query_check, {"foto_id": UUID(foto_id)})
        foto = result.first()
        
        if not foto:
            logger.error(f"❌ Foto no encontrada: {foto_id}")
            raise HTTPException(404, "Foto no encontrada")
        
        # Verificar propietario
        user_id, control_base_id, email, tipo = current_user
        
        query_prop = text("""
            SELECT id FROM fleet.propietario_vehiculo
            WHERE propietario_id = :user_id AND vehiculo_id = :vehiculo_id AND activo = true
        """)
        result = await db.execute(query_prop, {
            "user_id": user_id,
            "vehiculo_id": foto[1]
        })
        
        if not result.first():
            logger.error(f"❌ Usuario no es propietario")
            raise HTTPException(403, "No tienes permisos sobre este vehículo")
        
        # Eliminar de Cloudinary
        try:
            cloudinary.uploader.destroy(foto[2])
            logger.info(f"✅ Eliminado de Cloudinary: {foto[2]}")
        except Exception as cloud_error:
            logger.warning(f"⚠️ Error eliminando de Cloudinary: {cloud_error}")
        
        # Eliminar de base de datos
        query_delete = text("""
            DELETE FROM fleet.foto_vehiculo WHERE id = :foto_id
        """)
        await db.execute(query_delete, {"foto_id": UUID(foto_id)})
        await db.commit()
        
        logger.info(f"✅ Foto eliminada correctamente")
        
        return {"message": "Foto eliminada correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al eliminar foto: {e}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(500, f"Error al eliminar foto: {str(e)}")