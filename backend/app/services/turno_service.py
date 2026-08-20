"""
Servicio de gestión de turnos (Check-in / Check-out) CON HORARIOS FLEXIBLES
"""

import uuid
from uuid import UUID
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy import text
from fastapi import HTTPException, status

from app.models.fleet import ContratoVehiculo, Vehiculo, ChoferVehiculo, CategoriaGasto
from app.models.turno import TurnoChofer
from app.models.gasto_turno import GastoTurno
from app.models.auth import Usuario
from app.models.trip import ViajeSolicitado
from app.services.turno_authorization import TurnoAuthorizationService


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
        if total_horas >= 12:
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
            chofer_vehiculo.estado_laboral = 'ocupado'

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

        turno.km_final = km_final
        turno.combustible_final = combustible_final
        turno.recaudacion_ticketera_calle = recaudacion_ticketera
        turno.fin_turno = datetime.now()
        turno.estado = 'PENDIENTE_CONFIRMACION'

        await db.commit()
        await db.refresh(turno)

        return {
            "turno_id": turno.id,
            "estado": turno.estado,
            "mensaje": "Turno cerrado correctamente. Pendiente de confirmación y liquidación."
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
            WHERE id = :contrato_id AND estado_contrato = 'ACTIVO' AND activo = true
        """)
        result = await db.execute(query, {"contrato_id": contrato_id})
        row = result.first()
        if not row:
            raise HTTPException(404, "Contrato no encontrado o no ACTIVO")

        control_base_id = row[1]

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

        return {
            "token": token,
            "fecha_expiracion": fecha_expiracion
        }

    @staticmethod
    async def escanear_qr(
        conductor_id: UUID,
        token: str,
        db: AsyncSession
    ) -> dict:
        """
        Escanea un QR operativo, ejecuta C1 y genera autorización temporal.
        """
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

        query_tenant = text("SELECT control_base_id FROM auth.usuario WHERE id = :conductor_id")
        result = await db.execute(query_tenant, {"conductor_id": conductor_id})
        conductor_tenant = result.scalar()
        if conductor_tenant != control_base_id:
            return {"autorizado": False, "mensaje": "El QR pertenece a otro tenant"}

        autorizacion = await TurnoAuthorizationService.autorizar_inicio_jornada(
            usuario_id=conductor_id,
            contrato_id=contrato_id,
            db=db
        )

        if not autorizacion.autorizado:
            await TurnoService._registrar_escaneo(
                db=db,
                qr_id=qr_id,
                conductor_id=conductor_id,
                contrato_id=contrato_id,
                tipo="OPERATIVO",
                resultado="RECHAZADO",
                motivo=autorizacion.mensaje
            )
            return {"autorizado": False, "mensaje": autorizacion.mensaje}

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

        await TurnoService._registrar_escaneo(
            db=db,
            qr_id=qr_id,
            conductor_id=conductor_id,
            contrato_id=contrato_id,
            tipo="OPERATIVO",
            resultado="EXITO",
            motivo=None,
            autorizacion_id=autorizacion_id
        )

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