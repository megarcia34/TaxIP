"""
Router de catalogo de mantenimiento (solo lectura).

Endpoints:
- GET /api/mantenimiento/catalogo/componentes    arbol de sistemas > subsistemas > componentes
- GET /api/mantenimiento/catalogo/controles      controles por componente
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models.fleet import (
    MantenimientoCatalogoSistema,
    MantenimientoCatalogoSubsistema,
    MantenimientoCatalogoComponente,
    MantenimientoCatalogoControl,
)

router = APIRouter(prefix="/api/mantenimiento/catalogo", tags=["Mantenimiento - Catalogo"])


@router.get("/componentes")
async def listar_componentes(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Devuelve el arbol completo de sistemas > subsistemas > componentes.
    Solo lectura. Sin filtros por tenant (el catalogo es global).
    """
    sistemas = (await db.execute(
        select(MantenimientoCatalogoSistema)
        .where(MantenimientoCatalogoSistema.activo == True)
        .order_by(MantenimientoCatalogoSistema.orden)
    )).scalars().all()

    result = []
    for sistema in sistemas:
        subsistemas = (await db.execute(
            select(MantenimientoCatalogoSubsistema)
            .where(
                MantenimientoCatalogoSubsistema.sistema_id == sistema.id,
                MantenimientoCatalogoSubsistema.activo == True,
            )
            .order_by(MantenimientoCatalogoSubsistema.orden)
        )).scalars().all()

        subs_items = []
        for sub in subsistemas:
            componentes = (await db.execute(
                select(MantenimientoCatalogoComponente)
                .where(
                    MantenimientoCatalogoComponente.subsistema_id == sub.id,
                    MantenimientoCatalogoComponente.activo == True,
                )
                .order_by(MantenimientoCatalogoComponente.orden)
            )).scalars().all()

            subs_items.append({
                "id": str(sub.id),
                "nombre": sub.nombre,
                "componentes": [
                    {"id": str(c.id), "nombre": c.nombre}
                    for c in componentes
                ],
            })

        result.append({
            "id": str(sistema.id),
            "nombre": sistema.nombre,
            "subsistemas": subs_items,
        })

    return {"sistemas": result}


@router.get("/controles")
async def listar_controles(
    componente_id: Optional[UUID] = Query(None),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Devuelve los controles. Si componente_id viene, filtra por ese componente.
    Los controles genericos (componente_id=NULL) se incluyen siempre.
    """
    query = select(MantenimientoCatalogoControl).where(
        MantenimientoCatalogoControl.activo == True
    )
    if componente_id:
        query = query.where(
            (MantenimientoCatalogoControl.componente_id == componente_id)
            | (MantenimientoCatalogoControl.componente_id.is_(None))
        )
    else:
        query = query.where(MantenimientoCatalogoControl.componente_id.is_(None))

    query = query.order_by(MantenimientoCatalogoControl.orden)
    controles = (await db.execute(query)).scalars().all()

    return [
        {
            "id": str(c.id),
            "nombre": c.nombre,
            "tipo": c.tipo,
            "unidad": c.unidad,
            "rango_normal": c.rango_normal,
        }
        for c in controles
    ]