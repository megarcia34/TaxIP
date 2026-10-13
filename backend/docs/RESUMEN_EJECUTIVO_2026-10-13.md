# RESUMEN EJECUTIVO — TaxIP 2.0

**Ultima actualizacion:** 2026-10-13 (post R18)
**Version:** 2.2.0
**Estado general:** Backend en produccion. Frontend web en produccion. App chofer en desarrollo.
**Alembic head:** m3_020
**Diff BD <-> ORM:** 0 items (alineado desde R14)

---

## 1. QUE ES TAXIP 2.0

TaxIP 2.0 es una plataforma moderna de gestion de taxis que nace de la
necesidad de los propietarios de taxis de competir con aplicaciones como
Uber y Didi, pero manteniendo el modelo de negocio tradicional (bajada
de bandera + fichas) y el control municipal.

La plataforma se comercializa **por municipios**: cada ciudad (tenant)
opera de forma independiente con su propia configuracion de tarifas,
flota y administracion.

### Ecosistema integrado

- **Landing publica** con motor de reservas web (reemplaza la app para pasajeros).
- **Dashboard administrativo** para gestion de flota, empresas y configuraciones.
- **Modulo corporativo** (despacho manual para hoteles, sanatorios, centrales de llamadas).
- **Modulo propietario** con gestion de vehiculos, contratos, gastos, mantenimiento, documentos y neumaticos.
- **Sistema de tarifas multi-tenant** con 4 modos de calculo.
- **App chofer** (backend listo, frontend en desarrollo).
- **Multi-tenant completo** con aislamiento de datos por `control_base_id`.

---

## 2. MODELO DE NEGOCIO

### 2.1. Actores del ecosistema

| Actor | Descripcion |
|-------|-------------|
| Propietario Intelectual | Dueno de la plataforma, define estrategia y acuerdos comerciales |
| Super Admin Maestro | Administra globalmente la plataforma, crea empresas operadoras |
| Super Admin | Colabora en la administracion global y soporte |
| Admin Tenant | Administra la operacion en una ciudad (empresa de taxis / remis) |
| Propietario | Dueno de vehiculos, gestiona contratos y flota |
| Empresa | Organizacion que solicita viajes para terceros (hoteles, sanatorios) |
| Empleado | Solicita viajes en representacion de la empresa |
| Conductor | Presta el servicio de transporte |
| Comercio Adherido | Genera QR publicos para solicitar taxis (gratuito) |
| Pasajero | Usuario final del servicio |

### 2.2. Flujo de ingresos

1. **Empresa Operadora (Admin Tenant)** paga un **canon mensual por vehiculo activo** al Propietario Intelectual.
2. La plataforma cobra un **porcentaje sobre cada viaje** (configurable por tenant).
3. Los propietarios pueden operar bajo **3 modelos**:
   - **Auto-gestionado** (dueno conduce).
   - **A porcentaje** (division de ganancias).
   - **Alquiler fijo** (canon diario).
4. **Los pagos electronicos se acreditan directamente en la cuenta recaudadora del propietario.** La plataforma no retiene fondos.

### 2.3. Diferenciacion

- **Exclusivo para taxis** (no vehiculos particulares).
- **Tarifa regulada:** bajada de bandera + fichas (adaptable a cada municipio).
- **Integracion con control municipal** y requisitos legales.

---

## 3. STACK TECNOLOGICO

| Capa | Tecnologia | Version |
|------|-----------|---------|
| Backend API | Python + FastAPI | Python 3.12.10 + FastAPI |
| Base de datos | PostgreSQL + PostGIS | PostgreSQL 17 + PostGIS 3.6 |
| ORM | SQLAlchemy async | 2.0+ |
| Migraciones | Alembic | head `m3_020` |
| Autenticacion | JWT (python-jose) + bcrypt | - |
| Tiempo real | WebSockets (nativos FastAPI) | - |
| Servidor HTTP | Uvicorn via `python run.py` | - |
| Geolocalizacion | GeoAlchemy2 + Google Maps API | - |
| Dashboard | Next.js 14 (App Router) + Tailwind + shadcn/ui | 14.x |
| Landing publica | Next.js 15 + CSS plano | 15.x |
| App chofer | Expo SDK 57 + React Native 0.86 + React 19 + expo-router 57.0.24 | - |

---

## 4. ARQUITECTURA GENERAL

