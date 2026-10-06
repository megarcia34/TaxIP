# DEUDA TECNICA ACTUAL — TaxIP 2.0

**Ultima actualizacion:** 2026-10-06 (cierre Ronda 9)
**Ronda activa:** 9 cerrada (`ronda9-fase9-completa`)
**Total items pendientes:** ~67
**Total criticos:** 1 (orm.db_desalineados)

---

## RESUMEN DE RONDA 9 (2026-10-06)

**Objetivo:** fix de `diff.py` (PKs) + limpieza de `indice_sobra`.

**Resultado:**
- Diff total: 404 → **332** (−72, −17.8%).
- Tier 1: 72 → **62** (−14%).
- Tier 2: 220 → **158** (−28%).
- `indice_falta`: 86 → **14** (los 14 son UNIQUE INDEX cosmeticos).
- Se descubrio que GeoAlchemy2 auto-genera indices GIST sobre columnas Geography.

**Fixes aplicados:**
1. Paso 9.1 — Excluir PKs de `indice_falta` en `diff.py` (`1ac1294`).
2. Paso 9.2 — Eliminar B-tree redundante en `fleet.chofer_vehiculo.ubicacion` (`158e594`).

**Tag:** `ronda9-fase9-completa`.

**Ver:** `docs/CONTEXTO_RONDA_9 a 10.md` (handoff), `docs/orm_sync/orm_decisiones.md` (D-022 a D-024).

---

## RESUMEN DE RONDA 8 (2026-10-05)

**Objetivo:** fix de `diff.py` + Fase 6 (indices reales).

**Resultado:**
- Diff total: 877 → **404** (−473, −54%).
- Tier 1: 141 → **72** (−49%).
- Tier 2: 625 → **220** (−65%).
- `fleet` schema 100% reconciliado.
- No quedan `indice_falta` reales.

**Fixes aplicados:**
1. Fix 1 — Geography case-insensitive en `diff.py` (`6927f08`).
2. Fix 2 — Exclusion de `*_not_null` autogenerados (`d3692f1`).
3. Fix 3 — Doble prefijo `ck_` en `trip.py` (`b2edb4e`).
4. Fase 6 — Todos los indices reales aplicados (~98).
5. Docs + baseline (`39649ed`, `270a1e7`, `6fd1de4`).

**Tag:** `ronda8-fase6-completa` en `c5bd634`.

**Ver:** `docs/CONTEXTO_RONDA_8 a 9.md` (handoff), `docs/orm_sync/orm_decisiones.md` (D-014 a D-019).

---

## BLOQUEANTE PARA PRODUCCION

### B5 — Modelo ViajeSolicitado desactualizado

**Estado:** TECNICAMENTE DESBLOQUEADO. Fase 4a completada en R6.
**Pendiente:** verificacion formal del cierre (Fase 5).

**Ver:** `docs/orm_sync/orm_diff_reporte.md`.

---

## CRITICO

### orm.db_desalineados — ACTUALIZADO 2026-10-06

**Estado:** en progreso. R9 bajo el diff a 332 items (−17.8% adicional).

**Datos reales (post R9):**

| Metrica | Original | R5 | R8 | R9 |
|---|---|---|---|---|
| Tablas faltantes | ~40 | 17 | ~16 | ~16 |
| Columnas faltantes | ~150 | 227 | 1 | 1 |
| Indices faltantes | ~80 | 251 | 86 | 14 (UNIQUE INDEX cosmeticos) |
| Constraints faltantes | ? | 541 | 274 | 274 |
| Diferencias totales | ~500 | 1,280 | 404 | **332** |

**Clasificacion por Tier (post R9):**
- Tier 1 (critico): 62
- Tier 2 (importante): 158
- Tier 3 (cosmetico): 111
- Tier 4 (muerte): 1

**Distribucion por clasificacion (top):**
- `constraint_nombre_desalineado`: 124 (cosmetico)
- `constraint_desalineada`: 72 (PKs con nombre distinto — manual)
- `constraint_falta`: 61 (CHECKs reales + FKs + UNIQUEs)
- `comment_desalineado`: 20
- `constraint_sobra`: 17 (UNIQUEs fantasma)
- `indice_falta`: 14 (UNIQUE INDEX cosmeticos)
- `tabla_falta`: 10
- Otros: ~14

**Deuda real estimada:** ~110 items (CHECKs + comments + tablas faltantes
+ Paso 9 + Paso 4 residual).

