# DEUDA TECNICA ACTUAL — TaxIP 2.0

**Ultima actualizacion:** 2026-10-08 (cierre Ronda 11)
**Ronda activa:** 11 cerrada (`ronda11-fase11-completa`)
**Total items pendientes:** ~71
**Total criticos:** 1 (orm.db_desalineados)

---

## RESUMEN DE RONDA 11 (2026-10-08)

**Objetivo:** fix de tooling (diff.py) + Paso 6 residual + Fase 4c +
nullable_desalineado + comments Tipo A. Todo SIN tocar DB.

**Resultado:**
- Diff total: 114 -> **71** (-43, -38%).
- Tier 1: 20 -> **17**.
- Tier 2: 79 -> **46**.
- Tier 3: 14 -> **7**.
- `indice_falta`: 22 -> **1**.
- `tabla_falta`: 10 -> **0**.
- `schema_falta`: 2 -> **0**.
- `nullable_desalineado`: 4 -> **0**.
- `comment_desalineado`: 20 -> **13** (los 13 restantes son mojibake, R12).

**Fixes aplicados:**

1. `diff.py` — nuevo helper `_orm_unique_cols()` + `_is_partial_index()`.
   Matchea `CREATE UNIQUE INDEX` (DB) contra `UniqueConstraint` (ORM) por
   columnas, excluyendo partial indexes. Impacto: -12 items.

2. Paso 6 residual (indices B-tree): declarados 9 indices + UNIQUEs
   compuestos en auth, corporate, fleet y payment.

3. Fase 4c (tablas faltantes): 10 tablas + 2 schemas nuevos
   (comunicacion, rentabilidad). 11 tablas efectivas + 3 tablas nuevas.
   Impacto: -11 items.

4. nullable_desalineado: 4 columnas alineadas a `nullable=False`
   (la DB ya tenia NOT NULL).

5. comments Tipo A: 7 comentarios movidos de `comment=` a `doc=`
   (documentacion interna, no persistida).

**Deudas cerradas en R11:**
- `orm.diff_indexes_colapsa_por_columnas`.
- `orm.geoalchemy2_indices_no_aplicados`.
- `orm.indice_falta` (parcial: 22 -> 1).
- `orm.tabla_falta_ampliada` (10 -> 0).
- `orm.schema_falta` (2 -> 0).
- `orm.nullable_desalineado` (4 -> 0).
- `orm.comment_tipo_a` (7 -> 0).

**Ver:** `docs/CONTEXTO_RONDA_11 a 12.md` (handoff).

---

## RESUMEN DE RONDA 10 (2026-10-06)

**Objetivo:** corregir bugs de tooling (introspector + diff), aplicar
migraciones DDL basicas, limpiar redundancias en ORM.

**Resultado:**
- Diff total: 332 → **114** (−218, −66%).
- Tier 1: 62 → **20**.
- Tier 2: 158 → **79**.
- Tier 3: 111 → **14**.
- `constraint_desalineada`: 72 → **0**.
- `constraint_nombre_desalineado`: 124 → **0**.
- `indice_falta_en_db`: 3 → **0**.

**Descubrimientos clave:**
1. `introspect_db.py` tenia un bug grave: `psycopg2` no adaptaba los
   arrays de `information_schema` a list de Python. Los PKs y UNIQUEs
   del `db_snapshot.json` tenian columnas corruptas
   (`['{','t','o','k','e','n','}']` en vez de `['token']`). Eso generaba
   ~100 falsos positivos en el diff.
2. `diff.py` comparaba nombres de PKs y FKs. La DB tiene dos
   convenciones mezcladas (`<tabla>_pkey` autogenerados + `pk_<tabla>`
   explicitos). El nombre de un PK/FK no tiene semantica funcional.
   Generaba 176 falsos positivos.
3. GeoAlchemy2 auto-genera GIST sobre Geography con `spatial_index=True`
   (default). El ORM los declara implicitamente. La DB no los tenia.

