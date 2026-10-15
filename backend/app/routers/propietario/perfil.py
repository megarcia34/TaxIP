"""
Perfil del propietario
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.propietario_schemas import PerfilPropietarioUpdate

router = APIRouter(prefix="/perfil", tags=["Perfil Propietario"])


@router.get("")
async def get_perfil(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el perfil del propietario autenticado.
    """
    user_id, control_base_id, email, tipo = current_user

    # Verificar que es propietario
    query_verify = text("""
        SELECT id FROM fleet.propietario_vehiculo
        WHERE propietario_id = :user_id AND activo = true
        LIMIT 1
    """)
    result = await db.execute(query_verify, {"user_id": user_id})
    if not result.first():
        raise HTTPException(status_code=403, detail="No eres propietario")

    # Obtener datos del perfil
    query = text("""
        SELECT
            u.id,
            u.email,
            u.activo,
            p.nombre,
            p.apellido,
            p.telefono,
            p.documento,
            p.direccion,
            cb.nombre as control_base_nombre,
            cb.id as control_base_id,
            p.foto_perfil_url,
            p.codigo_postal,
            p.fecha_nacimiento,
            p.ciudad_id,
            p.cuit_cuil,
            p.condicion_impositiva
        FROM auth.usuario u
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN tenant.control_base cb ON cb.id = u.control_base_id
        WHERE u.id = :user_id
    """)

    result = await db.execute(query, {"user_id": user_id})
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "id": str(row[0]),
        "email": row[1],
        "activo": row[2],
        "nombre": row[3] or "",
        "apellido": row[4] or "",
        "telefono": row[5] or "",
        "documento": row[6] or "",
        "direccion": row[7] or "",
        "tenant": {
            "id": str(row[9]) if row[9] else None,
            "nombre": row[8] or ""
        },
        "foto_perfil_url": row[10],
        "codigo_postal": row[11] or "",
        "fecha_nacimiento": str(row[12]) if row[12] else None,
        "ciudad_id": str(row[13]) if row[13] else None,
        "cuit_cuil": row[14] or "",
        "condicion_impositiva": row[15] or ""
    }


@router.put("")
async def update_perfil(
    data: PerfilPropietarioUpdate,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza el perfil del propietario. Todos los campos son opcionales.
    """
    user_id, control_base_id, email, tipo = current_user

    # Verificar que es propietario
    query_verify = text("""
        SELECT id FROM fleet.propietario_vehiculo
        WHERE propietario_id = :user_id AND activo = true
        LIMIT 1
    """)
    result = await db.execute(query_verify, {"user_id": user_id})
    if not result.first():
        raise HTTPException(status_code=403, detail="No eres propietario")

    # Construir UPDATE dinamico con los campos que vienen
    data_dict = data.model_dump(exclude_unset=True)

    if not data_dict:
        return {"success": True, "message": "No hay datos para actualizar"}

    updates = []
    params = {"user_id": user_id}

    for campo, valor in data_dict.items():
        updates.append(f"{campo} = :{campo}")
        params[campo] = valor

    query = text(f"""
        UPDATE auth.perfil_general
        SET {', '.join(updates)},
            updated_at = NOW()
        WHERE usuario_id = :user_id
        RETURNING id
    """)

    result = await db.execute(query, params)
    await db.commit()

    if not result.first():
        return {"success": False, "message": "Perfil no encontrado"}

    return {"success": True, "message": "Perfil actualizado correctamente"}


@router.post("/solicitar-ser-chofer")
async def solicitar_ser_chofer(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Permite al propietario postularse como chofer (auto-gestion).

    Crea una fila en fleet.chofer_vehiculo con estado 'pendiente'.
    No valida datos minimos ni vehiculos: el propietario completa despues.
    Al apretar 'Enviar a revision', se valida todo junto.

    Si ya tiene una postulacion 'rechazada', la inactiva y crea una nueva.
    """
    user_id, control_base_id, email, tipo = current_user

    # 1. Verificar que es propietario
    if tipo.lower() != "propietario":
        raise HTTPException(status_code=403, detail="No eres propietario")

    # 2. Verificar postulacion previa
    query_existente = text("""
        SELECT id, estado_aprobacion FROM fleet.chofer_vehiculo
        WHERE usuario_id = :user_id AND activo = true
    """)
    result = await db.execute(query_existente, {"user_id": user_id})
    row = result.first()

    if row:
        estado = row[1]
        if estado == 'rechazado':
            query_inactivar = text("""
                UPDATE fleet.chofer_vehiculo
                SET activo = false, updated_at = NOW()
                WHERE id = :id
            """)
            await db.execute(query_inactivar, {"id": row[0]})
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Ya tiene una solicitud en estado '{estado}'. No puede crear otra."
            )

    # 3. Crear la nueva fila
    insert = text("""
        INSERT INTO fleet.chofer_vehiculo (
            id, usuario_id, control_base_id, vehiculo_id,
            estado_laboral, estado_aprobacion, activo,
            created_at, updated_at
        )
        VALUES (
            gen_random_uuid(), :user_id, :control_base_id, NULL,
            'fuera_servicio', 'pendiente', true,
            NOW(), NOW()
        )
        RETURNING id
    """)
    result = await db.execute(insert, {
        "user_id": user_id,
        "control_base_id": control_base_id
    })
    chofer_vehiculo_id = result.scalar()
    await db.commit()

    return {
        "success": True,
        "message": "Solicitud iniciada. Puede cargar sus documentos cuando desee.",
        "chofer_vehiculo_id": str(chofer_vehiculo_id)
    }


