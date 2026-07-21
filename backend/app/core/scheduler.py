"""
Background scheduler for processing scheduled rides (reservas anticipadas)
"""

import asyncio
import logging
from datetime import datetime
from sqlalchemy import text
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def procesar_reservas():
    """
    Procesa las reservas cuya fecha_programada ha llegado.
    Convierte el estado de 'programada' a 'pendiente' para que choferes puedan aceptarlas.
    """
    async with AsyncSessionLocal() as db:
        # Buscar reservas que están vencidas y no procesadas
        query = text("""
            SELECT id, pasajero_id, control_base_id, 
                   origen, destino, distancia_metros, precio_estimado
            FROM trip.viaje_solicitado
            WHERE estado = 'programada' 
              AND reserva_procesada = false
              AND fecha_programada <= NOW()
        """)
        
        result = await db.execute(query)
        reservas = result.all()
        
        if reservas:
            logger.info(f"📅 Procesando {len(reservas)} reservas programadas")
            
            for reserva in reservas:
                reserva_id = reserva[0]
                pasajero_id = reserva[1]
                control_base_id = reserva[2]
                
                # Buscar chofer disponible en ese momento (simplificado)
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
                    
                    # Actualizar reserva a pendiente con chofer asignado
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
                        "chofer_vehiculo_id": chofer_vehiculo_id
                    })
                    
                    # Actualizar estado del chofer
                    update_driver = text("""
                        UPDATE fleet.chofer_vehiculo
                        SET estado_laboral = 'ocupado'
                        WHERE id = :chofer_vehiculo_id
                    """)
                    await db.execute(update_driver, {"chofer_vehiculo_id": chofer_vehiculo_id})
                    
                    logger.info(f"✅ Reserva {reserva_id} procesada - Chofer asignado: {chofer_id}")
                    
                    # TODO: Enviar notificación push al pasajero y chofer
                    
                else:
                    # No hay chofer disponible, mantener como programada y reintentar después
                    logger.warning(f"⚠️ Reserva {reserva_id} - No hay choferes disponibles, reintentando más tarde")
        
        await db.commit()


async def scheduler_loop():
    """
    Loop infinito que ejecuta procesar_reservas cada 60 segundos
    """
    logger.info("🕐 Scheduler de reservas iniciado - Revisando cada 60 segundos")
    
    while True:
        try:
            await procesar_reservas()
        except Exception as e:
            logger.error(f"❌ Error en scheduler: {e}")
        
        # Esperar 60 segundos antes de la próxima ejecución
        await asyncio.sleep(60)


def start_scheduler():
    """
    Función para iniciar el scheduler en segundo plano
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(scheduler_loop())
    except KeyboardInterrupt:
        logger.info("🛑 Scheduler detenido")
    finally:
        loop.close()