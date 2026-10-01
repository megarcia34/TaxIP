# Plan de aplicacion ORM - DB

**Fecha:** 2026-10-01
**Ronda:** 6, Fase 2, Sesion 2
**Head Alembic:** m3_010
**Basado en:** docs/orm_sync/orm_diff.json (1.280 diferencias),
docs/orm_sync/orm_decisiones.md (D-001 a D-012),
docs/DEUDA_TECNICA_ACTUAL.md (53 items).

---

## Proposito

Traducir el diagnostico de Fase 1 y las decisiones de Fase 2 en un plan
concreto de aplicacion. Este documento NO ejecuta cambios: describe QUE
cambiar, EN QUE ORDEN, y COMO (automatico vs manual).

La ejecucion real es Fase 3 (apply.py) y Fase 4 (aplicacion por archivo).

---

## 1. Resumen ejecutivo

### 1.1 Magnitud

- 1.280 diferencias totales.
- 247 Tier 1 (critico).
- 912 Tier 2 (importante).
- 120 Tier 3 (cosmetico).
- 1 Tier 4 (muerte).
- 24 items requerian decision manual -> resueltos en Fase 2 (D-005, D-006,
  D-007, D-012).

### 1.2 Concentracion del Tier 1

- app/models/trip.py: 111 T1 (45% del total T1).
- app/models/fleet.py: 93 T1 (38%).
- app/models/auth.py: 17 T1 (7%).
- app/models/tenant.py: 15 T1 (6%).
- app/models/payment.py: 11 T1 (4%).

trip.py + fleet.py = 204/247 T1 = 82%.

### 1.3 Distribucion por clasificacion (Tier 1)

| Clasificacion | Cantidad |
|---|---|
| constraint_falta | 58 |
| nullable_desalineado | 37 |
| columna_falta | 34 |
| indice_falta | 33 |
| constraint_nombre_desalineado | 27 |
| tipo_desalineado | 24 |
| comment_desalineado | 11 |
| constraint_desalineada | 10 |
| indice_nombre_desalineado | 4 |
| indice_sobra | 4 |
| constraint_sobra | 3 |
| tabla_falta | 2 |
| **TOTAL** | **247** |

### 1.4 Distribucion por archivo (total, no solo T1)

| Items | Archivo |
|---|---|
| 408 | app/models/fleet.py |
| 171 | app/models/trip.py |
| 144 | app/models/auth.py |
| 134 | app/models/fleet.py (neumatico_*) |
| 119 | app/models/payment.py |
| 99 | app/models/corporate.py |
| 92 | app/models/tenant.py |
| 44 | app/models/audit.py |
| 36 | app/models/public.py |
| 20 | app/models/geo.py |
| 11 | app/models/notification.py |
| 1 | app/models/comunicacion.py (NO EXISTE) |
| 1 | app/models/rentabilidad.py (NO EXISTE) |
| **TOTAL** | **1.280** |

---

## 2. Principios de aplicacion

### 2.1 Regla de oro

La DB es la fuente de verdad. El ORM se adapta a la DB, no al reves.
Excepcion explicita: D-007 (control_base.lat/lng) donde el ORM tenia un
error grave (String(50) en vez de Numeric).

### 2.2 Orden de aplicacion

1. Primero Tier 1 (critico), agrupado por archivo del ORM.
2. Despues Tier 2 y Tier 3, agrupados por tipo de cambio.
3. Al final Tier 4 (eliminacion de trip.reserva).
4. Schemas nuevos (comunicacion, rentabilidad) al cierre.

### 2.3 Reglas operativas

- NO `alembic revision --autogenerate` (destructivo).
- Backup DB antes de cada sub-fase que toque schema.
- Un commit por archivo o por sub-fase.
- `alembic check` despues de cada sub-fase para verificar progreso.
- Verificar `alembic current` y `alembic heads` antes y despues.
- Comentarios en ASCII puro (N10).
- Un bloque por mensaje al aplicar.

### 2.4 Estrategia apply.py

apply.py genera **borradores** (archivos .md con el codigo propuesto),
NO reescribe archivos .py del ORM directamente.

Razon: reescribir .py automaticamente es riesgoso (sintaxis, indentacion,
relaciones SQLAlchemy, orden de declaracion de clases). Con borradores,
el operador revisa y pega a mano, manteniendo control total.

apply.py tiene 3 modos:
- `--dry-run`: genera borradores sin tocar nada.
- `--report`: lista los items sin generar codigo.
- `--generate FILE`: genera el borrador de un archivo especifico.

Nunca hay modo "aplicar directo". La aplicacion siempre es manual.

---

## 3. Orden de aplicacion propuesto

### Fase 4a - Critico trip.py (B5)

**Objetivo:** cerrar B5 (ViajeSolicitado desactualizado).

