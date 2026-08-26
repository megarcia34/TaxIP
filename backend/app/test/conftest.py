"""
Configuración de pytest para TAXIP 2.1.0
Fixtures y configuración para tests de liquidación
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path para poder importar app
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from app.database import Base
from app.core.config import settings
from app.test.helpers import CreateTestData


# ============================================================
# CONFIGURACIÓN DE BASE DE DATOS DE PRUEBAS
# ============================================================

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres123@localhost:5432/taxip_db"
)

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)


@pytest.fixture(scope="session")
async def engine():
    return test_engine


@pytest_asyncio.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Proporciona una sesión de base de datos para cada test.
    """
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with async_session() as session:
        await session.begin()
        try:
            yield session
            # Solo commit si la transacción está activa y no hubo error
            if session.is_active:
                await session.commit()
        except Exception:
            # Rollback en caso de error
            if session.is_active:
                await session.rollback()
        finally:
            if session.is_active:
                await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def create_test_data(db_session: AsyncSession):
    """
    Proporciona un helper para crear datos de prueba.
    """
    return CreateTestData(db_session)