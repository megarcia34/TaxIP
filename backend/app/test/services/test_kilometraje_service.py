"""
Tests de KilometrajeService.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.kilometraje_service import KilometrajeService, LecturaKilometraje


def _mock_result(value):
    """Helper: arma un resultado de SQLAlchemy con scalar_one_or_none -> value."""
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=value)
    return result


@pytest.mark.asyncio
async def test_km_desde_turno_activo():
    """Test: turno ACTIVO -> km_inicial."""
    db = AsyncMock()
    vehiculo_id = uuid4()
    turno = MagicMock()
    turno.id = uuid4()
    turno.km_inicial = 100000
    turno.km_final = None
    turno.inicio_turno = datetime.now() - timedelta(hours=2)
    turno.fin_turno = None
    turno.estado = "ACTIVO"

    # Una sola query: busca ACTIVO
    db.execute = AsyncMock(return_value=_mock_result(turno))

    result = await KilometrajeService.obtener_km_actual(db, vehiculo_id)

    assert result.km_actual == 100000
    assert result.fuente == "turno_activo"
    assert result.confiable is True
    assert result.vigente is True


@pytest.mark.asyncio
async def test_km_desde_turno_conciliado():
    """Test: turno CONCILIADO -> km_final."""
    db = AsyncMock()
    vehiculo_id = uuid4()
    turno = MagicMock()
    turno.id = uuid4()
    turno.km_inicial = 99000
    turno.km_final = 100500
    turno.inicio_turno = datetime.now() - timedelta(hours=6)
    turno.fin_turno = datetime.now() - timedelta(hours=1)
    turno.estado = "CONCILIADO"

    # 1ra query: ACTIVO -> None. 2da query: CONCILIADO/CERRADO -> turno.
    db.execute = AsyncMock(
        side_effect=[_mock_result(None), _mock_result(turno)]
    )

    result = await KilometrajeService.obtener_km_actual(db, vehiculo_id)

    assert result.km_actual == 100500
    assert result.fuente == "conciliado"
    assert result.confiable is True


@pytest.mark.asyncio
async def test_km_stale():
    """Test: turno cerrado hace > 7 dias -> stale."""
    db = AsyncMock()
    vehiculo_id = uuid4()
    turno = MagicMock()
    turno.id = uuid4()
    turno.km_inicial = 99000
    turno.km_final = 100500
    turno.inicio_turno = datetime.now() - timedelta(days=10, hours=6)
    turno.fin_turno = datetime.now() - timedelta(days=10)
    turno.estado = "CONCILIADO"

    db.execute = AsyncMock(
        side_effect=[_mock_result(None), _mock_result(turno)]
    )

    result = await KilometrajeService.obtener_km_actual(db, vehiculo_id)

    assert result.km_actual == 100500
    assert result.vigente is False
    assert result.requiere_verificacion is True
    assert len(result.advertencias) > 0


@pytest.mark.asyncio
async def test_validar_coherencia_km_retrocede():
    """Test: km_nuevo < km_actual -> incoherente."""
    db = AsyncMock()
    vehiculo_id = uuid4()

    lectura = LecturaKilometraje(
        km_actual=100000,
        fuente="conciliado",
        confiable=True,
        vigente=True,
        fecha_lectura=datetime.now(),
        turno_id=uuid4(),
    )

    KilometrajeService.obtener_km_actual = AsyncMock(return_value=lectura)

    es_coherente, advertencias = await KilometrajeService.validar_coherencia(
        db, vehiculo_id, km_nuevo=90000
    )

    assert es_coherente is False
    assert "Km retrocede" in advertencias[0]


@pytest.mark.asyncio
async def test_validar_coherencia_salto_anormal():
    """Test: km_nuevo > km_actual * 1.5 -> salto anormal."""
    db = AsyncMock()
    vehiculo_id = uuid4()

    lectura = LecturaKilometraje(
        km_actual=100000,
        fuente="conciliado",
        confiable=True,
        vigente=True,
        fecha_lectura=datetime.now(),
        turno_id=uuid4(),
    )

    KilometrajeService.obtener_km_actual = AsyncMock(return_value=lectura)

    es_coherente, advertencias = await KilometrajeService.validar_coherencia(
        db, vehiculo_id, km_nuevo=200000
    )

    assert es_coherente is False
    assert "Salto anormal" in advertencias[0]


@pytest.mark.asyncio
async def test_validar_coherencia_ok():
    """Test: km_nuevo coherente -> OK."""
    db = AsyncMock()
    vehiculo_id = uuid4()

    lectura = LecturaKilometraje(
        km_actual=100000,
        fuente="conciliado",
        confiable=True,
        vigente=True,
        fecha_lectura=datetime.now(),
        turno_id=uuid4(),
    )

    KilometrajeService.obtener_km_actual = AsyncMock(return_value=lectura)

    es_coherente, advertencias = await KilometrajeService.validar_coherencia(
        db, vehiculo_id, km_nuevo=105000
    )

    assert es_coherente is True
    assert len(advertencias) == 0