"""
Background scheduler for TaxIP.

Jobs programados:
- Timeouts de broadcast (cada 5s)
- Reservas programadas (cada 60s)
- Refresco de vista materializada KPIs (cada 1h)
- Limpieza de viajes huerfanos (cada 1h)
- Limpieza de turnos colgados (cada 1h)
- Cancelacion de viajes pendientes vencidos (cada 1 min)
- Notificaciones de vencimiento de documentos (cada 6h)
"""
import asyncio
import logging
from datetime import datetime

from sqlalchemy import text

from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


# ============================================================
# JOB 1: TIMEOUTS DE BROADCAST (cada 5s)
# ============================================================

async def procesar_timeouts_broadcast():
    """..."""
    from app.services.broadcast_service import manejar_timeout_broadcast

    async with AsyncSessionLocal() as db:
        result = await db.execute(text("""
            SELECT id
            FROM trip.viaje_solicitado
            WHERE estado = 'publicado'
              AND fecha_expiracion IS NOT NULL
              AND fecha_expiracion <= NOW()
        """))
        viajes = result.all()

        if not viajes:
            return

        logger.info(f"Procesando {len(viajes)} timeouts de broadcast")

        for (viaje_id,) in viajes:
            try:
                resultado = await manejar_timeout_broadcast(db, viaje_id)
                logger.info(f"   Viaje {viaje_id}: {resultado}")
            except Exception as e:
                logger.error(f"   Error procesando timeout {viaje_id}: {e}")


# ============================================================
# JOB 2: RESERVAS PROGRAMADAS (cada 60s)
# ============================================================

async def procesar_reservas():
    """..."""
    async with AsyncSessionLocal() as db:
        query = text("""
            SELECT id, pasajero_id, control_base_id
            FROM trip.viaje_solicitado
            WHERE estado = 'programada'
              AND reserva_procesada = false
              AND fecha_programada <= NOW()
        """)

        result = await db.execute(query)
        reservas = result.all()

        if not reservas:
            return

        logger.info(f"Procesando {len(reservas)} reservas programadas")

        for reserva in reservas:
            reserva_id = reserva[0]
            control_base_id = reserva[2]

            driver_query = text("""
                SELECT cv.id, cv.usuario_id
                FROM fleet.chofer_vehiculo cv
                WHERE cv.control_base_id = :control_base_id
                  AND cv.estado_laboral = 'libre'
                  AND cv.activo = true
                LIMIT 1
            """)

            driver_result = await db.execute(driver_query, {"control_base_id": control_base_id})
            driver_row = driver_result.first()

            if driver_row:
                chofer_vehiculo_id = driver_row[0]
                chofer_id = driver_row[1]

                update_query = text("""
                    UPDATE trip.viaje_solicitado
                    SET estado = 'pendiente',
                        reserva_procesada = true,
                        chofer_id = :chofer_id,
                        vehiculo_id = (SELECT vehiculo_id FROM fleet.chofer_vehiculo WHERE id = :chofer_vehiculo_id),
                        procesado_en = NOW()
                    WHERE id = :reserva_id
                """)

                await db.execute(update_query, {
                    "reserva_id": reserva_id,
                    "chofer_id": chofer_id,
                    "chofer_vehiculo_id": chofer_vehiculo_id,
                })

                update_driver = text("""
                    UPDATE fleet.chofer_vehiculo
                    SET estado_laboral = 'ocupado'
                    WHERE id = :chofer_vehiculo_id
                """)
                await db.execute(update_driver, {"chofer_vehiculo_id": chofer_vehiculo_id})

                logger.info(f"Reserva {reserva_id} procesada - Chofer: {chofer_id}")
            else:
                logger.warning(f"Reserva {reserva_id} - Sin choferes disponibles")

        await db.commit()


# ============================================================
# JOB 3: REFRESCO DE KPIs (cada 1h)
# ============================================================

async def refrescar_mv_broadcast_kpis():
    """..."""
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(text(
                "REFRESH MATERIALIZED VIEW CONCURRENTLY trip.mv_broadcast_kpis"
            ))
            await db.commit()
            logger.info("Vista mv_broadcast_kpis refrescada")
        except Exception as e:
            logger.error(f"Error refrescando KPIs: {e}")


