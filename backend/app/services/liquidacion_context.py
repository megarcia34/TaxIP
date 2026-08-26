# app/services/liquidacion_context.py
"""
Contexto de liquidación: carga y valida los hechos necesarios
CON HORARIOS FLEXIBLES Y CAMPOS DE ALQUILER
AHORA CON INGRESO_TURNO - Reemplaza campos legacy de recaudación
"""

from uuid import UUID
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import json

from app.models.turno import TurnoChofer
from app.models.fleet import ContratoVehiculo, PropietarioVehiculo, GastoVehiculo, IngresoTurno
from app.models.trip import ViajeSolicitado
from app.models.gasto_turno import GastoTurno
from app.schemas.liquidacion import LiquidacionContextSchema
from app.core.exceptions import LiquidacionError
from app.core.validaciones_compartidas import calcular_duracion_horas


class LiquidacionContext:
    """
    Carga y valida todos los hechos necesarios para una liquidación.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def cargar(self, turno_id: UUID) -> LiquidacionContextSchema:
        """
        Carga el contexto completo para un turno dado.
        """
        # 1. Cargar turno
        turno = await self.db.get(TurnoChofer, turno_id)
        if not turno:
            raise LiquidacionError(f"Turno no encontrado: {turno_id}")

        # 2. Cargar contrato
        contrato = await self.db.get(ContratoVehiculo, turno.contrato_id)
        if not contrato:
            raise LiquidacionError(f"Contrato no encontrado para turno {turno_id}")

        # 3. Obtener propietario del vehículo
        propietario_id = await self._obtener_propietario(turno.vehiculo_id)

        # 4. Cargar viajes asociados al turno
        viajes = await self._cargar_viajes(turno_id)

        # 5. Cargar gastos del turno
        gastos_turno = await self._cargar_gastos_turno(turno_id)

        # 6. Cargar gastos del vehículo en el período del turno
        gastos_vehiculo = await self._cargar_gastos_vehiculo(
            vehiculo_id=turno.vehiculo_id,
            desde=turno.inicio_turno,
            hasta=turno.fin_turno or datetime.now()
        )

        # 7. Validar tenant
        control_base_id = turno.vehiculo.control_base_id if turno.vehiculo else None
        if not control_base_id:
            raise LiquidacionError("El turno no tiene control_base_id asociado")

        # ============================================================
        # NUEVO: CARGAR INGRESOS DESDE INGRESO_TURNO
        # ============================================================

        # 8. Cargar ingresos aprobados del turno
        ingresos = await self._cargar_ingresos_turno(turno_id)

        # 9. Calcular totales por tipo de ingreso
        total_ingresos_aprobados = Decimal(0)
        total_efectivo = Decimal(0)
        total_electronico = Decimal(0)
        total_taximetro = Decimal(0)
        total_manual = Decimal(0)
        total_corporativo = Decimal(0)

        for ingreso in ingresos:
            monto = ingreso.monto or Decimal(0)
            total_ingresos_aprobados += monto

            if ingreso.tipo_ingreso == "efectivo":
                total_efectivo += monto
            elif ingreso.tipo_ingreso == "electronico":
                total_electronico += monto
            elif ingreso.tipo_ingreso == "taximetro":
                total_taximetro += monto
            elif ingreso.tipo_ingreso == "manual":
                total_manual += monto
            elif ingreso.tipo_ingreso == "corporativo":
                total_corporativo += monto

        # ============================================================
        # FUENTE DE VERDAD: SOLO INGRESO_TURNO
        # ============================================================
        recaudacion_ticketera = total_taximetro + total_manual
        recaudacion_efectivo = total_efectivo
        recaudacion_electronico = total_electronico + total_corporativo
        total_recaudacion = total_ingresos_aprobados

        # ============================================================
        # DATOS DEL TURNO
        # ============================================================

        km_inicial = turno.km_inicial
        km_final = turno.km_final

        # Calcular kilómetros recorridos
        km_recorridos = Decimal(0)
        if km_inicial is not None and km_final is not None:
            km_recorridos = Decimal(str(km_final - km_inicial))

        # ============================================================
        # DATOS DEL CONTRATO (ALQUILER)
        # ============================================================

        canon_diario = contrato.canon_diario
        km_incluidos_dia = contrato.km_incluidos_dia
        valor_km_excedente = contrato.valor_km_excedente
        modalidad_computo = contrato.modalidad_computo or 'DIARIO'
        tratamiento_dia_no_trabajado = contrato.tratamiento_dia_no_trabajado or 'POR_DISPONIBILIDAD'
        
        # Obtener días contractuales
        dias_contractuales = contrato.dias_contractuales
        if isinstance(dias_contractuales, str):
            try:
                dias_contractuales = json.loads(dias_contractuales)
            except:
                dias_contractuales = []
        elif not isinstance(dias_contractuales, list):
            dias_contractuales = []

        # ============================================================
        # HORARIOS FLEXIBLES
        # ============================================================

        hora_inicio = contrato.hora_inicio.strftime("%H:%M") if contrato.hora_inicio else None
        hora_fin = contrato.hora_fin.strftime("%H:%M") if contrato.hora_fin else None
        hora_fin_extension = contrato.hora_fin_extension.strftime("%H:%M") if contrato.hora_fin_extension else None
        duracion_minima_horas = contrato.duracion_minima_horas
        permite_extension = contrato.permite_extension
        dia_inicio_semana = contrato.dia_inicio_semana

        # Calcular duración del turno (horas trabajadas)
        duracion_turno_horas = Decimal(0)
        if turno.inicio_turno and turno.fin_turno:
            diff = turno.fin_turno - turno.inicio_turno
            duracion_turno_horas = Decimal(str(diff.total_seconds() / 3600))
        elif turno.inicio_turno:
            diff = datetime.now() - turno.inicio_turno
            duracion_turno_horas = Decimal(str(diff.total_seconds() / 3600))

        # Calcular días del turno
        dias_turno = self._calcular_dias_turno(turno.inicio_turno, turno.fin_turno)
        
        # Calcular días trabajados contractualmente
        dias_trabajados = self._calcular_dias_trabajados(
            dias_turno=dias_turno,
            dias_contractuales=dias_contractuales,
            tratamiento=tratamiento_dia_no_trabajado,
            turno_id=turno_id
        )

        # Calcular km incluidos totales según modalidad
        km_incluidos_totales = self._calcular_km_incluidos_totales(
            km_incluidos_dia=km_incluidos_dia,
            dias_trabajados=dias_trabajados,
            modalidad=modalidad_computo,
            dias_contractuales=dias_contractuales,
            dia_inicio_semana=dia_inicio_semana,
            turno_id=turno_id
        )

        # Calcular km excedentes
        km_excedentes = Decimal(0)
        cargo_km_excedentes = Decimal(0)
        if km_incluidos_totales is not None and km_recorridos > km_incluidos_totales:
            km_excedentes = km_recorridos - km_incluidos_totales
            if valor_km_excedente is not None:
                cargo_km_excedentes = km_excedentes * Decimal(str(valor_km_excedente))

        # Calcular canon según días trabajados
        canon_calculado = Decimal(0)
        if canon_diario is not None and dias_trabajados > 0:
            canon_calculado = Decimal(str(canon_diario)) * Decimal(str(dias_trabajados))

        # ============================================================
        # FILTRAR INGRESOS CON MONTO > 0
        # ============================================================
        ingresos_filtrados = []
        for ing in ingresos:
            if ing.monto and ing.monto > 0:
                ingresos_filtrados.append(self._ingreso_to_dict(ing))

        # ============================================================
        # CONSTRUIR CONTEXTO
        # ============================================================

        contexto = LiquidacionContextSchema(
            turno_id=turno.id,
            contrato_id=contrato.id,
            vehiculo_id=turno.vehiculo_id,
            chofer_id=turno.chofer_id,
            propietario_id=propietario_id,
            control_base_id=control_base_id,
            tipo_contrato=contrato.tipo_contrato,
            fecha_inicio=turno.inicio_turno,
            fecha_fin=turno.fin_turno or datetime.now(),
            viajes=[self._viaje_to_dict(v) for v in viajes],
            gastos_turno=[self._gasto_turno_to_dict(g) for g in gastos_turno],
            gastos_vehiculo=[self._gasto_vehiculo_to_dict(g) for g in gastos_vehiculo],
            
            # PORCENTAJE - USANDO NUEVOS INGRESOS
            porcentaje_chofer=contrato.porcentaje_chofer,
            recaudacion_ticketera=recaudacion_ticketera,
            
            # ALQUILER
            canon_diario=canon_diario,
            canon_calculado=canon_calculado,
            km_inicial=km_inicial,
            km_final=km_final,
            km_recorridos=km_recorridos,
            km_incluidos_dia=km_incluidos_dia,
            km_incluidos_totales=km_incluidos_totales,
            km_excedentes=km_excedentes,
            cargo_km_excedentes=cargo_km_excedentes,
            valor_km_excedente=valor_km_excedente,
            modalidad_computo=modalidad_computo,
            dias_contractuales=dias_contractuales,
            dias_trabajados=dias_trabajados,
            tratamento_dia_no_trabajado=tratamiento_dia_no_trabajado,
            
            # HORARIOS FLEXIBLES
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            duracion_minima_horas=duracion_minima_horas,
            permite_extension=permite_extension,
            hora_fin_extension=hora_fin_extension,
            dia_inicio_semana=dia_inicio_semana,
            duracion_turno_horas=duracion_turno_horas,
            
            # NUEVO: INGRESOS DETALLADOS (SOLO CON MONTO > 0)
            ingresos=ingresos_filtrados,
            total_ingresos_aprobados=total_ingresos_aprobados,
            total_efectivo=total_efectivo,
            total_electronico=total_electronico,
            total_taximetro=total_taximetro,
            total_manual=total_manual,
            total_corporativo=total_corporativo
        )

        return contexto

    # ============================================================
    # MÉTODOS PRIVADOS
    # ============================================================

    async def _obtener_propietario(self, vehiculo_id: UUID) -> UUID:
        """Obtiene el propietario activo del vehículo"""
        query = select(PropietarioVehiculo).where(
            and_(
                PropietarioVehiculo.vehiculo_id == vehiculo_id,
                PropietarioVehiculo.activo == True
            )
        ).limit(1)
        result = await self.db.execute(query)
        prop = result.scalar_one_or_none()
        if not prop:
            raise LiquidacionError(f"No se encontró propietario activo para vehículo {vehiculo_id}")
        return prop.propietario_id

    async def _cargar_viajes(self, turno_id: UUID) -> List[ViajeSolicitado]:
        """Carga viajes asociados al turno mediante turno_id"""
        query = select(ViajeSolicitado).where(
            and_(
                ViajeSolicitado.turno_id == turno_id,
                ViajeSolicitado.estado == 'finalizado'
            )
        ).order_by(ViajeSolicitado.finalizado_en)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def _cargar_gastos_turno(self, turno_id: UUID) -> List[GastoTurno]:
        """Carga gastos asociados al turno"""
        query = select(GastoTurno).where(GastoTurno.turno_id == turno_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def _cargar_gastos_vehiculo(self, vehiculo_id: UUID, desde: datetime, hasta: datetime) -> List[GastoVehiculo]:
        """Carga gastos del vehículo en el período del turno"""
        query = select(GastoVehiculo).where(
            and_(
                GastoVehiculo.vehiculo_id == vehiculo_id,
                GastoVehiculo.fecha_gasto >= desde.date(),
                GastoVehiculo.fecha_gasto <= hasta.date()
            )
        ).order_by(GastoVehiculo.fecha_gasto)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def _cargar_ingresos_turno(self, turno_id: UUID) -> List[IngresoTurno]:
        """
        Carga los ingresos aprobados del turno desde IngresoTurno
        """
        query = select(IngresoTurno).where(
            and_(
                IngresoTurno.turno_id == turno_id,
                IngresoTurno.estado == "aprobado"
            )
        ).order_by(IngresoTurno.fecha_hora)
        result = await self.db.execute(query)
        return result.scalars().all()

    def _viaje_to_dict(self, viaje: ViajeSolicitado) -> Dict[str, Any]:
        return {
            "id": viaje.id,
            "precio_final": viaje.precio_final or Decimal(0),
            "estado": viaje.estado,
            "finalizado_en": viaje.finalizado_en,
            "vehiculo_id": viaje.vehiculo_id,
            "chofer_id": viaje.chofer_id,
            "control_base_id": viaje.control_base_id,
        }

    def _gasto_turno_to_dict(self, gasto: GastoTurno) -> Dict[str, Any]:
        return {
            "id": gasto.id,
            "monto": gasto.monto,
            "tipo_gasto": gasto.tipo_gasto,
            "categoria_id": gasto.categoria_id,
            "subcategoria": gasto.subcategoria,
            "km_registro": gasto.km_registro,
            "created_at": gasto.created_at,
        }

    def _gasto_vehiculo_to_dict(self, gasto: GastoVehiculo) -> Dict[str, Any]:
        return {
            "id": gasto.id,
            "monto": gasto.monto,
            "tipo_gasto": gasto.tipo_gasto,
            "categoria_id": gasto.categoria_id,
            "subcategoria": gasto.subcategoria,
            "km_registro": gasto.km_registro,
            "fecha_gasto": gasto.fecha_gasto,
            "descripcion": gasto.descripcion,
            "comprobante_url": gasto.comprobante_url,
        }

    def _ingreso_to_dict(self, ingreso: IngresoTurno) -> Dict[str, Any]:
        """Convierte un ingreso a diccionario para el contexto"""
        return {
            "id": ingreso.id,
            "tipo_ingreso": ingreso.tipo_ingreso,
            "medio_pago": ingreso.medio_pago,
            "origen": ingreso.origen,
            "monto": ingreso.monto or Decimal(0),
            "moneda": ingreso.moneda,
            "fecha_hora": ingreso.fecha_hora,
            "estado": ingreso.estado,
            "viaje_id": ingreso.viaje_id,
            "referencia_pago": ingreso.referencia_pago,
        }

    def _calcular_dias_turno(self, inicio: datetime, fin: Optional[datetime] = None) -> int:
        """
        Calcula la cantidad de días que abarca el turno.
        """
        if fin is None:
            fin = datetime.now()
        diff = fin - inicio
        return max(1, diff.days + 1)

    def _calcular_dias_trabajados(
        self,
        dias_turno: int,
        dias_contractuales: List[str],
        tratamiento: str,
        turno_id: UUID
    ) -> int:
        """
        Calcula cuántos días del turno son contractuales según el tratamiento.
        """
        if not dias_contractuales:
            return dias_turno

        if tratamiento == "POR_DISPONIBILIDAD":
            return dias_turno
        elif tratamiento == "POR_USO_EFECTIVO":
            return dias_turno if dias_turno > 0 else 0
        else:
            return dias_turno

    def _calcular_km_incluidos_totales(
        self,
        km_incluidos_dia: Optional[Decimal],
        dias_trabajados: int,
        modalidad: str,
        dias_contractuales: List[str],
        dia_inicio_semana: Optional[str],
        turno_id: UUID
    ) -> Optional[Decimal]:
        """
        Calcula los kilómetros incluidos totales según modalidad.
        """
        if km_incluidos_dia is None:
            return None

        if modalidad == "DIARIO":
            return km_incluidos_dia * Decimal(str(dias_trabajados))
        
        elif modalidad == "SEMANAL":
            dias_semana = len(dias_contractuales) if dias_contractuales else 7
            return km_incluidos_dia * Decimal(str(dias_semana))
        
        else:
            return km_incluidos_dia * Decimal(str(dias_trabajados))