**Fixes aplicados:**
1. `diff_indexes` matchea por `(nombre_normalizado, columnas)` en vez de
   solo columnas (`113f324`).
2. Nueva clasificacion `indice_falta_en_db` para GIST de GeoAlchemy2
   (`113f324`).
3. `trip.py`: restaurar `idx_viaje_origen_gist` + `spatial_index=False`
   en `origen` (`1d4debd`).
4. `auth.py` + `fleet.py`: eliminar `index=True` redundante en columnas
   UNIQUE (`ccead93`).
5. `gasto_turno.py`: alinear nombre de CHECK a la convention (`1af08de`).
6. `diff_constraints`: PKs y FKs matchean por columnas, no por nombre
   (`9520129`).
7. `introspect_db.py`: cast `::text[]` en `array_agg` de
   `information_schema` (`783363b`).

**Migraciones aplicadas:**
- `m3_011` (`783363b`): 3 GIST sobre Geography
  (`fleet.chofer_vehiculo`, `trip.panico`, `trip.viaje_solicitado.destino`).
- `m3_012` (`b8ffd5a`): rename CHECK `gasto_turno_monto_check` →
  `ck_gasto_turno_monto_check`.

**Ver:** `docs/CONTEXTO_RONDA_10 a 11.md` (handoff).

---

## RESUMEN DE RONDA 9 (2026-10-06)

**Objetivo:** fix de `diff.py` (PKs) + limpieza de `indice_sobra`.

**Resultado:**
- Diff total: 404 → **332** (−72, −17.8%).
- `indice_falta`: 86 → **14**.
- Se descubrio que GeoAlchemy2 auto-genera indices GIST sobre columnas
  Geography.

**Fixes aplicados:**
1. Excluir PKs de `indice_falta` en `diff.py` (`1ac1294`).
2. Eliminar B-tree redundante en `fleet.chofer_vehiculo.ubicacion`
   (`158e594`).

**Tag:** `ronda9-fase9-completa` en `a887cc3`.

---

## RESUMEN DE RONDA 8 (2026-10-05)

**Objetivo:** fix de `diff.py` + Fase 6 (indices reales).

**Resultado:**
- Diff total: 877 → **404** (−473, −54%).
- `fleet` schema 100% reconciliado.

**Fixes aplicados:**
1. Fix 1 — Geography case-insensitive en `diff.py` (`6927f08`).
2. Fix 2 — Exclusion de `*_not_null` autogenerados (`d3692f1`).
3. Fix 3 — Doble prefijo `ck_` en `trip.py` (`b2edb4e`).
4. Fase 6 — Todos los indices reales aplicados (~98).

**Tag:** `ronda8-fase6-completa` en `c5bd634`.

---

## BLOQUEANTE PARA PRODUCCION

### B5 — Modelo ViajeSolicitado desactualizado

**Estado:** TECNICAMENTE DESBLOQUEADO. Fase 4a completada en R6.
**Pendiente:** verificacion formal del cierre (Fase 5).

**Ver:** `docs/orm_sync/orm_diff_reporte.md`.

---

## CRITICO

### orm.db_desalineados — ACTUALIZADO 2026-10-06

### orm.db_desalineados — ACTUALIZADO 2026-10-08

**Estado:** en progreso. R11 bajo el diff a **71 items** (-38% desde R10).

**Datos reales (post R11):**

| Metrica | Original | R5 | R8 | R9 | R10 | R11 |
|---|---|---|---|---|---|---|
| Tablas faltantes | ~40 | 17 | ~16 | ~16 | 12 (10+2 schemas) | **0** |
| Columnas faltantes | ~150 | 227 | 1 | 1 | 1 | **1** |
| Indices faltantes | ~80 | 251 | 86 | 14 | 22 | **1** |
| Constraints faltantes | ? | 541 | 274 | 61 | 48 | **49** |
| Diferencias totales | ~500 | 1,280 | 404 | 332 | 114 | **71** |