# ============================================================
# JOB 4: NOTIFICACIONES DE VENCIMIENTO (cada 6h)
# ============================================================

async def procesar_notificaciones_vencimiento():
    """..."""
    from app.services.notificacion_vencimiento import NotificacionVencimientoService

    logger.info("Procesando notificaciones de vencimiento de documentos...")

    try:
        async with AsyncSessionLocal() as db:
            service = NotificacionVencimientoService(db)
            resultado = await service.verificar_y_enviar_notificaciones()

            if resultado["enviados"] > 0:
                logger.info(f"Notificaciones enviadas: {resultado['enviados']}")
            else:
                logger.info("No hay notificaciones pendientes")

            if resultado["errores"] > 0:
                logger.warning(f"{resultado['errores']} errores al enviar notificaciones")

    except Exception as e:
        logger.error(f"Error en procesar_notificaciones_vencimiento: {e}")


# ============================================================
# JOB 5: LIMPIEZA DE VIAJES HUERFANOS (cada 1h) -- J17
# ============================================================

async def procesar_viajes_huerfanos():
    """..."""
    async with AsyncSessionLocal() as db:
        try:
            query = text("""
                SELECT
                    id,
                    estado,
                    chofer_id,
                    chofer_vehiculo_id,
                    iniciado_en,
                    aceptado_en
                FROM trip.viaje_solicitado
                WHERE chofer_id IS NOT NULL
                  AND (
                    (estado = 'en_curso' AND iniciado_en < NOW() - INTERVAL '4 hours')
                    OR
                    (estado = 'aceptado' AND aceptado_en < NOW() - INTERVAL '15 minutes')
                  )
            """)
            result = await db.execute(query)
            viajes = result.all()

            if not viajes:
                return

            logger.warning(f"Auto-cancelando {len(viajes)} viajes huerfanos")

            for viaje in viajes:
                viaje_id = viaje[0]
                estado = viaje[1]
                chofer_id = viaje[2]
                chofer_vehiculo_id = viaje[3]
                fecha_ref = viaje[4] if estado == "en_curso" else viaje[5]

                logger.info(
                    f"   Viaje {viaje_id}: estado={estado}, "
                    f"chofer_id={chofer_id}, ref={fecha_ref}"
                )

                await db.execute(text("""
                    UPDATE trip.viaje_solicitado
                    SET estado = 'cancelado',
                        cancelado_en = NOW(),
                        cancelado_por = 'sistema',
                        motivo_cancelacion = 'Viaje huerfano. Auto-cancelado por scheduler (J17).',
                        updated_at = NOW()
                    WHERE id = :viaje_id
                """), {"viaje_id": viaje_id})

                await db.execute(text("""
                    INSERT INTO trip.historial_estado_viaje (
                        id, viaje_id, estado, observacion, created_at
                    ) VALUES (
                        gen_random_uuid(), :viaje_id, 'cancelado',
                        :obs, NOW()
                    )
                """), {
                    "viaje_id": viaje_id,
                    "obs": f"Auto-cancelado por scheduler. Estado previo: {estado}. Referencia: {fecha_ref}.",
                })

                if chofer_vehiculo_id:
                    await db.execute(text("""
                        UPDATE fleet.chofer_vehiculo
                        SET estado_laboral = CASE
                                WHEN EXISTS (
                                    SELECT 1 FROM fleet.turno_chofer
                                    WHERE chofer_id = :chofer_id
                                      AND estado = 'ACTIVO'
                                ) THEN 'libre'
                                ELSE 'fuera_servicio'
                            END,
                            updated_at = NOW()
                        WHERE id = :chofer_vehiculo_id
                    """), {
                        "chofer_id": chofer_id,
                        "chofer_vehiculo_id": chofer_vehiculo_id,
                    })

            await db.commit()
            logger.info(f"Limpieza de huerfanos completada: {len(viajes)} viajes cancelados")

        except Exception as e:
            logger.error(f"Error en procesar_viajes_huerfanos: {e}")
            await db.rollback()


# ============================================================
# JOB 6: LIMPIEZA DE TURNOS COLGADOS (cada 1h) - G64
# ============================================================

