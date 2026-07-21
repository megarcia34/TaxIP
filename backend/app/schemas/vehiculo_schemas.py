"""
Vehicle schemas for QR and photo endpoints
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID


class GenerarQRRequest(BaseModel):
    chofer_vehiculo_id: UUID


class GenerarQRResponse(BaseModel):
    qr_code_base64: str
    token: str
    expiration_minutes: int


class ValidarQRRequest(BaseModel):
    qr_token: str


class ValidarQRResponse(BaseModel):
    es_valido: bool
    datos_conductor: Optional[Dict[str, Any]] = None
    datos_vehiculo: Optional[Dict[str, Any]] = None
    mensaje: Optional[str] = None


class SubirFotoRequest(BaseModel):
    viaje_id: UUID


class SubirFotoResponse(BaseModel):
    success: bool
    foto_id: UUID
    url: str
    mensaje: str