**Clasificacion por Tier (post R11):**
- Tier 1 (critico): **17**
- Tier 2 (importante): **46**
- Tier 3 (cosmetico): **7**
- Tier 4 (muerte): **1**

**Distribucion por clasificacion (post R11):**
- `constraint_falta`: 49 (CHECKs D-027 + FKs + UNIQUEs)
- `comment_desalineado`: 13 (mojibake, todos requieren DB)
- `constraint_sobra`: 6 (5 UNIQUEs Caso C + 1 metodo_pago)
- `tabla_sobra`: 1 (trip.reserva)
- `columna_falta`: 1 (usuario_rol.control_base_id)
- `indice_falta`: 1 (redundante contrato_vehiculo)

**Todo lo que queda requiere DB o decision funcional.**

**Riesgo:** cualquier `alembic revision --autogenerate` es DESTRUCTIVA.
Verificado: ninguna migracion historica uso autogenerate.

**Plan:** 5 fases (0 a 4). Fases 0-4a completas en R5-R7.
Fase 4b (fleet.py) completa en R7.
Fase 6 (indices reales) completa en R8.
Fix de tooling (diff, introspector) completa en R9-R10.
Migraciones m3_011 y m3_012 aplicadas en R10.
Fase 4c (tablas faltantes) completa en R11.
nullable_desalineado + comments Tipo A cerrados en R11.

**Ver:**
- `docs/orm_sync/orm_diff_reporte.md`
- `docs/orm_sync/db_snapshot.json`
- `docs/orm_sync/orm_snapshot.json`
- `docs/orm_sync/orm_decisiones.md`

## NUEVOS — Ronda 10 (Fase 10)

### orm.introspect_db_arrays_corruptos — CERRADA 2026-10-06

`psycopg2` no adaptaba arrays de `information_schema` a `list`. El
`db_snapshot.json` tenia PKs y UNIQUEs con columnas corruptas.

**Fix:** `783363b` — cast `::text[]` en `array_agg`.

### orm.diff_nombres_pk_fk — CERRADA 2026-10-06

`diff_constraints` comparaba nombre de PKs y FKs. La DB tiene dos
convenciones mezcladas. 176 falsos positivos.

**Fix:** `9520129` — PK/FK matchean por columnas, no por nombre.

### orm.indice_falta_en_db — CERRADA 2026-10-06

3 GIST de GeoAlchemy2 sin aplicar en DB.

**Fix:** `m3_011` (`783363b`).

### orm.gasto_turno_check_nombre — CERRADA 2026-10-06

CHECK de `fleet.gasto_turno` con nombre divergente entre ORM y DB.

**Fix:** `m3_012` (`b8ffd5a`).

### orm.unique_constraints_caso_c — NUEVA 2026-10-06

5 UNIQUEs que el ORM declara y la DB no tiene:
- `auth.perfil_general.usuario_id`
- `auth.reset_token.token`
- `fleet.vehiculo.qr_uuid`
- `tenant.configuracion_tenant.control_base_id`
- `trip.calificacion.viaje_id`

**Verificacion:** 0 duplicados en las 5 tablas.

**Accion:** migracion `m3_013` (agregar UNIQUEs a DB con nombres del ORM).

**Tier 2.**

### metodo_pago.catalogo_sucio — ACTUALIZADA 2026-10-06

`payment.metodo_pago` tiene 2 pares de duplicados (`efectivo` x2,
`mercadopago` x2). El ORM declara UNIQUE sobre `nombre`.

**Accion:** limpiar el catalogo antes de agregar el UNIQUE. Requiere
decision funcional (D-005). Postergado.

**Tier 2.**

---

## NUEVOS — Ronda 5 (Fase 1)

### orm.nullable_desalineado — 2026-10-01

4 columnas con nullable divergente entre ORM y DB.
Bug potencial activo: si ORM declara nullable=True pero DB tiene NOT NULL,
los INSERTs del ORM pueden fallar silenciosamente.

**Tier 2.**