async def procesar_turnos_colgados():
    """
    Detecta y cancela turnos colgados.

    Un turno es colgado si:
    - estado='ACTIVO' y inicio_turno < NOW() - 16h

    Un turno normal dura 8-12 horas. Uno excepcional hasta 16 horas.
    16h es claramente abandono.

    Efectos:
    - Marca el turno como CANCELADO.
    - Guarda fin_turno.
    - Libera al chofer (libre si tiene contrato activo, fuera_servicio si no).
    - Notifica al chofer por WebSocket.
    """
    from app.websocket.connection_manager import manager
    from app.websocket.events import EventType

    async with AsyncSessionLocal() as db:
        try:
            # 1. Detectar turnos colgados
            query = text("""
                SELECT id, chofer_id, vehiculo_id, inicio_turno
                FROM fleet.turno_chofer
                WHERE estado = 'ACTIVO'
                  AND inicio_turno < NOW() - INTERVAL '16 hours'
            """)
            result = await db.execute(query)
            turnos = result.all()

            if not turnos:
                return

            logger.warning(f"Auto-cancelando {len(turnos)} turnos colgados")

            for turno in turnos:
                turno_id = turno[0]
                chofer_id = turno[1]
                vehiculo_id = turno[2]
                inicio_turno = turno[3]

                logger.info(
                    f"   Turno {turno_id}: chofer_id={chofer_id}, "
                    f"vehiculo_id={vehiculo_id}, inicio={inicio_turno}"
                )

                # 2. Marcar turno como CANCELADO
                await db.execute(text("""
                    UPDATE fleet.turno_chofer
                    SET estado = 'CANCELADO',
                        fin_turno = NOW(),
                        updated_at = NOW()
                    WHERE id = :turno_id
                """), {"turno_id": turno_id})

                # 3. Verificar si el chofer tiene un contrato activo
                #    Si lo tiene, queda 'libre' (puede iniciar otro turno).
                #    Si no, queda 'fuera_servicio'.
                contrato_query = await db.execute(
                    text("""
                        SELECT 1 FROM fleet.contrato_vehiculo
                        WHERE chofer_id = :chofer_id
                          AND estado_contrato = 'ACTIVO'
                          AND activo = true
                        LIMIT 1
                    """),
                    {"chofer_id": chofer_id},
                )
                tiene_contrato = contrato_query.first() is not None

                estado_laboral = 'libre' if tiene_contrato else 'fuera_servicio'

                await db.execute(text("""
                    UPDATE fleet.chofer_vehiculo
                    SET estado_laboral = :estado,
                        updated_at = NOW()
                    WHERE usuario_id = :chofer_id
                """), {"chofer_id": chofer_id, "estado": estado_laboral})

                # 4. Notificar al chofer por WebSocket
                try:
                    await manager.send_personal(
                        user_id=str(chofer_id),
                        event=getattr(EventType, 'TURNO_CANCELADO', 'turno_cancelado'),
                        data={
                            "turno_id": str(turno_id),
                            "motivo": "turno_colgado",
                            "mensaje": (
                                f"Tu turno fue cancelado automaticamente porque "
                                f"supero las 16 horas de duracion. "
                                f"Inicia un nuevo turno cuando quieras."
                            ),
                        },
                    )
                    logger.info(f"Notificacion de cancelacion enviada al chofer {chofer_id}")
                except Exception as e:
                    logger.warning(
                        f"No se pudo notificar cancelacion de turno {turno_id}: {e}"
                    )

            await db.commit()
            logger.info(
                f"Limpieza de turnos colgados completada: "
                f"{len(turnos)} turnos cancelados"
            )

        except Exception as e:
            logger.error(f"Error en procesar_turnos_colgados: {e}")
            await db.rollback()


# ============================================================
# JOB 7: CANCELACION DE VIAJES PENDIENTES VENCIDOS (cada 1 min)
# ============================================================

