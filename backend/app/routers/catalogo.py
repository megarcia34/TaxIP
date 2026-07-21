"""
Catalog endpoints for vehicle brands and models
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/catalogo", tags=["Catálogo"])


@router.get("/marcas")
async def listar_marcas(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all vehicle brands
    """
    query = text("""
        SELECT id, nombre, created_at
        FROM fleet.marca
        ORDER BY nombre ASC
    """)
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        {
            "id": str(row[0]),
            "nombre": row[1],
            "created_at": row[2]
        }
        for row in rows
    ]


@router.get("/modelos/{marca_id}")
async def listar_modelos_por_marca(
    marca_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List vehicle models by brand ID
    """
    query = text("""
        SELECT m.id, m.nombre, m.marca_id, ma.nombre as marca_nombre
        FROM fleet.modelo m
        JOIN fleet.marca ma ON ma.id = m.marca_id
        WHERE m.marca_id = :marca_id
        ORDER BY m.nombre ASC
    """)
    
    result = await db.execute(query, {"marca_id": marca_id})
    rows = result.all()
    
    if not rows:
        raise HTTPException(status_code=404, detail="No se encontraron modelos para esta marca")
    
    return [
        {
            "id": str(row[0]),
            "nombre": row[1],
            "marca_id": str(row[2]),
            "marca_nombre": row[3]
        }
        for row in rows
    ]


@router.get("/modelos")
async def listar_todos_modelos(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all vehicle models with their brands
    """
    query = text("""
        SELECT m.id, m.nombre, m.marca_id, ma.nombre as marca_nombre
        FROM fleet.modelo m
        JOIN fleet.marca ma ON ma.id = m.marca_id
        ORDER BY ma.nombre ASC, m.nombre ASC
    """)
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        {
            "id": str(row[0]),
            "nombre": row[1],
            "marca_id": str(row[2]),
            "marca_nombre": row[3]
        }
        for row in rows
    ]


@router.post("/marcas")
async def crear_marca(
    nombre: str,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new vehicle brand (admin only)
    """
    user_id, control_base_id, email, user_tipo = current_user
    
    if user_tipo.lower() != 'admin':
        raise HTTPException(status_code=403, detail="Solo administradores")
    
    query = text("""
        INSERT INTO fleet.marca (id, nombre, created_at)
        VALUES (gen_random_uuid(), :nombre, NOW())
        RETURNING id, nombre
    """)
    
    result = await db.execute(query, {"nombre": nombre})
    await db.commit()
    row = result.first()
    
    return {
        "id": str(row[0]),
        "nombre": row[1],
        "message": "Marca creada correctamente"
    }


@router.post("/modelos")
async def crear_modelo(
    marca_id: UUID,
    nombre: str,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new vehicle model (admin only)
    """
    user_id, control_base_id, email, user_tipo = current_user
    
    if user_tipo.lower() != 'admin':
        raise HTTPException(status_code=403, detail="Solo administradores")
    
    # Verificar que la marca existe
    check_query = text("SELECT id FROM fleet.marca WHERE id = :marca_id")
    result = await db.execute(check_query, {"marca_id": marca_id})
    if not result.first():
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    
    query = text("""
        INSERT INTO fleet.modelo (id, marca_id, nombre, created_at)
        VALUES (gen_random_uuid(), :marca_id, :nombre, NOW())
        RETURNING id, nombre
    """)
    
    result = await db.execute(query, {"marca_id": marca_id, "nombre": nombre})
    await db.commit()
    row = result.first()
    
    return {
        "id": str(row[0]),
        "nombre": row[1],
        "message": "Modelo creado correctamente"
    }