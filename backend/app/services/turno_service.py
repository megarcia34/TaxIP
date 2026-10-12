"""
Servicio de gestión de turnos (Check-in / Check-out) CON HORARIOS FLEXIBLES
"""

import logging
import uuid
from uuid import UUID
from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy import text
from fastapi import HTTPException, status

from app.models.fleet import ContratoVehiculo, Vehiculo, ChoferVehiculo, CategoriaGasto, IngresoTurno
from app.models.turno import TurnoChofer
from app.models.gasto_turno import GastoTurno
from app.models.auth import Usuario
from app.models.trip import ViajeSolicitado

logger = logging.getLogger(__name__)

# ============================================
# FUNCIONES AUXILIARES PARA HORARIOS
# ============================================

def calcular_minutos(hora: str) -> int:
    """Convierte HH:MM a minutos desde medianoche"""
    h, m = map(int, hora.split(':'))
    return h * 60 + m


def cruza_medianoche(inicio: str, fin: str) -> bool:
    """Determina si un horario cruza medianoche"""
    return calcular_minutos(fin) <= calcular_minutos(inicio)


def hora_actual_esta_en_rango(hora_actual: datetime, hora_inicio: str, hora_fin: str) -> bool:
    """
    Determina si la hora actual está dentro del rango horario.
    Soporta cruce de medianoche.
    """
    ahora = hora_actual.time()
    minutos_actuales = ahora.hour * 60 + ahora.minute
    
    i1 = calcular_minutos(hora_inicio)
    f1 = calcular_minutos(hora_fin)
    
    if cruza_medianoche(hora_inicio, hora_fin):
        # Rango: [i1, 1440) ∪ [0, f1]
        return minutos_actuales >= i1 or minutos_actuales < f1
    else:
        # Rango: [i1, f1]
        return i1 <= minutos_actuales < f1


def dia_semana_espanol(fecha: datetime) -> str:
    """Convierte el día de la semana a español"""
    dias_espanol = {
        "monday": "lunes",
        "tuesday": "martes",
        "wednesday": "miercoles",
        "thursday": "jueves",
        "friday": "viernes",
        "saturday": "sabado",
        "sunday": "domingo"
    }
    return dias_espanol.get(fecha.strftime("%A").lower(), fecha.strftime("%A").lower())


# ============================================
# SERVICIO DE TURNOS
# ============================================