### 4.1. Estructura multi-tenant

Cada tenant (`control_base_id`) representa una empresa operadora
(municipio). Todas las tablas principales incluyen este identificador
para aislar los datos.

control_base (tenant)
├── empresa (corporativa)
├── vehiculo
├── usuario (con rol)
├── viaje_solicitado
├── configuracion_tarifa
└── ...

### 4.2. Esquemas de base de datos (12 schemas)

| Schema | Proposito |
|--------|-----------|
| `auth` | Usuarios, roles, perfiles, tokens, turnos de empleados |
| `tenant` | Control base, empresas, configuracion |
| `geo` | Pais, provincia, ciudad |
| `fleet` | Vehiculos, choferes, contratos, turnos, gastos, mantenimiento, documentos, neumaticos |
| `trip` | Viajes, calificaciones, panico, objetos olvidados |
| `payment` | Billetera, transacciones, tarifas, facturas, metodo_pago |
| `notification` | Notificaciones push/in-app |
| `audit` | Logs GPS, alertas de desvio, auditoria de acciones |
| `corporate` | Empresas corporativas, cuentas corrientes, movimientos |
| `comunicacion` | Conversaciones, mensajes, emails enviados |
| `rentabilidad` | Analisis de medios de pago, rentabilidad diaria/mensual |
| `public` | Comercio adherido, escaneos QR |

### 4.3. Tablas principales (20+)

| Tabla | Schema | Proposito |
|-------|--------|-----------|
| `usuario` | auth | Usuarios con bcrypt, JWT, roles, suspension |
| `perfil_general` | auth | Datos personales |
| `tipo_usuario` | auth | Roles (admin, chofer, pasajero, propietario, etc.) |
| `refresh_token` / `reset_token` | auth | Tokens de refresco y recuperacion |
| `turno_empleado` | auth | Control de turnos de empleados corporativos |
| `control_base` | tenant | Empresa operadora (tenant) |
| `empresa` | tenant | Empresa corporativa (cliente) |
| `configuracion_tenant` | tenant | Parametros financieros (canon, comisiones, costos) |
| `vehiculo` | fleet | Vehiculos con QR unico (`qr_uuid`) |
| `chofer_vehiculo` | fleet | Asignacion activa con ubicacion y estado laboral |
| `contrato_vehiculo` | fleet | Contrato propietario-chofer (porcentaje, fijo, auto) |
| `turno_chofer` | fleet | Jornada laboral con check-in/out, km, combustible, liquidacion |
| `gasto_vehiculo` / `gasto_turno` | fleet | Gastos de vehiculo y gastos durante turno |
| `mantenimiento_vehiculo` | fleet | Mantenimientos programados |
| `documento_vehiculo` / `documento_propietario` | fleet | Documentacion con alertas de vencimiento |
| `foto_vehiculo` | fleet | Fotos del vehiculo (Cloudinary) |
| `neumatico_*` (7 tablas) | fleet | Gestion completa de neumaticos |
| `viaje_solicitado` | trip | Viajes con origen/destino, precios |
| `calificacion` | trip | Calificaciones 1-5 |
| `configuracion_tarifa` | payment | Tarifa por tenant con modo de recargos |
| `billetera` / `transaccion` | payment | Wallet digital (Momento 3 - futuro) |
| `factura_empresa` | payment | Facturacion corporativa |
| `metodo_pago` | payment | Catalogo de metodos de pago (4 filas) |

**Nota:** `trip.reserva` fue **deprecada** en R13. El modulo corporativo
ahora usa `trip.viaje_solicitado` con estados mapeados.

---

## 5. MODULOS DEL SISTEMA (ESTADO ACTUAL)

### 5.1. Backend API (FastAPI)

**Estado:** Produccion
**Endpoints:** 200+ funcionales
**Documentacion:** Swagger en `/docs`
**Alembic head:** `m3_020`
**Diff BD <-> ORM:** 0 items

**Grupos principales:**