**Riesgo:** cualquier `alembic revision --autogenerate` es DESTRUCTIVA.
Verificado: ninguna migracion historica uso autogenerate.

**Plan:** 5 fases (0 a 4). Fases 0 y 1 completas en Ronda 5.
Fase 2 (decisiones) completa en Ronda 6, Sesion 1.
Fase 3 (apply.py) completa en Ronda 6.
Fase 4a (trip.py) completa en Ronda 6.
Fase 4b (fleet.py) completa en Ronda 7.
Fase 6 (indices reales) completa en Ronda 8.
Paso 9.1 (fix PKs en diff.py) completo en Ronda 9.
Paso 9.2 (limpieza B-tree redundante) completo en Ronda 9.

**Ver:**
- `docs/orm_sync/orm_diff_reporte.md`
- `docs/orm_sync/db_snapshot.json`
- `docs/orm_sync/orm_snapshot.json`
- `docs/orm_sync/orm_decisiones.md`

---

## NUEVOS — Ronda 5 (Fase 1)

### orm.nullable_desalineado — 2026-10-01

158 columnas con nullable divergente entre ORM y DB.
Bug potencial activo: si ORM declara nullable=True pero DB tiene NOT NULL,
los INSERTs del ORM pueden fallar silenciosamente.

**Tier 2.** Requiere revision en Fase 4.

**Ver:** `docs/orm_sync/orm_diff_reporte.md` (H-017).

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

**Ver:** `docs/orm_sync/orm_decisiones.md` (H-005).

### orm.system_tables_whitelist — 2026-10-01

`public.alembic_version` y `public.spatial_ref_sys` son tablas de sistema.
No deben considerarse parte del diff.

**Accion:** whitelist en `diff.py` (ya implementado).

**Ver:** `docs/orm_sync/orm_decisiones.md` (H-014).

---

## NUEVOS — Ronda 6 (Fase 2, Sesion 1)

### orm.reserva_modulo_activo — NUEVA 2026-10-02

La tabla `trip.reserva` NO existe en DB, pero el modulo de reservas
corporativas la usa activamente desde multiples lugares:
- `app/models/trip_service.py` (crear_reserva, procesar_reserva).
- `app/services/trip_service.py` (duplicado exacto del anterior).
- `app/routers/reservas.py` (CRUD completo: POST, GET, PATCH).
- `app/routers/operativo.py` (queries SELECT FROM trip.reserva).
- `app/main.py` (registra el router reservas.router en /api/reservas).
- `app/schemas/reserva_schemas.py`.

Los endpoints `/api/reservas` estan rotos actualmente (la tabla no existe).
Requiere decision funcional: crear la tabla en DB o deprecar el modulo.

**Origen:** D-004 decia "borrar modelo Reserva (huerfano)". En Fase 4a se
descubrio que el modulo esta previsto para uso posterior. NO es huerfano.

**Tier 2.** Postergado a Fase 4d o ronda especifica. Requiere coordinar
con frontend si el modulo esta en uso.

**Ver:** `docs/orm_sync/orm_decisiones.md` (D-004).

### orm.foto_viaje_out_of_scope — NUEVA 2026-10-02

El item D-1125 (`foto_viaje.created_at` nullable desalineado) NO esta en
`trip.py`, esta en `app/models/foto_viaje.py`. Fase 4a cubrio solo `trip.py`,
asi que este item queda pendiente para Fase 4d.

**Tier 2.** Resolver junto con el resto de `foto_viaje.py` en Fase 4d.

### metodo_pago.catalogo_sucio — NUEVA 2026-10-01

`payment.metodo_pago` tiene 12 filas con:
- 2 duplicados: efectivo (x2), mercadopago (x2).
- 1 sinonimo: wallet = billetera.
- 1 pasarela mezclada: mercadopago (es proveedor, no metodo).

**Impacto:** todos los reportes leen del catalogo sucio en vez de
`viaje_solicitado.metodo_pago`. Bug real de calculo de comisiones.

**Tier 2.** Limpiar en Fase 4 (dedupe + renombre + decidir si mercadopago
queda como pasarela separada).

**Ver:** `docs/orm_sync/orm_decisiones.md` (D-005, H-026).

### metodo_pago.fk_catalogo — NUEVA 2026-10-01

Refactor estructural: evaluar FK por `metodo_pago_id` en
`trip.viaje_solicitado` y `fleet.ingreso_turno` (en vez de string).

