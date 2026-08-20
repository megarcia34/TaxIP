import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID

from app.core.email import send_notificacion_vencimiento_email
from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificacionVencimientoService:
    """Servicio para gestionar notificaciones de vencimiento de documentos"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def verificar_y_enviar_notificaciones(self) -> Dict:
        """
        Verifica documentos por vencer y envía notificaciones
        Retorna: { "enviados": N, "errores": N, "detalles": [...] }
        """
        resultados = {
            "enviados": 0,
            "errores": 0,
            "detalles": []
        }

        documentos = await self._obtener_documentos_por_vencer()

        if not documentos:
            logger.info("📋 No hay documentos por vencer que requieran notificación")
            return resultados

        logger.info(f"📋 Se encontraron {len(documentos)} documentos por vencer")

        for doc in documentos:
            try:
                logger.info(f"📝 Procesando: {doc['subtipo']} - {doc['numero']} ({doc['dias_restantes']} días)")

                ya_notificado = await self._ya_notificado_recientemente(
                    doc["documento_id"],
                    doc["nivel"]
                )

                if ya_notificado:
                    logger.info(f"⏭️ Documento {doc['subtipo']} ya notificado recientemente")
                    continue

                email = await self._obtener_email_propietario(doc["propietario_id"])

                if not email:
                    logger.warning(f"❌ Propietario {doc['propietario_id']} sin email")
                    resultados["errores"] += 1
                    continue

                logger.info(f"📧 Enviando email a {email}")
                email_enviado = await self._enviar_email(
                    email=email,
                    documento=doc
                )

                if email_enviado:
                    await self._registrar_notificacion(
                        documento_id=doc["documento_id"],
                        propietario_id=doc["propietario_id"],
                        entidad_tipo=doc["entidad_tipo"],
                        tipo_documento=doc["subtipo"],
                        numero=doc["numero"],
                        nivel=doc["nivel"],
                        dias_restantes=doc["dias_restantes"],
                        fecha_vencimiento=doc["fecha_vencimiento"],
                        email_enviado=True
                    )
                    resultados["enviados"] += 1
                    resultados["detalles"].append({
                        "documento": doc["subtipo"],
                        "numero": doc["numero"],
                        "email": email,
                        "dias": doc["dias_restantes"],
                        "estado": "enviado"
                    })
                    logger.info(f"✅ Notificación enviada para {doc['subtipo']} - {doc['numero']}")
                else:
                    resultados["errores"] += 1
                    logger.error(f"❌ Error enviando email para {doc['subtipo']}")

            except Exception as e:
                logger.error(f"❌ Error procesando documento {doc.get('subtipo', 'unknown')}: {e}")
                resultados["errores"] += 1

        logger.info(f"📊 Resumen: {resultados['enviados']} enviados, {resultados['errores']} errores")
        return resultados

    async def _obtener_documentos_por_vencer(self) -> List[Dict]:
        """Obtiene documentos con vencimiento en los próximos 30 días"""
        query = text("""
            WITH documentos_propietario AS (
                SELECT 
                    dp.id as documento_id,
                    'propietario' as entidad_tipo,
                    dp.propietario_id,
                    dp.tipo_documento as subtipo,
                    dp.numero,
                    dp.fecha_vencimiento,
                    'documento_propietario' as tabla
                FROM fleet.documento_propietario dp
                WHERE dp.fecha_vencimiento IS NOT NULL
            ),
            documentos_vehiculo AS (
                SELECT 
                    dv.id as documento_id,
                    'vehiculo' as entidad_tipo,
                    pv.propietario_id,
                    dv.tipo_documento as subtipo,
                    dv.numero,
                    COALESCE(dv.vtv_fecha_vencimiento, dv.seguro_fecha_vencimiento, dv.fecha_vencimiento) as fecha_vencimiento,
                    'documento_vehiculo' as tabla
                FROM fleet.documento_vehiculo dv
                JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = dv.vehiculo_id
                WHERE dv.activo = true
            ),
            all_documentos AS (
                SELECT * FROM documentos_propietario
                UNION ALL
                SELECT * FROM documentos_vehiculo
            )
            SELECT 
                documento_id,
                entidad_tipo,
                propietario_id,
                subtipo,
                numero,
                fecha_vencimiento,
                (fecha_vencimiento - NOW()::DATE) as dias_restantes,
                CASE 
                    WHEN (fecha_vencimiento - NOW()::DATE) < 0 THEN 'vencido'
                    WHEN (fecha_vencimiento - NOW()::DATE) <= 7 THEN 'critico'
                    WHEN (fecha_vencimiento - NOW()::DATE) <= 15 THEN 'urgente'
                    WHEN (fecha_vencimiento - NOW()::DATE) <= 30 THEN 'preventivo'
                    ELSE 'vigente'
                END as nivel
            FROM all_documentos
            WHERE fecha_vencimiento IS NOT NULL
              AND (fecha_vencimiento - NOW()::DATE) <= 30
            ORDER BY dias_restantes ASC
        """)

        result = await self.db.execute(query)
        rows = result.all()

        return [
            {
                "documento_id": str(row[0]),
                "entidad_tipo": row[1],
                "propietario_id": str(row[2]),
                "subtipo": row[3],
                "numero": row[4],
                "fecha_vencimiento": row[5],
                "dias_restantes": int(row[6]) if row[6] is not None else 0,
                "nivel": row[7]
            }
            for row in rows
        ]

    async def _ya_notificado_recientemente(self, documento_id: str, nivel: str) -> bool:
        """Verifica si ya se envió notificación para este documento y nivel en las últimas 24h"""
        query = text("""
            SELECT COUNT(*) FROM fleet.notificacion_vencimiento
            WHERE documento_id = :documento_id
              AND nivel = :nivel
              AND email_enviado = true
              AND created_at > NOW() - INTERVAL '1 day'
        """)
        result = await self.db.execute(query, {
            "documento_id": UUID(documento_id),
            "nivel": nivel
        })
        count = result.scalar() or 0
        return count > 0

    async def _obtener_email_propietario(self, propietario_id: str) -> Optional[str]:
        """Obtiene el email del propietario"""
        query = text("""
            SELECT email FROM auth.usuario WHERE id = :propietario_id AND activo = true
        """)
        result = await self.db.execute(query, {"propietario_id": UUID(propietario_id)})
        row = result.first()
        return row[0] if row else None

    async def _enviar_email(self, email: str, documento: Dict) -> bool:
        """Envía el email de notificación de vencimiento"""
        try:
            return await send_notificacion_vencimiento_email(
                to_email=email,
                tipo_documento=documento["subtipo"],
                numero=documento["numero"],
                fecha_vencimiento=documento["fecha_vencimiento"],
                dias_restantes=documento["dias_restantes"],
                nivel=documento["nivel"]
            )
        except Exception as e:
            logger.error(f"❌ Error enviando email: {e}")
            return False

    async def _registrar_notificacion(
        self,
        documento_id: str,
        propietario_id: str,
        entidad_tipo: str,
        tipo_documento: str,
        numero: str,
        nivel: str,
        dias_restantes: int,
        fecha_vencimiento: str,
        email_enviado: bool = True
    ):
        """Registra la notificación en la base de datos"""
        query = text("""
            INSERT INTO fleet.notificacion_vencimiento (
                documento_id, propietario_id, entidad_tipo, tipo_documento, numero,
                nivel, dias_restantes, fecha_vencimiento,
                email_enviado, email_enviado_en
            ) VALUES (
                :documento_id, :propietario_id, :entidad_tipo, :tipo_documento, :numero,
                :nivel, :dias_restantes, :fecha_vencimiento,
                :email_enviado, :email_enviado_en
            )
        """)

        await self.db.execute(query, {
            "documento_id": UUID(documento_id),
            "propietario_id": UUID(propietario_id),
            "entidad_tipo": entidad_tipo,
            "tipo_documento": tipo_documento,
            "numero": numero,
            "nivel": nivel,
            "dias_restantes": dias_restantes,
            "fecha_vencimiento": fecha_vencimiento,
            "email_enviado": email_enviado,
            "email_enviado_en": datetime.now() if email_enviado else None
        })
        await self.db.commit()
        logger.info(f"💾 Notificación registrada: {tipo_documento} - {numero} ({nivel})")