# CONTEXTO — Gestion de altas pendientes (Tenant + Propietarios)

**Fecha de creacion:** 2026-10-13
**Proposito:** documento de arranque para el chat dedicado a la gestion de
altas pendientes (choferes y propietarios) desde el tenant y la carga de
datos del propietario (selfie, CBU, condicion impositiva, codigo de
asignacion de chofer).

**Estado del proyecto:** R18 cerrada. Alembic head `m3_020`. Diff BD <-> ORM
= 0. Tag `ronda18-fase18-completa`.

---

## 1. Objetivo del chat

**Implementar la gestion de altas pendientes desde el dashboard del tenant
y completar la carga de datos del propietario.**

### 1.1. Tenant (Admin Tenant)

- **Ver solicitudes de alta de choferes pendientes.**
- **Ver solicitudes de alta de propietarios pendientes.**
- **Aprobar / rechazar** ambas.

### 1.2. Propietarios (dashboard del propietario)

- Cargar **selfie** (foto de perfil).
- Cargar **condicion impositiva** (monotributo, responsable inscripto, etc.).
- Cargar **CBU** (para cobros).
- **Generar codigo** para asignar un chofer a un vehiculo.

---

## 2. Contexto del modelo de negocio

### 2.1. Tipos de chofer

**A) Chofer independiente:**
- Se registra en la app chofer.
- Carga documentos personales (licencia, seguro, antecedentes, selfie).
- El tenant lo revisa y aprueba.
- Espera que un propietario lo vincule a un vehiculo.

**B) Propietario-chofer (auto-gestion):**
- Se registra en el dashboard como propietario.
- Carga datos personales, vehiculos, documentacion, estado, neumaticos.
- El sistema lo crea como `fleet.chofer_vehiculo` (vehiculo_id=NULL).
- **El tenant lo revisa y aprueba.**
- Puede auto-asignarse uno de sus vehiculos.

**C) Chofer contratado por propietario:**
- El propietario genera un **codigo** de vinculacion.
- El chofer lo usa para vincularse al vehiculo.
- Se crea un `fleet.contrato_vehiculo`.

### 2.2. Doble validacion del propietario-chofer

1. **Es propietario registrado.**
2. **Fue aprobado por el tenant.**

Ambas condiciones necesarias para operar como chofer.

---

## 3. Estado actual del sistema

### 3.1. Endpoints existentes (tenant)

**En `app/routers/control_base.py`:**

| Endpoint | Metodo | Funcion |
|----------|--------|---------|
| `GET /api/control-base/choferes-pendientes` | GET | Lista choferes con `estado_aprobacion = 'pendiente'` |
| `PUT /api/control-base/aprobar-chofer/{chofer_vehiculo_id}` | PUT | Aprueba chofer (`estado_aprobacion = 'aprobado'`) |
| `PUT /api/control-base/rechazar-chofer/{chofer_vehiculo_id}` | PUT | Rechaza chofer (`estado_aprobacion = 'rechazado'` + `activo = false`) |

**Auth:** `get_current_admin_user`.

### 3.2. Endpoints existentes (propietario)

**En `app/routers/propietario/`:**

| Endpoint | Metodo | Funcion |
|----------|--------|---------|
| `GET /api/propietario/perfil` | GET | Obtiene perfil basico |
| `PUT /api/propietario/perfil` | PUT | Actualiza nombre, apellido, telefono, documento, direccion |
| `PUT /api/propietario/vehiculos/{id}/kilometraje` | PUT | Actualiza kilometraje |
| `POST /api/propietario/vehiculos` | POST | Crea vehiculo |
| `POST /api/propietario/contratos` | POST | Crea contrato (chofer <-> vehiculo) |

### 3.3. Modelo `fleet.chofer_vehiculo`

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | uuid | PK |
| `usuario_id` | uuid | FK a `auth.usuario` (CASCADE) |
| `vehiculo_id` | uuid | FK a `fleet.vehiculo` (CASCADE), **nullable** |
| `control_base_id` | uuid | FK a `tenant.control_base` |
| `estado_laboral` | varchar(20) | default `fuera_servicio` |
| `estado_aprobacion` | varchar(20) | default **`pendiente`** |
| `activo` | boolean | default true |