**Ver:** `docs/orm_sync/orm_diff_reporte.md`.

### orm.constraint_nombres_numericos — 2026-10-01

2 constraints con nombres autogenerados por Alembic:
- `63669_63825_1_not_null` (trip.viaje_solicitado).
- `63669_63825_38_not_null` (trip.viaje_solicitado).

**Tier 3.** Renombrar en Fase 4.

**Ver:** `docs/orm_sync/orm_decisiones.md` (H-004).

### orm.indices_duplicados — 2026-10-01

Indices duplicados funcionales:
- `idx_viaje_estado` + `ix_viaje_estado` (trip.viaje_solicitado).

**Tier 3.** Eliminar uno en Fase 4.

### orm.system_tables_whitelist — 2026-10-01

`public.alembic_version` y `public.spatial_ref_sys` son tablas de sistema.
No deben considerarse parte del diff.

**Accion:** whitelist en `diff.py` (ya implementado).

---

## NUEVOS — Ronda 6 (Fase 2, Sesion 1)

### orm.reserva_modulo_activo — NUEVA 2026-10-02

La tabla `trip.reserva` NO existe en DB, pero el modulo de reservas
corporativas la usa activamente.

Los endpoints `/api/reservas` estan rotos actualmente (la tabla no existe).
Requiere decision funcional: crear la tabla en DB o deprecar el modulo.

**Tier 2.** Postergado a Fase 4d.

**Ver:** `docs/orm_sync/orm_decisiones.md` (D-004).

### orm.foto_viaje_out_of_scope — NUEVA 2026-10-02

El item D-1125 (`foto_viaje.created_at` nullable desalineado) NO esta en
`trip.py`, esta en `app/models/foto_viaje.py`. Pendiente Fase 4d.

**Tier 2.**

### metodo_pago.catalogo_sucio — NUEVA 2026-10-01

`payment.metodo_pago` tiene 12 filas con:
- 2 duplicados: efectivo (x2), mercadopago (x2).
- 1 sinonimo: wallet = billetera.
- 1 pasarela mezclada: mercadopago (es proveedor, no metodo).

**Impacto:** todos los reportes leen del catalogo sucio.

**Tier 2.** Limpiar en Fase 4.

### metodo_pago.fk_catalogo — NUEVA 2026-10-01

Refactor estructural: evaluar FK por `metodo_pago_id` en
`trip.viaje_solicitado` y `fleet.ingreso_turno` (en vez de string).

**Tier 2.** Refactor grande. NO en Fase 2.

### metodo_pago.ingreso_turno — NUEVA 2026-10-01

`fleet.ingreso_turno.medio_pago`:
- Comment en DB: 6 valores. Sin CHECK.
- Datos reales: solo 2 valores (efectivo=57, debito=16).
- ORM: comment divergente, 4 valores.

**Tier 2.** Alinear comment del ORM con DB en Fase 4.

### metodo_pago.frontend_e2 — NUEVA 2026-10-01

MetodoPago del frontend limitado a 4 valores (deuda E2 original).

**Tier 3.** Resolver en Fase 4 si se decide ampliar vocabulario.

---

## NUEVOS — Ronda 7 (Fase 4b)

### datos.turno_chofer_km_final_outlier — NUEVA 2026-10-03

`fleet.turno_chofer.km_final` tiene un valor maximo de 1.523.999,00 km,
irreal para un taxi urbano.

**Tier 3.** Revisar registros con `km_final > 500000` en ronda de limpieza.

### orm.snapshot_desactualizado — NUEVA 2026-10-03

Practica preventiva: el `orm_snapshot.json` puede quedar desactualizado
si se editan archivos del ORM sin regenerarlo.

**Tier 2.** Regenerar snapshots al inicio de cada paso.

### orm.diff_falsos_positivos_tipo_cambio — NUEVA 2026-10-03

Cuando se cambia el tipo o nullable de una columna, `diff.py` puede
reportarla como `columna_falta` en el proximo diff.

