import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool, create_engine
from dotenv import load_dotenv

from alembic import context

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ✅ 1. IMPORTAR BASE Y TODOS LOS MODELOS EXPLÍCITAMENTE
# Esto garantiza que Base.metadata tenga todas las tablas registradas correctamente
from app.database import Base
import app.models.tenant
import app.models.auth
import app.models.fleet
import app.models.trip
import app.models.payment
import app.models.geo
import app.models.notification
import app.models.foto_viaje
import app.models.turno
import app.models.gasto_turno
import app.models.audit

# this is the Alembic Config object
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ 2. METADATA DE LOS MODELOS
target_metadata = Base.metadata

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:taxip154@localhost:5432/taxip_db"
)

# Convertir asyncpg a psycopg2 para migraciones síncronas
SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")


# ✅ Función para ignorar tablas del sistema que no están en nuestros modelos
def include_name(name, type_, parent_names):
    if type_ == "table":
        # Ignorar tablas de extensión PostGIS u otras del sistema que no gestionamos
        if name in ["spatial_ref_sys", "geography_columns", "geometry_columns"]:
            return False
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=SYNC_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_schemas=True,       # ✅ 3. CLAVE: Inspeccionar todos los schemas
        include_name=include_name,  # ✅ 4. CLAVE: Filtrar tablas del sistema
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(SYNC_DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_schemas=True,       # ✅ 3. CLAVE: Inspeccionar todos los schemas
            include_name=include_name,  # ✅ 4. CLAVE: Filtrar tablas del sistema
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()