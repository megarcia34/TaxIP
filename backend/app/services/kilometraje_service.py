"""
KilometrajeService: fuente unica de verdad del km actual del vehiculo.

Extrae la logica de propietario/mantenimientos.py legacy, con mejoras de R25:
- Considera turnos ACTIVO, CONCILIADO, CONCILIADO_AUTOMATICO, CERRADO,
  LIQUIDADO, PENDIENTE_CONFIRMACION.
- Detecta stale (ultimo turno cerrado > stale_dias).
- Detecta coherencia (km retrocede, salto anormal).
- Devuelve metadata (fuente, confiable, vigente, advertencias).

Read-only. No persiste nada. Los llamadores (MantenimientoEngine, endpoints)
deciden que hacer con el resultado.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.turno import TurnoChofer
from app.models.fleet import MantenimientoVehiculo, GastoVehiculo


@dataclass
class LecturaKilometraje:
    """Resultado de obtener_km_actual."""
    km_actual: int
    fuente: str  # turno_activo | conciliado | cerrado | pendiente_confirmacion | legacy | gasto | cero
    confiable: bool
    vigente: bool
    fecha_lectura: datetime
    turno_id: Optional[UUID]
    advertencias: List[str] = field(default_factory=list)
    requiere_verificacion: bool = False


class KilometrajeService:
    """Servicio de kilometraje. Read-only."""

    STALE_DIAS_DEFAULT = 7
    SALTO_ANORMAL_PCT = 0.50  # 50%

    # Estados de turno por prioridad (mayor a menor confiabilidad)
    ESTADOS_PRIORIDAD = [
        ("ACTIVO", "turno_activo", True),
        ("CONCILIADO", "conciliado", True),
        ("CONCILIADO_AUTOMATICO", "conciliado", True),
        ("CERRADO", "cerrado", True),
        ("LIQUIDADO", "cerrado", True),
        ("PENDIENTE_CONFIRMACION", "pendiente_confirmacion", False),
    ]

    @staticmethod
    async def obtener_km_actual(
        db: AsyncSession,
        vehiculo_id: UUID,
        stale_dias: int = STALE_DIAS_DEFAULT,
    ) -> LecturaKilometraje:
        """
        Obtiene el km actual del vehiculo con la jerarquia de fuentes.

        Orden:
        1. Turno ACTIVO -> km_inicial (confiable, vigente)
        2. Turno CONCILIADO / CONCILIADO_AUTOMATICO -> km_final (confiable, vigente)
        3. Turno CERRADO / LIQUIDADO -> km_final (confiable, vigente)
        4. Turno PENDIENTE_CONFIRMACION -> km_final (no confiable, vigente)
        5. Legacy mantenimiento_vehiculo -> kilometraje (no confiable)
        6. gasto_vehiculo -> km_registro (no confiable)
        7. 0 con stale=true
        """
        # 1-4: Turnos (prioridad por estado)
        for estado, fuente, confiable in KilometrajeService.ESTADOS_PRIORIDAD:
            query = (
                select(TurnoChofer)
                .where(
                    TurnoChofer.vehiculo_id == vehiculo_id,
                    TurnoChofer.estado == estado,
                )
                .order_by(desc(TurnoChofer.inicio_turno))
                .limit(1)
            )
            result = await db.execute(query)
            turno = result.scalar_one_or_none()
            if turno:
                km = turno.km_inicial if estado == "ACTIVO" else turno.km_final
                if km is None:
                    km = turno.km_inicial or 0
                fecha = (
                    turno.inicio_turno
                    if estado == "ACTIVO"
                    else (turno.fin_turno or turno.inicio_turno)
                )
                vigente = (datetime.now() - fecha) <= timedelta(days=stale_dias)
                advertencias = []
                if not vigente:
                    dias = (datetime.now() - fecha).days
                    advertencias.append(f"Turno cerrado hace {dias} dias")
                return LecturaKilometraje(
                    km_actual=int(km),
                    fuente=fuente,
                    confiable=confiable,
                    vigente=vigente,
                    fecha_lectura=fecha,
                    turno_id=turno.id,
                    advertencias=advertencias,
                    requiere_verificacion=not vigente,
                )

        # 5: Legacy mantenimiento_vehiculo
        query_mant = (
            select(MantenimientoVehiculo)
            .where(MantenimientoVehiculo.vehiculo_id == vehiculo_id)
            .order_by(desc(MantenimientoVehiculo.fecha_servicio))
            .limit(1)
        )
        result = await db.execute(query_mant)
        ultimo_mant = result.scalar_one_or_none()
        if ultimo_mant and ultimo_mant.kilometraje:
            return LecturaKilometraje(
                km_actual=ultimo_mant.kilometraje,
                fuente="legacy",
                confiable=False,
                vigente=True,
                fecha_lectura=ultimo_mant.fecha_servicio or ultimo_mant.created_at or datetime.now(),
                turno_id=None,
                advertencias=["Km de mantenimiento legacy (no confiable)"],
                requiere_verificacion=True,
            )

        # 6: Gasto
        query_gasto = (
            select(GastoVehiculo)
            .where(GastoVehiculo.vehiculo_id == vehiculo_id)
            .where(GastoVehiculo.km_registro.isnot(None))
            .order_by(desc(GastoVehiculo.fecha_gasto))
            .limit(1)
        )
        result = await db.execute(query_gasto)
        ultimo_gasto = result.scalar_one_or_none()
        if ultimo_gasto and ultimo_gasto.km_registro:
            return LecturaKilometraje(
                km_actual=int(ultimo_gasto.km_registro),
                fuente="gasto",
                confiable=False,
                vigente=True,
                fecha_lectura=ultimo_gasto.fecha_gasto or ultimo_gasto.created_at or datetime.now(),
                turno_id=None,
                advertencias=["Km de gasto (no confiable)"],
                requiere_verificacion=True,
            )

        # 7: Cero
        return LecturaKilometraje(
            km_actual=0,
            fuente="cero",
            confiable=False,
            vigente=False,
            fecha_lectura=datetime.now(),
            turno_id=None,
            advertencias=["No hay turnos ni mantenimientos para este vehiculo"],
            requiere_verificacion=True,
        )

    @staticmethod
    async def validar_coherencia(
        db: AsyncSession,
        vehiculo_id: UUID,
        km_nuevo: int,
    ) -> tuple[bool, List[str]]:
        """
        Valida que el km_nuevo sea coherente con el km actual.

        Detecta:
        - Km retrocede (km_nuevo < km_actual).
        - Salto anormal (km_nuevo > km_actual * 1.5).

        Returns:
            (es_coherente, advertencias)
        """
        lectura = await KilometrajeService.obtener_km_actual(db, vehiculo_id)
        advertencias = []

        if lectura.km_actual > 0:
            # Km retrocede
            if km_nuevo < lectura.km_actual:
                advertencias.append(
                    f"Km retrocede: nuevo={km_nuevo}, actual={lectura.km_actual}"
                )

            # Salto anormal
            pct = (km_nuevo - lectura.km_actual) / lectura.km_actual
            if pct > KilometrajeService.SALTO_ANORMAL_PCT:
                advertencias.append(
                    f"Salto anormal: {pct*100:.1f}% (umbral {KilometrajeService.SALTO_ANORMAL_PCT*100:.0f}%)"
                )

        return (len(advertencias) == 0, advertencias)