**Estados validos:** `pendiente`, `en_revision`, `aprobado`, `rechazado`.

**Importante:** no hay UNIQUE sobre `usuario_id` ni `(usuario_id, vehiculo_id)`.

### 3.4. Modelo `fleet.documentos_chofer`

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | uuid | PK |
| `usuario_id` | uuid | FK a `auth.usuario` (CASCADE) |
| `tipo_documento` | varchar(50) | UNIQUE con `usuario_id` |
| `url` | text | |
| `subido_en` | timestamp | default now() |
| `fecha_vencimiento` | date | nullable |
| `activo` | boolean | default true |

**Tipos existentes:** `licencia`, `seguro`, `antecedentes`.

---

## 4. Bug conocido

### 4.1. `LEFT JOIN` mal usado en `control_base.py:438`

**El endpoint `GET /api/control-base/choferes-pendientes` usa:**

```sql
JOIN fleet.vehiculo v ON v.id = cv.vehiculo_id

Es un JOIN (no LEFT JOIN). Excluye a todos los choferes con
vehiculo_id = NULL.

Impacto:

    Los propietarios-chofer (con vehiculo_id = NULL) no aparecen en la lista de pendientes.

    El admin no puede aprobarlos.

    ~50+ choferes afectados.

Fix: cambiar JOIN a LEFT JOIN y usar COALESCE en las columnas del vehiculo.
5. Caso de estudio: propietario.nuevo@taxip.com
5.1. Estado
Aspecto	Valor
Tipo principal	propietario
Rol adicional	chofer (en usuario_rol)
chofer_vehiculo.id	b6da25d6-3b38-47be-9eac-66af1229d096
chofer_vehiculo.vehiculo_id	NULL
chofer_vehiculo.estado_aprobacion	pendiente
foto_perfil_url	NULL
Documentos (documentos_chofer)	0 filas
Contratos activos	2 (para 2 vehiculos)
Vehiculos propios activos	2
5.2. Conclusión

El propietario-chofer no completo la carga de documentacion (docs + selfie) y por lo tanto no puede ser aprobado por el tenant.
6. Lo que hay que implementar
6.1. Tenant — Gestion de altas pendientes

Endpoints faltantes:

    GET /api/control-base/propietarios-pendientes — Lista propietarios con
    estado_aprobacion = 'pendiente' (o su equivalente).

    PUT /api/control-base/aprobar-propietario/{id} — Aprueba propietario.

    PUT /api/control-base/rechazar-propietario/{id} — Rechaza propietario.

Modificaciones:

    GET /api/control-base/choferes-pendientes → fix JOIN a LEFT JOIN.

UI (dashboard tenant):

    Pantalla de "Solicitudes pendientes" con dos tabs: choferes y propietarios.

    Por cada uno: datos personales, documentos, vehiculos.

    Boton aprobar / rechazar.

6.2. Propietario — Carga de datos

Endpoints faltantes:

    PUT /api/propietario/perfil/selfie — Sube selfie (URL de Cloudinary).

    PUT /api/propietario/perfil/cbu — Carga CBU.

    PUT /api/propietario/perfil/condicion-impositiva — Carga condicion fiscal.

    POST /api/propietario/choferes/codigo-invitacion — Genera codigo para
    asignar un chofer.

    POST /api/propietario/choferes/vincular — Vincula chofer por codigo.

UI (dashboard propietario):

    Pantalla de perfil con seccion para selfie, CBU, condicion impositiva.

    Pantalla de "mis choferes" con boton "generar codigo de invitacion".

6.3. DB — Migraciones

Posibles migraciones:

    Agregar cbu a auth.perfil_general (o tabla nueva).

    Agregar condicion_impositiva a auth.perfil_general (o tabla nueva).

    Agregar selfie_url (o usar foto_perfil_url existente).

    Tabla nueva fleet.codigo_invitacion_chofer (o usar fleet.contrato_qr).

Verificar con \d antes de decidir.
7. Reglas criticas del proyecto
7.1. Alineacion BD <-> ORM

    La DB es la fuente de verdad.

    No tocar la DB sin backup previo.

    No correr alembic revision --autogenerate.

    Usar diff.py como fuente de verdad (no alembic check).

    Reglas completas: docs/REGLAS_ALINEACION_BD_ORM.md.

7.2. Codigo

    N10: ASCII puro en comentarios y logs.

    UTF-8 sin BOM en todos los archivos.

    1 commit por paso.

    Un bloque por mensaje.

7.3. Entorno

    Backend: python run.py (no python -m uvicorn).

    Root backend: D:\aTaxip\backend.

    Git root: D:\aTaxip (monorepo).

    Dashboard: D:\aTaxip\dashboard.

    Landing: D:\aTaxip\Landing.

    App chofer: D:\aTaxip\app-chofer.

8. Documentacion de referencia

Backend:

    docs/CONTEXTO_TAXIP_v1.md — estado y deuda pendiente.

    docs/REGLAS_ALINEACION_BD_ORM.md — reglas tecnicas.

    docs/HISTORICO_CERRADAS.md — historico de rondas.

    docs/RESUMEN_EJECUTIVO_2026-10-13.md — contexto de negocio.

    docs/PROPUESTA_MODULOS_APP_CHOFER.md — propuesta de modulos.

Modelos ORM:

    app/models/fleet.py — ChoferVehiculo, ContratoVehiculo.

    app/models/auth.py — Usuario, PerfilGeneral.

    app/models/tenant.py — ControlBase, Empresa.

Routers:

    app/routers/control_base.py — endpoints del tenant.

    app/routers/propietario/ — endpoints del propietario.

    app/routers/chofer_registro.py — registro de chofer.

    app/routers/chofer_documentos.py — documentos del chofer.

Schemas:

    app/schemas/ — schemas Pydantic.

9. Proximo paso inmediato

Al arrancar el chat:

    Correr el checklist de arranque:
    powershell

    cd D:\aTaxip\backend
    .\venv\Scripts\Activate.ps1
    alembic current      # -> m3_020
    git log --oneline -1 # -> c5bcdf2
    git status           # -> clean

    Verificar el diff BD <-> ORM:
    powershell

    python -B scripts\orm_sync\apply.py --stats
    # -> Total items: 0

    Hacer backup DB antes de tocar schema:
    powershell

    $env:PGPASSWORD = "postgres123"
    & "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda19.dump"

    Investigar:

        Estructura actual de auth.perfil_general (para CBU y condicion impositiva).

        fleet.contrato_qr (por si se reutiliza para el codigo de invitacion).

        Endpoints existentes en propietario/ y control_base.py.

    Decidir el plan de trabajo con las respuestas a las preguntas abiertas.

10. Preguntas abiertas
10.1. Modelo de datos

    ¿CBU va en auth.perfil_general o en tabla nueva?

    ¿Condicion impositiva va en auth.perfil_general o en tabla nueva?

    ¿Reutilizamos foto_perfil_url o creamos selfie_url?

    ¿Reutilizamos fleet.contrato_qr para el codigo de invitacion o creamos tabla nueva?

10.2. Flujo

    ¿El propietario-chofer se aprueba una sola vez o se re-aprueba por cada vehiculo?

    ¿El codigo de invitacion es de un solo uso o reutilizable?

    ¿Tiene expiracion?

    ¿Quien genera el codigo? (¿el propietario? ¿el tenant?)

10.3. Alcance

    ¿Se incluye el frontend (dashboard tenant + propietario) o solo el backend?

    ¿Se incluye la app chofer? (por ejemplo, que el chofer use el codigo)

FIN DEL DOCUMENTO