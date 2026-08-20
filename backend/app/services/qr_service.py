# app/services/qr_service.py
"""
Servicio de gestión de QR operativos y autorización de turnos
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.services.turno_authorization import TurnoAuthorizationService


class QRService:
    """Servicio para generación y escaneo de QR operativos"""

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
        # Verificar contrato
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

        control_base_id = row[1]

        import uuid
        token = str(uuid.uuid4())
        fecha_expiracion = datetime.now() + timedelta(days=dias_validez)

        # Guardar QR
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
        Escanea un QR operativo y ejecuta autorización.
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

        # 3. Ejecutar autorización (C1)
        autorizacion = await TurnoAuthorizationService.autorizar_inicio_jornada(
            usuario_id=conductor_id,
            contrato_id=contrato_id,
            db=db
        )

        if not autorizacion.autorizado:
            await QRService._registrar_escaneo(
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
        await QRService._registrar_escaneo(
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

    # =============================================================
    # C3 — CONSUMIR AUTORIZACIÓN Y CREAR TURNO
    # =============================================================

    @staticmethod
    async def consumir_autorizacion(
        auth_token: str,
        km_inicial: float,
        combustible_inicial: str,
        db: AsyncSession
    ) -> dict:
        """
        Consume una autorización temporal y crea un turno.
        """
        # 1. Buscar autorización por token
        query = text("""
            SELECT 
                ai.id, ai.contrato_id, ai.chofer_id, ai.vehiculo_id,
                ai.control_base_id, ai.tipo_contrato, ai.turno_contractual,
                ai.dia_contractual, ai.expires_at, ai.used_at,
                v.patente
            FROM auth.autorizacion_inicio ai
            JOIN fleet.vehiculo v ON v.id = ai.vehiculo_id
            WHERE ai.token = :auth_token
        """)
        result = await db.execute(query, {"auth_token": auth_token})
        row = result.first()
        if not row:
            return {"success": False, "mensaje": "Autorización no encontrada"}

        (auth_id, contrato_id, chofer_id, vehiculo_id,
         control_base_id, tipo_contrato, turno_contractual,
         dia_contractual, expires_at, used_at, patente) = row

        # 2. Validar expiración
        if expires_at and expires_at < datetime.now():
            return {"success": False, "mensaje": "Autorización expirada"}

        # 3. Validar que no esté usada
        if used_at:
            return {"success": False, "mensaje": "Autorización ya utilizada"}

        # 4. Revalidar contrato ACTIVO
        query_contrato = text("""
            SELECT estado_contrato, activo FROM fleet.contrato_vehiculo
            WHERE id = :contrato_id
        """)
        result = await db.execute(query_contrato, {"contrato_id": contrato_id})
        row = result.first()
        if not row or row[0] != "ACTIVO" or not row[1]:
            return {"success": False, "mensaje": "El contrato ya no está ACTIVO"}

        # 5. Revalidar conductor ocupado
        query_ocupado = text("""
            SELECT id FROM fleet.turno_chofer
            WHERE chofer_id = :chofer_id AND estado = 'ACTIVO'
        """)
        result = await db.execute(query_ocupado, {"chofer_id": chofer_id})
        if result.first():
            return {"success": False, "mensaje": "El conductor ya tiene una jornada activa"}

        # 6. Revalidar vehículo ocupado
        query_vehiculo_ocupado = text("""
            SELECT id FROM fleet.turno_chofer
            WHERE vehiculo_id = :vehiculo_id AND estado = 'ACTIVO'
        """)
        result = await db.execute(query_vehiculo_ocupado, {"vehiculo_id": vehiculo_id})
        if result.first():
            return {"success": False, "mensaje": f"El vehículo {patente} ya tiene una jornada activa"}

        try:
            # 7a. Marcar autorización como usada
            await db.execute(
                text("UPDATE auth.autorizacion_inicio SET used_at = NOW() WHERE id = :auth_id"),
                {"auth_id": auth_id}
            )

            # 7b. Crear turno
            insert_turno = text("""
                INSERT INTO fleet.turno_chofer (
                    id, contrato_id, chofer_id, vehiculo_id,
                    estado, inicio_turno, km_inicial, combustible_inicial,
                    snapshot_dia_contractual, snapshot_turno_contractual
                ) VALUES (
                    gen_random_uuid(), :contrato_id, :chofer_id, :vehiculo_id,
                    'ACTIVO', NOW(), :km_inicial, :combustible_inicial,
                    :dia_contractual, :turno_contractual
                )
                RETURNING id
            """)
            result = await db.execute(insert_turno, {
                "contrato_id": contrato_id,
                "chofer_id": chofer_id,
                "vehiculo_id": vehiculo_id,
                "km_inicial": km_inicial,
                "combustible_inicial": combustible_inicial,
                "dia_contractual": dia_contractual,
                "turno_contractual": turno_contractual
            })
            turno_id = result.scalar()

            # 7c. Actualizar chofer_vehiculo (compatibilidad)
            update_cv = text("""
                UPDATE fleet.chofer_vehiculo
                SET vehiculo_id = :vehiculo_id, estado_laboral = 'ocupado', updated_at = NOW()
                WHERE usuario_id = :chofer_id AND control_base_id = :control_base_id
            """)
            await db.execute(update_cv, {
                "vehiculo_id": vehiculo_id,
                "chofer_id": chofer_id,
                "control_base_id": control_base_id
            })

            # Confirmar transacción
            await db.commit()

            return {
                "success": True,
                "turno_id": turno_id,
                "mensaje": "Jornada iniciada correctamente",
                "contrato_id": contrato_id,
                "vehiculo_id": vehiculo_id,
                "patente": patente
            }
        except Exception as e:
            await db.rollback()
            return {"success": False, "mensaje": f"Error al crear turno: {str(e)}"}