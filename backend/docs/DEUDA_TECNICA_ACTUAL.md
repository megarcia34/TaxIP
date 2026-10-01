# DEUDA TECNICA ACTUAL — TaxIP 2.0

**Ultima actualizacion:** 2026-10-01 (Ronda 6, Fase 2, Sesion 1)
**Total items pendientes:** 53
**Total criticos:** 1 (orm.db_desalineados)

---

## BLOQUEANTE PARA PRODUCCION

### B5 — Modelo ViajeSolicitado desactualizado

**Estado:** TECNICAMENTE DESBLOQUEADO (Ronda 5 produjo el diagnostico).
**Detalle actualizado:**
- ORM declara 37 columnas.
- DB tiene 66 columnas.
- **Faltan 29 columnas** (confirmado por diff.py, D-XXXX).
- Los CHECK constraints de la DB incluyen 10 (ninguno en ORM).

**Razon original:** el ORM no refleja la DB en multiples tablas. Agregar 29
columnas a un ORM roto era parche parcial.

**Siguiente paso:** Fase 4 (aplicacion de Tier 1) cierra B5 formalmente.

**Ver:**
- docs/orm_sync/orm_diff_reporte.md (Tier 1).
- docs/orm_sync/orm_decisiones.md (H-001, H-002).

---

## CRITICO

### orm.db_desalineados — ACTUALIZADO 2026-10-01

**Estado:** DECISIONES TOMADAS (Fase 2 completa). Pendiente de aplicacion.

**Datos reales (post Fase 1):**

| Metrica | Diagnostico original | Real (diff.py) |
|---|---|---|
| Tablas faltantes | ~40 | 17 (mas 2 schemas completos) |
| Columnas faltantes | ~150 | 227 |
| Indices faltantes | ~80 | 251 |
| Constraints faltantes | no mencionado | 541 |
| Diferencias totales | ~500 | 1,280 |

**Clasificacion por Tier:**
- Tier 1 (critico): 247
- Tier 2 (importante): 912
- Tier 3 (cosmetico): 120
- Tier 4 (muerte): 1

**Items que requerian decision manual:** 24.
**Items con decision tomada en Fase 2:** 24/24 (Ronda 6, Sesion 1).

**Decisiones tomadas en Fase 2:**
- D-005 (metodo_pago): vocabulario canonico acotado, sin migracion.
- D-006 (J9 auth): falso positivo, declarar ambas tablas sin unificar.
- D-007 (control_base): ORM String(50) -> Numeric (ya estaba).
- D-012 (timestamps neumatico_*): ORM a naive (opcion a).

**Riesgo:** cualquier `alembic revision --autogenerate` es DESTRUCTIVA.
Verificado: ninguna migracion historica uso autogenerate.

**Plan:** 5 fases (0 a 4). Fases 0 y 1 completas en Ronda 5.
Fase 2 (decisiones) completa en Ronda 6, Sesion 1.

**Ver:**
- docs/orm_sync/orm_diff_reporte.md
- docs/orm_sync/db_snapshot.json
- docs/orm_sync/orm_snapshot.json
- docs/orm_sync/orm_decisiones.md

---

## NUEVOS — Ronda 5 (Fase 1)

### orm.nullable_desalineado — 2026-10-01

158 columnas con nullable divergente entre ORM y DB.
Bug potencial activo: si ORM declara nullable=True pero DB tiene NOT NULL,
los INSERTs del ORM pueden fallar silenciosamente.

**Tier 2.** Requiere revision en Fase 4.

**Ver:** docs/orm_sync/orm_diff_reporte.md (H-017).

### orm.schema_falta_comunicacion — 2026-10-01

El schema `comunicacion` (3 tablas: conversacion, email_enviado, mensaje)
existe en DB pero no en ORM.

**Tier 2.** Crear modulo `app/models/comunicacion.py` en Fase 4.

**Ver:** docs/orm_sync/orm_decisiones.md (H-012).

### orm.schema_falta_rentabilidad — 2026-10-01