**Impacto:** toca app, reportes, ORM. Refactor grande.

**Tier 2.** Evaluar en Fase 4. NO en Fase 2.

**Ver:** `docs/orm_sync/orm_decisiones.md` (D-005).

### metodo_pago.ingreso_turno — NUEVA 2026-10-01

`fleet.ingreso_turno.medio_pago`:
- Comment en DB: 6 valores (efectivo, debito, credito, qr, transferencia,
  billetera). Sin CHECK.
- Datos reales: solo 2 valores (efectivo=57, debito=16).
- ORM: comment divergente, 4 valores.

**Tier 2.** Alinear comment del ORM con DB en Fase 4. Decidir si se agrega
CHECK.

**Ver:** `docs/orm_sync/orm_decisiones.md` (D-005, H-003).

### metodo_pago.frontend_e2 — NUEVA 2026-10-01

MetodoPago del frontend limitado a 4 valores (deuda E2 original).
Si se amplia el vocabulario (credito, billetera), hay que ampliar el
frontend tambien.

**Tier 3.** Resolver en Fase 4 si se decide ampliar vocabulario.

**Ver:** `docs/orm_sync/orm_decisiones.md` (D-005).

---

## NUEVOS — Ronda 7 (Fase 4b)

### datos.turno_chofer_km_final_outlier — NUEVA 2026-10-03

`fleet.turno_chofer.km_final` tiene un valor maximo de 1.523.999,00 km,
irreal para un taxi urbano. Probablemente sea un dato mal cargado
(un monto en un campo de km) o un dato de prueba olvidado.

**Impacto:** bajo. No rompe nada, pero distorsiona reportes de km.

**Accion:** revisar registros con `km_final > 500000` en ronda de limpieza.

**Tier 3.**

### orm.snapshot_desactualizado — NUEVA 2026-10-03

Practica preventiva: el `orm_snapshot.json` puede quedar desactualizado
si se editan archivos del ORM sin regenerarlo.

**Impacto:** el diff puede reportar items ya resueltos.

**Accion:** regenerar snapshots (`introspect_orm.py` + `diff.py`) al inicio
de cada paso.

**Tier 2.**

### orm.diff_falsos_positivos_tipo_cambio — NUEVA 2026-10-03

Cuando se cambia el tipo o nullable de una columna, `diff.py` puede
reportarla como `columna_falta` en el proximo diff (porque no re-matchea
la columna). Tambien puede reportar `constraint_sobra` para FKs que
no matchean por nombre.

**Impacto:** bajo. Genera falsos positivos al aplicar cambios.

**Tier 2.** Postergado.

### orm.diff_check_constraints_duplicados — NUEVA 2026-10-03

`diff.py` compara CHECKs por nombre. Cuando el ORM declara un CHECK con
`name="X"` y la DB lo tiene con `name="ck_<tabla>_X"`, el diff los cuenta
como 2 items distintos.

**Impacto:** genera falsos positivos.
**Tier 2.** Parcialmente mitigado por Fix 2 de R8.

### orm.naming_convention_check_divergente — NUEVA 2026-10-04

La naming convention de `app/database.py` para CHECKs es
`ck_%(table_name)s_%(constraint_name)s`. La DB, en cambio, tiene CHECKs
con nombres que NO siguen esa convention.

**Impacto:** ~13 falsos positivos permanentes en `constraint_falta`.
**Tier 2.**

**Actualizacion 2026-10-05:** el fix de R8 (D-016, `b2edb4e`) resolvio
los 8 CHECKs de `trip.viaje_solicitado`. Los ~13 CHECKs restantes con
convention divergente siguen pendientes. Fix propuesto para R9: matchear
CHECKs por definicion normalizada en `diff.py` (en vez de por nombre).

### orm.paso4_check_constraints_residual — ACTUALIZADO 2026-10-05

El Paso 4 (CHECKs reales del ORM) esta **parcialmente desbloqueado** por
el Fix 3 de R8. Los 8 CHECKs de `trip.viaje_solicitado` ya estan alineados.

**Residual:** ~61 items de `constraint_falta`:
- ~33 CHECKs reales en otros schemas.
- ~20 items `other` (sin clasificar, requieren investigacion).
- ~9 UNIQUEs faltantes.
- ~7 FKs faltantes.

**Tier 2.** Requiere decision sobre `orm.naming_convention_check_divergente`.
Postergado a R10.

