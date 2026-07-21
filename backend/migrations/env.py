from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config, pool, create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

from alembic import context

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio raíz al path para poder importar app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar Base y modelos
from app.database import Base
from app.models import *  # Importa todos los modelos

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ METADATA DE LOS MODELOS (crítico para autogenerate)
target_metadata = Base.metadata

# Obtener URL de la base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:taxip154@localhost:5432/taxip_db"
)

# Convertir asyncpg a psycopg2 para migraciones síncronas
SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=SYNC_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
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
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()