El schema `rentabilidad` (3 tablas: analisis_medios_pago,
rentabilidad_diaria_vehiculo, rentabilidad_mensual_vehiculo) existe en DB
pero no en ORM.

**Tier 2.** Crear modulo `app/models/rentabilidad.py` en Fase 4.

**Ver:** docs/orm_sync/orm_decisiones.md (H-013).

### orm.constraint_nombres_numericos — 2026-10-01

2 constraints con nombres autogenerados por Alembic:
- 63669_63825_1_not_null (trip.viaje_solicitado).
- 63669_63825_38_not_null (trip.viaje_solicitado).

**Tier 3.** Renombrar en Fase 4.

**Ver:** docs/orm_sync/orm_decisiones.md (H-004).

### orm.indices_duplicados — 2026-10-01

Indices duplicados funcionales:
- idx_viaje_estado + ix_viaje_estado (trip.viaje_solicitado).

**Tier 3.** Eliminar uno en Fase 4.

**Ver:** docs/orm_sync/orm_decisiones.md (H-005).

### orm.system_tables_whitelist — 2026-10-01

`public.alembic_version` y `public.spatial_ref_sys` son tablas de sistema.
No deben considerarse parte del diff.

**Accion:** whitelist en diff.py (ya implementado).

**Ver:** docs/orm_sync/orm_decisiones.md (H-014).

---

## NUEVOS — Ronda 6 (Fase 2, Sesion 1)

### metodo_pago.catalogo_sucio — NUEVA 2026-10-01

`payment.metodo_pago` tiene 12 filas con:
- 2 duplicados: efectivo (x2), mercadopago (x2).
- 1 sinonimo: wallet = billetera.
- 1 pasarela mezclada: mercadopago (es proveedor, no metodo).

**Impacto:** todos los reportes leen del catalogo sucio en vez de
`viaje_solicitado.metodo_pago`. Bug real de calculo de comisiones.

**Tier 2.** Limpiar en Fase 4 (dedupe + renombre + decidir si mercadopago
queda como pasarela separada).

**Ver:** docs/orm_sync/orm_decisiones.md (D-005, H-026).

### metodo_pago.fk_catalogo — NUEVA 2026-10-01

Refactor estructural: evaluar FK por `metodo_pago_id` en
`trip.viaje_solicitado` y `fleet.ingreso_turno` (en vez de string).

**Impacto:** toca app, reportes, ORM. Refactor grande.

**Tier 2.** Evaluar en Fase 4. NO en Fase 2.

**Ver:** docs/orm_sync/orm_decisiones.md (D-005).

### metodo_pago.ingreso_turno — NUEVA 2026-10-01

`fleet.ingreso_turno.medio_pago`:
- Comment en DB: 6 valores (efectivo, debito, credito, qr, transferencia,
  billetera). Sin CHECK.
- Datos reales: solo 2 valores (efectivo=57, debito=16).
- ORM: comment divergente, 4 valores.

**Tier 2.** Alinear comment del ORM con DB en Fase 4. Decidir si se agrega
CHECK.

**Ver:** docs/orm_sync/orm_decisiones.md (D-005, H-003).

### metodo_pago.frontend_e2 — NUEVA 2026-10-01

MetodoPago del frontend limitado a 4 valores (deuda E2 original).
Si se amplia el vocabulario (credito, billetera), hay que ampliar el
frontend tambien.

**Tier 3.** Resolver en Fase 4 si se decide ampliar vocabulario.

**Ver:** docs/orm_sync/orm_decisiones.md (D-005).

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

### metodo_pago.pasarela — 2026-09-30

Pasarela de pago: campo/tabla separada. No existe.
Bloqueante de `/cobro-qr` (M3 pendiente). Requiere decision comercial
de proveedor (MercadoPago, Uala Bis, AstroPay).

---

## MEDIA PRIORIDAD

### F5 — ViajeSolicitado.origen_lat/lng vs ViajeActivo.origen

Numeros sueltos vs Coordenada. Mapear en el store al conectar el WS.

