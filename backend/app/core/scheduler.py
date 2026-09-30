"""
Background scheduler for TaxIP.

Jobs programados:
- Timeouts de broadcast (cada 5s)
- Reservas programadas (cada 60s)
- Refresco de vista materializada KPIs (cada 1h)
- Limpieza de viajes huerfanos (cada 1h)
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
    """
    Procesa viajes publicados cuyo timeout expiro.
    Llama a manejar_timeout_broadcast para cada uno.
    """
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
    """
    Procesa las reservas cuya fecha_programada ha llegado.
    Convierte el estado de 'programada' a 'pendiente' para que choferes puedan aceptarlas.
    """
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
    """
    Refresca la vista materializada trip.mv_broadcast_kpis.
    """
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
    """
    Procesa notificaciones de vencimiento de documentos.
    """
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
    """
    Detecta y cancela viajes huerfanos.

    Un viaje es huerfano si:
    - estado='en_curso' y iniciado_en < NOW() - 24h
    - estado='aceptado' y aceptado_en < NOW() - 4h

    Solo se consideran viajes con chofer asignado (chofer_id IS NOT NULL),
    porque son los que bloquean el check-out del chofer.

    Efectos:
    - Cancela el viaje.
    - Inserta en historial_estado_viaje.
    - Libera al chofer (libre si tiene turno activo, fuera_servicio si no).
    """
    async with AsyncSessionLocal() as db:
        try:
            # 1. Detectar huerfanos
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
                    (estado = 'en_curso' AND iniciado_en < NOW() - INTERVAL '24 hours')
                    OR
                    (estado = 'aceptado' AND aceptado_en < NOW() - INTERVAL '4 hours')
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

                # 2. Cancelar viaje
                await db.execute(text("""
                    UPDATE trip.viaje_solicitado
                    SET estado = 'cancelado',
                        cancelado_en = NOW(),
                        cancelado_por = 'sistema',
                        motivo_cancelacion = 'Viaje huerfano. Auto-cancelado por scheduler (J17).',
                        updated_at = NOW()
                    WHERE id = :viaje_id
                """), {"viaje_id": viaje_id})

                # 3. Historial
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

                # 4. Liberar chofer
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
# LOOP PRINCIPAL DEL SCHEDULER
# ============================================================

async def scheduler_loop():
    """
    Loop principal que ejecuta todos los jobs.

    Granularidad: 5 segundos (necesario para timeout de broadcast de 50s).
    """
    logger.info("Scheduler iniciado")
    logger.info("   Timeouts broadcast: cada 5s")
    logger.info("   Reservas: cada 60s")
    logger.info("   KPIs: cada 1h")
    logger.info("   Viajes huerfanos: cada 1h")
    logger.info("   Vencimientos: cada 6h")

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