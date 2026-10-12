"""
Contadores en memoria para metricas de la app.

R17 - G63: alerta si el motor de precios cae a fallback.

Este modulo expone un registro thread-safe de contadores consultables
via endpoint /health/metrics.

NO reemplaza a una solucion de monitoreo real (Sentry, Grafana, etc).
Cuando se integre una, este modulo se puede reemplazar por el cliente
del proveedor o complementarse.

Uso:
    from app.core.metrics import metrics, Keys
    metrics.increment(Keys.FALLBACK_PRECIO_MOTOR_ERROR)
    valor = metrics.get(Keys.FALLBACK_PRECIO_MOTOR_ERROR)
    snapshot = metrics.snapshot()
"""
import threading
from collections import defaultdict
from typing import Dict


class MetricsRegistry:
    """Registro thread-safe de contadores en memoria."""

    def __init__(self):
        self._lock = threading.Lock()
        self._counters: Dict[str, int] = defaultdict(int)

    def increment(self, key: str, amount: int = 1) -> None:
        """Incrementa un contador. Thread-safe."""
        if amount <= 0:
            return
        with self._lock:
            self._counters[key] += amount

    def get(self, key: str) -> int:
        """Lee un contador. Retorna 0 si no existe."""
        with self._lock:
            return self._counters.get(key, 0)

    def snapshot(self) -> Dict[str, int]:
        """Snapshot completo de contadores (copia). Thread-safe."""
        with self._lock:
            return dict(self._counters)

    def reset(self) -> None:
        """Resetea todos los contadores. Util para tests."""
        with self._lock:
            self._counters.clear()


# Instancia global (singleton por proceso)
metrics = MetricsRegistry()


class Keys:
    """Claves canonicas de contadores.

    Evitar strings sueltos en el codigo. Si se necesita una nueva,
    agregarla aca.
    """

    # G63 - Fallbacks del motor de precios y del calculo de distancia.
    FALLBACK_DIRECTIONS_PERSISTIDOS = "fallback.directions.persistidos"
    FALLBACK_DIRECTIONS_HAVERSINE = "fallback.directions.haversine"
    FALLBACK_PRECIO_MOTOR_ERROR = "fallback.precio.motor_error"