### F6 — auth.codigo_metadatos es tabla separada

El INSERT en codigo_verificacion solo no alcanza. Documentar en flujo
del propietario.

**Nota Fase 2:** relacionado con D-006. Ver H-023. La tabla es satelite
de codigo_verificacion, no alternativa.

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
**Relacionado con:** orm.db_desalineados (critico). Cuantificado
como 158 items nullable_desalineado (H-017).

### J15 — No hay deteccion de viaje activo al abrir la app

Plan: endpoint GET /api/chofer/viaje-activo + chequeo en
(app)/_layout.tsx.

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
`fleet.ingreso_turno` que SI existe en DB. Verificado via introspect_db.py.

Comments de `tipo_ingreso`, `medio_pago`, `origen` mezclan vocabularios.
`medio_pago` con espacio final en el comment.

**Accion:** alinear comment del ORM con DB y canonizar vocabulario
(conecta con metodo_pago.catalogo). Resuelto en D-005.

**Ver:** docs/orm_sync/orm_decisiones.md (D-005, H-003).

### G82 — 2026-09-30

`run.py` tiene `reload=True` hardcodeado. Contradice N14.
Propuesta: `reload=os.getenv("RELOAD", "false").lower() == "true"`,
default apagado. No bloqueante.

---

## BAJA PRIORIDAD

### Backend heredadas

- **A1** — Modelo Reserva apunta a tabla dropeada (trip.reserva).
  **Confirmado 2026-10-01:** trip.reserva esta en ORM (29 columnas), no
  en DB. Borrar modelo en Fase 4 (D-004).
- **A2** — Schemas legacy snake_case mezclados en viajes/schemas.py.
- **A5** — ~22 warnings Duplicate Operation ID en neumaticos OpenAPI.

### Frontend

- **D2** — tsconfig.json con ignoreDeprecations "6.0".
- **D6** — splash.tsx "paso 2 veces la pantalla" (no reproducible).
- **E2** — MetodoPago limitado a 4 valores.
  **Conecta con D-005.** Ver metodo_pago.frontend_e2.

### Endpoints faltantes

- **F4** — /cobro-qr, webhooks de pasarela. Bloqueado por
  `metodo_pago.pasarela`.
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
  **Confirmado en diff** (parte de los 158 nullable_desalineado).
- **J2** — es_anonimo existe en DB pero no en ORM.
  **Confirmado en diff** (columna faltante en trip.viaje_solicitado).
- **J3** — origen_tipo, paradas_intermedias, metodo_pago en DB pero no
  en ORM. **Parcialmente cubierto por B5.**
- **J4** — Extension de viaje (agregar destino a mitad de camino).
- **J5** — "Siga ese auto" (viaje sin destino fijo).
- **J14** — viaje.store construye ViajeActivo a mano desde ViajeSolicitado.
- **J19** — Recargos: iniciado_en vs now().

### Nuevas Ronda 4

- **metodo_pago.config_credito** — `mix_credito`, `comision_credito` en
  `tenant.configuracion_tenant` sin uso cuando desaparece `credito`.
  **Confirmado:** las columnas existen en DB pero no en ORM
  (parte de las 19 faltantes de configuracion_tenant).
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

## CERRADAS EN RONDA 4 (2026-09-30)

- **G30** — CERRADO. print() -> logger.info() en main.py (12 prints).
- **B9** — CERRADO. Semantica solicitado_en vs created_at documentada.
- **B7** — CERRADO. Migracion m3_010 (CHECK + normalizacion metodo_pago)
  + 3 ediciones de codigo en routes.py, viaje_schemas.py, medios_pago.py.
- **Limpieza** — 4 tablas backup huerfanas dropeadas de auth (28 filas).

---

## CERRADAS EN RONDA 5 (2026-10-01)

### Fase 0 — Preparacion

- Baseline reproducible (git tag `ronda5-baseline-pre`).
- Backup DB pre-Fase 1: `docs/backups/taxip_db_2026-09-30.dump`.
- Snapshot `alembic check`: `docs/orm_sync/alembic_check_baseline_2026-09-30.txt`.
- `.gitattributes` configurado.

