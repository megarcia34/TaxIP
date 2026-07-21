# app/services/vehiculo_service.py
"""
Servicio de gestión de vehículos con QR fijo
"""

import uuid
import qrcode
from io import BytesIO
import base64
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from fastapi import HTTPException, status

from app.models.fleet import Vehiculo, PropietarioVehiculo
from app.models.auth import Usuario
from app.core.config import settings


class VehiculoService:
    """Servicio para gestión de vehículos y QR"""

    @staticmethod
    async def crear_vehiculo(
        db: AsyncSession,
        propietario_id: uuid.UUID,
        control_base_id: uuid.UUID,
        patente: str,
        marca: str = None,
        modelo: str = None,
        anio: int = None,
        numero_licencia: str = None
    ) -> dict:
        """
        Crear un nuevo vehículo y generar QR fijo
        """
        # Validar patente única
        existing = await db.execute(
            select(Vehiculo).where(Vehiculo.patente == patente)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La patente ya está registrada"
            )

        # Verificar que el propietario existe
        propietario = await db.get(Usuario, propietario_id)
        if not propietario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Propietario no encontrado"
            )

        # Crear vehículo
        vehiculo = Vehiculo(
            control_base_id=control_base_id,
            patente=patente,
            marca=marca,
            modelo=modelo,
            anio=anio,
            numero_licencia=numero_licencia,
            qr_uuid=uuid.uuid4(),
            qr_activo=True,
            activo=True
        )
        db.add(vehiculo)
        await db.flush()

        # Crear relación propietario-vehículo
        propietario_vehiculo = PropietarioVehiculo(
            propietario_id=propietario_id,
            vehiculo_id=vehiculo.id,
            fecha_inicio=datetime.now().date(),
            activo=True
        )
        db.add(propietario_vehiculo)
        await db.commit()
        await db.refresh(vehiculo)

        # Generar QR
        qr_data = await VehiculoService.generar_qr(vehiculo.id, vehiculo.qr_uuid)

        return {
            "vehiculo": vehiculo,
            "qr_url": qr_data["qr_url"],
            "qr_base64": qr_data["qr_base64"]
        }

    @staticmethod
    async def generar_qr(vehiculo_id: uuid.UUID, qr_uuid: uuid.UUID) -> dict:
        """
        Generar código QR del vehículo
        """
        # Construir URL pública
        qr_url = f"{settings.API_BASE_URL}/public/qr/{qr_uuid}"
        
        # Generar imagen QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()

        return {
            "qr_url": qr_url,
            "qr_base64": qr_base64
        }

    @staticmethod
    async def obtener_vehiculo_por_qr(
        db: AsyncSession,
        qr_uuid: uuid.UUID
    ) -> Vehiculo:
        """
        Obtener vehículo por QR UUID
        """
        result = await db.execute(
            select(Vehiculo)
            .where(
                and_(
                    Vehiculo.qr_uuid == qr_uuid,
                    Vehiculo.qr_activo == True,
                    Vehiculo.activo == True
                )
            )
        )
        vehiculo = result.scalar_one_or_none()
        
        if not vehiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehículo no encontrado o QR inactivo"
            )
        
        return vehiculo