**Tier 2.** Postergado.

### orm.diff_check_constraints_duplicados — NUEVA 2026-10-03

`diff.py` compara CHECKs por nombre. Cuando el ORM declara un CHECK con
`name="X"` y la DB lo tiene con `name="ck_<tabla>_X"`, el diff los cuenta
como 2 items distintos.

**Tier 2.** Parcialmente mitigado por Fix 2 de R8.

### orm.naming_convention_check_divergente — ACTUALIZADA 2026-10-06

La naming convention de `app/database.py` para CHECKs es
`ck_%(table_name)s_%(constraint_name)s`. La DB tiene CHECKs con nombres
que NO siguen esa convention.

**Progreso R10:**
- `gasto_turno_monto_check` renombrado a `ck_gasto_turno_monto_check`
  via `m3_012`. ✅
- Quedan ~26 CHECKs con naming divergente en otros schemas.

**Tier 2.** Migracion `m3_014` planificada para R11.

### orm.paso4_check_constraints_residual — ACTUALIZADO 2026-10-06

Los 8 CHECKs de `trip.viaje_solicitado` alineados en R8.
`gasto_turno_monto_check` alineado en R10.

**Residual:** ~48 items de `constraint_falta`:
- ~26 CHECKs con naming convention divergente (doble prefijo + sin
  convention).
- ~10 FKs reales faltantes.
- ~10 UNIQUEs faltantes.
- ~2 other.

**Tier 2.** Migracion `m3_014` planificada.

**Ver:** `python scripts/orm_sync/filtrar_check.py --stats`.

### orm.alembic_check_ruidoso — ACTUALIZADO 2026-10-06

`alembic check` reporta cientos de operaciones de upgrade pendientes
porque el ORM y la DB estan desalineados. NO es un gate util por paso.

**Tier 2.** Investigar en Fase 5.

---

## NUEVOS — Ronda 8 (Fase 6 + fixes)

### orm.unique_constraint_vs_unique_index — ACTUALIZADA 2026-10-06

El ORM declara `UniqueConstraint` y la DB tiene `CREATE UNIQUE INDEX`.
Funcionalmente equivalentes.

**Reduccion en R10:** el fix del introspector (`783363b`) elimino los
falsos positivos por columnas corruptas. Los que quedan son:

- 5 UNIQUEs que el ORM declara y la DB NO tiene (Caso C):
  `auth.perfil_general`, `auth.reset_token`, `fleet.vehiculo.qr_uuid`,
  `tenant.configuracion_tenant`, `trip.calificacion`.
  → `m3_013` los agrega a DB.
- 1 UNIQUE que el ORM declara y la DB NO tiene (por catalogo sucio):
  `payment.metodo_pago.nombre`.
  → Postergado hasta limpiar D-005.

**Tier 2.**

### orm.comercio_indice_redundante — NUEVA 2026-10-05

`public.comercio.idx_comercio_codigo_qr` es redundante con el UNIQUE
constraint `comercio_codigo_qr_key`.

**Tier 3.** Evaluar eliminacion en ronda de optimizacion.

### orm.tabla_falta_ampliada — ACTUALIZADA 2026-10-05

Tablas faltantes (~16):

**Schema comunicacion (3):**
- `comunicacion.conversacion` (7 cols).
- `comunicacion.email_enviado` (9 cols).
- `comunicacion.mensaje` (8 cols).

**Schema rentabilidad (3):**
- `rentabilidad.analisis_medios_pago` (10 cols).
- `rentabilidad.rentabilidad_diaria_vehiculo` (13 cols).
- `rentabilidad.rentabilidad_mensual_vehiculo` (13 cols).

**Schema auth (4):**
- `auth.codigo_metadatos` (6 cols).
- `auth.codigo_verificacion` (9 cols).
- `auth.plantilla_viaje` (19 cols).
- `auth.prestadora_telefonica` (6 cols).

