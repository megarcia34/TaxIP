"""
Helpers para creación de datos de prueba en TAXIP 2.1.0
NO usa campos legacy (turno_asignado, recaudacion_app_*, etc.)
"""

from uuid import uuid4, UUID
from datetime import datetime, time
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.auth import Usuario, TipoUsuario
from app.models.tenant import ControlBase
from app.models.fleet import (
    Vehiculo,
    PropietarioVehiculo,
    ContratoVehiculo,
    ChoferVehiculo,
    IngresoTurno,
)
from app.models.turno import TurnoChofer
from app.models.trip import ViajeSolicitado
from app.models.gasto_turno import GastoTurno
from app.core.security import get_password_hash


# ============================================================
# CONFIGURACIÓN DE TENANT PARA TESTS
# ============================================================
# Usar un tenant existente en la base de datos
FIXED_TENANT_ID = UUID("95dd425d-5840-4ded-a838-2ccd0ead0e0b")


class CreateTestData:
    """
    Helper para crear datos de prueba en los tests.
    Todas las operaciones usan modelos alineados con TAXIP 2.1.0.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # USUARIOS
    # ============================================================

    async def usuario(
        self,
        email: str = None,
        password: str = "test123",
        tipo: str = "chofer",
        tenant_id: UUID = None,
        nombre: str = None,
        apellido: str = None,
        **kwargs
    ) -> Usuario:
        """Crea un usuario con el rol especificado usando un tenant existente"""
        email = email or f"test_{uuid4().hex[:8]}@example.com"
        
        # ============================================================
        # USAR TENANT FIJO
        # ============================================================
        if tenant_id is None:
            tenant_id = FIXED_TENANT_ID
        elif isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        # ============================================================
        # OBTENER O CREAR TIPO_USUARIO (SOLO id y nombre)
        # ============================================================
        tipo_query = select(TipoUsuario).where(TipoUsuario.nombre == tipo)
        result = await self.db.execute(tipo_query)
        tipo_usuario = result.scalar_one_or_none()
        
        if not tipo_usuario:
            tipo_usuario = TipoUsuario(
                id=uuid4(),
                nombre=tipo
            )
            self.db.add(tipo_usuario)
            await self.db.flush()
            await self.db.refresh(tipo_usuario)
        
        # Crear usuario
        usuario = Usuario(
            id=uuid4(),
            control_base_id=tenant_id,
            tipo_usuario_id=tipo_usuario.id,
            email=email,
            password_hash=get_password_hash(password),
            activo=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.db.add(usuario)
        await self.db.flush()
        await self.db.refresh(usuario)
        
        return usuario

    # ============================================================
    # VEHÍCULOS
    # ============================================================

    async def vehiculo(
        self,
        propietario_id: UUID,
        patente: str = None,
        marca: str = "Toyota",
        modelo: str = "Corolla",
        anio: int = 2020,
        **kwargs
    ) -> Vehiculo:
        """Crea un vehículo y lo asigna al propietario"""
        patente = patente or f"AB{str(uuid4())[:3].upper()}"
        
        # Obtener control_base_id del propietario
        propietario = await self.db.get(Usuario, propietario_id)
        control_base_id = propietario.control_base_id if propietario else FIXED_TENANT_ID
        
        # Crear vehículo
        vehiculo = Vehiculo(
            id=uuid4(),
            control_base_id=control_base_id,
            patente=patente,
            marca=marca,
            modelo=modelo,
            anio=anio,
            qr_uuid=uuid4(),
            qr_activo=True,
            activo=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.db.add(vehiculo)
        await self.db.flush()
        await self.db.refresh(vehiculo)
        
        # Asignar propietario
        propietario_vehiculo = PropietarioVehiculo(
            id=uuid4(),
            propietario_id=propietario_id,
            vehiculo_id=vehiculo.id,
            porcentaje_participacion=100,
            fecha_inicio=datetime.now(),
            activo=True,
            created_at=datetime.now()
        )
        self.db.add(propietario_vehiculo)
        await self.db.flush()
        
        return vehiculo

    # ============================================================
    # CONTRATOS (con jornadas flexibles, SIN turno_asignado)
    # ============================================================

    async def contrato(
        self,
        propietario_id: UUID,
        chofer_id: UUID,
        vehiculo_id: UUID,
        tipo_contrato: str = "PORCENTAJE",
        porcentaje_chofer: float = 70,
        hora_inicio: str = "06:00",
        hora_fin: str = "14:00",
        duracion_minima_horas: int = 6,
        dias_contractuales: list = None,
        **kwargs
    ) -> ContratoVehiculo:
        """
        Crea un contrato con jornadas flexibles.
        NO usa turno_asignado.
        """
        # Obtener control_base_id del vehículo
        vehiculo = await self.db.get(Vehiculo, vehiculo_id)
        control_base_id = vehiculo.control_base_id if vehiculo else FIXED_TENANT_ID
        
        # Parsear horarios
        hora_inicio_obj = datetime.strptime(hora_inicio, "%H:%M").time()
        hora_fin_obj = datetime.strptime(hora_fin, "%H:%M").time()
        
        contrato = ContratoVehiculo(
            id=uuid4(),
            control_base_id=control_base_id,
            propietario_id=propietario_id,
            vehiculo_id=vehiculo_id,
            chofer_id=chofer_id,
            tipo_contrato=tipo_contrato,
            # Horarios flexibles
            hora_inicio=hora_inicio_obj,
            hora_fin=hora_fin_obj,
            duracion_minima_horas=duracion_minima_horas,
            permite_extension=kwargs.get("permite_extension", False),
            hora_fin_extension=None,
            # Porcentaje o alquiler
            porcentaje_chofer=porcentaje_chofer if tipo_contrato == "PORCENTAJE" else None,
            monto_diario=kwargs.get("monto_diario"),
            canon_diario=kwargs.get("canon_diario"),
            km_incluidos_dia=kwargs.get("km_incluidos_dia"),
            valor_km_excedente=kwargs.get("valor_km_excedente"),
            modalidad_computo=kwargs.get("modalidad_computo", "DIARIO"),
            tratamiento_dia_no_trabajado=kwargs.get("tratamiento_dia_no_trabajado", "POR_DISPONIBILIDAD"),
            dias_contractuales=dias_contractuales or ["lunes", "martes", "miercoles", "jueves", "viernes"],
            dia_inicio_semana=kwargs.get("dia_inicio_semana", "lunes"),
            compensacion_km=kwargs.get("compensacion_km", "DIARIA"),
            # Estado
            estado_contrato="ACTIVO",
            fecha_inicio=datetime.now(),
            activo=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.db.add(contrato)
        await self.db.flush()
        await self.db.refresh(contrato)
        
        # Asignar chofer al vehículo (para estado laboral)
        chofer_vehiculo = ChoferVehiculo(
            id=uuid4(),
            usuario_id=chofer_id,
            vehiculo_id=vehiculo_id,
            control_base_id=control_base_id,
            estado_laboral="libre",
            activo=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.db.add(chofer_vehiculo)
        await self.db.flush()
        
        return contrato

    # ============================================================
    # TURNOS
    # ============================================================

    async def turno(
        self,
        contrato_id: UUID,
        chofer_id: UUID,
        vehiculo_id: UUID,
        estado: str = "ACTIVO",
        km_inicial: float = 1000,
        km_final: float = None,
        **kwargs
    ) -> TurnoChofer:
        """Crea un turno para un chofer"""
        contrato = await self.db.get(ContratoVehiculo, contrato_id)
        control_base_id = contrato.control_base_id if contrato else FIXED_TENANT_ID
        
        turno = TurnoChofer(
            id=uuid4(),
            contrato_id=contrato_id,
            chofer_id=chofer_id,
            vehiculo_id=vehiculo_id,
            estado=estado,
            km_inicial=km_inicial,
            km_final=km_final,
            combustible_inicial=kwargs.get("combustible_inicial", "LLENO"),
            combustible_final=kwargs.get("combustible_final"),
            inicio_turno=kwargs.get("inicio_turno", datetime.now()),
            fin_turno=kwargs.get("fin_turno"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.db.add(turno)
        await self.db.flush()
        await self.db.refresh(turno)
        
        return turno

    # ============================================================
    # VIAJES
    # ============================================================

    async def viaje(
        self,
        chofer_id: UUID,
        vehiculo_id: UUID,
        precio_final: Decimal = Decimal(500),
        turno_id: UUID = None,
        estado: str = "finalizado",
        **kwargs
    ) -> ViajeSolicitado:
        """Crea un viaje asociado a un turno usando coordenadas PostGIS"""
        vehiculo = await self.db.get(Vehiculo, vehiculo_id)
        control_base_id = vehiculo.control_base_id if vehiculo else FIXED_TENANT_ID
        
        # ============================================================
        # USAR COORDENADAS POSTGIS VÁLIDAS
        # ============================================================
        origen = kwargs.get("origen", "POINT(-58.3816 -34.6037)")
        destino = kwargs.get("destino", "POINT(-58.3816 -34.6037)")
        
        # Si no son coordenadas PostGIS, convertir a POINT
        if not str(origen).startswith("POINT"):
            origen = "POINT(-58.3816 -34.6037)"
        if not str(destino).startswith("POINT"):
            destino = "POINT(-58.3816 -34.6037)"
        
        viaje = ViajeSolicitado(
            id=uuid4(),
            control_base_id=control_base_id,
            chofer_id=chofer_id,
            vehiculo_id=vehiculo_id,
            turno_id=turno_id,
            estado=estado,
            precio_final=precio_final,
            origen=origen,
            destino=destino,
            created_at=kwargs.get("created_at", datetime.now()),
            finalizado_en=kwargs.get("finalizado_en", datetime.now())
        )
        self.db.add(viaje)
        await self.db.flush()
        await self.db.refresh(viaje)
        
        return viaje

    # ============================================================
    # GASTOS DE TURNO
    # ============================================================

    async def gasto_turno(
        self,
        turno_id: UUID,
        monto: Decimal = Decimal(50),
        tipo_gasto: str = "COMBUSTIBLE",
        **kwargs
    ) -> GastoTurno:
        """Crea un gasto asociado a un turno"""
        gasto = GastoTurno(
            id=uuid4(),
            turno_id=turno_id,
            tipo_gasto=tipo_gasto,
            monto=monto,
            km_registro=kwargs.get("km_registro"),
            url_comprobante=kwargs.get("url_comprobante"),
            categoria_id=kwargs.get("categoria_id"),
            subcategoria=kwargs.get("subcategoria"),
            created_at=datetime.now()
        )
        self.db.add(gasto)
        await self.db.flush()
        await self.db.refresh(gasto)
        
        return gasto

    # ============================================================
    # INGRESOS DE TURNO (NUEVA FUENTE DE VERDAD)
    # ============================================================

    async def ingreso_turno(
        self,
        turno_id: UUID,
        monto: Decimal = Decimal(100),
        tipo_ingreso: str = "taximetro",
        estado: str = "aprobado",
        **kwargs
    ) -> IngresoTurno:
        """
        Crea un ingreso en IngresoTurno (nueva fuente de verdad).
        NO usa campos legacy.
        """
        ingreso = IngresoTurno(
            id=uuid4(),
            turno_id=turno_id,
            viaje_id=kwargs.get("viaje_id"),
            tipo_ingreso=tipo_ingreso,
            medio_pago=kwargs.get("medio_pago", "efectivo"),
            origen=kwargs.get("origen", "taximetro"),
            monto=monto,
            moneda=kwargs.get("moneda", "ARS"),
            fecha_hora=kwargs.get("fecha_hora", datetime.now()),
            declarado_por=kwargs.get("declarado_por"),
            estado=estado,
            observaciones=kwargs.get("observaciones"),
            referencia_pago=kwargs.get("referencia_pago"),
            transaccion_id=kwargs.get("transaccion_id"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.db.add(ingreso)
        await self.db.flush()
        await self.db.refresh(ingreso)
        
        return ingreso


def create_test_data(db: AsyncSession) -> CreateTestData:
    """Factory para crear el helper de datos de prueba"""
    return CreateTestData(db)