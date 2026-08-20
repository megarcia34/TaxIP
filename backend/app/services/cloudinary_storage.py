"""
Servicio de almacenamiento en Cloudinary para comprobantes de gastos
"""

import cloudinary
import cloudinary.uploader
from typing import Optional
from fastapi import UploadFile
import uuid
from datetime import datetime
import re

from app.core.config import settings


class CloudinaryStorageService:
    """Servicio para subir y gestionar archivos en Cloudinary"""

    def __init__(self):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )

    async def upload_comprobante(
        self,
        file: UploadFile,
        propietario_id: str,
        gasto_id: str,
        tipo: str = "gasto_vehiculo"
    ) -> str:
        """
        Sube un comprobante a Cloudinary y retorna la URL segura.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        # Obtener extensión
        file_extension = file.filename.split('.')[-1] if file.filename else 'pdf'
        if file_extension.lower() not in ['jpg', 'jpeg', 'png', 'pdf']:
            file_extension = 'pdf'
        
        # Leer el archivo
        content = await file.read()
        
        # Subir a Cloudinary
        upload_result = cloudinary.uploader.upload(
            content,
            folder=f"comprobantes/{tipo}/{propietario_id}",
            public_id=f"{gasto_id}_{timestamp}_{unique_id}",
            resource_type="auto",
            use_filename=True,
            unique_filename=True,
            format=file_extension
        )
        
        return upload_result.get("secure_url")

    async def delete_comprobante(self, public_id: str) -> bool:
        """Elimina un comprobante de Cloudinary por su public_id."""
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception:
            return False

    def extract_public_id_from_url(self, url: str) -> Optional[str]:
        """Extrae el public_id de una URL de Cloudinary."""
        if not url:
            return None
        match = re.search(r'/upload/(?:v\d+/)?(.+?)(?:\.[^.]+)?$', url)
        if match:
            return match.group(1)
        return None


cloudinary_storage = CloudinaryStorageService()