**Items:** 111 T1 en trip.py + 60 T2 = 171 total.
**Archivos:** app/models/trip.py.
**Duracion estimada:** 1-2 sesiones.
**Decisiones aplicables:** D-004 (borrar Reserva, aunque es T4), H-001,
H-002, H-008, H-016.

**Sub-pasos:**
1. Declarar 29 columnas faltantes en ViajeSolicitado (H-001).
2. Declarar 10 CHECK constraints (H-002).
3. Renombrar 2 CHECKs autogenerados (H-002, H-004).
4. Declarar 13 indices faltantes (H-016).
5. Eliminar 1 indice duplicado (H-005).
6. Alinear nullable (parte de los 158 nullable_desalineado).
7. Alinear comment_desalineado.
8. Borrar modelo Reserva (D-004, T4).

**Verificacion:**
- `alembic check` sin diffs para trip.viaje_solicitado.
- E2E app chofer (crear viaje, listar, estados).
- B5 se cierra formalmente.

### Fase 4b - Critico fleet.py

**Objetivo:** alinear fleet a la DB.

**Items:** 93 T1 en fleet.py + 315 T2 = 408 total.
**Archivos:** app/models/fleet.py.
**Duracion estimada:** 2 sesiones.
**Decisiones aplicables:** D-005 (comment IngresoTurno).

**Sub-pasos:**
1. ChoferVehiculo: alinear columnas, constraints, indices.
2. TurnoChofer: idem.
3. IngresoTurno: alinear comment de medio_pago (D-005).
4. ContratoVehiculo: idem.
5. Vehiculo: idem.
6. Resto de clases fleet.py.

**Verificacion:**
- `alembic check` sin diffs para fleet.* (excepto neumatico_*).
- E2E app chofer (turno, ingreso).

### Fase 4c - Critico auth.py + tenant.py + payment.py

**Objetivo:** alinear los schemas auth, tenant, payment.

**Items:** 17+15+11 = 43 T1.
**Archivos:** app/models/auth.py, app/models/tenant.py, app/models/payment.py.
**Duracion estimada:** 1-2 sesiones.
**Decisiones aplicables:** D-006 (auth.codigo_verificacion +
codigo_metadatos), D-007 (tenant.control_base.lat/lng).

**Sub-pasos:**
1. auth.py: declarar codigo_verificacion (9 columnas, H-007).
2. auth.py: declarar codigo_metadatos (6 columnas, D-006).
3. auth.py: alinear Usuario y resto.
4. tenant.py: ControlBase.lat/lng String(50) -> Numeric (D-007).
5. tenant.py: resto de alineaciones.
6. payment.py: MetodoPago, Transaccion, etc.

**Verificacion:**
- `alembic check` sin diffs para auth.*, tenant.*, payment.*.
- Test manual: alta usuario, alta tenant, alta metodo_pago.

### Fase 4d - Tier 2/3 agrupado por tipo

**Objetivo:** resolver la masa de items no criticos.

**Items:** 912 T2 + 120 T3 = 1.032.
**Duracion estimada:** 2-3 sesiones.
**Agrupacion por tipo (no por archivo):**

**4d.1 - constraint_nombre_desalineado (124 items, T3):**
- Renombrar constraints para alinear naming convention.
- Automatizable con apply.py (borrador de renombres).
- Afecta: todos los archivos.

**4d.2 - indice_nombre_desalineado (4+ items, T3):**
- Idem anterior para indices.

**4d.3 - indice_falta (207 items, T2):**
- Declarar indices faltantes.
- Semi-automatizable (patron uniforme).

**4d.4 - columna_falta (227 items, T2):**
- Declarar columnas faltantes.
- Semi-automatizable.

**4d.5 - nullable_desalineado (158 items, T2):**
- Alinear nullable en ORM o DB (decision por caso).
- Manual.

**4d.6 - tipo_desalineado (114 items, T1/T2):**
- Incluye los 19 timestamps naive (D-012, ya decidido).
- Manual.

**4d.7 - comment_desalineado:**
- Alinear comments.

**4d.8 - schemas nuevos comunicacion + rentabilidad:**
- Crear app/models/comunicacion.py (3 tablas, H-012).
- Crear app/models/rentabilidad.py (3 tablas, H-013).
- Registrar en app/models/__init__.py.

**4d.9 - tablas faltantes adicionales:**
- audit.alertas_vencimiento
- auth.plantilla_viaje
- auth.prestadora_telefonica
- fleet.historial_chofer_vehiculo
- fleet.relacion_propietario_vehiculo
- payment.configuracion_pasarela
- payment.qr_cobro
- trip.broadcast_log

### Fase 4e - Tier 4

**Objetivo:** eliminar trip.reserva.

**Items:** 1 (D-0013).
**Accion:** borrar modelo Reserva de app/models/trip.py.
**Verificacion:** ningun import roto, ningun relationship roto.

### Fase 4f - Cierre

**Objetivo:** verificacion final.