| Grupo | Endpoints |
|-------|-----------|
| Autenticacion | `/api/auth/*` |
| Usuarios | `/api/usuarios/*` |
| Choferes | `/api/choferes/*` |
| Vehiculos | `/api/propietario/vehiculos/*` |
| Viajes | `/api/viajes/*` (publicos y autenticados) |
| Control Base | `/api/control-base/*` |
| Propietario | `/api/propietario/*` (contratos, turnos, gastos, mantenimiento, documentos, neumaticos) |
| Empresas | `/api/empresa/*`, `/api/admin/empresas/*` |
| Pagos | `/api/pagos/*`, `/api/billetera/*` |
| Super Admin | `/api/super-admin/*` |
| Publicos | `/api/public/*` (calculo de tarifa, solicitud, estado) |
| Chofer Turnos | `/api/chofer/turno/*` (check-in, check-out, viajes huerfanos) |
| Metricas | `/health/metrics` (super_admin) |
| Metricas propietario | `/api/propietario/metricas/fallbacks` |

**WebSockets:**

- Endpoint: `ws://.../ws/{user_id}`
- Eventos: actualizacion de ubicacion, aceptacion de viaje, seguimiento en tiempo real, panico.

### 5.2. Dashboard Administrativo (Next.js 14)

**Estado:** Produccion

**Rutas protegidas por rol (middleware + layout):**

| Rol | Ruta | Funcionalidad |
|-----|------|---------------|
| Super Admin Maestro | `/super-admin` | Control global, gestion de tenants, KPIs (con recaudacion) |
| Super Admin | `/super-admin` | Control global, KPIs (sin recaudacion) |
| Admin Tenant | `/admin` | Gestion de empresas, choferes, vehiculos, viajes, estadisticas |
| Admin Empresa | `/dashboard-empresa` | Gestion de empleados, viajes corporativos, facturacion |
| Propietario | `/dashboard-propietario` | Gestion de flota, contratos, gastos, mantenimiento, neumaticos, documentos |
| Empleado | `/operativo` | Despacho manual, turnos, solicitudes, seguimiento |

**Caracteristicas transversales:**

- NextAuth con credentials provider.
- Interceptores para refresh de token.
- Sidebar dinamico segun rol.
- TanStack Query para caching y sincronizacion.

### 5.3. Landing Publica (Next.js 15)

**Estado:** Produccion

**URLs publicas:** `/` (landing), `/pedir` (motor de reservas),
`/pedir/seguimiento/[id]`

**Caracteristicas:**

- Diseno con CSS plano (Tailwind descartado por problemas de deteccion).
- Motor de reservas web completo:
  - Formulario con Google Maps (Places + Directions).
  - Calculo de tarifa en tiempo real (segun modo configurado).
  - Validacion de email con SMTP.
  - Autenticacion automatica (registro/login segun email).
  - WebSocket para seguimiento en tiempo real.
  - Pipeline de estados (pendiente -> aceptado -> en_curso -> finalizado).
- Secciones informativas: hero, canales de solicitud, beneficios, metodos de pago, tipos de vehiculo, estadisticas, ecosistema, FAQ.
- **Reemplaza la necesidad de app movil para pasajeros.**

### 5.4. Modulo Corporativo (Despacho Manual)

**Estado:** Produccion
**Ruta:** `/operativo/nueva-solicitud`

**Flujo:**

1. Empleado inicia turno (check-in).
2. Completa formulario con origen (precargado), destino, pasajero, tipo de vehiculo, centro de costo, paradas intermedias.
3. El mapa muestra la ruta y la ubicacion de choferes disponibles.
4. Calculo de tarifa en tiempo real con Google Directions.
5. **Validacion de choferes disponibles** (bloquea si no hay).
6. Despacho -> reserva creada en `trip.viaje_solicitado` (post R13).
7. Pipeline de estados: reservado -> despachado -> vehiculo_llego -> pasajero_a_bordo -> completado.
8. Seguimiento en tiempo real con WebSocket.

**Mejoras clave:**

- Autocompletado con soporte para intersecciones y direcciones sin numero.
- Validacion de disponibilidad antes del despacho (alertas roja/amarilla).
- Badge de "Coches Libres" actualizado cada 30 segundos.

### 5.5. Modulo Propietario

**Estado:** Produccion
**Ruta base:** `/dashboard-propietario`

**Submodulos funcionales:**

| Modulo | Funcionalidad |
|--------|---------------|
| Vehiculos | CRUD completo con QR unico (`qr_uuid`) |
| Contratos | 3 modelos: auto-gestionado, porcentaje, alquiler fijo |
| Turnos | Check-in/out, km, combustible, liquidacion automatica |
| Gastos | Registro por vehiculo con categorias |
| Mantenimiento | Preventivo y correctivo, alertas por km/fecha |
| Ingresos | Recaudacion manual y automatica |
| Rentabilidad | KPIs por vehiculo, margen, ROI, benchmarking |
| Documentos | Gestion de documentos (propietario y vehiculo) con alertas de vencimiento |
| Neumaticos | Registro, medicion, rotacion, sugerencias automaticas |
| Reportes | Exportacion a CSV/Excel |