**Ver:** `python scripts/orm_sync/filtrar_check.py --stats`.

### orm.alembic_check_ruidoso — NUEVA 2026-10-03

`alembic check` reporta cientos de operaciones de upgrade pendientes
porque el ORM y la DB estan desalineados. NO es un gate util por paso.

**Actualizacion 2026-10-05:** snapshot post-R8 guardado en
`docs/orm_sync/alembic_check_cierre_r8_2026-10-05.txt`. Sigue ruidoso
(~200 operaciones). El ruido bajo marginalmente respecto a R7.

**Tier 2.** Investigar en Fase 5.

---

## NUEVOS — Ronda 8 (Fase 6 + fixes)

### orm.unique_constraint_vs_unique_index — NUEVA 2026-10-05

14 items en el diff (`indice_falta` con nombre `uq_*`/`unique_*`/`*_key`)
donde el ORM declara `UniqueConstraint` y la DB tiene `CREATE UNIQUE INDEX`.
Son funcionalmente equivalentes (el introspector de DB clasifica UNIQUE
INDEX como indice, no como constraint).

**Tablas afectadas:** `auth.autorizacion_inicio`, `auth.refresh_token`,
`auth.tipo_usuario`, `auth.usuario_rol`, `corporate.cuenta_corriente`,
`corporate.factura_corporativa`, `fleet.categoria_gasto`, `fleet.contrato_qr`,
`fleet.marca`, `fleet.vehiculo`, `payment.billetera`, `payment.metodo_pago`,
`public.comercio`, `tenant.configuracion_tenant`, `tenant.factura`,
`trip.calificacion`.

**Tier 3.** Cosmetico. Fix posible: cambiar `UniqueConstraint` por
`Index(unique=True)` en masa (patron D-017). Bajo riesgo.

### orm.indice_falta_incluye_pks — CERRADA en R9

`diff.py` reportaba 72 PKs (`pk_*` / `*_pkey`) como `indice_falta`.
Cerrada por Paso 9.1 (commit `1ac1294`).

**Ver:** `## CERRADAS EN RONDA 9`.

### orm.comercio_indice_redundante — NUEVA 2026-10-05

`public.comercio.idx_comercio_codigo_qr` es redundante con el UNIQUE constraint
`comercio_codigo_qr_key` (misma columna). Aplicado en ORM por fidelidad.

**Tier 3.** Evaluar eliminacion en ronda de optimizacion.

### orm.tabla_falta_ampliada — ACTUALIZADA 2026-10-05

**Reemplaza y amplia** `orm.schema_falta_comunicacion` + `orm.schema_falta_rentabilidad`
+ `orm.tabla_falta_auth`. El `alembic check` de cierre R8 revelo que las
tablas faltantes son ~16:

**Schema comunicacion (3):**
- `comunicacion.conversacion` (7 cols).
- `comunicacion.email_enviado` (9 cols).
- `comunicacion.mensaje` (8 cols).

**Schema rentabilidad (3):**
- `rentabilidad.analisis_medios_pago` (10 cols).
- `rentabilidad.rentabilidad_diaria_vehiculo` (13 cols).
- `rentabilidad.rentabilidad_mensual_vehiculo` (13 cols).

**Schema auth (4):**
- `auth.codigo_metadatos` (6 cols) — decision D-006 (R6).
- `auth.codigo_verificacion` (9 cols) — decision D-006 (R6).
- `auth.plantilla_viaje` (19 cols) — hallazgo nuevo.
- `auth.prestadora_telefonica` (6 cols) — hallazgo nuevo.

**Schema payment (2):**
- `payment.qr_cobro` (10 cols) — hallazgo nuevo R8.
- `payment.configuracion_pasarela` (7 cols) — hallazgo nuevo R8.

**Schema audit (1):**
- `audit.alertas_vencimiento` (8 cols).

**Schema trip (1):**
- `trip.broadcast_log` (11 cols).

**Schema fleet (2):**
- `fleet.historial_chofer_vehiculo` (6 cols).
- `fleet.relacion_propietario_vehiculo` (7 cols).

**Tier 2.** Ronda 4c extendida (crear modulos ORM). Prioridad media.
**Ver:** `docs/orm_sync/alembic_check_cierre_r8_2026-10-05.txt`.

### metodo_pago.pasarela — ACTUALIZADA 2026-10-05

