"""
Servicio de autorización de turnos (CON HORARIOS FLEXIBLES)
"""

from datetime import datetime, timedelta
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

    @staticmethod
    async def generar_qr(
        propietario_id: UUID,
        contrato_id: UUID,
        db: AsyncSession,
        dias_validez: int = 30
    ) -> dict:
        """
        Genera un QR operativo para un contrato ACTIVO.
        """
        query = text("""
            SELECT id, control_base_id FROM fleet.contrato_vehiculo
            WHERE id = :contrato_id
              AND propietario_id = :propietario_id
              AND estado_contrato = 'ACTIVO'
              AND activo = true
        """)
        result = await db.execute(query, {
            "contrato_id": contrato_id,
            "propietario_id": propietario_id
        })
        row = result.first()
        if not row:
            raise ValueError("Contrato no encontrado o no ACTIVO")

        import uuid
        token = str(uuid.uuid4())
        fecha_expiracion = datetime.now() + timedelta(days=dias_validez)

        insert = text("""
            INSERT INTO fleet.contrato_qr (
                id, contrato_id, token, fecha_expiracion, activo, created_at, created_by, usos
            ) VALUES (
                gen_random_uuid(), :contrato_id, :token, :fecha_expiracion, true, NOW(), :propietario_id, 0
            )
            RETURNING id
        """)
        await db.execute(insert, {
            "contrato_id": contrato_id,
            "token": token,
            "fecha_expiracion": fecha_expiracion,
            "propietario_id": propietario_id
        })
        await db.commit()

        return {"token": token, "fecha_expiracion": fecha_expiracion}

    @staticmethod
    async def escanear_qr(
        conductor_id: UUID,
        token: str,
        db: AsyncSession
    ) -> dict:
        """
        Escanea un QR operativo y ejecuta C1.
        """
        # 1. Validar QR
        query_qr = text("""
            SELECT cq.id, cq.contrato_id, cq.fecha_expiracion, cq.activo,
                   cv.control_base_id, cv.propietario_id
            FROM fleet.contrato_qr cq
            JOIN fleet.contrato_vehiculo cv ON cv.id = cq.contrato_id
            WHERE cq.token = :token
        """)
        result = await db.execute(query_qr, {"token": token})
        row = result.first()
        if not row:
            return {"autorizado": False, "mensaje": "QR inválido o no encontrado"}

        qr_id, contrato_id, fecha_expiracion, activo, control_base_id, propietario_id = row

        if fecha_expiracion and fecha_expiracion < datetime.now():
            return {"autorizado": False, "mensaje": "QR expirado"}
        if not activo:
            return {"autorizado": False, "mensaje": "QR inactivo"}

        # 2. Validar tenant
        tenant_usr = await db.execute(
            text("SELECT control_base_id FROM auth.usuario WHERE id = :uid"),
            {"uid": conductor_id}
        )
        conductor_tenant = tenant_usr.scalar()
        if conductor_tenant != control_base_id:
            return {"autorizado": False, "mensaje": "El QR pertenece a otro tenant"}

        # 3. Ejecutar C1
        autorizacion = await TurnoAuthorizationService.autorizar_inicio_jornada(
            usuario_id=conductor_id,
            contrato_id=contrato_id,
            db=db
        )

        if not autorizacion.autorizado:
            await TurnoAuthorizationService._registrar_escaneo(
                db=db,
                qr_id=qr_id,
                conductor_id=conductor_id,
                contrato_id=contrato_id,
                tipo="OPERATIVO",
                resultado="RECHAZADO",
                motivo=autorizacion.mensaje
            )
            return {"autorizado": False, "mensaje": autorizacion.mensaje}

        # 4. Generar autorización temporal
        import uuid
        auth_token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(minutes=5)

        insert_autorizacion = text("""
            INSERT INTO auth.autorizacion_inicio (
                id, token, contrato_id, chofer_id, vehiculo_id, control_base_id,
                tipo_contrato, turno_contractual, dia_contractual,
                created_at, expires_at, qr_referencia, created_by
            ) VALUES (
                gen_random_uuid(), :auth_token, :contrato_id, :conductor_id, :vehiculo_id, :control_base_id,
                :tipo_contrato, :turno_contractual, :dia_contractual,
                NOW(), :expires_at, :qr_referencia, :created_by
            )
            RETURNING id
        """)
        result = await db.execute(insert_autorizacion, {
            "auth_token": auth_token,
            "contrato_id": contrato_id,
            "conductor_id": conductor_id,
            "vehiculo_id": autorizacion.vehiculo_id,
            "control_base_id": control_base_id,
            "tipo_contrato": autorizacion.tipo_contrato,
            "turno_contractual": autorizacion.turno_contractual,
            "dia_contractual": autorizacion.dia_contractual,
            "expires_at": expires_at,
            "qr_referencia": qr_id,
            "created_by": propietario_id
        })
        autorizacion_id = result.scalar()

        # 5. Registrar escaneo exitoso
        await TurnoAuthorizationService._registrar_escaneo(
            db=db,
            qr_id=qr_id,
            conductor_id=conductor_id,
            contrato_id=contrato_id,
            tipo="OPERATIVO",
            resultado="EXITO",
            motivo=None,
            autorizacion_id=autorizacion_id
        )

        # 6. Incrementar usos
        await db.execute(
            text("UPDATE fleet.contrato_qr SET usos = usos + 1 WHERE id = :qr_id"),
            {"qr_id": qr_id}
        )
        await db.commit()

        return {
            "autorizado": True,
            "mensaje": "Autorización concedida",
            "auth_token": auth_token,
            "expires_at": expires_at
        }

    @staticmethod
    async def _registrar_escaneo(
        db: AsyncSession,
        qr_id: UUID,
        conductor_id: UUID,
        contrato_id: UUID,
        tipo: str,
        resultado: str,
        motivo: Optional[str] = None,
        autorizacion_id: Optional[UUID] = None
    ) -> None:
        """Registra un escaneo de QR en public.escaneo_qr."""
        insert = text("""
            INSERT INTO public.escaneo_qr (
                id, comercio_id, viaje_id, contrato_id, tipo_qr, resultado, motivo, autorizacion_id,
                user_agent, ip_address, created_at
            ) VALUES (
                gen_random_uuid(), NULL, NULL, :contrato_id, :tipo, :resultado, :motivo, :autorizacion_id,
                NULL, NULL, NOW()
            )
        """)
        await db.execute(insert, {
            "contrato_id": contrato_id,
            "tipo": tipo,
            "resultado": resultado,
            "motivo": motivo,
            "autorizacion_id": autorizacion_id
        })