**Modelos de contrato:**

- **Porcentaje:** division de ganancias (ej. 70% propietario, 30% chofer).
- **Alquiler fijo:** canon diario fijo.
- **Auto-gestionado:** propietario conduce.

**Liquidacion automatica:**

Al cerrar el turno, el sistema calcula:

- Monto bruto (viajes app).
- Comision del chofer segun contrato.
- Utilidad del propietario.
- Libera el vehiculo para otro chofer de forma inmediata.

### 5.6. Sistema de Tarifas Multi-Tenant

**Estado:** Produccion
**Configuracion:** por `control_base_id` en `payment.configuracion_tarifa`

**Modos de calculo:**

| Modo | Formula | Uso tipico |
|------|---------|------------|
| Ficha Argentina | Bajada + (distancia/100 x precio_ficha) + (espera_min x precio_espera) | Tucuman y otras provincias |
| Por Kilometro | Bajada + (km x precio_km) + (minutos x precio_minuto) | CABA, estandar internacional |
| Por Minuto | Precio base x minutos | Ciudades con tarifa horaria |
| Mixto | Combinacion personalizada | Regulaciones especiales |

**Recargos configurables:**

- Nocturno (rango horario).
- Domingo.
- Feriado.

**Tipos de vehiculo:** Standard, Premium, Van, Minivan (cada uno con
factores de precio).

**Integracion:** Google Directions API para distancia y tiempo real.

**Motor unificado TaxIP 2.1:** una sola formula, variables
configurables por tenant, mismo resultado siempre.

### 5.7. Administracion de Empresas Corporativas

**Estado:** Produccion

**Jerarquia:**

- Admin Tenant crea y gestiona empresas (hoteles, sanatorios, oficinas).
- Admin Empresa gestiona empleados y vehiculos de la empresa.
- Empleado solicita viajes en nombre de terceros.

**Caracteristicas:**

- Suspension a nivel de tenant, empresa o usuario individual.
- Facturacion consolidada (estructura lista).
- Cuenta corriente y limite de credito.
- Dashboard con KPIs propios.

### 5.8. App Chofer (Expo / React Native)

**Estado:** En desarrollo
**Build:** EAS Build (perfil development)

**Backend listo:**

- Auth + JWT.
- Check-in / check-out con codigo de validacion.
- Ciclo de vida del viaje (aceptar, llegar, iniciar, finalizar).
- Gestion de viajes huerfanos (R17).
- Notificaciones in-app.
- WebSocket para ubicacion en tiempo real.

**Frontend pendiente:**

- UI del flujo de forzar cierre de viajes huerfanos (G67).
- UI de metricas propias del chofer.
- Configuracion de URL del backend publico (G80, bloqueada por deploy).

---

## 6. ROLES Y PERMISOS

| Rol en DB | Nombre amigable | Ruta destino | Backend Dependency |
|-----------|----------------|--------------|-------------------|
| `super_admin` | Super Admin Maestro | `/super-admin` | `get_current_user()` + validacion manual |
| `admin` (sin tenant) | Super Admin | `/super-admin` | `get_current_user()` + `control_base_id` NULL |
| `admin` (con tenant) | Admin Tenant | `/admin` | `get_current_admin_user()` |
| `admin_empresa` | Admin Empresa | `/dashboard-empresa` | `get_current_user()` + validacion de empresa |
| `propietario` | Propietario | `/dashboard-propietario` | `get_propietario_id()` |
| `admin_propietario` | Admin Propietario | `/dashboard-propietario` | `get_propietario_id()` |
| `empresa` | Empresa | `/dashboard-empresa` | `get_current_user()` + validacion de empresa |
| `empleado` | Empleado | `/operativo` | `get_current_user()` |
| `chofer` / `conductor` | Conductor | `/operativo` | `get_current_driver_user()` |

**Redireccion en login:**

- Si `tipo_usuario = 'admin'` y `control_base_id` es NULL -> `/super-admin`.
- Si `tipo_usuario = 'admin'` y `control_base_id` existe -> `/admin`.
- Resto segun `roleMap`.