**Hallazgo R8:** las tablas `payment.qr_cobro` (10 cols) y
`payment.configuracion_pasarela` (7 cols) **YA EXISTEN en la DB** pero no
estan declaradas en el ORM.

`payment.qr_cobro`: id, viaje_id, token, monto, pasarela, estado, url_pago,
id_transaccion_externa, creado_en, expira_en, pagado_en, control_base_id.

`payment.configuracion_pasarela`: id, control_base_id, pasarela, activa,
credenciales (jsonb), comision_porcentaje, created_at.

**Implicacion:** el trabajo de infraestructura para `/cobro-qr` ya esta hecho
en DB. Falta:
- Declarar las tablas en ORM (Fase 4c).
- Implementar endpoints.
- Decidir proveedor comercial (MercadoPago, Uala Bis, AstroPay).

**Tier 2.** Actualizar al planificar `/cobro-qr` (M3 pendiente).

---

## NUEVOS — Ronda 9 (Paso 9)

### orm.indice_sobra_ambiguo — NUEVA 2026-10-06

`diff.py` clasifica como `indice_sobra` dos casos distintos que aparecen
identicos en el reporte:
1. Ruido real: B-tree sobre Geography (inutil, DB nunca lo tuvo).
2. Indices GIST auto-generados por GeoAlchemy2, ausentes en DB.

**Items actuales (3):**
- `fleet.chofer_vehiculo` (D-0091) — GIST, util.
- `trip.panico` (D-0312) — GIST, util.
- `trip.viaje_solicitado` (D-0331) — GIST, util.

**Tier 3.** Requiere analisis manual por item.

### orm.geoalchemy2_indices_no_aplicados — NUEVA 2026-10-06

GeoAlchemy2 agrega automaticamente un `Index GIST` sobre columnas
`Geography` con `spatial_index=True` (default). El ORM los declara en
runtime, pero la DB no los tiene aplicados.

**Items (3):**
- `fleet.chofer_vehiculo.idx_chofer_vehiculo_ubicacion` sobre `ubicacion`.
- `trip.panico.idx_panico_ubicacion` sobre `ubicacion`.
- `trip.viaje_solicitado.idx_viaje_solicitado_destino` sobre `destino`.

**Impacto:** queries espaciales sin indice → full scan.
**Accion:** crear migracion Alembic para crearlos en DB (R10).
**Tier 2.**

### orm.diff_indexes_colapsa_por_columnas — NUEVA 2026-10-06

`diff.py` matchea indices por `tuple(columns)`, no por nombre. Si el ORM
declara dos indices sobre la misma columna (ej: B-tree + GIST sobre
`ubicacion`), el dict `orm_idx` colapsa a uno solo. El otro queda invisible.

**Impacto:** enmascara fixes (el diff no bajo en Paso 9.2).
**Tier 2.** Fix de tooling: matchear por `(nombre, columnas)` o nombre
normalizado. R10.

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

**Nota Fase 2:** relacionado con D-006. La tabla es satelite de
codigo_verificacion, no alternativa.

### G68 — Job procesar_viajes_huerfanos corre cada 1h

Bajar a 15 min si en produccion se ve friccion.

### G70 — Confusion de paths public/viajes

Existen tres (backend publico, proxy dashboard, helper dashboard), uno
huerfano. Renombrar o documentar.

### G72 — Regla de pegado sin tildes desde chat

Refuerza N10. Nunca pegar bloques con tildes/emojis desde el chat al
editor. Comentarios en codigo pegado: ASCII puro.

### G74 — Endpoint /api/viajes/solicitar deprecado

Sigue en codigo. Eliminar en Fase 2 junto con SolicitarViajeRequest y
SolicitarViajeResponse si no aparecen usos nuevos.

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
Vocabulario propio por definir. Probablemente `efectivo | transferencia`.

### metodo_pago.flujo_empresa — 2026-09-30

`empresa_dashboard.py:790`. Dominio: como la empresa le paga a TaxIP.
Valores actuales: transferencia, efectivo, tarjeta, deposito, otros.
Requiere vocabulario propio.

### metodo_pago.recaudacion — 2026-09-30

`schemas/recaudacion_schemas.py:22` con valores
`efectivo | debito | credito | qr | transferencia | billetera`.
Alinear cuando se toque ese modulo.

### flujo_caja.ingreso_turno — ACTUALIZADO 2026-10-01

**Correccion:** el modelo IngresoTurno en `models/fleet.py` declara tabla
`fleet.ingreso_turno` que SI existe en DB.

