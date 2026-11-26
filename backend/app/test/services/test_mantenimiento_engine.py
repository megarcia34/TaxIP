"""
Tests unitarios del MantenimientoEngine.
Validan la logica pura de calculo de estados y vencimientos.
"""
import pytest
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock
from uuid import uuid4

from app.models.fleet import (
    MantenimientoPlan,
    MantenimientoPlanItem,
    MantenimientoPlanVehiculo,
    MantenimientoCatalogoComponente,
)
from app.services.mantenimiento_engine import MantenimientoEngine, VencimientoCalculado


# ============================================================
# HELPERS
# ============================================================

def _make_plan(umbrales_override=None, activo=True) -> MagicMock:
    """Arma un plan mock con los atributos necesarios."""
    plan = MagicMock(spec=MantenimientoPlan)
    plan.id = uuid4()
    plan.control_base_id = uuid4()
    plan.propietario_id = uuid4()
    plan.nombre = "Plan Test"
    plan.tipo = "preventivo"
    plan.activo = activo
    plan.umbrales_override = umbrales_override
    plan.items = []
    return plan


def _make_item(
    intervalo_km=None,
    intervalo_dias=None,
    intervalo_meses=None,
    umbrales_override=None,
    prioridad="media",
    criticidad="normal",
) -> MagicMock:
    """Arma un item mock con los atributos necesarios."""
    item = MagicMock(spec=MantenimientoPlanItem)
    item.id = uuid4()
    item.intervalo_km = intervalo_km
    item.intervalo_dias = intervalo_dias
    item.intervalo_meses = intervalo_meses
    item.umbrales_override = umbrales_override
    item.prioridad = prioridad
    item.criticidad = criticidad
    
    componente = MagicMock(spec=MantenimientoCatalogoComponente)
    componente.nombre = "Componente Test"
    item.componente = componente
    
    return item


def _make_plan_vehiculo(plan, control_base_id=None) -> MagicMock:
    """Arma un plan_vehiculo mock."""
    pv = MagicMock(spec=MantenimientoPlanVehiculo)
    pv.id = uuid4()
    pv.plan = plan
    pv.control_base_id = control_base_id or plan.control_base_id
    pv.vehiculo_id = uuid4()
    pv.activo = True
    return pv


# ============================================================
# TESTS: calcular_estado (logica pura)
# ============================================================