**Sub-pasos:**
1. Regenerar snapshots (introspect_db, introspect_orm, diff).
2. Verificar que diff da 0 diferencias (o solo whitelisted).
3. `alembic check` limpio.
4. Actualizar DEUDA_TECNICA_ACTUAL.md.
5. Commit final + tag.

---

## 4. Automatizable vs manual

### 4.1 Totalmente automatizable (apply.py sin revision humana)

| Clasificacion | Cantidad | Accion |
|---|---|---|
| constraint_nombre_desalineado | 124 | Renombrar constraint |
| indice_nombre_desalineado | 4+ | Renombrar indice |
| indice_sobra | 4 | Eliminar indice |

**Total:** ~132 items.
**Como:** apply.py genera SQL o codigo SQLAlchemy con el renombre.
**Riesgo:** bajo (solo cambia nombres, no estructura).

### 4.2 Semi-automatizable (apply.py genera borrador, humano revisa)

| Clasificacion | Cantidad | Accion |
|---|---|---|
| columna_falta | 227 | Declarar columna |
| indice_falta | 207 | Declarar indice |

**Total:** ~434 items.
**Como:** apply.py genera el codigo Python del Column() o Index().
**Riesgo:** medio (hay que revisar tipo, nullable, default).

### 4.3 Manual (requiere decision humana por item)

| Clasificacion | Cantidad | Razon |
|---|---|---|
| constraint_falta | 428 | Cada CHECK/FK/UNIQUE es distinto |
| nullable_desalineado | 158 | Requiere decidir ORM o DB |
| tipo_desalineado | 114 | Revisar cada tipo |
| constraint_desalineada | 10 | Idem constraint_falta |
| comment_desalineado | 11 | Bajo riesgo, pero requiere copy |
| tabla_falta | 2+8 | Crear modelo nuevo |

**Total:** ~723 items.
**Como:** humano escribe el codigo a mano.
**Riesgo:** alto (requiere entendimiento del dominio).

### 4.4 Borrado (Tier 4)

| Item | Cantidad | Accion |
|---|---|---|
| trip.reserva | 1 | Borrar modelo |

---

## 5. Decisiones de Fase 2 aplicables

| Decision | Aplicable en | Archivo |
|---|---|---|
| D-004 (borrar trip.reserva) | Fase 4a | app/models/trip.py |
| D-005 (comment IngresoTurno) | Fase 4b | app/models/fleet.py |
| D-006 (codigo_verificacion + codigo_metadatos) | Fase 4c | app/models/auth.py |
| D-007 (control_base lat/lng Numeric) | Fase 4c | app/models/tenant.py |
| D-012 (timestamps neumatico_* naive) | Fase 4d.6 | app/models/fleet.py |

---

## 6. Precauciones

### 6.1 Antes de cada sub-fase

- Verificar `alembic current` y `alembic heads` = m3_010.
- `git status` limpio.
- Backup DB si la sub-fase toca schema.

### 6.2 Durante cada sub-fase

- Un bloque por mensaje.
- NO tocar la DB con DDL sin backup.
- Verificar que `alembic check` no empeore.
- Comentarios en ASCII puro.

### 6.3 Despues de cada sub-fase

- Correr tests E2E de la funcionalidad afectada.
- Actualizar DEUDA_TECNICA_ACTUAL.md.
- Commit con mensaje descriptivo.
- Tag por sub-fase si es Tier 1.

### 6.4 Rollback

Si algo sale mal:
- `git reset --hard HEAD~1` para el ultimo commit.
- `git checkout <archivo>` para revertir un archivo.
- Restaurar DB desde backup si se toco schema.

---

## 7. Fases del roadmap (contexto)

| Fase | Estado |
|---|---|
| Fase 0 - Preparacion | COMPLETA (Ronda 5) |
| Fase 1 - Diagnostico | COMPLETA (Ronda 5) |
| Fase 2 - Decisiones | EN CURSO (Ronda 6) |
| Fase 3 - apply.py + dry-run | PENDIENTE |
| Fase 4 - Aplicacion por Tiers | PENDIENTE |
| Fase 5 - Verificacion y cierre | PENDIENTE |

---

## 8. Proximos pasos inmediatos

1. Cerrar Fase 2 (Sesion 3): commit de este plan + tag.
2. Arrancar Fase 3: escribir scripts/orm_sync/apply.py.
3. Generar dry-run con apply.py.
4. Revisar borradores generados.
5. Aplicar Fase 4a (trip.py).

---

## 9. Referencias

- docs/orm_sync/orm_diff.json
- docs/orm_sync/orm_diff_reporte.md
- docs/orm_sync/orm_diff_acciones.csv
- docs/orm_sync/orm_decisiones.md
- docs/DEUDA_TECNICA_ACTUAL.md
- docs/orm_reconciliacion_plan.md

---

**FIN DEL DOCUMENTO**