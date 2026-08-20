# tests/test_liquidacion_engine.py
"""
Pruebas para el motor de liquidaciones (requiere base de datos real)
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from decimal import Decimal

from app.services.liquidacion_engine import LiquidacionEngine
from app.repositories.liquidacion_repository import LiquidacionRepository
from app.models.turno import TurnoChofer
from app.models.fleet import ContratoVehiculo, Vehiculo, PropietarioVehiculo
from app.models.auth import Usuario
from app.models.trip import ViajeSolicitado
from app.models.gasto_turno import GastoTurno
from app.core.exceptions import LiquidacionError


@pytest.mark.asyncio
async def test_calcular_liquidacion_sin_viajes(db_session: AsyncSession, create_test_data):
    """Test: Liquidación de turno sin viajes"""
    # Crear datos de prueba: propietario, chofer, vehículo, contrato, turno
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

    # Ejecutar motor
    engine = LiquidacionEngine(db_session)
    liquidacion_id = await engine.calcular(turno.id)

    # Verificar
    repo = LiquidacionRepository(db_session)
    liquidacion = await repo.obtener_por_id(liquidacion_id)

    assert liquidacion is not None
    assert liquidacion.monto_bruto == Decimal(0)
    assert liquidacion.total_gastos == Decimal(0)
    assert liquidacion.comision_chofer == Decimal(0)
    assert liquidacion.total_chofer == Decimal(0)
    assert len(liquidacion.detalles) == 0


@pytest.mark.asyncio
async def test_calcular_liquidacion_con_viaje(db_session: AsyncSession, create_test_data):
    """Test: Liquidación de turno con un viaje"""
    # Similar al anterior, pero creando un viaje asociado al turno
    # (requiere que el viaje tenga turno_id)
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
    assert liquidacion.comision_chofer == Decimal(150)  # 30% para propietario
    assert liquidacion.total_chofer == Decimal(350)
    assert len(liquidacion.detalles) == 2  # Ingreso + Comisión


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
        porcentaje_chofer=70
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
    assert liquidacion.total_gastos == Decimal(50)
    assert liquidacion.comision_chofer == Decimal(150)  # 30%
    # El total del chofer es ingreso - gastos - comisión
    assert liquidacion.total_chofer == Decimal(300)
    assert len(liquidacion.detalles) == 3  # Ingreso, Gasto, Comisión


@pytest.mark.asyncio
async def test_tenant_mismatch_rechazado(db_session: AsyncSession, create_test_data):
    """Test: Tenant incorrecto → rechazar"""
    propietario = await create_test_data.usuario(tipo='propietario', tenant_id='tenant1')
    chofer = await create_test_data.usuario(tipo='chofer', tenant_id='tenant2')  # Tenant diferente

    # ... crear datos con tenants distintos
    # El motor debe lanzar TenantMismatchError
    with pytest.raises(LiquidacionError):
        engine = LiquidacionEngine(db_session)
        await engine.calcular(turno_id)


@pytest.mark.asyncio
async def test_checkout_no_llama_legacy(db_session: AsyncSession, create_test_data):
    """Test: El check-out NO ejecuta LiquidacionService legacy"""
    from app.services.turno_service import TurnoService

    # Crear turno activo
    turno = await create_test_data.turno(estado='ACTIVO')

    # Ejecutar check-out
    result = await TurnoService.check_out(
        db=db_session,
        turno_id=turno.id,
        chofer_id=turno.chofer_id,
        km_final=1500,
        combustible_final='1/2',
        recaudacion_ticketera=100
    )

    # Verificar que no se llamó a LiquidacionService
    # (No hay forma directa de verificarlo, pero podemos ver que el estado cambió)
    assert result["estado"] == "PENDIENTE_CONFIRMACION"
    assert "liquidacion" not in result  # No debe devolver liquidación

    # Además, los campos legacy no deben haber sido actualizados
    # (recaudacion_app_efectivo, etc. deben ser 0)
    from sqlalchemy import select
    query = select(TurnoChofer).where(TurnoChofer.id == turno.id)
    result = await db_session.execute(query)
    turno_actualizado = result.scalar_one()
    assert turno_actualizado.recaudacion_app_efectivo == Decimal(0)
    assert turno_actualizado.monto_bruto_calculado == Decimal(0)