#!/bin/bash

# TaxIP 2.0 - Setup Script (Native Python)
# Uso: chmod +x setup.sh && ./setup.sh

set -e

echo "🚀 Iniciando setup de TaxIP 2.0..."

# Verificar Python 3.11+
echo "📌 Verificando Python..."
if command -v python3.11 &>/dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ "$PYTHON_VERSION" < "3.11" ]]; then
        echo "❌ Se requiere Python 3.11 o superior. Versión actual: $PYTHON_VERSION"
        exit 1
    fi
    PYTHON_CMD="python3"
else
    echo "❌ Python no encontrado. Instale Python 3.11+"
    exit 1
fi

echo "✅ Python $($PYTHON_CMD --version)"

# Crear entorno virtual
echo "📌 Creando entorno virtual..."
$PYTHON_CMD -m venv venv
source venv/bin/activate

# Actualizar pip
echo "📌 Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📌 Instalando dependencias..."
pip install -r requirements.txt

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📌 Creando archivo .env desde .env.example..."
    cp .env.example .env
    echo "⚠️  EDITAR .env con tus credenciales antes de continuar"
fi

# Verificar PostgreSQL
echo "📌 Verificando PostgreSQL..."
if command -v psql &>/dev/null; then
    echo "✅ PostgreSQL encontrado"
else
    echo "⚠️  PostgreSQL no encontrado. Instalar PostgreSQL 15+ con PostGIS"
fi

# Verificar Redis
echo "📌 Verificando Redis..."
if command -v redis-cli &>/dev/null; then
    echo "✅ Redis encontrado"
else
    echo "⚠️  Redis no encontrado. Instalar Redis"
fi

# Crear directorio para migraciones
echo "📌 Inicializando Alembic..."
alembic init migrations
echo "✅ Migraciones inicializadas"

echo ""
echo "✅ Setup completado exitosamente!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Editar archivo .env con tus credenciales"
echo "2. Crear base de datos: sudo -u postgres createdb taxip_db"
echo "3. Habilitar PostGIS: sudo -u postgres psql -d taxip_db -c 'CREATE EXTENSION IF NOT EXISTS postgis;'"
echo "4. Ejecutar migraciones: alembic upgrade head"
echo "5. Iniciar servidor: python run.py"
echo ""
echo "🌐 Servidor disponible en: http://localhost:8000"
echo "📚 Documentación API: http://localhost:8000/docs"