async def procesar_pendientes_vencidos():
    """..."""
    async with AsyncSessionLocal() as db:
        try:
            query = text("""
                SELECT id, pasajero_id, control_base_id
                FROM trip.viaje_solicitado
                WHERE estado = 'pendiente'
                  AND chofer_id IS NULL
                  AND created_at < NOW() - INTERVAL '5 minutes'
            """)
            result = await db.execute(query)
            viajes = result.all()

            if not viajes:
                return

            logger.warning(f"Cancelando {len(viajes)} viajes pendientes vencidos (sin moviles)")

            for viaje in viajes:
                viaje_id = viaje[0]
                pasajero_id = viaje[1]

                logger.info(f"   Viaje {viaje_id}: sin moviles disponibles tras 5 min")

                await db.execute(text("""
                    UPDATE trip.viaje_solicitado
                    SET estado = 'cancelado',
                        cancelado_en = NOW(),
                        cancelado_por = 'sistema',
                        motivo_cancelacion = 'sin_moviles_disponibles',
                        updated_at = NOW()
                    WHERE id = :viaje_id
                """), {"viaje_id": viaje_id})

                await db.execute(text("""
                    INSERT INTO trip.historial_estado_viaje (
                        id, viaje_id, estado, observacion, created_at
                    ) VALUES (
                        gen_random_uuid(), :viaje_id, 'cancelado',
                        'Cancelado automaticamente: sin moviles disponibles.',
                        NOW()
                    )
                """), {"viaje_id": viaje_id})

                if pasajero_id:
                    try:
                        from app.websocket.connection_manager import manager
                        from app.websocket.events import EventType

                        await manager.send_personal(
                            user_id=str(pasajero_id),
                            event=getattr(EventType, 'VIAJE_CANCELADO', 'viaje_cancelado'),
                            data={
                                "viaje_id": str(viaje_id),
                                "motivo": "sin_moviles_disponibles",
                                "mensaje": "No hay moviles en la zona. Intenta mas tarde.",
                            }
                        )
                    except Exception as e:
                        logger.warning(f"No se pudo notificar cancelacion al pasajero {pasajero_id}: {e}")

            await db.commit()
            logger.info(f"Limpieza de pendientes completada: {len(viajes)} viajes cancelados")

        except Exception as e:
            logger.error(f"Error en procesar_pendientes_vencidos: {e}")
            await db.rollback()


# ============================================================
# LOOP PRINCIPAL DEL SCHEDULER
# ============================================================

async def scheduler_loop():
    """
    Loop principal que ejecuta todos los jobs.

    Granularidad: 5 segundos (necesario para timeout de broadcast de 50s).
    """
    logger.info("   Scheduler iniciado")
    logger.info("   Timeouts broadcast: cada 5s")
    logger.info("   Reservas: cada 60s")
    logger.info("   KPIs: cada 1h")
    logger.info("   Viajes huerfanos: cada 1h")
    logger.info("   Turnos colgados: cada 1h")
    logger.info("   Vencimientos: cada 6h")
    logger.info("   Pendientes vencidos (sin moviles): cada 60s")

    seconds_counter = 0

    while True:
        try:
            # Cada 5s: timeouts de broadcast
            await procesar_timeouts_broadcast()

            # Cada 60s: reservas programadas
            if seconds_counter % 60 == 0:
                await procesar_reservas()

            # Cada 3600s: refrescar KPIs
            if seconds_counter % 3600 == 0 and seconds_counter > 0:
                await refrescar_mv_broadcast_kpis()

            # Cada 3600s: limpieza de viajes huerfanos (J17)
            if seconds_counter % 3600 == 0 and seconds_counter > 0:
                await procesar_viajes_huerfanos()

            # Cada 60s: cancelacion de pendientes vencidos (sin moviles)
            if seconds_counter % 60 == 0 and seconds_counter > 0:
                await procesar_pendientes_vencidos()

            # Cada 3600s: limpieza de turnos colgados (G64)
            if seconds_counter % 3600 == 0 and seconds_counter > 0:
                await procesar_turnos_colgados()

            # Cada 21600s (6h): notificaciones de vencimiento (solo 6-22hs)
            if seconds_counter % 21600 == 0 and seconds_counter > 0:
                if 6 <= datetime.now().hour <= 22:
                    await procesar_notificaciones_vencimiento()

            seconds_counter += 5

        except Exception as e:
            logger.error(f"Error en scheduler loop: {e}")

        await asyncio.sleep(5)


def start_scheduler():
    """
    LEGACY: funcion original que creaba un nuevo event loop.
    Ya NO se usa. El scheduler se arranca desde lifespan en main.py.
    """
    logger.warning("start_scheduler() esta deprecada. Usar lifespan en main.py")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(scheduler_loop())
    except KeyboardInterrupt:
        logger.info("Scheduler detenido")
    finally:
        loop.close()