---

## 7. FLUJOS DE TRABAJO PRINCIPALES

### 7.1. Alta de vehiculo y QR

1. Propietario registra vehiculo -> se genera `qr_uuid` unico.
2. El sistema crea URL firmada y dibuja el codigo QR.
3. Propietario descarga e imprime el QR (fisico, en vinilo).
4. El QR es fijo y nunca cambia.

### 7.2. Vinculacion chofer-propietario

1. Propietario genera **codigo de validacion**, envia a chofer por WhatsApp o mensajeria interna.
2. Chofer ingresa el codigo en su app.
3. Backend crea contrato en estado `PENDIENTE_CONFIGURACION`.
4. Propietario recibe notificacion y configura condiciones (porcentaje o canon).
5. Contrato pasa a `ACTIVO` y chofer puede iniciar turno.

**Nota (R13):** este flujo cambio respecto al modelo original (que usaba QR escaneado).

### 7.3. Turno y liquidacion

1. Chofer ingresa **codigo de validacion** en su app (check-in), ingresa km inicial y combustible.
2. Durante el turno, recibe viajes y puede registrar gastos.
3. Al cerrar turno (check-out), ingresa km final, combustible y monto de ticketera.
4. El sistema calcula liquidacion instantanea y libera el vehiculo.
5. Propietario confirma la liquidacion.

**R17 - Forzar cierre:** si el chofer tiene viajes huerfanos (`aceptado`
o `en_curso`) al intentar cerrar turno:

- Puede listarlos en `GET /api/chofer/turno/viajes-huerfanos`.
- Puede cerrarlos uno por uno en `POST /api/chofer/turno/viajes-huerfanos/{id}/cerrar`.
- Motivos: `pasajero_cancelo`, `pasajero_no_aparecio`, `pasajero_pidio_bajarse`, `pasajero_abandono`, `emergencia`, `chofer_cancelo`, `error_sistema`, `otro`.

### 7.4. Solicitud de viaje (todos los canales)

- **Landing web** (`/pedir`) con seguimiento en tiempo real.
- **QR publico** (comercios adheridos).
- **Portal corporativo** (empleados).
- **Via publica** (chofer registra viaje manual).
- **App movil** (backend listo, frontend en desarrollo).

### 7.5. Despacho manual (corporativo)

- Empleado con turno activo.
- Formulario con mapa interactivo.
- Validacion de choferes disponibles.
- Creacion de reserva y seguimiento por pipeline de estados.
- Asignacion de centro de costo para facturacion.

### 7.6. Gestion de documentos y alertas

- Propietario sube documentos (DNI, licencia, seguro, VTV, cedula verde).
- Sistema calcula vencimientos y genera niveles: vencido, critico, urgente, preventivo.
- Scheduler automatico (cada 6 horas) envia notificaciones por email.
- Dashboard muestra alertas y badge en el sidebar.

### 7.7. Gestion de neumaticos

- Registro de neumaticos por vehiculo (marca, modelo, medida, tipo).
- Posicionamiento en ejes (delantero/trasero, izquierdo/derecho).
- Medicion de profundidad con indicador visual (verde/amarillo/rojo).
- Rotacion automatica (patron cruzado).
- Sugerencias automaticas (rotacion, cambio, revision).
- Historial de operaciones e imagenes (Cloudinary).

---

## 8. SEGURIDAD

- **Contrasenas:** bcrypt exclusivo (NO SHA512 legacy).
- **JWT:** Access token (30 min) + Refresh token (7 dias) almacenado en DB.
- **Recuperacion:** por email con token temporal (expira 1 hora).
- **Suspensiones:** a nivel de tenant, empresa o usuario individual.
- **CORS:** configurado para frontends autorizados.
- **Proteccion de rutas:** middleware en Next.js + dependencies en FastAPI.
- **Auditoria forense:** `audit.log_acciones` registra eventos criticos.

---

## 9. ESTADO DE DESARROLLO (RESUMEN)

