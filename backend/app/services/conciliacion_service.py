"""
Servicio de Conciliacion de Turnos.

Logica de negocio:
- Listar turnos pendientes de conciliar.
- Obtener detalle de un turno para conciliar.
- Aprobar/rechazar gastos.
- Calcular diferencias (efectivo, gastos rechazados).
- Cerrar conciliacion y generar liquidacion.
- Saldar diferencias.
- Abrir/resolver disputas.

Reglas de negocio confirmadas (R24):
- Recaudacion declarada = recaudacion manual + recaudacion electronica.
- Efectivo en mano = suma de viajes finalizados con metodo_pago = 'efectivo'.
- Diferencia de efectivo = efectivo declarado - efectivo calculado de viajes.
- Al cerrar turno se esta en condiciones de conciliar.
- Gasto rechazado -> DEUDA_CHOFER (impase hasta saldar).
- Conciliacion automatica (7 dias): aprobar gastos, generar liquidacion,
  registrar diferencias como deudas pendientes.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging

from app.models.conciliacion import ConciliacionDiferencia, ConciliacionDisputa
from app.schemas.conciliacion import (
    ConciliacionPendienteItem,
    ConciliacionPendienteResponse,
    ConciliacionDetalleResponse,
    GastoConciliacionItem,
    DiferenciaItem,
    DisputaResponse,
)


logger = logging.getLogger(__name__)


# ============================================================
# CONSTANTES
# ============================================================

DIAS_PLAZO_CONCILIACION = 7
DIAS_PLAZO_TENANT = 5
DIAS_PLAZO_PLATAFORMA = 5


# ============================================================
# SERVICIO
# ============================================================

class ConciliacionService:
    """Servicio de conciliacion de turnos."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # BANDEJA DE PENDIENTES
    # ============================================================

    async def listar_pendientes(
        self, propietario_id: UUID
    ) -> ConciliacionPendienteResponse:
        """
        Lista los turnos pendientes de conciliar del propietario.

        Incluye:
        - Turnos en estado PENDIENTE_CONFIRMACION.
        - Turnos en estado CON_DIFERENCIAS_PENDIENTES.
        - Turnos en estado EN_DISPUTA.

        Ordenados por fin_turno ascendente (mas viejos primero).
        """
        query = text("""
            SELECT
                t.id AS turno_id,
                t.fin_turno,
                t.estado,
                v.patente AS vehiculo_patente,
                COALESCE(p.nombre || ' ' || p.apellido, u.email) AS chofer_nombre,
                c.tipo_contrato,
                COALESCE((
                    SELECT SUM(vs.precio_final)
                    FROM trip.viaje_solicitado vs
                    WHERE vs.turno_id = t.id
                      AND vs.estado = 'finalizado'
                ), 0) AS recaudacion_viajes,
                COALESCE((
                    SELECT SUM(it.monto)
                    FROM fleet.ingreso_turno it
                    WHERE it.turno_id = t.id
                      AND LOWER(COALESCE(it.origen, '')) = 'manual'
                ), 0) AS recaudacion_manual,
                COALESCE(t.recaudacion_ticketera, 0) AS efectivo_declarado,
                COALESCE((
                    SELECT SUM(gt.monto)
                    FROM fleet.gasto_turno gt
                    WHERE gt.turno_id = t.id
                ), 0) AS gastos_declarados,
                EXTRACT(EPOCH FROM (NOW() - t.fin_turno)) / 86400 AS dias_transcurridos
            FROM fleet.turno_chofer t
            JOIN fleet.vehiculo v ON v.id = t.vehiculo_id
            JOIN fleet.contrato_vehiculo c ON c.id = t.contrato_id
            JOIN auth.usuario u ON u.id = t.chofer_id
            LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
            JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
            WHERE pv.propietario_id = :propietario_id
              AND pv.activo = true
              AND t.estado IN (
                  'PENDIENTE_CONFIRMACION',
                  'CON_DIFERENCIAS_PENDIENTES',
                  'EN_DISPUTA'
              )
            ORDER BY t.fin_turno ASC
        """)

        result = await self.db.execute(query, {"propietario_id": propietario_id})
        rows = result.fetchall()

        items = []
        for row in rows:
            recaudacion_viajes = float(row[6] or 0)
            recaudacion_manual = float(row[7] or 0)
            efectivo_declarado = float(row[8] or 0)
            gastos_declarados = float(row[9] or 0)
            dias_transcurridos = float(row[10] or 0)

            # Calcular diferencia: efectivo declarado - efectivo calculado de viajes
            # (Por ahora, usamos recaudacion_viajes como proxy. El detalle exacto
            # se calcula en obtener_detalle).
            diferencia = efectivo_declarado - recaudacion_viajes

            dias_restantes = max(0, DIAS_PLAZO_CONCILIACION - int(dias_transcurridos))

            items.append(ConciliacionPendienteItem(
                turno_id=row[0],
                fin_turno=row[1],
                vehiculo_patente=row[3],
                chofer_nombre=row[4] or "Sin chofer",
                tipo_contrato=row[5],
                recaudacion_declarada=Decimal(str(recaudacion_viajes + recaudacion_manual)),
                efectivo_en_mano=Decimal(str(efectivo_declarado)),
                gastos_declarados=Decimal(str(gastos_declarados)),
                diferencia=Decimal(str(diferencia)),
                dias_restantes=dias_restantes,
                estado=row[2],
            ))

        return ConciliacionPendienteResponse(total=len(items), turnos=items)

    # ============================================================
    # DETALLE DE CONCILIACION
    # ============================================================

    async def obtener_detalle(
        self, turno_id: UUID, propietario_id: UUID
    ) -> ConciliacionDetalleResponse:
        """
        Obtiene el detalle completo de un turno para conciliar.

        Incluye:
        - Datos del turno y del chofer.
        - Recaudacion (viajes + manual).
        - Efectivo en mano.
        - Gastos declarados.
        - Diferencias registradas.
        """
        # 1. Datos del turno
        query_turno = text("""
            SELECT
                t.id AS turno_id,
                t.fin_turno,
                t.recaudacion_ticketera,
                t.estado,
                v.patente AS vehiculo_patente,
                COALESCE(p.nombre || ' ' || p.apellido, u.email) AS chofer_nombre,
                c.tipo_contrato,
                c.porcentaje_chofer,
                c.canon_diario,
                c.tratamiento_gastos
            FROM fleet.turno_chofer t
            JOIN fleet.vehiculo v ON v.id = t.vehiculo_id
            JOIN fleet.contrato_vehiculo c ON c.id = t.contrato_id
            JOIN auth.usuario u ON u.id = t.chofer_id
            LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
            JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
            WHERE t.id = :turno_id
              AND pv.propietario_id = :propietario_id
              AND pv.activo = true
        """)
        result = await self.db.execute(query_turno, {
            "turno_id": turno_id,
            "propietario_id": propietario_id,
        })
        row = result.first()

        if not row:
            raise ValueError(f"Turno {turno_id} no encontrado o no pertenece al propietario")

        (
            turno_id_val, fin_turno, recaudacion_ticketera, estado_turno,
            vehiculo_patente, chofer_nombre, tipo_contrato, porcentaje_chofer,
            canon_diario, tratamiento_gastos,
        ) = row

        # 2. Recaudacion de viajes (finalizados)
        query_viajes = text("""
            SELECT
                COALESCE(SUM(precio_final), 0) AS recaudacion_total,
                COALESCE(SUM(CASE WHEN metodo_pago = 'efectivo' THEN precio_final ELSE 0 END), 0) AS recaudacion_efectivo,
                COALESCE(SUM(CASE WHEN metodo_pago != 'efectivo' THEN precio_final ELSE 0 END), 0) AS recaudacion_electronico
            FROM trip.viaje_solicitado
            WHERE turno_id = :turno_id
              AND estado = 'finalizado'
        """)
        result = await self.db.execute(query_viajes, {"turno_id": turno_id})
        row_viajes = result.first()
        recaudacion_viajes = float(row_viajes[0] or 0)
        recaudacion_efectivo = float(row_viajes[1] or 0)
        recaudacion_electronico = float(row_viajes[2] or 0)

        # 3. Recaudacion manual (ingresos manuales del turno)
        query_manual = text("""
            SELECT COALESCE(SUM(monto), 0)
            FROM fleet.ingreso_turno
            WHERE turno_id = :turno_id
              AND LOWER(COALESCE(origen, '')) = 'manual'
        """)
        result = await self.db.execute(query_manual, {"turno_id": turno_id})
        recaudacion_manual = float(result.scalar() or 0)

        # 4. Gastos del turno
        query_gastos = text("""
            SELECT
                id,
                tipo_gasto,
                monto,
                COALESCE(descripcion, '') AS descripcion,
                url_comprobante,
                created_at
            FROM fleet.gasto_turno
            WHERE turno_id = :turno_id
            ORDER BY created_at ASC
        """)
        result = await self.db.execute(query_gastos, {"turno_id": turno_id})
        rows_gastos = result.fetchall()

        gastos_list = []
        gastos_total = 0.0
        for g in rows_gastos:
            monto = float(g[2] or 0)
            gastos_total += monto
            gastos_list.append(GastoConciliacionItem(
                id=g[0],
                tipo_gasto=g[1],
                monto=Decimal(str(monto)),
                descripcion=g[3] or None,
                url_comprobante=g[4],
                created_at=g[5],
                estado_aprobacion="pendiente",  # TODO: leer de conciliacion_diferencia
            ))

        # 5. Diferencias registradas
        query_diferencias = text("""
            SELECT
                id,
                tipo,
                concepto,
                monto,
                descripcion,
                estado
            FROM fleet.conciliacion_diferencia
            WHERE turno_id = :turno_id
            ORDER BY created_at ASC
        """)
        result = await self.db.execute(query_diferencias, {"turno_id": turno_id})
        rows_diferencias = result.fetchall()

        diferencias_list = []
        diferencias_total = 0.0
        for d in rows_diferencias:
            monto = float(d[3] or 0)
            diferencias_total += monto
            diferencias_list.append(DiferenciaItem(
                id=d[0],
                tipo=d[1],
                concepto=d[2],
                monto=Decimal(str(monto)),
                descripcion=d[4],
                estado=d[5],
            ))

        # 6. Calcular diferencia de efectivo
        efectivo_declarado = float(recaudacion_ticketera or 0)
        diferencia_efectivo = efectivo_declarado - recaudacion_efectivo

        # 7. Determinar si puede cerrar
        puede_cerrar = (
            diferencia_efectivo == 0
            and diferencias_total == 0
            and estado_turno == "PENDIENTE_CONFIRMACION"
        )

        return ConciliacionDetalleResponse(
            turno_id=turno_id_val,
            fin_turno=fin_turno,
            vehiculo_patente=vehiculo_patente,
            chofer_nombre=chofer_nombre or "Sin chofer",
            tipo_contrato=tipo_contrato,
            porcentaje_chofer=Decimal(str(porcentaje_chofer)) if porcentaje_chofer else None,
            canon_diario=Decimal(str(canon_diario)) if canon_diario else None,
            tratamiento_gastos=tratamiento_gastos,
            recaudacion_viajes=Decimal(str(recaudacion_viajes)),
            recaudacion_manual=Decimal(str(recaudacion_manual)),
            recaudacion_total=Decimal(str(recaudacion_viajes + recaudacion_manual)),
            efectivo_en_mano=Decimal(str(efectivo_declarado)),
            recaudacion_electronico=Decimal(str(recaudacion_electronico)),
            diferencia_efectivo=Decimal(str(diferencia_efectivo)),
            gastos=gastos_list,
            gastos_total=Decimal(str(gastos_total)),
            diferencias=diferencias_list,
            diferencias_total=Decimal(str(diferencias_total)),
            puede_cerrar=puede_cerrar,
        )

    # ============================================================
    # APROBAR / RECHAZAR GASTO
    # ============================================================

    async def aprobar_gasto(
        self, turno_id: UUID, gasto_id: UUID, propietario_id: UUID
    ) -> None:
        """Aprueba un gasto declarado por el chofer."""
        # Validar que el turno pertenece al propietario
        query_val = text("""
            SELECT t.id FROM fleet.turno_chofer t
            JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = t.vehiculo_id
            WHERE t.id = :turno_id
              AND pv.propietario_id = :propietario_id
              AND pv.activo = true
        """)
        result = await self.db.execute(query_val, {
            "turno_id": turno_id,
            "propietario_id": propietario_id,
        })
        if not result.first():
            raise ValueError(f"Turno {turno_id} no encontrado o no pertenece al propietario")

        # TODO: agregar campo estado_aprobacion a fleet.gasto_turno
        # Por ahora, no hacemos nada (el gasto se considera aprobado por defecto)
        logger.info(f"Gasto {gasto_id} aprobado para turno {turno_id}")

    async def rechazar_gasto(
        self, turno_id: UUID, gasto_id: UUID, motivo: str, propietario_id: UUID
    ) -> None:
        """
        Rechaza un gasto declarado por el chofer.

        Genera una diferencia DEUDA_CHOFER por el monto del gasto.
        """
        # Validar que el turno pertenece al propietario
        query_val = text("""
            SELECT t.id FROM fleet.turno_chofer t
            JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = t.vehiculo_id
            WHERE t.id = :turno_id
              AND pv.propietario_id = :propietario_id
              AND pv.activo = true
        """)
        result = await self.db.execute(query_val, {
            "turno_id": turno_id,
            "propietario_id": propietario_id,
        })
        if not result.first():
            raise ValueError(f"Turno {turno_id} no encontrado o no pertenece al propietario")

        # Obtener monto del gasto
        query_gasto = text("""
            SELECT monto, tipo_gasto FROM fleet.gasto_turno WHERE id = :gasto_id
        """)
        result = await self.db.execute(query_gasto, {"gasto_id": gasto_id})
        row = result.first()
        if not row:
            raise ValueError(f"Gasto {gasto_id} no encontrado")

        monto = Decimal(str(row[0]))
        tipo_gasto = row[1]

        # Crear diferencia DEUDA_CHOFER
        diferencia = ConciliacionDiferencia(
            turno_id=turno_id,
            tipo="DEUDA_CHOFER",
            concepto="GASTO_RECHAZADO",
            monto=monto,
            descripcion=f"Gasto rechazado: {tipo_gasto}. Motivo: {motivo}",
            estado="PENDIENTE",
        )
        self.db.add(diferencia)

        # Cambiar estado del turno a CON_DIFERENCIAS_PENDIENTES
        await self.db.execute(
            text("""
                UPDATE fleet.turno_chofer
                SET estado = 'CON_DIFERENCIAS_PENDIENTES', updated_at = NOW()
                WHERE id = :turno_id
            """),
            {"turno_id": turno_id},
        )

        await self.db.commit()
        logger.info(f"Gasto {gasto_id} rechazado, diferencia creada para turno {turno_id}")

    # ============================================================
    # CERRAR CONCILIACION
    # ============================================================

    async def cerrar_conciliacion(
        self, turno_id: UUID, propietario_id: UUID, observaciones: Optional[str] = None
    ) -> None:
        """
        Cierra la conciliacion de un turno.

        Requisitos:
        - No debe haber diferencias pendientes.
        - El turno debe estar en PENDIENTE_CONFIRMACION.

        Efectos:
        - Genera la liquidacion.
        - Cambia estado del turno a CONCILIADO.
        - Registra quien concilio y cuando.
        """
        # Obtener detalle para validar
        detalle = await self.obtener_detalle(turno_id, propietario_id)

        if not detalle.puede_cerrar:
            raise ValueError(
                f"No se puede cerrar la conciliacion. "
                f"Diferencias pendientes: {detalle.diferencias_total}"
            )

        # Cambiar estado del turno
        await self.db.execute(
            text("""
                UPDATE fleet.turno_chofer
                SET estado = 'CONCILIADO', updated_at = NOW()
                WHERE id = :turno_id
            """),
            {"turno_id": turno_id},
        )

        # TODO: generar liquidacion con LiquidacionEngine
        # (se implementa en el siguiente paso)

        await self.db.commit()
        logger.info(f"Conciliacion cerrada para turno {turno_id} por propietario {propietario_id}")

    # ============================================================
    # SALDAR DIFERENCIA
    # ============================================================

    async def saldar_diferencia(
        self, diferencia_id: UUID, propietario_id: UUID
    ) -> None:
        """
        Marca una diferencia como saldada.

        Solo el propietario puede saldar diferencias.
        """
        # Verificar que la diferencia existe y pertenece al propietario
        query = text("""
            SELECT d.id, d.turno_id
            FROM fleet.conciliacion_diferencia d
            JOIN fleet.turno_chofer t ON t.id = d.turno_id
            JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = t.vehiculo_id
            WHERE d.id = :diferencia_id
              AND pv.propietario_id = :propietario_id
              AND pv.activo = true
        """)
        result = await self.db.execute(query, {
            "diferencia_id": diferencia_id,
            "propietario_id": propietario_id,
        })
        row = result.first()
        if not row:
            raise ValueError(f"Diferencia {diferencia_id} no encontrada o no pertenece al propietario")

        turno_id = row[1]

        # Marcar diferencia como saldada
        await self.db.execute(
            text("""
                UPDATE fleet.conciliacion_diferencia
                SET estado = 'SALDADA',
                    saldada_en = NOW(),
                    saldada_por = :propietario_id
                WHERE id = :diferencia_id
            """),
            {"diferencia_id": diferencia_id, "propietario_id": propietario_id},
        )

        # Verificar si quedan diferencias pendientes en el turno
        query_pendientes = text("""
            SELECT COUNT(*) FROM fleet.conciliacion_diferencia
            WHERE turno_id = :turno_id AND estado = 'PENDIENTE'
        """)
        result = await self.db.execute(query_pendientes, {"turno_id": turno_id})
        pendientes = result.scalar() or 0

        # Si no quedan pendientes, cambiar estado del turno a PENDIENTE_CONFIRMACION
        if pendientes == 0:
            await self.db.execute(
                text("""
                    UPDATE fleet.turno_chofer
                    SET estado = 'PENDIENTE_CONFIRMACION', updated_at = NOW()
                    WHERE id = :turno_id AND estado = 'CON_DIFERENCIAS_PENDIENTES'
                """),
                {"turno_id": turno_id},
            )

        await self.db.commit()
        logger.info(f"Diferencia {diferencia_id} saldada")

    # ============================================================
    # DISPUTAS
    # ============================================================

    async def abrir_disputa(
        self, turno_id: UUID, usuario_id: UUID, motivo: str
    ) -> DisputaResponse:
        """
        Abre una disputa sobre una conciliacion.

        Puede abrirla el chofer o el propietario.
        """
        # Verificar que no exista una disputa abierta
        query_existente = text("""
            SELECT id FROM fleet.conciliacion_disputa
            WHERE turno_id = :turno_id
              AND estado IN ('ABIERTA', 'EN_TENANT', 'EN_PLATAFORMA')
            LIMIT 1
        """)
        result = await self.db.execute(query_existente, {"turno_id": turno_id})
        if result.first():
            raise ValueError(f"Ya existe una disputa abierta para el turno {turno_id}")

        # Calcular plazos
        ahora = datetime.now()
        plazo_tenant = ahora + timedelta(days=DIAS_PLAZO_TENANT)
        plazo_plataforma = plazo_tenant + timedelta(days=DIAS_PLAZO_PLATAFORMA)

        # Crear disputa
        disputa = ConciliacionDisputa(
            turno_id=turno_id,
            abierta_por=usuario_id,
            motivo=motivo,
            estado="ABIERTA",
            plazo_tenant=plazo_tenant,
            plazo_plataforma=plazo_plataforma,
        )
        self.db.add(disputa)

        # Cambiar estado del turno a EN_DISPUTA
        await self.db.execute(
            text("""
                UPDATE fleet.turno_chofer
                SET estado = 'EN_DISPUTA', updated_at = NOW()
                WHERE id = :turno_id
            """),
            {"turno_id": turno_id},
        )

        await self.db.commit()

        return DisputaResponse(
            id=disputa.id,
            turno_id=disputa.turno_id,
            abierta_por=disputa.abierta_por,
            motivo=disputa.motivo,
            estado=disputa.estado,
            resolucion=disputa.resolucion,
            resuelta_por=disputa.resuelta_por,
            resuelta_en=disputa.resuelta_en,
            plazo_tenant=disputa.plazo_tenant,
            plazo_plataforma=disputa.plazo_plataforma,
            created_at=disputa.created_at,
        )

    async def resolver_disputa(
        self, disputa_id: UUID, usuario_id: UUID, resolucion: str, a_favor_de: str
    ) -> None:
        """
        Resuelve una disputa.

        Solo el tenant o la plataforma pueden resolverla.
        """
        # TODO: validar que el usuario tiene permiso (tenant o plataforma)
        # Por ahora, se asume que el usuario tiene permiso

        # Obtener disputa
        query = text("""
            SELECT id, turno_id FROM fleet.conciliacion_disputa
            WHERE id = :disputa_id
        """)
        result = await self.db.execute(query, {"disputa_id": disputa_id})
        row = result.first()
        if not row:
            raise ValueError(f"Disputa {disputa_id} no encontrada")

        turno_id = row[1]

        # Marcar disputa como resuelta
        await self.db.execute(
            text("""
                UPDATE fleet.conciliacion_disputa
                SET estado = 'RESUELTA',
                    resolucion = :resolucion,
                    resuelta_por = :usuario_id,
                    resuelta_en = NOW()
                WHERE id = :disputa_id
            """),
            {
                "disputa_id": disputa_id,
                "resolucion": resolucion,
                "usuario_id": usuario_id,
            },
        )

        # Cambiar estado del turno según resolución
        nuevo_estado = "PENDIENTE_CONFIRMACION" if a_favor_de == "chofer" else "CON_DIFERENCIAS_PENDIENTES"
        await self.db.execute(
            text("""
                UPDATE fleet.turno_chofer
                SET estado = :nuevo_estado, updated_at = NOW()
                WHERE id = :turno_id
            """),
            {"turno_id": turno_id, "nuevo_estado": nuevo_estado},
        )

        await self.db.commit()
        logger.info(f"Disputa {disputa_id} resuelta a favor de {a_favor_de}")