Comments de `tipo_ingreso`, `medio_pago`, `origen` mezclan vocabularios.
`medio_pago` con espacio final en el comment.

**Accion:** alinear comment del ORM con DB y canonizar vocabulario.
Resuelto en D-005.

**Ver:** `docs/orm_sync/orm_decisiones.md` (D-005, H-003).

### G82 — 2026-09-30

`run.py` tiene `reload=True` hardcodeado. Contradice N14.
Propuesta: `reload=os.getenv("RELOAD", "false").lower() == "true"`,
default apagado. No bloqueante.

---

## BAJA PRIORIDAD

### Backend heredadas

- **A1** — Modelo Reserva apunta a tabla dropeada (trip.reserva).
  **Confirmado 2026-10-01:** trip.reserva esta en ORM (29 columnas), no
  en DB. **Reclasificado** (D-004): no borrar. Ver `orm.reserva_modulo_activo`.
- **A2** — Schemas legacy snake_case mezclados en viajes/schemas.py.
- **A5** — ~22 warnings Duplicate Operation ID en neumaticos OpenAPI.

### Frontend

- **D2** — tsconfig.json con ignoreDeprecations "6.0".
- **D6** — splash.tsx "paso 2 veces la pantalla" (no reproducible).
- **E2** — MetodoPago limitado a 4 valores.
  **Conecta con D-005.** Ver `metodo_pago.frontend_e2`.

### Endpoints faltantes

- **F4** — /cobro-qr, webhooks de pasarela. Bloqueado parcialmente por
  `metodo_pago.pasarela` (tablas existen, ORM no las declara).
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
- **J4** — Extension de viaje (agregar destino a mitad de camino).
- **J5** — "Siga ese auto" (viaje sin destino fijo).
- **J14** — viaje.store construye ViajeActivo a mano desde ViajeSolicitado.
- **J19** — Recargos: iniciado_en vs now().

### Nuevas Ronda 4

- **metodo_pago.config_credito** — `mix_credito`, `comision_credito` en
  `tenant.configuracion_tenant` sin uso cuando desaparece `credito`.
- **metodo_pago.billetera_futuro** — Cuando se implemente la wallet TaxIP,
  agregar `billetera` al CHECK de `viaje_solicitado.metodo_pago`.
- **logs.auth_prints** — `routers/auth.py:289` con
  `print("... [PASO 5c] ...")` con emoji. Barrer prints en routers.
- **orm_viaje.fk_comercio_schema** — FK de `viaje_solicitado.comercio_id`
  apunta a `comercio(id)` sin schema.
  **Confirmado 2026-10-01:** `public.comercio` existe con 13 columnas.
  La FK resuelve por search_path. Revisar en Fase 4 (D-009).

---

## DEUDAS DE EXPO-ROUTER CON REACT 19 (workaround activo)

- **G77** — Bug de expo-router 57.0.24 con React 19 (2 useEffect sin deps).
- **G78** — Workaround: 2 parches en `patches/expo-router+57.0.24.patch`.
- **G79** — Workflow de compilacion migrado a EAS Build.

Cuenta: megarcia34. Proyecto: @megarcia34/taxip-chofer.
projectId: b54c9f37-bdd0-4845-8c78-9628a3cda6a2.
**No tocar hasta que expo saque fix upstream.**

---

## CERRADAS EN RONDA 9 (2026-10-06)

### Fixes de tooling (diff.py)

- **orm.indice_falta_incluye_pks** — CERRADA. `RE_PK_INDEX` + filtro en
  `diff_indexes` excluye PKs (`pk_*` / `*_pkey`). −72 items (`1ac1294`).

### Fixes del ORM

- **`fleet.chofer_vehiculo.ubicacion`** — `index=True` eliminado (B-tree
  redundante con GIST auto-generado por GeoAlchemy2). No baja el diff
  por bug de colapso, pero es cleanup real (`158e594`).

---

## CERRADAS EN RONDA 8 (2026-10-05)

### Fixes de tooling (diff.py)

- **orm.geography_case_divergente** — CERRADA. `_types_equivalent()`
  normaliza Geography a lowercase (`6927f08`).
- **orm.diff_check_nombres_no_matchean** — CERRADA. Exclusion de
  `*_not_null` autogenerados bajo ~358 items (`d3692f1`).

### Fixes del ORM