@router.post("/enviar-a-revision")
async def enviar_a_revision(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Envia a revision los vehiculos y la postulacion como chofer (todo o nada).

    Regla TODO O NADA:
    - TODOS los vehiculos activos deben tener documentacion_completa = true.
    - Si tiene chofer_vehiculo activo: los 5 docs de chofer deben estar completos.
    - Si falla alguna validacion, NO se envia nada (error 400).

    Accion:
    - Vehiculos en estado 'pendiente' con docs completos -> 'en_revision'.
    - chofer_vehiculo activo -> 'en_revision'.
    """
    user_id, control_base_id, email, tipo = current_user

    # 1. Validar propietario
    if tipo.lower() != "propietario":
        raise HTTPException(status_code=403, detail="No eres propietario")

    # 2. Verificar que tenga al menos 1 vehiculo activo
    query_count = text("""
        SELECT COUNT(*) FROM fleet.propietario_vehiculo pv
        JOIN fleet.vehiculo v ON v.id = pv.vehiculo_id
        WHERE pv.propietario_id = :user_id
          AND pv.activo = true
          AND v.activo = true
    """)
    result = await db.execute(query_count, {"user_id": user_id})
    total = result.scalar() or 0

    if total == 0:
        raise HTTPException(
            status_code=400,
            detail="Debe cargar al menos un vehiculo antes de enviar a revision."
        )

    # 3. Verificar que TODOS los vehiculos tengan docs completos
    query_incompletos = text("""
        SELECT v.patente
        FROM fleet.propietario_vehiculo pv
        JOIN fleet.vehiculo v ON v.id = pv.vehiculo_id
        WHERE pv.propietario_id = :user_id
          AND pv.activo = true
          AND v.activo = true
          AND v.documentacion_completa = false
    """)
    result = await db.execute(query_incompletos, {"user_id": user_id})
    incompletos = result.all()

    if incompletos:
        patentes = [r[0] for r in incompletos]
        raise HTTPException(
            status_code=400,
            detail=f"Los siguientes vehiculos tienen documentacion incompleta: {', '.join(patentes)}. Complete o elimine estos vehiculos antes de enviar."
        )

    # 4. Verificar docs del chofer (si tiene postulacion activa)
    query_chofer = text("""
        SELECT id, estado_aprobacion FROM fleet.chofer_vehiculo
        WHERE usuario_id = :user_id AND activo = true
    """)
    result = await db.execute(query_chofer, {"user_id": user_id})
    chofer_row = result.first()

    tiene_postulacion_chofer = chofer_row is not None
    chofer_vehiculo_id = chofer_row[0] if chofer_row else None
    chofer_estado = chofer_row[1] if chofer_row else None

    if tiene_postulacion_chofer and chofer_estado == 'pendiente':
        query_docs = text("""
            SELECT COUNT(DISTINCT tipo_documento)
            FROM fleet.documentos_chofer
            WHERE usuario_id = :user_id
              AND tipo_documento IN ('dni', 'licencia', 'buena_conducta', 'antecedentes', 'sanidad')
        """)
        result = await db.execute(query_docs, {"user_id": user_id})
        docs_count = result.scalar() or 0

        if docs_count < 5:
            raise HTTPException(
                status_code=400,
                detail=f"Debe completar los 5 documentos de chofer. Tiene {docs_count}/5."
            )

    # 5. Actualizar estados
    # 5a. Vehiculos pendientes -> en_revision
    query_upd_veh = text("""
        UPDATE fleet.vehiculo
        SET estado_aprobacion = 'en_revision', updated_at = NOW()
        WHERE id IN (
            SELECT v.id FROM fleet.vehiculo v
            JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
            WHERE pv.propietario_id = :user_id
              AND pv.activo = true
              AND v.activo = true
              AND v.estado_aprobacion = 'pendiente'
              AND v.documentacion_completa = true
        )
    """)
    await db.execute(query_upd_veh, {"user_id": user_id})

    # 5b. Chofer_vehiculo pendiente -> en_revision
    if tiene_postulacion_chofer and chofer_estado == 'pendiente':
        query_upd_chofer = text("""
            UPDATE fleet.chofer_vehiculo
            SET estado_aprobacion = 'en_revision', updated_at = NOW()
            WHERE id = :chofer_id
        """)
        await db.execute(query_upd_chofer, {"chofer_id": chofer_vehiculo_id})

    await db.commit()

    return {
        "success": True,
        "message": "Enviado a revision. El tenant revisara su solicitud.",
        "vehiculos_enviados": total,
        "chofer_enviado": tiene_postulacion_chofer and chofer_estado == 'pendiente'
    }