class TurnoService:
    """Servicio para gestión de turnos de choferes"""

    @staticmethod
    async def check_in(
        db: AsyncSession,
        chofer_id: uuid.UUID,
        vehiculo_id: uuid.UUID,
        km_inicial: float,
        combustible_inicial: str
    ) -> dict:
        """
        Iniciar jornada laboral (Check-in) CON VALIDACIONES DE HORARIOS FLEXIBLES
        """
        combustibles_validos = ['RESERVA', '1/4', '1/2', '3/4', 'LLENO']
        if combustible_inicial not in combustibles_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Combustible inválido. Permitidos: {combustibles_validos}"
            )

        # 1. Validar vehículo
        vehiculo = await db.get(Vehiculo, vehiculo_id)
        if not vehiculo or not vehiculo.activo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehículo no encontrado o inactivo"
            )

        # 2. Verificar que el vehículo no tenga turno activo
        turno_activo = await db.execute(
            select(TurnoChofer)
            .where(
                and_(
                    TurnoChofer.vehiculo_id == vehiculo_id,
                    TurnoChofer.estado == 'ACTIVO'
                )
            )
        )
        if turno_activo.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El vehículo ya tiene un turno activo"
            )

        # 3. Verificar límite de horas trabajadas (12h en 24h)
        hace_24h = datetime.now() - timedelta(hours=24)
        horas_trabajadas = await db.execute(
            select(func.sum(
                func.extract('epoch', TurnoChofer.fin_turno - TurnoChofer.inicio_turno) / 3600
            ))
            .where(
                and_(
                    TurnoChofer.chofer_id == chofer_id,
                    TurnoChofer.inicio_turno >= hace_24h,
                    TurnoChofer.estado != 'ACTIVO'
                )
            )
        )
        total_horas = horas_trabajadas.scalar() or 0
        if total_horas >= 24:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Límite de 12 horas de trabajo excedido en las últimas 24 horas"
            )

        # 4. Obtener contrato activo (CON HORARIOS FLEXIBLES)
        query = text("""
            SELECT 
                c.id, c.estado_contrato, c.fecha_inicio, c.fecha_fin,
                c.dias_contractuales, c.hora_inicio, c.hora_fin,
                c.duracion_minima_horas, c.permite_extension, c.hora_fin_extension
            FROM fleet.contrato_vehiculo c
            WHERE c.chofer_id = :chofer_id
              AND c.vehiculo_id = :vehiculo_id
              AND c.estado_contrato = 'ACTIVO'
              AND c.activo = true
        """)
        result = await db.execute(query, {
            "chofer_id": chofer_id,
            "vehiculo_id": vehiculo_id
        })
        row = result.first()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No tienes un contrato activo con este vehículo"
            )

        contrato_id = row[0]
        estado_contrato = row[1]
        fecha_inicio = row[2]
        fecha_fin = row[3]
        dias_contractuales = row[4]
        hora_inicio = row[5]
        hora_fin = row[6]
        duracion_minima_horas = row[7]
        permite_extension = row[8]
        hora_fin_extension = row[9]

        # 5. Validar fechas de vigencia
        ahora = datetime.now()
        fecha_actual = ahora.date()

        if fecha_inicio and fecha_inicio.date() > fecha_actual:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El contrato aún no está vigente (inicia: {fecha_inicio})"
            )
        if fecha_fin and fecha_fin.date() < fecha_actual:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El contrato ya finalizó (terminó: {fecha_fin})"
            )

        # 6. Validar día contractual
        dias_list = []
        if dias_contractuales:
            if isinstance(dias_contractuales, list):
                dias_list = dias_contractuales
            elif isinstance(dias_contractuales, str):
                try:
                    import json
                    dias_list = json.loads(dias_contractuales)
                except:
                    dias_list = []

        dia_actual = dia_semana_espanol(ahora)
        if dias_list and dia_actual not in dias_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El día {dia_actual} no está autorizado. Días permitidos: {', '.join(dias_list)}"
            )

        # 7. Validar horario actual (NUEVO: reemplaza turno_asignado)
        if not hora_inicio or not hora_fin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El contrato no tiene horario configurado"
            )

        hora_inicio_str = hora_inicio.strftime("%H:%M")
        hora_fin_str = hora_fin.strftime("%H:%M")
        hora_actual_str = ahora.strftime("%H:%M")

        if not hora_actual_esta_en_rango(ahora, hora_inicio_str, hora_fin_str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La hora actual ({hora_actual_str}) está fuera del horario del contrato ({hora_inicio_str}-{hora_fin_str})"
            )

        # 8. Crear turno con snapshots de horarios
        turno = TurnoChofer(
            contrato_id=contrato_id,
            chofer_id=chofer_id,
            vehiculo_id=vehiculo_id,
            estado='ACTIVO',
            km_inicial=km_inicial,
            combustible_inicial=combustible_inicial,
            inicio_turno=datetime.now(),
            snapshot_dia_contractual=dia_actual,
            # NUEVOS: Snapshots de horarios
            snapshot_hora_inicio=hora_inicio,
            snapshot_hora_fin=hora_fin,
            snapshot_duracion_minima_horas=duracion_minima_horas,
            snapshot_permite_extension=permite_extension,
            snapshot_hora_fin_extension=hora_fin_extension
        )
        db.add(turno)
        await db.commit()
        await db.refresh(turno)

                # 9. Actualizar estado laboral del chofer
        chofer_vehiculo = await db.execute(
            select(ChoferVehiculo)
            .where(
                and_(
                    ChoferVehiculo.usuario_id == chofer_id,
                    ChoferVehiculo.vehiculo_id == vehiculo_id
                )
            )
        )
        chofer_vehiculo = chofer_vehiculo.scalar_one_or_none()
        if chofer_vehiculo:
            chofer_vehiculo.estado_laboral = 'libre'
            chofer_vehiculo.updated_at = datetime.now()

        await db.commit()

        return {
            "turno_id": turno.id,
            "estado": turno.estado,
            "mensaje": "Jornada iniciada correctamente",
            "inicio_turno": turno.inicio_turno,
            "horario": f"{hora_inicio_str}-{hora_fin_str}",
            "dia_contractual": dia_actual
        }

    @staticmethod
    async def check_out(
        db: AsyncSession,
        turno_id: uuid.UUID,
        chofer_id: uuid.UUID,
        km_final: float,
        combustible_final: str,
        recaudacion_ticketera: float = 0
    ) -> dict:
        """
        Cerrar turno (Check-out)
        SOLO registra hechos operativos, NO calcula liquidación.
        Los ingresos declarados (ticketera) se registran como IngresoTurno con estado PENDIENTE.
        """
        combustibles_validos = ['RESERVA', '1/4', '1/2', '3/4', 'LLENO']
        if combustible_final not in combustibles_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Combustible inválido. Permitidos: {combustibles_validos}"
            )

        turno = await db.get(TurnoChofer, turno_id)
        if not turno:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Turno no encontrado"
            )

        if turno.chofer_id != chofer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para cerrar este turno"
            )

        if turno.estado != 'ACTIVO':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El turno ya está en estado {turno.estado}"
            )

        # Actualizar datos del turno
        turno.km_final = km_final
        turno.combustible_final = combustible_final
        turno.fin_turno = datetime.now()
        turno.estado = 'PENDIENTE_CONFIRMACION'

        # ============================================================
        # REGISTRAR INGRESO TICKETERA COMO INGRESO_TURNO PENDIENTE
        # Los campos legacy (recaudacion_ticketera_calle) ya NO existen
        # ============================================================
        if recaudacion_ticketera > 0:
            ingreso = IngresoTurno(
                turno_id=turno.id,
                tipo_ingreso="taximetro",
                medio_pago="efectivo",
                origen="taximetro",
                monto=Decimal(str(recaudacion_ticketera)),
                declarado_por=chofer_id,
                estado="pendiente",
                observaciones="Declaración de ticketera al cierre de turno"
            )
            db.add(ingreso)

        await db.commit()
        await db.refresh(turno)

        return {
            "turno_id": turno.id,
            "estado": turno.estado,
            "mensaje": "Turno cerrado correctamente. Pendiente de confirmación y liquidación.",
            "ingresos_registrados": 1 if recaudacion_ticketera > 0 else 0
        }

    @staticmethod
    async def forzar_cierre_viaje(
        db: AsyncSession,
        turno_id: uuid.UUID,
        chofer_id: uuid.UUID,
        viaje_id: uuid.UUID,
        motivo: str,
        notas: Optional[str] = None,
    ) -> dict:
        """
        Cierra forzadamente un viaje huerfano del turno.

        R17 - G67.

        Reglas:
        - Solo el chofer del turno puede cerrarlo.
        - Solo viajes en estado 'aceptado' o 'en_curso' del turno.
        - 'aceptado' -> estado final 'cancelado', sin cobro.
        - 'en_curso' -> estado final 'finalizado', con precio_estimado.
        - Registra en viaje_solicitado, historial_estado_viaje y audit.
        - Notifica al chofer y al propietario.
        """
        from app.schemas.turno_schemas import MOTIVOS_FORZAR_CIERRE

        # 1. Validar motivo
        if motivo not in MOTIVOS_FORZAR_CIERRE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Motivo invalido. Validos: {list(MOTIVOS_FORZAR_CIERRE.keys())}",
            )

        if motivo == "otro" and not notas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El motivo 'otro' requiere notas.",
            )

        # 2. Validar que el turno pertenece al chofer y esta activo
        turno = await db.get(TurnoChofer, turno_id)
        if not turno:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Turno no encontrado",
            )
        if turno.chofer_id != chofer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tenes permiso para cerrar viajes de este turno",
            )

        # 3. Leer el viaje
        viaje_query = text("""
            SELECT id, estado, chofer_id, vehiculo_id, turno_id,
                   precio_estimado, precio_final, control_base_id,
                   direccion_origen, direccion_destino
            FROM trip.viaje_solicitado
            WHERE id = :viaje_id
            LIMIT 1
        """)
        viaje_row = (await db.execute(viaje_query, {"viaje_id": viaje_id})).first()

        if not viaje_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Viaje no encontrado",
            )

        (v_id, estado_previo, v_chofer_id, vehiculo_id, v_turno_id,
         precio_estimado, precio_final, control_base_id,
         direccion_origen, direccion_destino) = viaje_row

        # 4. Validar pertenencia
        if v_chofer_id != chofer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El viaje no pertenece a este chofer",
            )
        if v_turno_id != turno_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El viaje no pertenece a este turno",
            )
        if estado_previo not in ("aceptado", "en_curso"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El viaje ya esta en estado '{estado_previo}' y no puede cerrarse forzadamente",
            )

        # 5. Determinar estado final y precio
        if estado_previo == "aceptado":
            estado_nuevo = "cancelado"
            precio_final_usado = None
        else:  # en_curso
            estado_nuevo = "finalizado"
            precio_final_usado = float(precio_estimado) if precio_estimado else None

        # 6. UPDATE del viaje
        if estado_nuevo == "cancelado":
            update_query = text("""
                UPDATE trip.viaje_solicitado
                SET estado = 'cancelado',
                    cancelado_en = NOW(),
                    cancelado_por = :chofer_id,
                    motivo_cancelacion = :motivo_full,
                    updated_at = NOW()
                WHERE id = :viaje_id
            """)
        else:  # finalizado
            update_query = text("""
                UPDATE trip.viaje_solicitado
                SET estado = 'finalizado',
                    finalizado_en = NOW(),
                    motivo_cancelacion = :motivo_full,
                    precio_final = :precio_final,
                    updated_at = NOW()
                WHERE id = :viaje_id
            """)

        motivo_full = MOTIVOS_FORZAR_CIERRE[motivo]
        if notas:
            motivo_full += f" | Notas: {notas}"

        params = {
            "viaje_id": str(viaje_id),
            "chofer_id": str(chofer_id),
            "motivo_full": motivo_full[:500],
        }
        if estado_nuevo == "finalizado":
            params["precio_final"] = precio_final_usado

        await db.execute(update_query, params)

        # 7. Historial
        observacion = (
            f"Viaje cerrado forzadamente por chofer. "
            f"Motivo: {MOTIVOS_FORZAR_CIERRE[motivo]}."
        )
        if notas:
            observacion += f" Notas: {notas}"

        await db.execute(
            text("""
                INSERT INTO trip.historial_estado_viaje (
                    id, viaje_id, estado, observacion, created_at
                )
                VALUES (gen_random_uuid(), :viaje_id, :estado, :obs, NOW())
            """),
            {
                "viaje_id": str(viaje_id),
                "estado": estado_nuevo,
                "obs": observacion[:1000],
            },
        )

        # 8. Audit
        await db.execute(
            text("""
                INSERT INTO audit.log_acciones (
                    id, usuario_id, email, accion, tabla_afectada,
                    registro_id, datos_nuevos, control_base_id,
                    ip_address, created_at
                )
                VALUES (
                    gen_random_uuid(),
                    :chofer_id,
                    'system@g67.local',
                    'FORZAR_CIERRE_VIAJE',
                    'trip.viaje_solicitado',
                    :viaje_id,
                    jsonb_build_object(
                        'motivo', :motivo,
                        'motivo_label', :motivo_label,
                        'notas', :notas,
                        'estado_previo', :estado_previo,
                        'estado_nuevo', :estado_nuevo,
                        'precio_final', :precio_final
                    ),
                    :control_base_id,
                    NULL,
                    NOW()
                )
            """),
            {
                "chofer_id": str(chofer_id),
                "viaje_id": str(viaje_id),
                "motivo": motivo,
                "motivo_label": MOTIVOS_FORZAR_CIERRE[motivo],
                "notas": notas,
                "estado_previo": estado_previo,
                "estado_nuevo": estado_nuevo,
                "precio_final": precio_final_usado,
                "control_base_id": str(control_base_id),
            },
        )

        # 9. Notificacion al chofer (confirmacion)
        await db.execute(
            text("""
                INSERT INTO notification.notificacion (
                    id, usuario_id, titulo, mensaje, tipo, leida, created_at
                )
                VALUES (
                    gen_random_uuid(), :usuario_id,
                    'Viaje cerrado forzadamente',
                    :mensaje,
                    'viaje',
                    false,
                    NOW()
                )
            """),
            {
                "usuario_id": str(chofer_id),
                "mensaje": (
                    f"Cerraste el viaje {str(viaje_id)[:8]} "
                    f"con motivo: {MOTIVOS_FORZAR_CIERRE[motivo]}."
                ),
            },
        )

        # 10. Notificacion al propietario
        prop_query = text("""
            SELECT pv.propietario_id
            FROM fleet.propietario_vehiculo pv
            WHERE pv.vehiculo_id = :vehiculo_id AND pv.activo = true
            LIMIT 1
        """)
        prop_row = (await db.execute(prop_query, {"vehiculo_id": vehiculo_id})).first()

        if prop_row:
            propietario_id = prop_row[0]
            mensaje_prop = (
                f"El chofer cerro forzadamente el viaje {str(viaje_id)[:8]}. "
                f"Motivo: {MOTIVOS_FORZAR_CIERRE[motivo]}."
            )
            if notas:
                mensaje_prop += f" Notas: {notas}"

            await db.execute(
                text("""
                    INSERT INTO notification.notificacion (
                        id, usuario_id, titulo, mensaje, tipo, leida, created_at
                    )
                    VALUES (
                        gen_random_uuid(), :usuario_id,
                        'Viaje cerrado forzadamente',
                        :mensaje,
                        'alerta',
                        false,
                        NOW()
                    )
                """),
                {
                    "usuario_id": str(propietario_id),
                    "mensaje": mensaje_prop[:1000],
                },
            )

        await db.commit()

        # 11. Verificar si quedan huerfanos
        check_query = text("""
            SELECT COUNT(*) FROM trip.viaje_solicitado
            WHERE chofer_id = :chofer_id
              AND estado IN ('aceptado', 'en_curso')
        """)
        huerfanos_restantes = (await db.execute(check_query, {"chofer_id": str(chofer_id)})).scalar() or 0

        return {
            "viaje_id": viaje_id,
            "estado_previo": estado_previo,
            "estado_nuevo": estado_nuevo,
            "motivo": motivo,
            "motivo_label": MOTIVOS_FORZAR_CIERRE[motivo],
            "precio_final": precio_final_usado,
            "puede_cerrar_turno": huerfanos_restantes == 0,
        }



    @staticmethod
    async def registrar_gasto(
        db: AsyncSession,
        turno_id: uuid.UUID,
        chofer_id: uuid.UUID,
        tipo_gasto: str,
        monto: float,
        km_registro: float = None,
        url_comprobante: str = None,
        categoria_id: Optional[uuid.UUID] = None,
        subcategoria: Optional[str] = None
    ) -> dict:
        """
        Registrar gasto durante el turno.
        Ahora soporta categorías (opcional, para migración gradual).
        """
        tipos_validos = ['COMBUSTIBLE', 'LUBRICANTE', 'LAVADO', 'REPARACION', 'OTROS']
        if tipo_gasto not in tipos_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de gasto inválido. Permitidos: {tipos_validos}"
            )

        turno = await db.get(TurnoChofer, turno_id)
        if not turno:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Turno no encontrado"
            )

        if turno.chofer_id != chofer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para registrar gastos en este turno"
            )

        if turno.estado != 'ACTIVO':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden registrar gastos en turnos activos"
            )

        if categoria_id:
            categoria = await db.get(CategoriaGasto, categoria_id)
            if not categoria:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada"
                )
            if "turno" not in categoria.aplica_a:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La categoría '{categoria.nombre}' no aplica a turnos"
                )
            if subcategoria and categoria.subcategorias and subcategoria not in categoria.subcategorias:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Subcategoría '{subcategoria}' no válida. Opciones: {', '.join(categoria.subcategorias)}"
                )

        gasto = GastoTurno(
            turno_id=turno.id,
            tipo_gasto=tipo_gasto,
            monto=monto,
            km_registro=km_registro,
            url_comprobante=url_comprobante,
            categoria_id=categoria_id,
            subcategoria=subcategoria
        )
        db.add(gasto)
        await db.commit()
        await db.refresh(gasto)

        return {
            "gasto_id": gasto.id,
            "mensaje": "Gasto registrado correctamente"
        }
