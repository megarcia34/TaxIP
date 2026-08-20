"""
Owner module schemas (vehicle expenses, maintenance, contracts, tires)
"""

from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Union, Any, Literal
from uuid import UUID
from datetime import date, datetime, time


# ============================================
# TIPOS NORMALIZADOS PARA CONTRATOS
# ============================================

TipoContrato = Literal["ALQUILER", "PORCENTAJE", "AUTO_GESTION"]
ModalidadComputo = Literal["DIARIO", "SEMANAL"]
TratamientoDia = Literal["POR_DISPONIBILIDAD", "POR_USO_EFECTIVO"]
DiaSemana = Literal["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]


# ============================================
# FUNCIONES AUXILIARES PARA HORARIOS
# ============================================

def validar_horario(hora: str) -> bool:
    """Valida formato HH:MM"""
    try:
        datetime.strptime(hora, "%H:%M")
        return True
    except ValueError:
        return False


def calcular_minutos(hora: str) -> int:
    """Convierte HH:MM a minutos desde medianoche"""
    h, m = map(int, hora.split(':'))
    return h * 60 + m


def calcular_duracion_horas(inicio: str, fin: str) -> float:
    """
    Calcula duración en horas entre dos horarios (soporta cruce de medianoche).
    
    Ejemplos:
    06:00-14:00 → 8.0 horas
    22:00-06:00 → 8.0 horas (cruza medianoche)
    14:00-22:00 → 8.0 horas
    """
    i_h, i_m = map(int, inicio.split(':'))
    f_h, f_m = map(int, fin.split(':'))
    
    inicio_minutos = i_h * 60 + i_m
    fin_minutos = f_h * 60 + f_m
    
    if fin_minutos <= inicio_minutos:
        return (24 * 60 - inicio_minutos + fin_minutos) / 60
    else:
        return (fin_minutos - inicio_minutos) / 60


def es_horario_posterior(hora1: str, hora2: str) -> bool:
    """
    Determina si hora1 es posterior a hora2.
    
    Soporta cruce de medianoche:
    - 08:00 es posterior a 06:00 → True (mismo día)
    - 06:00 es posterior a 22:00 → True (cruza medianoche)
    - 14:00 es posterior a 06:00 → True (mismo día)
    - 06:00 es posterior a 14:00 → False (mismo día, pero anterior)
    """
    min1 = calcular_minutos(hora1)
    min2 = calcular_minutos(hora2)
    
    if min1 > min2:
        return True
    if min1 < min2:
        return (min1 + 24 * 60) - min2 > 0
    return False


# ============================================
# GASTOS
# ============================================

class GastoVehiculoRequest(BaseModel):
    """Register vehicle expense"""
    vehiculo_id: UUID
    tipo_gasto: str = Field(..., description="combustible, mantenimiento, reparacion, seguro, impuesto, patente, otros")
    monto: float = Field(..., gt=0)
    descripcion: Optional[str] = None
    kilometraje: Optional[int] = None
    comprobante_url: Optional[str] = None
    fecha_gasto: date

    class Config:
        from_attributes = True


class GastoVehiculoResponse(BaseModel):
    """Vehicle expense response"""
    id: UUID
    vehiculo_id: UUID
    vehiculo_patente: str
    tipo_gasto: Optional[str] = None
    monto: float
    descripcion: Optional[str] = None
    kilometraje: Optional[int] = None
    comprobante_url: Optional[str] = None
    fecha_gasto: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ResumenGastosResponse(BaseModel):
    """Expense summary response"""
    total_gastos: float
    por_tipo: Dict[str, float]
    por_vehiculo: List[Dict[str, Union[str, float]]]
    periodo_desde: date
    periodo_hasta: date

    class Config:
        from_attributes = True


# ============================================
# MANTENIMIENTOS
# ============================================

class MantenimientoVehiculoRequest(BaseModel):
    """Register vehicle maintenance"""
    vehiculo_id: UUID
    tipo_servicio: str = Field(..., description="SERVICE_MENOR, SERVICE_MAYOR, NEUMATICOS, FRENOS, DISTRIBUCION, ALINEACION, CAMBIO_ACEITE, LUBRICACION, ELECTRICO, GENERAL")
    taller_nombre: str
    taller_direccion: Optional[str] = None
    costo: Optional[float] = None
    kilometraje: Optional[int] = None
    observaciones: Optional[str] = None
    fecha_servicio: date

    class Config:
        from_attributes = True


class MantenimientoVehiculoResponse(BaseModel):
    """Vehicle maintenance response"""
    id: UUID
    vehiculo_id: UUID
    vehiculo_patente: str
    tipo_servicio: Optional[str] = None
    taller_nombre: Optional[str] = None
    taller_direccion: Optional[str] = None
    costo: Optional[float] = None
    kilometraje: Optional[int] = None
    observaciones: Optional[str] = None
    fecha_servicio: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MantenimientoProximoResponse(BaseModel):
    """Próximo mantenimiento programado"""
    tipo_servicio: str
    tipo_nombre: str
    km_restante: Optional[int] = None
    dias_restantes: Optional[int] = None
    alerta_a: str
    urgencia: str

    class Config:
        from_attributes = True


class MantenimientoAlertasResponse(BaseModel):
    """Alertas de mantenimiento"""
    total_alertas: int
    vehiculos_con_alertas: List[Dict[str, Union[str, int, List]]]

    class Config:
        from_attributes = True


# ============================================
# CONTRATOS (VERSIÓN CORREGIDA)
# ============================================

class ContratoCreate(BaseModel):
    """Crear un nuevo contrato con horarios flexibles"""
    vehiculo_id: UUID
    chofer_id: UUID
    tipo_contrato: TipoContrato
    
    # Horarios flexibles
    hora_inicio: str = Field(
        ..., 
        pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        description="Hora de inicio del turno (HH:MM)"
    )
    hora_fin: str = Field(
        ..., 
        pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        description="Hora de fin del turno (HH:MM)"
    )
    duracion_minima_horas: int = Field(
        6, 
        ge=1, 
        le=24,
        description="Duración mínima del turno en horas (default: 6)"
    )
    permite_extension: bool = Field(
        False,
        description="Permite extender el horario más allá de hora_fin"
    )
    hora_fin_extension: Optional[str] = Field(
        None,
        pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        description="Hora límite de extensión (solo si permite_extension = true)"
    )
    
    # Campos para ALQUILER
    canon_diario: Optional[float] = Field(None, gt=0)
    km_incluidos_dia: Optional[float] = Field(None, gt=0)
    valor_km_excedente: Optional[float] = Field(None, ge=0)
    modalidad_computo: Optional[ModalidadComputo] = None
    dias_contractuales: Optional[List[DiaSemana]] = None
    tratamiento_dia_no_trabajado: Optional[TratamientoDia] = None
    
    # NUEVO: Compensación de KM
    compensacion_km: Optional[str] = Field(
        'DIARIA',
        pattern="^(DIARIA|ACUMULADA|COMPENSADA)$",
        description="Modo de compensación de KM excedentes"
    )
    
    # Para PORCENTAJE
    porcentaje_chofer: Optional[float] = Field(None, ge=0, le=100)
    
    # Fechas de vigencia
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    dia_inicio_semana: Optional[DiaSemana] = None

    @model_validator(mode='after')
    def validate_horarios(self):
        """
        Valida que los horarios sean lógicos y consistentes.
        
        Soporta:
        - Horarios normales: 06:00-14:00
        - Cruce de medianoche: 22:00-06:00
        """
        if not validar_horario(self.hora_inicio) or not validar_horario(self.hora_fin):
            raise ValueError("Formato de hora inválido. Use HH:MM")
        
        if self.hora_inicio == self.hora_fin:
            raise ValueError("hora_inicio y hora_fin no pueden ser iguales")
        
        duracion = calcular_duracion_horas(self.hora_inicio, self.hora_fin)
        if duracion < self.duracion_minima_horas:
            raise ValueError(
                f"La duración del turno ({duracion:.1f}h) es menor "
                f"a la duración mínima configurada ({self.duracion_minima_horas}h)"
            )
        
        if self.permite_extension:
            if not self.hora_fin_extension:
                raise ValueError("Si permite_extension = true, hora_fin_extension es obligatorio")
            if not validar_horario(self.hora_fin_extension):
                raise ValueError("Formato de hora inválido para hora_fin_extension. Use HH:MM")
            if not es_horario_posterior(self.hora_fin_extension, self.hora_fin):
                raise ValueError("hora_fin_extension debe ser posterior a hora_fin")
        else:
            if self.hora_fin_extension is not None:
                raise ValueError("Si permite_extension = false, hora_fin_extension debe ser null")
        
        return self

    @model_validator(mode='after')
    def validate_tipo_contrato(self):
        """Valida parámetros según tipo de contrato"""
        if self.tipo_contrato == "ALQUILER":
            if self.canon_diario is None:
                raise ValueError("canon_diario es obligatorio para ALQUILER")
            if self.km_incluidos_dia is None:
                raise ValueError("km_incluidos_dia es obligatorio para ALQUILER")
            if self.valor_km_excedente is None:
                raise ValueError("valor_km_excedente es obligatorio para ALQUILER")
            if self.modalidad_computo is None:
                raise ValueError("modalidad_computo es obligatoria para ALQUILER")
            if self.dias_contractuales is None or len(self.dias_contractuales) == 0:
                raise ValueError("dias_contractuales es obligatorio y debe tener al menos un día")
            if self.tratamiento_dia_no_trabajado is None:
                raise ValueError("tratamiento_dia_no_trabajado es obligatorio para ALQUILER")
            
            if self.modalidad_computo == "SEMANAL" and self.dia_inicio_semana is None:
                raise ValueError("dia_inicio_semana es obligatorio para modalidad SEMANAL")
        
        elif self.tipo_contrato == "PORCENTAJE":
            if self.porcentaje_chofer is None:
                raise ValueError("porcentaje_chofer es obligatorio para PORCENTAJE")
        
        # ✅ CORREGIDO: Validar fechas de vigencia
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValueError("La fecha de finalización no puede ser anterior a la fecha de inicio")
        
        return self

    class Config:
        from_attributes = True


class ContratoResponse(BaseModel):
    """Respuesta de contrato con horarios flexibles"""
    id: UUID
    vehiculo_id: UUID
    patente: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    chofer_id: UUID
    chofer_nombre: Optional[str] = None
    chofer_apellido: Optional[str] = None
    tipo_contrato: str
    
    # Horarios flexibles
    hora_inicio: str
    hora_fin: str
    duracion_minima_horas: int
    permite_extension: bool
    hora_fin_extension: Optional[str] = None
    
    porcentaje_chofer: Optional[float] = None
    monto_diario: Optional[float] = None
    
    # ALQUILER
    canon_diario: Optional[float] = None
    km_incluidos_dia: Optional[float] = None
    valor_km_excedente: Optional[float] = None
    modalidad_computo: Optional[str] = None
    dias_contractuales: Optional[List[str]] = None
    tratamento_dia_no_trabajado: Optional[str] = None
    dia_inicio_semana: Optional[str] = None
    compensacion_km: Optional[str] = None
    
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    activo: bool
    estado_contrato: str

    class Config:
        from_attributes = True


class ConfigurarContratoRequest(BaseModel):
    """Configurar condiciones de un contrato pendiente con horarios flexibles"""
    tipo_contrato: TipoContrato
    
    # Horarios flexibles
    hora_inicio: str = Field(
        ..., 
        pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        description="Hora de inicio del turno (HH:MM)"
    )
    hora_fin: str = Field(
        ..., 
        pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        description="Hora de fin del turno (HH:MM)"
    )
    duracion_minima_horas: int = Field(
        6, 
        ge=1, 
        le=24,
        description="Duración mínima del turno en horas (default: 6)"
    )
    permite_extension: bool = Field(
        False,
        description="Permite extender el horario más allá de hora_fin"
    )
    hora_fin_extension: Optional[str] = Field(
        None,
        pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
        description="Hora límite de extensión (solo si permite_extension = true)"
    )
    
    # Campos para ALQUILER
    canon_diario: Optional[float] = Field(None, gt=0)
    km_incluidos_dia: Optional[float] = Field(None, gt=0)
    valor_km_excedente: Optional[float] = Field(None, ge=0)
    modalidad_computo: Optional[ModalidadComputo] = None
    dias_contractuales: Optional[List[DiaSemana]] = None
    tratamento_dia_no_trabajado: Optional[TratamientoDia] = None
    compensacion_km: Optional[str] = Field(
        'DIARIA',
        pattern="^(DIARIA|ACUMULADA|COMPENSADA)$",
        description="Modo de compensación de KM excedentes"
    )
    
    # Para PORCENTAJE
    porcentaje_chofer: Optional[float] = Field(None, ge=0, le=100)
    
    # Fechas de vigencia
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    dia_inicio_semana: Optional[DiaSemana] = None

    @model_validator(mode='after')
    def validate_horarios(self):
        if not validar_horario(self.hora_inicio) or not validar_horario(self.hora_fin):
            raise ValueError("Formato de hora inválido. Use HH:MM")
        
        if self.hora_inicio == self.hora_fin:
            raise ValueError("hora_inicio y hora_fin no pueden ser iguales")
        
        duracion = calcular_duracion_horas(self.hora_inicio, self.hora_fin)
        if duracion < self.duracion_minima_horas:
            raise ValueError(
                f"La duración del turno ({duracion:.1f}h) es menor "
                f"a la duración mínima configurada ({self.duracion_minima_horas}h)"
            )
        
        if self.permite_extension:
            if not self.hora_fin_extension:
                raise ValueError("Si permite_extension = true, hora_fin_extension es obligatorio")
            if not validar_horario(self.hora_fin_extension):
                raise ValueError("Formato de hora inválido para hora_fin_extension. Use HH:MM")
            if not es_horario_posterior(self.hora_fin_extension, self.hora_fin):
                raise ValueError("hora_fin_extension debe ser posterior a hora_fin")
        else:
            if self.hora_fin_extension is not None:
                raise ValueError("Si permite_extension = false, hora_fin_extension debe ser null")
        
        return self

    @model_validator(mode='after')
    def validate_tipo_contrato(self):
        if self.tipo_contrato == "ALQUILER":
            if self.canon_diario is None:
                raise ValueError("canon_diario es obligatorio para ALQUILER")
            if self.km_incluidos_dia is None:
                raise ValueError("km_incluidos_dia es obligatorio para ALQUILER")
            if self.valor_km_excedente is None:
                raise ValueError("valor_km_excedente es obligatorio para ALQUILER")
            if self.modalidad_computo is None:
                raise ValueError("modalidad_computo es obligatoria para ALQUILER")
            if self.dias_contractuales is None or len(self.dias_contractuales) == 0:
                raise ValueError("dias_contractuales es obligatorio y debe tener al menos un día")
            if self.tratamiento_dia_no_trabajado is None:
                raise ValueError("tratamiento_dia_no_trabajado es obligatorio para ALQUILER")
            
            if self.modalidad_computo == "SEMANAL" and self.dia_inicio_semana is None:
                raise ValueError("dia_inicio_semana es obligatorio para modalidad SEMANAL")
        
        elif self.tipo_contrato == "PORCENTAJE":
            if self.porcentaje_chofer is None:
                raise ValueError("porcentaje_chofer es obligatorio para PORCENTAJE")
        
        # ✅ CORREGIDO: Validar fechas de vigencia
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValueError("La fecha de finalización no puede ser anterior a la fecha de inicio")
        
        return self

    class Config:
        from_attributes = True


class ContratoPendienteResponse(BaseModel):
    """Contrato pendiente de configuración"""
    contrato_id: UUID
    vehiculo_id: UUID
    patente: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    chofer_id: UUID
    chofer_nombre: str
    solicitado_en: datetime

    class Config:
        from_attributes = True


class ChoferDisponibleResponse(BaseModel):
    """Chofer disponible para contratar"""
    id: UUID
    email: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    calificacion_promedio: Optional[float] = None
    total_calificaciones: Optional[int] = None

    class Config:
        from_attributes = True


# ============================================
# INGRESOS
# ============================================

class RecaudacionManualRequest(BaseModel):
    """Registrar recaudación manual"""
    vehiculo_id: UUID
    monto: float = Field(..., gt=0)
    fecha: date
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True


class RegistrarCanonRequest(BaseModel):
    """Registrar pago de canon (DEPRECADO - usar contratos)"""
    contrato_id: UUID
    fecha_pago: date
    monto: float = Field(..., gt=0)

    class Config:
        from_attributes = True


class IngresoResponse(BaseModel):
    """Respuesta de ingreso"""
    id: UUID
    tipo: str
    monto: float
    fecha: str
    descripcion: Optional[str] = None
    vehiculo_patente: Optional[str] = None
    chofer_nombre: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================
# GASTOS CON CATEGORÍAS
# ============================================================

class GastoVehiculoCreate(BaseModel):
    """Registrar gasto de vehículo con categorías"""
    vehiculo_id: UUID
    categoria_id: UUID
    subcategoria: Optional[str] = Field(None, max_length=50)
    monto: float = Field(..., gt=0)
    fecha_gasto: date
    descripcion: Optional[str] = None
    km_registro: Optional[float] = Field(None, ge=0)
    tipo_gasto: Optional[str] = Field(None, max_length=50)

    class Config:
        from_attributes = True


class GastoVehiculoUpdate(BaseModel):
    """Actualizar gasto de vehículo"""
    categoria_id: Optional[UUID] = None
    subcategoria: Optional[str] = Field(None, max_length=50)
    monto: Optional[float] = Field(None, gt=0)
    fecha_gasto: Optional[date] = None
    descripcion: Optional[str] = None
    km_registro: Optional[float] = Field(None, ge=0)
    tipo_gasto: Optional[str] = Field(None, max_length=50)

    class Config:
        from_attributes = True


class GastoVehiculoDetailResponse(BaseModel):
    """Respuesta detallada de gasto de vehículo con categorías"""
    id: UUID
    vehiculo_id: UUID
    vehiculo_patente: str
    categoria_id: Optional[UUID] = None
    categoria_nombre: Optional[str] = None
    subcategoria: Optional[str] = None
    tipo_gasto: Optional[str] = None
    monto: float
    descripcion: Optional[str] = None
    km_registro: Optional[float] = None
    comprobante_url: Optional[str] = None
    fecha_gasto: date
    created_at: datetime

    class Config:
        from_attributes = True


class CategoriaGastoResponse(BaseModel):
    """Respuesta de categoría de gasto"""
    id: UUID
    control_base_id: UUID
    nombre: str
    descripcion: Optional[str] = None
    subcategorias: List[str]
    aplica_a: List[str]
    tratamiento_economico: str
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoriaGastoCreate(BaseModel):
    """Crear categoría de gasto"""
    nombre: str = Field(..., max_length=50)
    descripcion: Optional[str] = None
    subcategorias: List[str] = Field(default_factory=list)
    aplica_a: List[str] = Field(default_factory=list)
    tratamiento_economico: str = Field(default="configurable")

    class Config:
        from_attributes = True


class CategoriaGastoUpdate(BaseModel):
    """Actualizar categoría de gasto"""
    nombre: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = None
    subcategorias: Optional[List[str]] = None
    aplica_a: Optional[List[str]] = None
    tratamiento_economico: Optional[str] = None
    activo: Optional[bool] = None

    class Config:
        from_attributes = True


# ============================================================
# DOCUMENTOS
# ============================================================

class DocumentoVehiculoCreate(BaseModel):
    """Crear documento de vehículo"""
    tipo_documento: str
    numero: str
    fecha_emision: Optional[date] = None
    fecha_vencimiento: date
    observaciones: Optional[str] = None
    url_archivo: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentoVehiculoUpdate(BaseModel):
    """Actualizar documento de vehículo"""
    tipo_documento: Optional[str] = None
    numero: Optional[str] = None
    fecha_emision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    observaciones: Optional[str] = None
    url_archivo: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentoVehiculoResponse(BaseModel):
    """Respuesta de documento de vehículo"""
    id: UUID
    vehiculo_id: UUID
    patente: str
    tipo_documento: str
    tipo_nombre: Optional[str] = None
    numero: str
    fecha_emision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    observaciones: Optional[str] = None
    url_archivo: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentoPropietarioCreate(BaseModel):
    """Crear documento del propietario"""
    tipo_documento: str
    numero: str
    fecha_emision: Optional[date] = None
    fecha_vencimiento: date
    observaciones: Optional[str] = None
    url_archivo: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentoPropietarioUpdate(BaseModel):
    """Actualizar documento del propietario"""
    tipo_documento: Optional[str] = None
    numero: Optional[str] = None
    fecha_emision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    observaciones: Optional[str] = None
    url_archivo: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentoPropietarioResponse(BaseModel):
    """Respuesta de documento del propietario"""
    id: UUID
    propietario_id: UUID
    tipo_documento: str
    tipo_nombre: Optional[str] = None
    numero: str
    fecha_emision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    observaciones: Optional[str] = None
    url_archivo: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertaVencimientoResponse(BaseModel):
    """Alerta de vencimiento de documento"""
    id: UUID
    tipo_documento: str
    numero: str
    fecha_vencimiento: date
    patente: Optional[str] = None
    entidad_tipo: str
    dias_restantes: int
    alerta_a: str
    nivel: str

    class Config:
        from_attributes = True


# ============================================================
# SCHEMAS DE NEUMÁTICOS
# ============================================================

class NeumaticoCreate(BaseModel):
    """Crear un nuevo neumático"""
    codigo_interno: Optional[str] = Field(None, max_length=20)
    marca: str = Field(..., max_length=50)
    modelo_dibujo: Optional[str] = Field(None, max_length=50)
    medida: Optional[str] = Field(None, max_length=20)
    tipo_neumatico: str = Field(..., pattern="^(RADIAL|BIAS|TUBELESS|RUN_FLAT|TODO_TERRENO)$")
    fecha_fabricacion: Optional[date] = None
    posicion: str = Field(..., pattern="^(DI|DD|TI|TD|REPUESTO)$")
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True


class NeumaticoMontarRequest(BaseModel):
    """Montar uno o más neumáticos"""
    neumaticos: List[NeumaticoCreate]
    km_vehiculo_actual: int = Field(..., ge=0)
    observaciones_generales: Optional[str] = None

    class Config:
        from_attributes = True


class RotacionRequest(BaseModel):
    """Rotar neumáticos"""
    km_vehiculo_actual: int = Field(..., ge=0)
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True


class DesmontarRequest(BaseModel):
    """Desmontar un neumático"""
    km_vehiculo_actual: int = Field(..., ge=0)
    motivo: str = Field(..., pattern="^(CAMBIO_POR_DESGASTE|DAÑO|REPARACION|CAMBIO_ESTACIONAL|OTRO)$")
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True


class CambiarEstadoRequest(BaseModel):
    """Cambiar estado de un neumático"""
    estado: str = Field(..., pattern="^(DESMONTADO|DESECHADO)$")
    motivo: Optional[str] = None
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True


class MedicionRequest(BaseModel):
    """Registrar medición de profundidad"""
    profundidad_mm: float = Field(..., ge=0, le=20)
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True


class ReparacionRequest(BaseModel):
    """Registrar reparación de un neumático"""
    vehiculo_id: UUID
    neumatico_id: UUID
    tipo_reparacion: str = Field(..., pattern="^(PARCHE|VULCANIZACION|CAMBIO_VALVULA|OTRO)$")
    km_vehiculo_actual: int = Field(..., ge=0)
    proveedor: Optional[str] = Field(None, max_length=100)
    costo: Optional[float] = Field(None, ge=0)
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True


class SugerenciaAtenderRequest(BaseModel):
    """Marcar sugerencia como atendida"""
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True


class SugerenciaDesestimarRequest(BaseModel):
    """Desestimar sugerencia"""
    motivo: str
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True


class ConfiguracionNeumaticosUpdate(BaseModel):
    """Actualizar configuración de neumáticos"""
    vida_util_km: Optional[int] = Field(None, ge=30000, le=80000)
    umbral_rotacion_km: Optional[int] = Field(None, ge=5000, le=15000)
    umbral_cambio_km: Optional[int] = Field(None, ge=30000, le=70000)
    profundidad_minima_mm: Optional[float] = Field(None, ge=1.6, le=3.0)
    factor_desgaste_delantero: Optional[float] = Field(None, ge=1.2, le=2.0)

    class Config:
        from_attributes = True


class NeumaticoPosicionResponse(BaseModel):
    """Posición actual de un neumático"""
    eje: str
    km_montaje: int
    km_recorridos: int
    fecha_montaje: datetime
    fecha_desmontaje: Optional[datetime] = None

    class Config:
        from_attributes = True


class NeumaticoMedicionResponse(BaseModel):
    """Medición de profundidad"""
    id: UUID
    fecha: datetime
    profundidad_mm: float
    estado_color: str
    medido_por: Optional[str] = None
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True


class NeumaticoResponse(BaseModel):
    """Respuesta completa de un neumático"""
    id: UUID
    codigo_interno: Optional[str] = None
    marca: str
    modelo_dibujo: Optional[str] = None
    medida: Optional[str] = None
    tipo_neumatico: str
    estado: str
    vehiculo_id: UUID
    patente: str
    posicion_actual: Optional[str] = None
    km_totales_acumulados: int
    km_en_posicion_actual: Optional[int] = None
    fecha_alta: datetime
    fecha_baja: Optional[datetime] = None
    ultima_profundidad_mm: Optional[float] = None
    estado_color: str
    ultima_medicion_fecha: Optional[datetime] = None

    class Config:
        from_attributes = True


class NeumaticoActivoResponse(BaseModel):
    """Neumático activo en una posición"""
    id: UUID
    codigo_interno: Optional[str] = None
    marca: str
    modelo_dibujo: Optional[str] = None
    medida: Optional[str] = None
    km_montaje: int
    km_recorridos: int
    ultima_profundidad_mm: Optional[float] = None
    estado_color: str
    sugerencia: Optional[str] = None

    class Config:
        from_attributes = True


class NeumaticosActivosResponse(BaseModel):
    """Respuesta de los 4 neumáticos activos"""
    vehiculo_id: UUID
    patente: str
    vehiculo_marca: str
    vehiculo_modelo: str
    neumaticos: Dict[str, Optional[NeumaticoActivoResponse]]
    resumen: Dict[str, int]

    class Config:
        from_attributes = True


class OperacionNeumaticoResponse(BaseModel):
    """Operación de neumáticos"""
    id: UUID
    tipo: str
    fecha: datetime
    km_vehiculo: int
    descripcion: Optional[str] = None
    neumaticos_afectados: List[Dict[str, Optional[str]]] = []

    class Config:
        from_attributes = True


class SugerenciaResponse(BaseModel):
    """Sugerencia de neumáticos"""
    id: UUID
    tipo: str
    neumatico: Optional[str] = None
    posicion: Optional[str] = None
    mensaje: str
    prioridad: str
    color: str
    km_actual: int
    km_umbral: int
    fecha_generacion: datetime
    estado: str
    dias_activa: Optional[int] = None

    class Config:
        from_attributes = True


class ConfiguracionNeumaticosResponse(BaseModel):
    """Configuración de neumáticos"""
    control_base_id: UUID
    vida_util_km: int
    umbral_rotacion_km: int
    umbral_cambio_km: int
    profundidad_minima_mm: float
    factor_desgaste_delantero: float
    colores: Dict[str, Dict[str, Any]]
    ultima_actualizacion: datetime

    class Config:
        from_attributes = True


class ResumenNeumaticosResponse(BaseModel):
    """Resumen ejecutivo de neumáticos del vehículo"""
    vehiculo_id: UUID
    patente: str
    resumen: Dict[str, Any]
    neumaticos: List[Dict[str, Any]]
    alertas: Dict[str, List[Dict[str, Any]]]

    class Config:
        from_attributes = True


class EstadoFlotaNeumaticosResponse(BaseModel):
    """Estado general de neumáticos de la flota"""
    propietario_id: UUID
    total_vehiculos: int
    total_neumaticos: int
    resumen_global: Dict[str, int]
    vehiculos: List[Dict[str, Any]]
    sugerencias_totales: int
    alertas_criticas: int
    promedio_profundidad_flota: float

    class Config:
        from_attributes = True


# ============================================================
# DASHBOARD
# ============================================================

class ResumenFlotaResponse(BaseModel):
    total_vehiculos: int
    total_choferes_activos: int
    choferes_conectados: int
    choferes_disponibles: int
    choferes_ocupados: int
    choferes_fuera_servicio: int
    vehiculos_en_turno: int
    vehiculos_disponibles: int


class VehiculoUbicacionResponse(BaseModel):
    vehiculo_id: UUID
    patente: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    latitud: float
    longitud: float
    estado: str
    ultima_conexion: Optional[datetime] = None
    conductor: Optional[str] = None
    turno_activo: Optional[UUID] = None


class RentabilidadWidgetResponse(BaseModel):
    periodo: Dict[str, Any]
    ingresos: float
    gastos: float
    utilidad: float
    utilidad_promedio: float
    total_viajes: int
    ticket_promedio: float
    variacion: float
    tendencia: str


class GastosWidgetResponse(BaseModel):
    periodo: Dict[str, Any]
    total_gastos: float
    desglose: Dict[str, float]
    variacion: float
    tendencia: str


class AlertaWidgetResponse(BaseModel):
    total_alertas: int
    alertas: List[Dict[str, Any]]


class GraficoIngresosGastosResponse(BaseModel):
    labels: List[str]
    ingresos: List[float]
    gastos: List[float]
    utilidad: List[float]