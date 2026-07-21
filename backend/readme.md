# 🚖 TaxIP 2.0 - Plataforma de Taxis Moderna

## 📋 Descripción
Plataforma completa de solicitud de taxis (similar a Uber/Cabify) con:
- Geolocalización en tiempo real con PostGIS
- WebSockets para comunicación instantánea
- Autenticación JWT + bcrypt
- Múltiples métodos de pago (efectivo, billetera, MercadoPago)
- Módulo propietario para gestión de flota
- Cálculo dinámico de tarifas con Google Maps

## 🛠 Stack Tecnológico
- **Backend**: Python 3.11+ / FastAPI
- **Base de Datos**: PostgreSQL 15+ / PostGIS 3.4+
- **Tiempo Real**: WebSockets (nativos FastAPI)
- **Cache/Broker**: Redis
- **Hashing**: bcrypt (exclusivo)

## 📦 Requisitos Previos

### 1. PostgreSQL + PostGIS
```bash
# Ubuntu/Debian
sudo apt install postgresql-15 postgresql-15-postgis-3

# macOS
brew install postgresql@15 postgis

# Crear base de datos
sudo -u postgres createdb taxip_db
sudo -u postgres psql -d taxip_db -c "CREATE EXTENSION IF NOT EXISTS postgis;"
sudo -u postgres psql -d taxip_db -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"