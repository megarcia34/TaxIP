import re
import os

# Ruta exacta del archivo en Windows
path = r"D:\ataxip\backend\app\models\trip.py"

if not os.path.exists(path):
    print(f"ERROR: No se encuentra el archivo en {path}")
    exit(1)

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Eliminar el bloque mal formado de ViajeCorrelativo
# (el que empieza en "class ViajeCorrelativo(Base):" y termina antes de "class HistorialEstadoViaje")
pattern = r"class ViajeCorrelativo\(Base\):\n.*?(?=class HistorialEstadoViaje)"
content = re.sub(pattern, "", content, flags=re.DOTALL)

# 2. Eliminar el segundo ViajeCorrelativo duplicado al final del archivo (si quedo)
pattern2 = r"class ViajeCorrelativo\(Base\):\n.*?$"
content = re.sub(pattern2, "", content, flags=re.DOTALL)

# 3. Agregar el ViajeCorrelativo correcto al final
correcto = '''

class ViajeCorrelativo(Base):
    """
    Control de correlativos de viajes por tenant y anio.
    Fuente de verdad del ultimo numero asignado por tenant+anio.
    Ver funcion trip.generar_codigo_viaje (plpgsql, atomica).
    """
    __tablename__ = "viaje_correlativo"
    __table_args__ = {"schema": "trip"}

    control_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.control_base.id"),
        primary_key=True,
    )
    anio: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    ultimo_numero: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
'''

content = content.rstrip() + correcto

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Archivo limpiado. ViajeCorrelativo correcto al final.")