**Schema payment (2):**
- `payment.qr_cobro` (10 cols).
- `payment.configuracion_pasarela` (7 cols).

**Schema audit (1):**
- `audit.alertas_vencimiento` (8 cols).

**Schema trip (1):**
- `trip.broadcast_log` (11 cols).

**Schema fleet (2):**
- `fleet.historial_chofer_vehiculo` (6 cols).
- `fleet.relacion_propietario_vehiculo` (7 cols).

**Tier 2.** Fase 4c (crear modulos ORM).

**Ver:** `docs/orm_sync/alembic_check_cierre_r8_2026-10-05.txt`.

### metodo_pago.pasarela — ACTUALIZADA 2026-10-05

Las tablas `payment.qr_cobro` (10 cols) y
`payment.configuracion_pasarela` (7 cols) **YA EXISTEN en la DB** pero
no estan declaradas en el ORM.

**Tier 2.** Actualizar al planificar `/cobro-qr` (M3 pendiente).

---

## NUEVOS — Ronda 9 (Paso 9)

### orm.indice_sobra_ambiguo — RESUELTA 2026-10-06

`diff.py` clasificaba como `indice_sobra` GIST auto-generados por
GeoAlchemy2. Reclasificados como `indice_falta_en_db` y aplicados via
`m3_011`.

### orm.geoalchemy2_indices_no_aplicados — CERRADA 2026-10-06

3 GIST declarados por ORM (via GeoAlchemy2), ausentes en DB.

**Fix:** `m3_011` (`783363b`).

### orm.diff_indexes_colapsa_por_columnas — CERRADA 2026-10-06

`diff.py` matcheaba indices por `tuple(columns)`. Si el ORM declaraba
dos indices sobre la misma columna, solo uno aparecia.

**Fix:** `113f324` — matching por `(nombre_normalizado, columnas)`.

---

## ALTA PRIORIDAD

### G63 — Alerta si el motor de precios cae a fallback

`precio_final` puede caer a `precio_estimado` si el motor unificado falla.
Requiere infra de monitoreo (Sentry, Grafana o similar). Fase 2.

### G67 — check_out_turno sin escapatoria si hay viajes huerfanos

El chofer queda atrapado sin poder cerrar turno. Requiere decision de
negocio: auto-cancelar huerfanos con motivo, o boton "forzar cierre".

### G80 — App apunta a Metro (no funciona fuera de WiFi dev)

La app en el celular apunta a 192.168.1.14:8081. Para pruebas en terreno:
build preview o production apuntando al backend publico.

---

## MEDIA PRIORIDAD

### F5 — ViajeSolicitado.origen_lat/lng vs ViajeActivo.origen

Numeros sueltos vs Coordenada. Mapear en el store al conectar el WS.

### F6 — auth.codigo_metadatos es tabla separada

El INSERT en codigo_verificacion solo no alcanza. Documentar en flujo
del propietario.

### G68 — Job procesar_viajes_huerfanos corre cada 1h

Bajar a 15 min si en produccion se ve friccion.

### G70 — Confusion de paths public/viajes

Existen tres (backend publico, proxy dashboard, helper dashboard), uno
huerfano. Renombrar o documentar.

### G72 — Regla de pegado sin tildes desde chat

Refuerza N10. Nunca pegar bloques con tildes/emojis desde el chat al
editor. Comentarios en codigo pegado: ASCII puro.

### G74 — Endpoint /api/viajes/solicitar deprecado

Sigue en codigo. Eliminar en Fase 2.

### G76 — Worker de uvicorn a veces carga version vieja

Tras un cambio en un archivo que importa otro modulo modificado.
Verificar LastWriteTime vs StartTime del proceso Python.

### G81 — DB y modelos ORM desincronizados silenciosamente

Sintoma: INSERTs fallan por columna inexistente, sin error visible.
**Relacionado con:** `orm.db_desalineados`.

### J15 — No hay deteccion de viaje activo al abrir la app

Plan: endpoint GET /api/chofer/viaje-activo + chequeo en
`(app)/_layout.tsx`.