- **orm.naming_convention_doble_prefijo** — CERRADA. 8 CHECKs de
  `trip.viaje_solicitado` con prefijo `ck_viaje_solicitado_` duplicado
  corregidos (`b2edb4e`).

### Fase 6 — Indices reales

Todos los indices reales del diff aplicados:
- `audit.py`: 8 indices.
- `corporate.py`: 7 indices.
- `tenant.py`: 5 indices.
- `public.py`: 6 indices.
- `payment.py`: 4 indices.
- `geo.py`: 1 indice.
- `foto_viaje.py`: 1 indice.
- `fleet.py`: 60 indices (+2 UNIQUEs).
- `turno.py`: 4 indices.
- `gasto_turno.py`: 2 indices.

**Total: ~98 indices aplicados.** `fleet` schema 100% reconciliado.

### Cambios en este documento

- Nueva deuda: `orm.unique_constraint_vs_unique_index` (14 items).
- Nueva deuda: `orm.indice_falta_incluye_pks` (72 items de ruido). CERRADA en R9.
- Nueva deuda: `orm.comercio_indice_redundante` (1 item).
- Deuda ampliada: `orm.tabla_falta_ampliada` (10 → 16 tablas).
- Deuda actualizada: `metodo_pago.pasarela` (tablas ya existen en DB).
- Deuda actualizada: `orm.paso4_check_constraints_residual` (reemplaza
  `_bloqueado`).

---

## CERRADAS EN RONDA 7 (2026-10-01)

### Fase 4b (fleet.py + 13 archivos)

- Paso 2 residual (tipos): `fleet.gasto_vehiculo.km_registro`.
- Paso 3 (nullable/columnas/tipos/indices) en 14 archivos.
- Paso 7 (D-012): 19 timestamps naive en 7 clases `Neumatico*`.
- Paso 8 parcial: 9 comments.

### Items cerrados

- `orm.turno_chofer_estado_truncado` (Paso 2).
- D-012 (Paso 7).

**Ver:** `docs/HISTORICO_CERRADAS.md`.

---

## RECUENTO

| Categoria | Cantidad |
|---|---|
| Bloqueante | 1 |
| Critico | 1 |
| Nuevos Ronda 5 | 5 |
| Nuevos Ronda 6 (Fase 2) | 4 |
| Nuevos Ronda 7 (Fase 4b) | 7 |
| Nuevos Ronda 8 (Fase 6) | 4 |
| Nuevos Ronda 9 (Paso 9) | 3 |
| Alta prioridad | 3 |
| Media prioridad | 15 |
| Baja prioridad | 21 |
| Expo-router / EAS | 3 |
| **TOTAL PENDIENTES** | **~67** |

**Notas sobre el recuento R9:**
- Cerradas en R9: 1 (`orm.indice_falta_incluye_pks`).
- Nuevas en R9: 3 (`orm.indice_sobra_ambiguo`, `orm.geoalchemy2_indices_no_aplicados`, `orm.diff_indexes_colapsa_por_columnas`).
- Balance neto: −1 cerrada + 3 nuevas = +2.

**Notas sobre el recuento R8 (historicas):**
- Cerradas en R8: 3.
- Nuevas en R8: 4.
- Balance neto: +1.

---

## REFERENCIAS

- **Plan de reconciliacion:** `docs/orm_reconciliacion_plan.md`
- **Snapshots:** `docs/orm_sync/`
- **Reporte diff:** `docs/orm_sync/orm_diff_reporte.md`
- **Decisiones:** `docs/orm_sync/orm_decisiones.md`
- **Historico:** `docs/HISTORICO_CERRADAS.md`
- **Baseline:** `docs/orm_sync/baseline_info.md`
- **Handoff R7→R8:** `docs/CONTEXTO_RONDA_7 a 8.md`
- **Handoff R8→R9:** `docs/CONTEXTO_RONDA_8 a 9.md`
- **Handoff R9→R10:** `docs/CONTEXTO_RONDA_9 a 10.md`
- **Alembic check cierre R7:** `docs/orm_sync/alembic_check_cierre_r7_2026-10-04.txt`
- **Alembic check cierre R8:** `docs/orm_sync/alembic_check_cierre_r8_2026-10-05.txt`
- **Backups:** `docs/backups/`
- **Bitacoras:** `E:\Taxip\app chofer\BITACORA_M1.md`, `M2`, `M3`.

---

**FIN DEL DOCUMENTO**