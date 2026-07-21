"""
File storage service (local, S3, Cloudinary ready)
"""

import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import UploadFile

from app.core.config import settings


class StorageService:
    """Handle file uploads to local filesystem"""
    
    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE
        self.storage_path = Path(settings.STORAGE_PATH)
        
        if self.storage_type == "local":
            self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def save_photo(
        self,
        file: UploadFile,
        viaje_id: str,
        usuario_id: str,
        prefix: str = "interior"
    ) -> str:
        """Save a photo and return its URL"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        file_extension = Path(file.filename).suffix if file.filename else ".jpg"
        filename = f"{prefix}_{viaje_id}_{timestamp}_{unique_id}{file_extension}"
        
        if self.storage_type == "local":
            date_path = datetime.now().strftime("%Y/%m/%d")
            full_path = self.storage_path / "fotos" / date_path
            full_path.mkdir(parents=True, exist_ok=True)
            
            file_path = full_path / filename
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            return f"/uploads/fotos/{date_path}/{filename}"
        
        # TODO: Implement S3 or Cloudinary
        raise NotImplementedError(f"Storage type {self.storage_type} not implemented")
    
    async def save_document(
        self,
        file: UploadFile,
        usuario_id: str,
        tipo_documento: str
    ) -> str:
        """
        Save a driver document and return its URL
        
        Documents are stored in ./uploads/documentos/YYYY/MM/DD/
        Filename format: {tipo_documento}_{usuario_id}_{timestamp}_{uuid}{extension}
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        # Determinar extensión
        file_extension = Path(file.filename).suffix if file.filename else ".pdf"
        if not file_extension:
            file_extension = ".pdf"  # Default para documentos
        
        # Forzar lowercase
        file_extension = file_extension.lower()
        
        filename = f"{tipo_documento}_{usuario_id}_{timestamp}_{unique_id}{file_extension}"
        
        if self.storage_type == "local":
            date_path = datetime.now().strftime("%Y/%m/%d")
            full_path = self.storage_path / "documentos" / date_path
            full_path.mkdir(parents=True, exist_ok=True)
            
            file_path = full_path / filename
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            return f"/uploads/documentos/{date_path}/{filename}"
        
        # TODO: Implement S3 or Cloudinary
        raise NotImplementedError(f"Storage type {self.storage_type} not implemented")
    
    async def delete_file(self, url: str) -> bool:
        """Delete a file by its URL"""
        if self.storage_type == "local" and url.startswith("/uploads/"):
            relative_path = url[9:]  # Remove /uploads/
            full_path = self.storage_path / relative_path
            if full_path.exists():
                full_path.unlink()
                return True
        return False
    
    async def get_file_path(self, url: str) -> Optional[Path]:
        """Get the filesystem path for a given URL"""
        if self.storage_type == "local" and url.startswith("/uploads/"):
            relative_path = url[9:]
            full_path = self.storage_path / relative_path
            if full_path.exists():
                return full_path
        return None


storage_service = StorageService()