### metodo_pago.flujo_propietario — 2026-09-30

`liquidacion.py:329`, `fleet.py:875/880` (comments de IngresoTurno).
Dominio: como el propietario le paga al chofer.
Vocabulario propio por definir.

### metodo_pago.flujo_empresa — 2026-09-30

`empresa_dashboard.py:790`. Dominio: como la empresa le paga a TaxIP.
Requiere vocabulario propio.

### metodo_pago.recaudacion — 2026-09-30

`schemas/recaudacion_schemas.py:22`. Alinear cuando se toque ese modulo.

### flujo_caja.ingreso_turno — ACTUALIZADO 2026-10-01

Comments de `tipo_ingreso`, `medio_pago`, `origen` mezclan vocabularios.
`medio_pago` con espacio final en el comment.

**Accion:** alinear comment del ORM con DB y canonizar vocabulario.
Resuelto en D-005.

### G82 — 2026-09-30

`run.py` tiene `reload=True` hardcodeado. Contradice N14.
Propuesta: `reload=os.getenv("RELOAD", "false").lower() == "true"`.

---

## BAJA PRIORIDAD

### Backend heredadas

- **A1** — Modelo Reserva apunta a tabla dropeada (trip.reserva).
  **Confirmado 2026-10-01:** trip.reserva esta en ORM (29 columnas), no
  en DB. **Reclasificado** (D-004): no borrar.
- **A2** — Schemas legacy snake_case mezclados en viajes/schemas.py.
- **A5** — ~22 warnings Duplicate Operation ID en neumaticos OpenAPI.

### Frontend

- **D2** — tsconfig.json con ignoreDeprecations "6.0".
- **D6** — splash.tsx "paso 2 veces la pantalla" (no reproducible).
- **E2** — MetodoPago limitado a 4 valores.

### Endpoints faltantes

- **F4** — /cobro-qr, webhooks de pasarela.
- **F8** — app/_layout.tsx limpia taxip-turno al arrancar (fragil).

### Proceso, encoding, metadata

- **G23** — Backend no valida que destino_lat/lng esten cerca del origen.
- **G28** — Posible race en rotacion de logs con --reload.
- **G29** — Consola PowerShell 5.1 con mojibake en logs.
- **G32** — direccion_origen requerido en SolicitarViajeCalleRequest.
- **G33** — Idem G32 para el tipo TS SolicitarViajeCalleRequest.
- **G37** — Warning VirtualizedLists en calle.tsx.
- **G42** — Duplicacion de calculo de precio entre calcular_costo y
  solicitar_viaje_calle.
- **G45** — (sin detalle, ver doc original).
- **G54** — Landing usa Haversine en lugar de Directions.
- **G55** — Landing resuelve tenant con SELECT LIMIT 1 sin ORDER BY.
- **G73** — ~29 no-ASCII preexistentes en routes.py.

### Funcional heredada

- **H1** — splash.tsx navega a /registro/paso1-cuenta para etapas 1-4.
- **H2** — Home muestra datos mock (resultadosAyer).
- **H3** — Home tiene "viajes" y "finanzas" con disabled: true.

### ORM y funcional futuro

- **J1** — pasajero_id nullable en DB pero NOT NULL en ORM.
- **J2** — es_anonimo existe en DB pero no en ORM.
- **J3** — origen_tipo, paradas_intermedias, metodo_pago en DB pero no
  en ORM. **Parcialmente cubierto por B5.**
- **J4** — Extension de viaje.
- **J5** — "Siga ese auto".
- **J14** — viaje.store construye ViajeActivo a mano desde ViajeSolicitado.
- **J19** — Recargos: iniciado_en vs now().

### Nuevas Ronda 4

- **metodo_pago.config_credito** — `mix_credito`, `comision_credito` en
  `tenant.configuracion_tenant` sin uso cuando desaparece `credito`.
