"""
Servicio de autorización de turnos (CON HORARIOS FLEXIBLES)
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.schemas.turno_schemas import AutorizacionTurnoResult
from app.core.validaciones_compartidas import es_conductor


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


# ============================================
# SERVICIO DE AUTORIZACIÓN
# ============================================

class TurnoAuthorizationService:
    """Servicio central de autorización para inicio de jornada"""

    @staticmethod
    async def autorizar_inicio_jornada(
        usuario_id: UUID,
        contrato_id: UUID,
        db: AsyncSession,
        fecha_referencia: Optional[datetime] = None
    ) -> AutorizacionTurnoResult:
        """
        Valida si un usuario puede iniciar una jornada bajo un contrato.
        """
        ahora = fecha_referencia or datetime.now()
        fecha_actual = ahora.date()
        hora_actual_str = ahora.strftime("%H:%M")

        # Convertir día de la semana a español
        dias_espanol = {
            "monday": "lunes",
            "tuesday": "martes",
            "wednesday": "miercoles",
            "thursday": "jueves",
            "friday": "viernes",
            "saturday": "sabado",
            "sunday": "domingo"
        }
        dia_semana_actual = dias_espanol.get(ahora.strftime("%A").lower(), ahora.strftime("%A").lower())

        # 1. Obtener contrato (CON HORARIOS FLEXIBLES)
        query = text("""
            SELECT
                c.id, c.propietario_id, c.vehiculo_id, c.chofer_id,
                c.control_base_id, c.tipo_contrato,
                c.hora_inicio, c.hora_fin, c.duracion_minima_horas,
                c.permite_extension, c.hora_fin_extension,
                c.dias_contractuales, c.fecha_inicio, c.fecha_fin,
                c.estado_contrato, c.activo,
                v.patente
            FROM fleet.contrato_vehiculo c
            JOIN fleet.vehiculo v ON v.id = c.vehiculo_id
            WHERE c.id = :contrato_id
        """)
        result = await db.execute(query, {"contrato_id": contrato_id})
        row = result.first()
        if not row:
            return AutorizacionTurnoResult(
                autorizado=False,
                mensaje="Contrato no encontrado"
            )

        (cid, propietario_id, vehiculo_id, chofer_id,
         control_base_id, tipo_contrato,
         hora_inicio, hora_fin, duracion_minima_horas,
         permite_extension, hora_fin_extension,
         dias_contractuales, fecha_inicio, fecha_fin,
         estado_contrato, activo, patente) = row

        # Convertir dias_contractuales
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

        # Convertir time a string
        hora_inicio_str = hora_inicio.strftime("%H:%M") if hora_inicio else None
        hora_fin_str = hora_fin.strftime("%H:%M") if hora_fin else None
        hora_fin_extension_str = hora_fin_extension.strftime("%H:%M") if hora_fin_extension else None

        # 2. Validar que el usuario sea chofer o propietario (AUTO_GESTION)
        if usuario_id != chofer_id:
            if tipo_contrato == "AUTO_GESTION" and usuario_id == propietario_id:
                pass
            else:
                return AutorizacionTurnoResult(
                    autorizado=False,
                    mensaje="El usuario no corresponde al conductor del contrato"
                )

        # 3. Capacidad CONDUCTOR
        if not await es_conductor(usuario_id, db):
            return AutorizacionTurnoResult(
                autorizado=False,
                mensaje="El usuario no tiene capacidad CONDUCTOR"
            )

        # 4. Multi-tenant
        tenant_usr = await db.execute(
            text("SELECT control_base_id FROM auth.usuario WHERE id = :uid"),
            {"uid": usuario_id}
        )
        usuario_tenant = tenant_usr.scalar()
        if usuario_tenant != control_base_id:
            return AutorizacionTurnoResult(
                autorizado=False,
                mensaje="El usuario no pertenece al mismo tenant que el contrato"
            )

        # 5. Estado del contrato
        if estado_contrato != "ACTIVO" or not activo:
            return AutorizacionTurnoResult(
                autorizado=False,
                mensaje=f"El contrato no está ACTIVO (estado: {estado_contrato})"
            )

        # 6. Vigencia
        if fecha_inicio and fecha_inicio.date() > fecha_actual:
            return AutorizacionTurnoResult(
                autorizado=False,
                mensaje=f"El contrato aún no está vigente (inicia: {fecha_inicio})"
            )
        if fecha_fin and fecha_fin.date() < fecha_actual:
            return AutorizacionTurnoResult(
                autorizado=False,
                mensaje=f"El contrato ya finalizó (terminó: {fecha_fin})"
            )

        # 7. Día contractual
        if dias_list and dia_semana_actual not in dias_list:
            return AutorizacionTurnoResult(
                autorizado=False,
                mensaje=f"El día {dia_semana_actual} no está autorizado. Días permitidos: {', '.join(dias_list)}"
            )

        # 8. Validar horario actual (NUEVO: reemplaza turno_asignado)
        if not hora_inicio_str or not hora_fin_str:
            return AutorizacionTurnoResult(
                autorizado=False,
                mensaje="El contrato no tiene horario configurado"
            )

        if not hora_actual_esta_en_rango(ahora, hora_inicio_str, hora_fin_str):
            return AutorizacionTurnoResult(
                autorizado=False,
                mensaje=f"La hora actual ({hora_actual_str}) está fuera del horario del contrato ({hora_inicio_str}-{hora_fin_str})"
            )

        # 9. Exclusividad global (conductor)
        q_act = text("""
            SELECT id FROM fleet.turno_chofer
            WHERE chofer_id = :chofer_id AND estado = 'ACTIVO'
        """)
        res = await db.execute(q_act, {"chofer_id": chofer_id})
        if res.first():
            return AutorizacionTurnoResult(
                autorizado=False,
                mensaje="El conductor ya tiene una jornada activa (no puede iniciar otra)"
            )

        # 10. Exclusividad global (vehículo)
        q_act_veh = text("""
            SELECT id FROM fleet.turno_chofer
            WHERE vehiculo_id = :vehiculo_id AND estado = 'ACTIVO'
        """)
        res_veh = await db.execute(q_act_veh, {"vehiculo_id": vehiculo_id})
        if res_veh.first():
            return AutorizacionTurnoResult(
                autorizado=False,
                mensaje=f"El vehículo {patente} ya tiene una jornada activa (no puede iniciar otra)"
            )

        # 11. Todo OK
        return AutorizacionTurnoResult(
            autorizado=True,
            mensaje="Autorización concedida",
            contrato_id=cid,
            vehiculo_id=vehiculo_id,
            chofer_id=chofer_id,
            propietario_id=propietario_id,
            control_base_id=control_base_id,
            tipo_contrato=tipo_contrato,
            turno_contractual=None,  # DEPRECADO
            dia_contractual=dia_semana_actual,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            detalles_validacion={
                "patente": patente,
                "dias_permitidos": dias_list,
                "hora_inicio": hora_inicio_str,
                "hora_fin": hora_fin_str,
                "duracion_minima_horas": duracion_minima_horas,
                "permite_extension": permite_extension,
                "hora_fin_extension": hora_fin_extension_str
            }
        )
