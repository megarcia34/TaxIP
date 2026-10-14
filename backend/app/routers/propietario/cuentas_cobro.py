"""
Cuentas de cobro del propietario (CBU/CVU)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.propietario_schemas import (
    CuentaCobroCreate,
    CuentaCobroUpdate,
    CuentaCobroResponse,
)

router = APIRouter(prefix="/cuentas-cobro", tags=["Cuentas de Cobro"])

MAX_CUENTAS = 5


async def _validar_propietario(db: AsyncSession, user_id: UUID) -> None:
    query = text("""
        SELECT id FROM fleet.propietario_vehiculo
        WHERE propietario_id = :user_id AND activo = true
        LIMIT 1
    """)
    result = await db.execute(query, {"user_id": user_id})
    if not result.first():
        raise HTTPException(status_code=403, detail="No eres propietario")


@router.get("", response_model=list[CuentaCobroResponse])
async def listar_cuentas(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista las cuentas de cobro activas del propietario.
    """
    user_id = current_user[0]
    await _validar_propietario(db, user_id)

    query = text("""
        SELECT id, usuario_id, tipo, numero, alias, banco, titular,
               predeterminada, activo, created_at, updated_at
        FROM payment.cuenta_cobro
        WHERE usuario_id = :user_id AND activo = true
        ORDER BY predeterminada DESC, created_at ASC
    """)
    result = await db.execute(query, {"user_id": user_id})
    rows = result.all()

    return [
        CuentaCobroResponse(
            id=row[0], usuario_id=row[1], tipo=row[2], numero=row[3],
            alias=row[4], banco=row[5], titular=row[6],
            predeterminada=row[7], activo=row[8],
            created_at=row[9], updated_at=row[10]
        )
        for row in rows
    ]