- **metodo_pago.billetera_futuro** — Cuando se implemente la wallet TaxIP,
  agregar `billetera` al CHECK de `viaje_solicitado.metodo_pago`.
- **logs.auth_prints** — `routers/auth.py:289` con print con emoji.
- **orm_viaje.fk_comercio_schema** — FK de `viaje_solicitado.comercio_id`
  apunta a `comercio(id)` sin schema.

---

## DEUDAS DE EXPO-ROUTER CON REACT 19 (workaround activo)

- **G77** — Bug de expo-router 57.0.24 con React 19 (2 useEffect sin deps).
- **G78** — Workaround: 2 parches en `patches/expo-router+57.0.24.patch`.
- **G79** — Workflow de compilacion migrado a EAS Build.

Cuenta: megarcia34. Proyecto: @megarcia34/taxip-chofer.
projectId: b54c9f37-bdd0-4845-8c78-9628a3cda6a2.
**No tocar hasta que expo saque fix upstream.**

---

## CERRADAS EN RONDA 10 (2026-10-06)

### Fixes de tooling

- **orm.introspect_db_arrays_corruptos** — CERRADA. Cast `::text[]` en
  `array_agg` de `information_schema` (`783363b`).
- **orm.diff_nombres_pk_fk** — CERRADA. PK/FK matchean por columnas
  (`9520129`).
- **orm.diff_indexes_colapsa_por_columnas** — CERRADA. Matching por
  `(nombre, columnas)` (`113f324`).

### Fixes del ORM

- **trip.py** — Restaurado `idx_viaje_origen_gist` + `spatial_index=False`
  en `origen` (`1d4debd`).
- **auth.py + fleet.py** — Eliminado `index=True` redundante (`ccead93`).
- **gasto_turno.py** — Alineado CHECK a la convention (`1af08de`).

### Migraciones

- **m3_011** — 3 GIST sobre Geography (`783363b`).
- **m3_012** — Rename CHECK `gasto_turno` (`b8ffd5a`).

---

## RECUENTO

| Categoria | Cantidad |
|---|---|
| Bloqueante | 1 |
| Critico | 1 |
| Nuevos Ronda 5 | 5 |
| Nuevos Ronda 6 (Fase 2) | 4 |
| Nuevos Ronda 7 (Fase 4b) | 7 |
| Nuevos Ronda 8 (Fase 6) | 3 |
| Nuevos Ronda 9 (Paso 9) | 3 (2 cerradas, 1 resuelta) |
| Nuevos Ronda 10 (Fase 10) | 5 (4 cerradas, 1 nueva) |
| Alta prioridad | 3 |
| Media prioridad | 15 |
| Baja prioridad | 21 |
| Expo-router / EAS | 3 |
| **TOTAL PENDIENTES** | **~114 (items del diff) + deudas no-diff** |

**Notas:**
- El total del diff es 114. El "~114" del encabezado coincide con el
  total de items. Las deudas no-diff (G63, G67, etc.) son items aparte
  que no entran en el diff pero estan pendientes de resolucion.

---

## REFERENCIAS

- **Plan de reconciliacion:** `docs/orm_reconciliacion_plan.md`
- **Snapshots:** `docs/orm_sync/`
- **Reporte diff:** `docs/orm_sync/orm_diff_reporte.md`
- **Decisiones:** `docs/orm_sync/orm_decisiones.md`
- **Historico:** `docs/HISTORICO_CERRADAS.md`
- **Baseline:** `docs/orm_sync/baseline_info.md`
- **Handoff R9→R10:** `docs/CONTEXTO_RONDA_9 a 10.md`
- **Handoff R10→R11:** `docs/CONTEXTO_RONDA_10 a 11.md`
- **Alembic check cierre R8:** `docs/orm_sync/alembic_check_cierre_r8_2026-10-05.txt`
- **Backups:** `docs/backups/`
- **Bitacoras:** `E:\Taxip\app chofer\BITACORA_M1.md`, `M2`, `M3`.

---

**FIN DEL DOCUMENTO**