class TestCalcularEstado:
    """Tests del metodo puro calcular_estado."""

    def test_estado_normal_por_ambos(self):
        """Km y fecha lejos de los umbrales -> normal."""
        estado = MantenimientoEngine.calcular_estado(
            km_actual=100000,
            km_proximo=110000,  # 10000 km de margen
            hoy=date(2026, 11, 26),
            fecha_proximo=date(2027, 6, 1),  # +180 dias
            umbrales=MantenimientoEngine.UMBRALES_DEFAULT,
        )
        assert estado == "normal"

    def test_estado_proximo_por_km(self):
        """Km dentro del umbral proximo, fecha lejana -> proximo."""
        estado = MantenimientoEngine.calcular_estado(
            km_actual=100000,
            km_proximo=101500,  # 1500 km (<= 2000)
            hoy=date(2026, 11, 26),
            fecha_proximo=date(2027, 6, 1),  # lejos
            umbrales=MantenimientoEngine.UMBRALES_DEFAULT,
        )
        assert estado == "proximo"

    def test_estado_proximo_por_fecha(self):
        """Fecha dentro del umbral proximo, km lejano -> proximo."""
        estado = MantenimientoEngine.calcular_estado(
            km_actual=100000,
            km_proximo=110000,  # lejos
            hoy=date(2026, 11, 26),
            fecha_proximo=date(2026, 12, 20),  # +24 dias (<= 30)
            umbrales=MantenimientoEngine.UMBRALES_DEFAULT,
        )
        assert estado == "proximo"

    def test_estado_critico_por_km(self):
        """Km dentro del umbral critico -> critico."""
        estado = MantenimientoEngine.calcular_estado(
            km_actual=100000,
            km_proximo=100300,  # 300 km (<= 500)
            hoy=date(2026, 11, 26),
            fecha_proximo=date(2027, 6, 1),
            umbrales=MantenimientoEngine.UMBRALES_DEFAULT,
        )
        assert estado == "critico"

    def test_estado_critico_por_fecha(self):
        """Fecha dentro del umbral critico -> critico."""
        estado = MantenimientoEngine.calcular_estado(
            km_actual=100000,
            km_proximo=110000,
            hoy=date(2026, 11, 26),
            fecha_proximo=date(2026, 11, 30),  # +4 dias (<= 7)
            umbrales=MantenimientoEngine.UMBRALES_DEFAULT,
        )
        assert estado == "critico"

    def test_estado_vencido_por_km(self):
        """Km actual >= km proximo -> vencido."""
        estado = MantenimientoEngine.calcular_estado(
            km_actual=100000,
            km_proximo=100000,  # igual
            hoy=date(2026, 11, 26),
            fecha_proximo=date(2027, 6, 1),
            umbrales=MantenimientoEngine.UMBRALES_DEFAULT,
        )
        assert estado == "vencido"

    def test_estado_vencido_por_fecha(self):
        """Hoy >= fecha proximo -> vencido."""
        estado = MantenimientoEngine.calcular_estado(
            km_actual=100000,
            km_proximo=110000,
            hoy=date(2026, 11, 26),
            fecha_proximo=date(2026, 11, 26),  # hoy
            umbrales=MantenimientoEngine.UMBRALES_DEFAULT,
        )
        assert estado == "vencido"

    def test_estado_peor_de_los_dos(self):
        """Si km es normal pero fecha es critico, gana critico."""
        estado = MantenimientoEngine.calcular_estado(
            km_actual=100000,
            km_proximo=110000,  # normal
            hoy=date(2026, 11, 26),
            fecha_proximo=date(2026, 11, 29),  # +3 dias -> critico
            umbrales=MantenimientoEngine.UMBRALES_DEFAULT,
        )
        assert estado == "critico"

    def test_estado_sin_datos_es_normal(self):
        """Sin km ni fecha proximo, no se puede vencer."""
        estado = MantenimientoEngine.calcular_estado(
            km_actual=100000,
            km_proximo=None,
            hoy=date(2026, 11, 26),
            fecha_proximo=None,
            umbrales=MantenimientoEngine.UMBRALES_DEFAULT,
        )
        assert estado == "normal"


# ============================================================
# TESTS: _leer_umbrales (merge)
# ============================================================

class TestLeerUmbrales:
    """Tests del merge de umbrales."""

    def test_sin_override_usa_defaults(self):
        plan = _make_plan(umbrales_override=None)
        item = _make_item(umbrales_override=None)

        umbrales = MantenimientoEngine._leer_umbrales(plan, item)

        assert umbrales["umbral_proximo_km"] == 2000
        assert umbrales["umbral_critico_dias"] == 7

    def test_override_del_plan(self):
        plan = _make_plan(umbrales_override={"umbral_proximo_km": 3000})
        item = _make_item(umbrales_override=None)

        umbrales = MantenimientoEngine._leer_umbrales(plan, item)

        assert umbrales["umbral_proximo_km"] == 3000
        # Los demas siguen en default
        assert umbrales["umbral_proximo_dias"] == 30

    def test_override_del_item_pisa_al_plan(self):
        plan = _make_plan(umbrales_override={"umbral_proximo_km": 3000})
        item = _make_item(umbrales_override={"umbral_proximo_km": 4000})

        umbrales = MantenimientoEngine._leer_umbrales(plan, item)

        assert umbrales["umbral_proximo_km"] == 4000

    def test_clave_invalida_se_ignora(self):
        plan = _make_plan(umbrales_override={"clave_inventada": 9999})
        item = _make_item(umbrales_override=None)

        umbrales = MantenimientoEngine._leer_umbrales(plan, item)

        assert "clave_inventada" not in umbrales
        assert umbrales["umbral_proximo_km"] == 2000


# ============================================================
# TESTS: _dias_desde_intervalo
# ============================================================

