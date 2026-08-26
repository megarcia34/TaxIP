# tests/test_liquidacion_engine.py
"""
Pruebas para el motor de liquidaciones (requiere base de datos real)
ACTUALIZADO: Usa IngresoTurno como fuente de ingresos, no campos legacy
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime

from app.services.liquidacion_engine import LiquidacionEngine
from app.repositories.liquidacion_repository import LiquidacionRepository
from app.models.turno import TurnoChofer
from app.models.fleet import ContratoVehiculo, Vehiculo, PropietarioVehiculo, IngresoTurno
from app.models.auth import Usuario
from app.models.trip import ViajeSolicitado
from app.models.gasto_turno import GastoTurno
from app.core.exceptions import LiquidacionError
from app.test.helpers import FIXED_TENANT_ID


@pytest.mark.asyncio
async def test_calcular_liquidacion_sin_viajes(db_session: AsyncSession, create_test_data):
    """Test: Liquidación de turno sin viajes ni ingresos"""
    propietario = await create_test_data.usuario(tipo='propietario')
    chofer = await create_test_data.usuario(tipo='chofer')
    vehiculo = await create_test_data.vehiculo(propietario_id=propietario.id)
    contrato = await create_test_data.contrato(
        propietario_id=propietario.id,
        chofer_id=chofer.id,
        vehiculo_id=vehiculo.id,
        tipo_contrato='PORCENTAJE',
        porcentaje_chofer=70
    )
    turno = await create_test_data.turno(
        contrato_id=contrato.id,
        chofer_id=chofer.id,
        vehiculo_id=vehiculo.id,
        estado='ACTIVO'
    )

    engine = LiquidacionEngine(db_session)
    liquidacion_id = await engine.calcular(turno.id)

    repo = LiquidacionRepository(db_session)
    liquidacion = await repo.obtener_por_id(liquidacion_id)

    assert liquidacion is not None
    # Verificar que no hay ingresos contabilizados
    assert liquidacion.monto_bruto == Decimal(0)
    assert liquidacion.comision_chofer == Decimal(0)
    assert liquidacion.total_chofer == Decimal(0)
    assert liquidacion.total_gastos == Decimal(0)


@pytest.mark.asyncio
async def test_calcular_liquidacion_con_viaje(db_session: AsyncSession, create_test_data):
    """Test: Liquidación de turno con un viaje"""
    propietario = await create_test_data.usuario(tipo='propietario')
    chofer = await create_test_data.usuario(tipo='chofer')
    vehiculo = await create_test_data.vehiculo(propietario_id=propietario.id)
    contrato = await create_test_data.contrato(
        propietario_id=propietario.id,
        chofer_id=chofer.id,
        vehiculo_id=vehiculo.id,
        tipo_contrato='PORCENTAJE',
        porcentaje_chofer=70  # Propietario recibe 70%, chofer recibe 30%
    )
    turno = await create_test_data.turno(
        contrato_id=contrato.id,
        chofer_id=chofer.id,
        vehiculo_id=vehiculo.id,
        estado='ACTIVO'
    )
    viaje = await create_test_data.viaje(
        chofer_id=chofer.id,
        vehiculo_id=vehiculo.id,
        precio_final=Decimal(500),
        turno_id=turno.id,
        estado='finalizado',
        finalizado_en=datetime.now()
    )

    engine = LiquidacionEngine(db_session)
    liquidacion_id = await engine.calcular(turno.id)

    repo = LiquidacionRepository(db_session)
    liquidacion = await repo.obtener_por_id(liquidacion_id)

    assert liquidacion.monto_bruto == Decimal(500)
    assert liquidacion.total_gastos == Decimal(0)
    # El chofer recibe 30% de 500 = 150
    assert liquidacion.comision_chofer == Decimal(150)
    assert liquidacion.total_chofer == Decimal(150)
    # El propietario recibe 70% de 500 = 350
    assert liquidacion.total_propietario == Decimal(350)
    assert len(liquidacion.detalles) == 2


@pytest.mark.asyncio
async def test_calcular_liquidacion_con_gastos(db_session: AsyncSession, create_test_data):
    """Test: Liquidación con gastos"""
    propietario = await create_test_data.usuario(tipo='propietario')
    chofer = await create_test_data.usuario(tipo='chofer')
    vehiculo = await create_test_data.vehiculo(propietario_id=propietario.id)
    contrato = await create_test_data.contrato(
        propietario_id=propietario.id,
        chofer_id=chofer.id,
        vehiculo_id=vehiculo.id,
        tipo_contrato='PORCENTAJE',
        porcentaje_chofer=70  # Propietario recibe 70%, chofer recibe 30%
    )
    turno = await create_test_data.turno(
        contrato_id=contrato.id,
        chofer_id=chofer.id,
        vehiculo_id=vehiculo.id,
        estado='ACTIVO'
    )
    viaje = await create_test_data.viaje(
        chofer_id=chofer.id,
        vehiculo_id=vehiculo.id,
        precio_final=Decimal(500),
        turno_id=turno.id,
        estado='finalizado',
        finalizado_en=datetime.now()
    )
    gasto = await create_test_data.gasto_turno(
        turno_id=turno.id,
        monto=Decimal(50),
        tipo_gasto='COMBUSTIBLE'
    )

    engine = LiquidacionEngine(db_session)
    liquidacion_id = await engine.calcular(turno.id)

    repo = LiquidacionRepository(db_session)
    liquidacion = await repo.obtener_por_id(liquidacion_id)

    assert liquidacion.monto_bruto == Decimal(500)
    # El gasto debe ser contabilizado
    assert liquidacion.total_gastos == Decimal(50)
    # El gasto se descuenta antes de aplicar el porcentaje
    # Base liquidable = 500 - 50 = 450
    # Chofer recibe 30% de 450 = 135
    assert liquidacion.comision_chofer == Decimal(135)
    assert liquidacion.total_chofer == Decimal(135)
    # Propietario recibe: 500 - 50 - 135 = 315
    assert liquidacion.total_propietario == Decimal(315)
    assert len(liquidacion.detalles) == 3


@pytest.mark.asyncio
async def test_calcular_liquidacion_con_ingresos_turno(db_session: AsyncSession, create_test_data):
    """
    Test: Liquidación con ingresos registrados en IngresoTurno
    (reemplaza los campos legacy de recaudación)
    """
    propietario = await create_test_data.usuario(tipo='propietario')
    chofer = await create_test_data.usuario(tipo='chofer')
    vehiculo = await create_test_data.vehiculo(propietario_id=propietario.id)
    contrato = await create_test_data.contrato(
        propietario_id=propietario.id,
        chofer_id=chofer.id,
        vehiculo_id=vehiculo.id,
        tipo_contrato='PORCENTAJE',
        porcentaje_chofer=70  # Propietario recibe 70%, chofer recibe 30%
    )
    turno = await create_test_data.turno(
        contrato_id=contrato.id,
        chofer_id=chofer.id,
        vehiculo_id=vehiculo.id,
        estado='ACTIVO'
    )

    ingreso1 = IngresoTurno(
        turno_id=turno.id,
        tipo_ingreso="taximetro",
        medio_pago="efectivo",
        origen="taximetro",
        monto=Decimal(300),
        declarado_por=chofer.id,
        estado="aprobado"
    )
    ingreso2 = IngresoTurno(
        turno_id=turno.id,
        tipo_ingreso="electronico",
        medio_pago="debito",
        origen="app",
        monto=Decimal(200),
        declarado_por=chofer.id,
        estado="aprobado"
    )
    db_session.add(ingreso1)
    db_session.add(ingreso2)
    await db_session.flush()

    engine = LiquidacionEngine(db_session)
    liquidacion_id = await engine.calcular(turno.id)

    repo = LiquidacionRepository(db_session)
    liquidacion = await repo.obtener_por_id(liquidacion_id)

    assert liquidacion.monto_bruto == Decimal(500)
    assert liquidacion.total_gastos == Decimal(0)
    # El chofer recibe 30% de 500 = 150
    assert liquidacion.comision_chofer == Decimal(150)
    assert liquidacion.total_chofer == Decimal(150)
    # El propietario recibe 70% de 500 = 350
    assert liquidacion.total_propietario == Decimal(350)


@pytest.mark.asyncio
async def test_ingresos_pendientes_no_afectan_liquidacion(db_session: AsyncSession, create_test_data):
    """
    Test: Los ingresos en estado PENDIENTE NO deben afectar la liquidación
    """
    propietario = await create_test_data.usuario(tipo='propietario')
    chofer = await create_test_data.usuario(tipo='chofer')
    vehiculo = await create_test_data.vehiculo(propietario_id=propietario.id)
    contrato = await create_test_data.contrato(
        propietario_id=propietario.id,
        chofer_id=chofer.id,
        vehiculo_id=vehiculo.id,
        tipo_contrato='PORCENTAJE',
        porcentaje_chofer=70
    )
    turno = await create_test_data.turno(
        contrato_id=contrato.id,
        chofer_id=chofer.id,
        vehiculo_id=vehiculo.id,
        estado='ACTIVO'
    )

    ingreso_pendiente = IngresoTurno(
        turno_id=turno.id,
        tipo_ingreso="taximetro",
        medio_pago="efectivo",
        origen="taximetro",
        monto=Decimal(500),
        declarado_por=chofer.id,
        estado="pendiente"
    )
    db_session.add(ingreso_pendiente)
    await db_session.flush()

    engine = LiquidacionEngine(db_session)
    liquidacion_id = await engine.calcular(turno.id)

    repo = LiquidacionRepository(db_session)
    liquidacion = await repo.obtener_por_id(liquidacion_id)

    assert liquidacion.monto_bruto == Decimal(0)
    assert liquidacion.total_chofer == Decimal(0)


@pytest.mark.asyncio
async def test_checkout_crea_ingreso_pendiente(db_session: AsyncSession, create_test_data):
    """
    Test: El check-out debe crear un IngresoTurno con estado PENDIENTE
    (NO debe escribir en campos legacy)
    """
    from app.services.turno_service import TurnoService

    propietario = await create_test_data.usuario(tipo='propietario')
    chofer = await create_test_data.usuario(tipo='chofer')
    vehiculo = await create_test_data.vehiculo(propietario_id=propietario.id)
    contrato = await create_test_data.contrato(
        propietario_id=propietario.id,
        chofer_id=chofer.id,
        vehiculo_id=vehiculo.id,
        tipo_contrato='PORCENTAJE',
        porcentaje_chofer=70,
        hora_inicio='06:00',
        hora_fin='14:00'
    )
    turno = await create_test_data.turno(
        contrato_id=contrato.id,
        chofer_id=chofer.id,
        vehiculo_id=vehiculo.id,
        estado='ACTIVO'
    )

    result = await TurnoService.check_out(
        db=db_session,
        turno_id=turno.id,
        chofer_id=chofer.id,
        km_final=1500,
        combustible_final='1/2',
        recaudacion_ticketera=250
    )

    assert result["estado"] == "PENDIENTE_CONFIRMACION"
    assert result["ingresos_registrados"] == 1

    from sqlalchemy import select
    query = select(IngresoTurno).where(IngresoTurno.turno_id == turno.id)
    result = await db_session.execute(query)
    ingresos = result.scalars().all()

    assert len(ingresos) == 1
    assert ingresos[0].monto == Decimal(250)
    assert ingresos[0].tipo_ingreso == "taximetro"
    assert ingresos[0].estado == "pendiente"


@pytest.mark.asyncio
async def test_tenant_mismatch_rechazado(db_session: AsyncSession, create_test_data):
    """Test: Tenant incorrecto → rechazar"""
    # Crear un propietario en el tenant existente
    propietario = await create_test_data.usuario(
        tipo='propietario',
        tenant_id=FIXED_TENANT_ID
    )
    
    # Crear un chofer en un tenant diferente (no existente)
    with pytest.raises(Exception):
        chofer = await create_test_data.usuario(
            tipo='chofer',
            tenant_id=UUID("11111111-1111-1111-1111-111111111111")
        )