| Modulo | Estado | Observaciones |
|--------|--------|---------------|
| Backend API | Produccion | 200+ endpoints, WebSockets, PostGIS |
| Dashboard Administrativo | Produccion | Next.js 14, todos los roles |
| Landing Publica | Produccion | Next.js 15, motor de reservas web |
| Modulo Corporativo | Produccion | Despacho manual, pipeline de estados |
| Modulo Propietario | Produccion | Vehiculos, contratos, turnos, gastos, mantenimiento, documentos, neumaticos |
| Sistema de Tarifas | Produccion | 4 modos, configurable por tenant |
| App Movil (Chofer) | Backend listo, frontend en desarrollo | Backend soporta todo el ciclo |
| App Movil (Pasajero) | Reemplazada por landing web | No se hara |
| Modulo de Cupones / Puntos | Estructura lista, endpoints pendientes | Tablas creadas, sin UI |
| Facturacion PDF | Estructura lista, generacion pendiente | Endpoints de facturacion listos |

---

## 10. GUIA DE INSTALACION Y EJECUCION (NATIVA, SIN DOCKER)

### 10.1. Backend (FastAPI)

```bash
cd D:\aTaxip\backend
.\venv\Scripts\Activate.ps1
python run.py

Servidor: http://localhost:8000
Documentacion: http://localhost:8000/docs

Variables de entorno (.env):
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/taxip_db
SECRET_KEY=...
SMTP_HOST=smtp.gmail.com
SMTP_USER=...
SMTP_PASSWORD=...
CLOUDINARY_CLOUD_NAME=...

Backend con reload (solo dev):
powershell

$env:RELOAD = "true"
python run.py

Default: RELOAD=false (produccion).
10.2. Dashboard (Next.js 14)
bash

cd D:\aTaxip\dashboard
npm install
npm run dev

Acceso: http://localhost:3000
10.3. Landing (Next.js 15)
bash

cd D:\aTaxip\landing
npm install
npm run dev

Acceso: http://localhost:3001 (por defecto)
10.4. App Chofer (Expo)
bash

cd D:\aTaxip\app-chofer
npm install
eas build --profile development --platform android

Cuenta EAS: megarcia34
Proyecto: @megarcia34/taxip-chofer
projectId: b54c9f37-bdd0-4845-8c78-9628a3cda6a2

Workaround activo: 2 parches en patches/expo-router+57.0.24.patch
por bug de expo-router con React 19. No tocar hasta que expo saque fix upstream.
11. DOCUMENTACION ADICIONAL

    Swagger/OpenAPI: http://localhost:8000/docs

    Repositorio backend: D:\aTaxip\backend

    Repositorio dashboard: D:\aTaxip\dashboard

    Repositorio landing: D:\aTaxip\landing

    Repositorio app chofer: D:\aTaxip\app-chofer

    Base de datos: PostgreSQL con PostGIS

Documentos clave del proyecto:

    Contexto del proyecto: docs/CONTEXTO_TAXIP_v1.md

    Reglas BD <-> ORM: docs/REGLAS_ALINEACION_BD_ORM.md

    Deuda tecnica: docs/DEUDA_TECNICA_ACTUAL.md

    Historico de rondas: docs/HISTORICO_CERRADAS.md

    Decisiones ORM: docs/orm_sync/orm_decisiones.md

12. PENDIENTES Y PROXIMOS PASOS
Corto plazo (prioridad alta)

    App movil chofer (frontend nativo): completar UI del flujo de forzar cierre de viajes huerfanos.

    Notificaciones push (Firebase) para choferes y propietarios.

    Subida de comprobantes (gastos, mantenimientos) a Cloudinary.

    UI del dashboard propietario para metricas de fallback de precios (G63.frontend_propietario).

Mediano plazo

    Modulo de cupones y puntos (UI + endpoints).

    Facturacion PDF automatica para empresas corporativas.

    Graficos interactivos en dashboards (Chart.js).

    Billetera TaxIP (Momento 3): wallet con saldo del usuario final.

    Despliegue del backend a produccion (URL publica para G80).

Largo plazo

    Mantenimiento predictivo con IA.

    Integracion con gateways de pago (MercadoPago).

    Viajes compartidos (pool).

13. CONTACTO Y SOPORTE
Area	Responsable
Backend (FastAPI)	Equipo de desarrollo backend
Frontend (Dashboard / Landing)	Equipo de desarrollo frontend
App Chofer (Expo)	Equipo de desarrollo mobile
Base de Datos	DBA
Google Maps / Cloudinary	Administrador de servicios cloud

Este documento refleja el estado del sistema al 2026-10-13 (post R18).
Cualquier actualizacion debe registrar la fecha y la version.

FIN DEL DOCUMENTO