class TestDiasDesdeIntervalo:
    """Tests de conversion de intervalos a dias."""

    def test_solo_dias(self):
        item = _make_item(intervalo_dias=180)
        assert MantenimientoEngine._dias_desde_intervalo(item) == 180

    def test_solo_meses(self):
        item = _make_item(intervalo_meses=6)
        assert MantenimientoEngine._dias_desde_intervalo(item) == 180

    def test_ambos_gana_dias(self):
        item = _make_item(intervalo_dias=90, intervalo_meses=6)
        assert MantenimientoEngine._dias_desde_intervalo(item) == 90

    def test_sin_intervalos_es_none(self):
        item = _make_item()
        assert MantenimientoEngine._dias_desde_intervalo(item) is None


# ============================================================
# TESTS: calcular_vencimientos (logica pura)
# ============================================================

class TestCalcularVencimientos:
    """Tests del calculo completo de vencimientos (sin DB)."""

    def test_plan_con_km_y_dias(self):
        """Un item con km y dias debe generar km_proximo y fecha_proximo."""
        item = _make_item(intervalo_km=10000, intervalo_meses=6)
        plan = _make_plan()
        plan.items = [item]
        pv = _make_plan_vehiculo(plan)

        resultados = MantenimientoEngine.calcular_vencimientos(
            vehiculo_id=pv.vehiculo_id,
            control_base_id=pv.control_base_id,
            km_actual=100000,
            hoy=date(2026, 11, 26),
            plan_vehiculos=[pv],
            advertencias_km=[],
            requiere_verificacion_km=False,
        )

        assert len(resultados) == 1
        v = resultados[0]
        assert v.km_proximo == 110000.0
        assert v.fecha_proximo == date(2027, 5, 25)  # 26/11 + 180 dias
        assert v.estado == "normal"
        assert v.vigente is True
        assert v.km_para_vencer == 10000.0
        assert v.dias_para_vencer == 180

    def test_plan_con_solo_km(self):
        """Item con solo km no debe generar fecha_proximo."""
        item = _make_item(intervalo_km=10000)
        plan = _make_plan()
        plan.items = [item]
        pv = _make_plan_vehiculo(plan)

        resultados = MantenimientoEngine.calcular_vencimientos(
            vehiculo_id=pv.vehiculo_id,
            control_base_id=pv.control_base_id,
            km_actual=100000,
            hoy=date(2026, 11, 26),
            plan_vehiculos=[pv],
            advertencias_km=[],
            requiere_verificacion_km=False,
        )

        assert len(resultados) == 1
        assert resultados[0].km_proximo == 110000.0
        assert resultados[0].fecha_proximo is None

    def test_plan_inactivo_se_saltea(self):
        """Un plan inactivo no debe generar vencimientos."""
        item = _make_item(intervalo_km=10000)
        plan = _make_plan(activo=False)
        plan.items = [item]
        pv = _make_plan_vehiculo(plan)

        resultados = MantenimientoEngine.calcular_vencimientos(
            vehiculo_id=pv.vehiculo_id,
            control_base_id=pv.control_base_id,
            km_actual=100000,
            hoy=date(2026, 11, 26),
            plan_vehiculos=[pv],
            advertencias_km=[],
            requiere_verificacion_km=False,
        )

        assert len(resultados) == 0

    def test_km_stale_marca_no_vigente(self):
        """Si el km no es confiable, vigente=False."""
        item = _make_item(intervalo_km=10000)
        plan = _make_plan()
        plan.items = [item]
        pv = _make_plan_vehiculo(plan)

        resultados = MantenimientoEngine.calcular_vencimientos(
            vehiculo_id=pv.vehiculo_id,
            control_base_id=pv.control_base_id,
            km_actual=0.0,  # km no confiable
            hoy=date(2026, 11, 26),
            plan_vehiculos=[pv],
            advertencias_km=["Sin turnos registrados"],
            requiere_verificacion_km=True,
        )

        assert len(resultados) == 1
        v = resultados[0]
        assert v.vigente is False
        assert v.requiere_verificacion is True
        assert "Sin turnos registrados" in v.advertencias