@router.post("", response_model=CuentaCobroResponse, status_code=201)
async def crear_cuenta(
    data: CuentaCobroCreate,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crea una cuenta de cobro. Si es la primera, se marca como predeterminada.
    """
    user_id = current_user[0]
    await _validar_propietario(db, user_id)

    # Contar cuentas activas
    query_count = text("""
        SELECT COUNT(*) FROM payment.cuenta_cobro
        WHERE usuario_id = :user_id AND activo = true
    """)
    result = await db.execute(query_count, {"user_id": user_id})
    count = result.scalar() or 0

    if count >= MAX_CUENTAS:
        raise HTTPException(
            status_code=400,
            detail=f"Ya tienes {MAX_CUENTAS} cuentas de cobro activas. Elimina una antes de agregar otra."
        )

    # Validar numero unico por usuario
    query_dup = text("""
        SELECT id FROM payment.cuenta_cobro
        WHERE usuario_id = :user_id AND numero = :numero AND activo = true
    """)
    result = await db.execute(query_dup, {
        "user_id": user_id,
        "numero": data.numero
    })
    if result.first():
        raise HTTPException(
            status_code=400,
            detail="Ya tienes una cuenta con ese numero"
        )

    # Si es la primera, es predeterminada
    es_predeterminada = (count == 0)

    query_insert = text("""
        INSERT INTO payment.cuenta_cobro (
            id, usuario_id, tipo, numero, alias, banco, titular,
            predeterminada, activo, created_at, updated_at
        )
        VALUES (
            gen_random_uuid(), :user_id, :tipo, :numero, :alias, :banco, :titular,
            :predeterminada, true, NOW(), NOW()
        )
        RETURNING id, usuario_id, tipo, numero, alias, banco, titular,
                  predeterminada, activo, created_at, updated_at
    """)
    result = await db.execute(query_insert, {
        "user_id": user_id,
        "tipo": data.tipo,
        "numero": data.numero,
        "alias": data.alias,
        "banco": data.banco,
        "titular": data.titular,
        "predeterminada": es_predeterminada
    })
    row = result.first()
    await db.commit()

    return CuentaCobroResponse(
        id=row[0], usuario_id=row[1], tipo=row[2], numero=row[3],
        alias=row[4], banco=row[5], titular=row[6],
        predeterminada=row[7], activo=row[8],
        created_at=row[9], updated_at=row[10]
    )


@router.put("/{cuenta_id}", response_model=CuentaCobroResponse)
async def actualizar_cuenta(
    cuenta_id: UUID,
    data: CuentaCobroUpdate,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza una cuenta de cobro.
    """
    user_id = current_user[0]
    await _validar_propietario(db, user_id)

    # Verificar que existe y pertenece al usuario
    query_verify = text("""
        SELECT id FROM payment.cuenta_cobro
        WHERE id = :cuenta_id AND usuario_id = :user_id AND activo = true
    """)
    result = await db.execute(query_verify, {
        "cuenta_id": cuenta_id,
        "user_id": user_id
    })
    if not result.first():
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    data_dict = data.model_dump(exclude_unset=True)

    if not data_dict:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")

    # Si cambia el numero, validar que no exista
    if "numero" in data_dict:
        query_dup = text("""
            SELECT id FROM payment.cuenta_cobro
            WHERE usuario_id = :user_id AND numero = :numero
              AND activo = true AND id != :cuenta_id
        """)
        result = await db.execute(query_dup, {
            "user_id": user_id,
            "numero": data_dict["numero"],
            "cuenta_id": cuenta_id
        })
        if result.first():
            raise HTTPException(
                status_code=400,
                detail="Ya tienes otra cuenta con ese numero"
            )

    # Construir UPDATE dinamico
    updates = []
    params = {"cuenta_id": cuenta_id}

    for campo, valor in data_dict.items():
        updates.append(f"{campo} = :{campo}")
        params[campo] = valor

    query = text(f"""
        UPDATE payment.cuenta_cobro
        SET {', '.join(updates)}, updated_at = NOW()
        WHERE id = :cuenta_id
        RETURNING id, usuario_id, tipo, numero, alias, banco, titular,
                  predeterminada, activo, created_at, updated_at
    """)
    result = await db.execute(query, params)
    row = result.first()
    await db.commit()

    return CuentaCobroResponse(
        id=row[0], usuario_id=row[1], tipo=row[2], numero=row[3],
        alias=row[4], banco=row[5], titular=row[6],
        predeterminada=row[7], activo=row[8],
        created_at=row[9], updated_at=row[10]
    )


@router.delete("/{cuenta_id}")
async def eliminar_cuenta(
    cuenta_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina (soft delete) una cuenta de cobro.
    Si era predeterminada, marca la mas antigua como predeterminada.
    """
    user_id = current_user[0]
    await _validar_propietario(db, user_id)

    # Verificar que existe
    query_verify = text("""
        SELECT id, predeterminada FROM payment.cuenta_cobro
        WHERE id = :cuenta_id AND usuario_id = :user_id AND activo = true
    """)
    result = await db.execute(query_verify, {
        "cuenta_id": cuenta_id,
        "user_id": user_id
    })
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    era_predeterminada = row[1]

    # Soft delete
    query_delete = text("""
        UPDATE payment.cuenta_cobro
        SET activo = false,
            predeterminada = false,
            updated_at = NOW()
        WHERE id = :cuenta_id
    """)
    await db.execute(query_delete, {"cuenta_id": cuenta_id})

    # Si era predeterminada, marcar otra como predeterminada
    if era_predeterminada:
        query_new_pred = text("""
            UPDATE payment.cuenta_cobro
            SET predeterminada = true, updated_at = NOW()
            WHERE id = (
                SELECT id FROM payment.cuenta_cobro
                WHERE usuario_id = :user_id AND activo = true
                ORDER BY created_at ASC
                LIMIT 1
            )
        """)
        await db.execute(query_new_pred, {"user_id": user_id})

    await db.commit()

    return {"success": True, "message": "Cuenta eliminada correctamente"}


@router.put("/{cuenta_id}/predeterminada", response_model=CuentaCobroResponse)
async def marcar_predeterminada(
    cuenta_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Marca una cuenta como predeterminada.
    Desmarca cualquier otra predeterminada.
    """
    user_id = current_user[0]
    await _validar_propietario(db, user_id)

    # Verificar que existe
    query_verify = text("""
        SELECT id FROM payment.cuenta_cobro
        WHERE id = :cuenta_id AND usuario_id = :user_id AND activo = true
    """)
    result = await db.execute(query_verify, {
        "cuenta_id": cuenta_id,
        "user_id": user_id
    })
    if not result.first():
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    # Desmarcar todas las predeterminadas del usuario
    query_unmark = text("""
        UPDATE payment.cuenta_cobro
        SET predeterminada = false, updated_at = NOW()
        WHERE usuario_id = :user_id AND predeterminada = true
    """)
    await db.execute(query_unmark, {"user_id": user_id})

    # Marcar la nueva
    query_mark = text("""
        UPDATE payment.cuenta_cobro
        SET predeterminada = true, updated_at = NOW()
        WHERE id = :cuenta_id
        RETURNING id, usuario_id, tipo, numero, alias, banco, titular,
                  predeterminada, activo, created_at, updated_at
    """)
    result = await db.execute(query_mark, {"cuenta_id": cuenta_id})
    row = result.first()
    await db.commit()

    return CuentaCobroResponse(
        id=row[0], usuario_id=row[1], tipo=row[2], numero=row[3],
        alias=row[4], banco=row[5], titular=row[6],
        predeterminada=row[7], activo=row[8],
        created_at=row[9], updated_at=row[10]
    )