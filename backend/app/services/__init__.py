# app/services/__init__.py
"""
Servicios del sistema
"""

# Rentabilidad
from app.services.rentabilidad import (
    obtener_configuracion_tenant,
    calcular_ppv,
    calcular_costo_medio_ponderado_procesadoras,
    calcular_rentabilidad_viaje,
    calcular_rentabilidad_periodo,
    recalcular_tablas_rentabilidad
)

# Optimización
from app.services.optimizacion import (
    analizar_medios_pago,
    calcular_benchmarking
)

# Turnos
from app.services.turno_service import TurnoService
from app.services.turno_authorization import TurnoAuthorizationService

# QR
from app.services.qr_service import QRService

# Liquidación
from app.services.liquidacion_context import LiquidacionContext
from app.services.liquidacion_engine import LiquidacionEngine

# Cloudinary
from app.services.cloudinary_storage import CloudinaryStorageService

# Email (CORREGIDO)
from app.services.email_validation import EmailValidator


__all__ = [
    # Rentabilidad
    'obtener_configuracion_tenant',
    'calcular_ppv',
    'calcular_costo_medio_ponderado_procesadoras',
    'calcular_rentabilidad_viaje',
    'calcular_rentabilidad_periodo',
    'recalcular_tablas_rentabilidad',
    
    # Optimización
    'analizar_medios_pago',
    'calcular_benchmarking',
    
    # Turnos
    'TurnoService',
    'TurnoAuthorizationService',
    
    # QR
    'QRService',
    
    # Liquidación
    'LiquidacionContext',
    'LiquidacionEngine',
    
    # Cloudinary
    'CloudinaryStorageService',
    
    # Email
    'EmailValidator',
]