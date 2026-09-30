"""
Trip Service - Centraliza toda la lógica de gestión de viajes
Elimina SQL directo de routers y unifica el ciclo de vida del viaje
"""
import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, text
from sqlalchemy.orm import selectinload

from app.models.trip import ViajeSolicitado, HistorialEstadoViaje, Reserva
from app.models.fleet import ChoferVehiculo
from app.models.turno import TurnoChofer
from app.models.auth import Usuario
from app.models.public import Comercio
from app.models.tenant import Empresa
from app.schemas.trip_schemas import (
    ViajeCreate,
    ViajeUpdate,
    ViajeResponse,
    ViajeAceptar,
    ViajeIniciar,
    ViajeFinalizar,
    ViajeCancelar,
    ViajeListFilter
)
from app.core.exceptions import (
    TripNotFoundError,
    TripInvalidStateError,
    TripPermissionError,
    TripDriverNotAvailableError
)

logger = logging.getLogger(__name__)

class TripService:
    """
    Servicio centralizado para la gestión de viajes
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # CRUD BÁSICO
    # ============================================================

    async def crear_viaje(self, data: ViajeCreate) -> ViajeSolicitado:
        """
        Crear un nuevo viaje
        """
        # Validar que el pasajero existe
        pasajero = await self.db.get(Usuario, data.pasajero_id)
        if not pasajero:
            raise TripPermissionError("Pasajero no encontrado")

        # Validar control_base
        if data.control_base_id:
            query = text("SELECT id FROM tenant.control_base WHERE id = :id AND activo = true")
            result = await self.db.execute(query, {"id": data.control_base_id})
            if not result.first():
                raise TripPermissionError("Tenant no válido o inactivo")

        # Crear viaje
        viaje = ViajeSolicitado(
            id=uuid.uuid4(),
            control_base_id=data.control_base_id,
            pasajero_id=data.pasajero_id,
            direccion_origen=data.direccion_origen,
            direccion_destino=data.direccion_destino,
            estado="pendiente",
            precio_estimado=data.precio_estimado,
            moneda=data.moneda or "ARS",
            tiempo_estimado_segundos=data.tiempo_estimado_segundos,
            distancia_metros=data.distancia_metros,
            fecha_programada=data.fecha_programada,
            comercio_id=data.comercio_id,
            empresa_id=data.empresa_id,
            nombre_pasajero=data.nombre_pasajero,
            notas=data.notas,
            solicitado_en=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.db.add(viaje)
        await self.db.flush()

        # Registrar historial
        await self._registrar_historial(viaje.id, "pendiente")

        await self.db.commit()
        await self.db.refresh(viaje)

        return viaje

    async def get_viaje(self, viaje_id: UUID) -> Optional[ViajeSolicitado]:
        """
        Obtener un viaje por ID
        """
        query = select(ViajeSolicitado).where(
            ViajeSolicitado.id == viaje_id
        ).options(
            selectinload(ViajeSolicitado.pasajero),
            selectinload(ViajeSolicitado.chofer),
            selectinload(ViajeSolicitado.vehiculo),
            selectinload(ViajeSolicitado.turno),
            selectinload(ViajeSolicitado.historial_estados)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_viajes(self, filters: ViajeListFilter) -> List[ViajeSolicitado]:
        """
        Listar viajes con filtros
        """
        query = select(ViajeSolicitado)

        if filters.control_base_id:
            query = query.where(ViajeSolicitado.control_base_id == filters.control_base_id)
        if filters.pasajero_id:
            query = query.where(ViajeSolicitado.pasajero_id == filters.pasajero_id)
        if filters.chofer_id:
            query = query.where(ViajeSolicitado.chofer_id == filters.chofer_id)
        if filters.estado:
            query = query.where(ViajeSolicitado.estado == filters.estado)
        if filters.fecha_desde:
            query = query.where(ViajeSolicitado.solicitado_en >= filters.fecha_desde)
        if filters.fecha_hasta:
            query = query.where(ViajeSolicitado.solicitado_en <= filters.fecha_hasta)

        query = query.order_by(ViajeSolicitado.solicitado_en.desc())

        if filters.limit:
            query = query.limit(filters.limit)
        if filters.offset:
            query = query.offset(filters.offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_viaje(self, viaje_id: UUID, data: ViajeUpdate) -> ViajeSolicitado:
        """
        Actualizar un viaje
        """
        viaje = await self.get_viaje(viaje_id)
        if not viaje:
            raise TripNotFoundError(f"Viaje {viaje_id} no encontrado")

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(viaje, key, value)

        viaje.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(viaje)

        return viaje

    # ============================================================
    # CICLO DE VIDA DEL VIAJE
    # ============================================================

    async def aceptar_viaje(self, viaje_id: UUID, data: ViajeAceptar) -> ViajeSolicitado:
        """
        Aceptar un viaje por un chofer
        """
        viaje = await self.get_viaje(viaje_id)
        if not viaje:
            raise TripNotFoundError(f"Viaje {viaje_id} no encontrado")

        if viaje.estado != "pendiente":
            raise TripInvalidStateError(f"No se puede aceptar un viaje en estado {viaje.estado}")

        # Validar que el chofer existe
        chofer = await self.db.get(Usuario, data.chofer_id)
        if not chofer:
            raise TripPermissionError("Chofer no encontrado")

        # Validar disponibilidad del chofer
        disponibilidad = await self._verificar_disponibilidad_chofer(data.chofer_id)
        if not disponibilidad:
            raise TripDriverNotAvailableError("Chofer no disponible")

        # Asignar chofer y vehículo
        viaje.chofer_id = data.chofer_id
        viaje.vehiculo_id = data.vehiculo_id
        viaje.chofer_vehiculo_id = data.chofer_vehiculo_id
        viaje.estado = "aceptado"
        viaje.aceptado_en = datetime.now()
        viaje.updated_at = datetime.now()

        await self.db.flush()
        await self._registrar_historial(viaje.id, "aceptado")

        await self.db.commit()
        await self.db.refresh(viaje)

        return viaje

    async def iniciar_viaje(self, viaje_id: UUID, data: ViajeIniciar) -> ViajeSolicitado:
        """
        Iniciar un viaje (pasajero a bordo)
        """
        viaje = await self.get_viaje(viaje_id)
        if not viaje:
            raise TripNotFoundError(f"Viaje {viaje_id} no encontrado")

        if viaje.estado != "aceptado":
            raise TripInvalidStateError(f"No se puede iniciar un viaje en estado {viaje.estado}")

        viaje.estado = "en_curso"
        viaje.iniciado_en = datetime.now()
        viaje.updated_at = datetime.now()

        await self.db.flush()
        await self._registrar_historial(viaje.id, "en_curso")

        await self.db.commit()
        await self.db.refresh(viaje)

        return viaje

    async def finalizar_viaje(self, viaje_id: UUID, data: ViajeFinalizar) -> ViajeSolicitado:
        """
        Finalizar un viaje
        """
        viaje = await self.get_viaje(viaje_id)
        if not viaje:
            raise TripNotFoundError(f"Viaje {viaje_id} no encontrado")

        if viaje.estado != "en_curso":
            raise TripInvalidStateError(f"No se puede finalizar un viaje en estado {viaje.estado}")

        viaje.estado = "finalizado"
        viaje.finalizado_en = datetime.now()
        viaje.finalizado_at = datetime.now()
        if data.precio_final:
            viaje.precio_final = data.precio_final
        viaje.updated_at = datetime.now()

        await self.db.flush()
        await self._registrar_historial(viaje.id, "finalizado")

        await self.db.commit()
        await self.db.refresh(viaje)

        return viaje

    async def cancelar_viaje(self, viaje_id: UUID, data: ViajeCancelar) -> ViajeSolicitado:
        """
        Cancelar un viaje
        """
        viaje = await self.get_viaje(viaje_id)
        if not viaje:
            raise TripNotFoundError(f"Viaje {viaje_id} no encontrado")

        if viaje.estado in ["finalizado", "cancelado"]:
            raise TripInvalidStateError(f"No se puede cancelar un viaje en estado {viaje.estado}")

        viaje.estado = "cancelado"
        viaje.cancelado_en = datetime.now()
        viaje.cancelado_por = data.cancelado_por
        viaje.motivo_cancelacion = data.motivo
        viaje.updated_at = datetime.now()

        await self.db.flush()
        await self._registrar_historial(viaje.id, "cancelado", data.motivo)

        await self.db.commit()
        await self.db.refresh(viaje)

        return viaje

    # ============================================================
    # MÉTODOS PRIVADOS
    # ============================================================

    async def _registrar_historial(
        self,
        viaje_id: UUID,
        estado: str,
        observacion: Optional[str] = None
    ) -> None:
        """
        Registrar un cambio de estado en el historial
        """
        historial = HistorialEstadoViaje(
            id=uuid.uuid4(),
            viaje_id=viaje_id,
            estado=estado,
            observacion=observacion,
            created_at=datetime.now()
        )
        self.db.add(historial)

    async def _verificar_disponibilidad_chofer(self, chofer_id: UUID) -> bool:
        """
        Verificar si un chofer está disponible para tomar un viaje
        """
        query = select(ChoferVehiculo).where(
            and_(
                ChoferVehiculo.usuario_id == chofer_id,
                ChoferVehiculo.activo == True,
                ChoferVehiculo.estado_laboral == "libre"
            )
        )
        result = await self.db.execute(query)
        return result.first() is not None

    # ============================================================
    # MÉTODOS PARA RESERVAS
    # ============================================================

    async def crear_reserva(self, data: dict) -> Reserva:
        """
        Crear una reserva corporativa
        """
        reserva = Reserva(
            id=uuid.uuid4(),
            empresa_id=data.get("empresa_id"),
            empleado_id=data.get("empleado_id"),
            turno_id=data.get("turno_id"),
            pasajero_nombre=data.get("pasajero_nombre"),
            pasajero_telefono=data.get("pasajero_telefono"),
            direccion_origen=data.get("direccion_origen"),
            latitud_origen=data.get("latitud_origen"),
            longitud_origen=data.get("longitud_origen"),
            direccion_destino=data.get("direccion_destino"),
            latitud_destino=data.get("latitud_destino"),
            longitud_destino=data.get("longitud_destino"),
            paradas_intermedias=data.get("paradas_intermedias", []),
            tipo_vehiculo=data.get("tipo_vehiculo", "standard"),
            nota_conductor=data.get("nota_conductor"),
            estado="reservado",
            es_programado=data.get("es_programado", False),
            fecha_programada=data.get("fecha_programada"),
            distancia_estimada_km=data.get("distancia_estimada_km"),
            tiempo_estimado_minutos=data.get("tiempo_estimado_minutos"),
            precio_estimado=data.get("precio_estimado"),
            metodo_pago=data.get("metodo_pago", "vehiculo"),
            cantidad_pasajeros=data.get("cantidad_pasajeros", 1),
            cantidad_equipaje=data.get("cantidad_equipaje", 0),
            centro_costo=data.get("centro_costo"),
            creado_por=data.get("creado_por"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.db.add(reserva)
        await self.db.commit()
        await self.db.refresh(reserva)

        return reserva

    async def procesar_reserva(self, reserva_id: UUID) -> ViajeSolicitado:
        """
        Procesar una reserva y convertirla en un viaje
        """
        reserva = await self.db.get(Reserva, reserva_id)
        if not reserva:
            raise TripNotFoundError(f"Reserva {reserva_id} no encontrada")

        if reserva.estado != "reservado":
            raise TripInvalidStateError(f"No se puede procesar una reserva en estado {reserva.estado}")

        # Crear viaje desde la reserva
        viaje = ViajeSolicitado(
            id=uuid.uuid4(),
            control_base_id=reserva.empresa.control_base_id if reserva.empresa else None,
            pasajero_id=reserva.creado_por,
            direccion_origen=reserva.direccion_origen,
            direccion_destino=reserva.direccion_destino,
            estado="pendiente",
            precio_estimado=reserva.precio_estimado,
            moneda="ARS",
            empresa_id=reserva.empresa_id,
            nombre_pasajero=reserva.pasajero_nombre,
            notas=reserva.nota_conductor,
            solicitado_en=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.db.add(viaje)
        await self.db.flush()

        # Actualizar reserva
        reserva.estado = "procesado"
        reserva.updated_at = datetime.now()

        await self._registrar_historial(viaje.id, "pendiente")

        await self.db.commit()
        await self.db.refresh(viaje)

        return viaje

    # ============================================================
    # METODOS ATOMICOS M3 (broadcast + concurrencia)
    # ============================================================

    async def marcar_viaje_publicado(
        self,
        viaje_id: UUID,
        radio_metros: int = 2000,
    ) -> Optional[ViajeSolicitado]:
        """
        Marca un viaje como publicado (listo para broadcast).
        Se llama desde broadcast_service antes de enviar a choferes.
        """
        result = await self.db.execute(
            text("""
                UPDATE trip.viaje_solicitado
                SET estado = 'publicado',
                    fecha_publicacion = COALESCE(fecha_publicacion, NOW()),
                    fecha_expiracion = NOW() + INTERVAL '50 seconds',
                    radio_broadcast_metros = :radio,
                    updated_at = NOW()
                WHERE id = :viaje_id
                  AND estado IN ('pendiente', 'publicado')
                RETURNING id
            """),
            {"viaje_id": viaje_id, "radio": radio_metros},
        )
        row = result.first()

        if not row:
            return None

        await self._registrar_historial(viaje_id, "publicado")
        await self.db.commit()

        return await self.get_viaje(viaje_id)

    async def aceptar_viaje_atomico(
        self,
        viaje_id: UUID,
        chofer_id: UUID,
        vehiculo_id: UUID,
        chofer_vehiculo_id: UUID,
    ) -> Optional[ViajeSolicitado]:
        """
        Acepta un viaje de forma ATOMICA (concurrencia segura).
        """
        result = await self.db.execute(
            text("""
                UPDATE trip.viaje_solicitado
                SET estado = 'aceptado',
                    chofer_id = :chofer_id,
                    vehiculo_id = :vehiculo_id,
                    chofer_vehiculo_id = :chofer_vehiculo_id,
                    aceptado_en = NOW(),
                    updated_at = NOW()
                WHERE id = :viaje_id
                  AND estado = 'publicado'
                  AND chofer_id IS NULL
                RETURNING id
            """),
            {
                "viaje_id": viaje_id,
                "chofer_id": chofer_id,
                "vehiculo_id": vehiculo_id,
                "chofer_vehiculo_id": chofer_vehiculo_id,
            },
        )
        row = result.first()

        if not row:
            await self.db.rollback()
            logger.info(
                f"TripService: chofer {chofer_id} perdio carrera por viaje {viaje_id}"
            )
            return None

        await self._registrar_historial(viaje_id, "aceptado")
        await self.db.commit()

        return await self.get_viaje(viaje_id)