### Fase 1 — Diagnostico estructurado

- `scripts/orm_sync/introspect_db.py` + `db_snapshot.json`.
- `scripts/orm_sync/introspect_orm.py` + `orm_snapshot.json`.
- `scripts/orm_sync/diff.py` + `orm_diff.json` + reporte + CSV.
- 22 hallazgos documentados (H-001 a H-022).

### Items actualizados por Ronda 5

- **B5:** desbloqueado tecnicamente, cuantificado (29 columnas).
- **orm.db_desalineados:** cuantificado con datos reales (1,280 diferencias).
- **J9:** confirmado en diff (D-0004, D-0005).
- **J1, J2, J3:** confirmados en diff.
- **flujo_caja.ingreso_turno:** la tabla SI existe (doc decia que no).
- **A1:** trip.reserva confirmado huerfano.
- **orm_viaje.fk_comercio_schema:** public.comercio existe.

---

## CERRADAS EN RONDA 6 (2026-10-01, Fase 2, Sesion 1)

### Decisiones tomadas

- **D-005** (metodo_pago): vocabulario canonico acotado al CHECK actual de
  trip.viaje_solicitado. Sin migracion DB. 4 deudas nuevas derivadas.
- **D-006** (J9 auth): FALSO POSITIVO documental. Declarar ambas tablas
  en ORM, no unificar.
- **D-007** (control_base): confirmado, sin cambios.
- **D-012** (timestamps neumatico_*): ORM a naive (opcion a).

### Items cerrados

- **J9** — CERRADO como FALSO POSITIVO (H-023). No hay dos fuentes de
  verdad. codigo_metadatos es satelite de codigo_verificacion.
- **metodo_pago.catalogo** (item original de la deuda) — CERRADO en su
  parte de decision. La limpieza del catalogo pasa a metodo_pago.catalogo_sucio.

### Items con decision acotada

- **D-008** (fleet timestamps): corregido de 70 columnas (estimacion Fase 0)
  a 19 columnas (dato real Fase 1). Resuelto en D-012.
- **H-021** (24 items requieren decision): 24/24 resueltos.

### Hallazgos nuevos

- **H-023** — J9 es falso positivo.
- **H-024** — fleet tiene 68 columnas timestamp, todas naive.
- **H-025** — volumen de datos en neumatico_*: 41 filas de prueba.
- **H-026** — vocabularios de metodo_pago: 5 variantes documentadas.

---

## RECUENTO

| Categoria | Cantidad |
|---|---|
| Bloqueante | 1 |
| Critico | 1 |
| Nuevos Ronda 5 | 6 |
| Nuevos Ronda 6 (Fase 2) | 4 |
| Alta prioridad | 4 |
| Media prioridad | 15 |
| Baja prioridad | 21 |
| Expo-router / EAS | 3 |
| **TOTAL PENDIENTES** | **53** |

**Notas sobre el recuento:**
- Cerradas en Ronda 6: J9 (falso positivo), metodo_pago.catalogo (absorbido
  en D-005).
- Nuevas en Ronda 6: metodo_pago.catalogo_sucio, metodo_pago.fk_catalogo,
  metodo_pago.ingreso_turno, metodo_pago.frontend_e2.
- Balance neto: -2 cerradas + 4 nuevas = +2 items. De 51 a 53.

---

## REFERENCIAS

- **Plan de reconciliacion:** `D:\aTaxip\backend\docs\orm_reconciliacion_plan.md`
- **Snapshots:** `docs/orm_sync/`
- **Reporte diff:** `docs/orm_sync/orm_diff_reporte.md`
- **Decisiones:** `docs/orm_sync/orm_decisiones.md`
- **Baseline:** `docs/orm_sync/baseline_info.md`
- **Backups:** `docs/backups/`
- **Bitacoras:** `E:\Taxip\app chofer\BITACORA_M1.md`, `M2`, `M3`.

---

**FIN DEL DOCUMENTO**