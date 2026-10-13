# CONTEXTO TAXIP 2.0 — Estado y Deuda Pendiente

**Ultima actualizacion:** 2026-10-13 (post R18)
**Alembic head:** m3_020
**Diff BD <-> ORM:** 0 items (alineado desde R14)
**Tag activo:** ronda18-fase18-completa
**Repo:** github.com/megarcia34/TaxIP (main)

**Reglas de alineacion BD <-> ORM:** ver `docs/REGLAS_ALINEACION_BD_ORM.md`.
**Historico de rondas:** ver `docs/HISTORICO_CERRADAS.md`.
**Contexto de negocio:** ver `docs/RESUMEN_EJECUTIVO_2026-10-13.md`.
**Decisiones tecnicas ORM:** ver `docs/orm_sync/orm_decisiones.md`.

---

## Resumen ejecutivo

- **Alineacion estructural BD <-> ORM:** completa (diff = 0 desde R14).
- **Deuda `metodo_pago`:** cerrada en R18 (4/4 items).
- **Deuda alta prioridad:** 0 items.
- **Deuda media prioridad:** ~15 items.
- **Deuda baja prioridad:** ~25 items.
- **Tocar Frontend:** 2 items.
- **Expo-router / EAS:** 3 items (workaround activo, no tocar).

**Ultimas rondas cerradas:**

- **R14:** alineacion estructural BD <-> ORM completada.
- **R15:** limpieza de `metodo_pago` (12 -> 4 filas) + `alembic check` categorias C y D.
- **R16:** quick wins (G82, A5, G74, tooling, indices redundantes).
- **R17:** G63 (alerta fallback precios) + G67 (forzar cierre turno).
- **R18:** `metodo_pago` completo (flujo_propietario, flujo_empresa, billetera, fk_catalogo via muerta).

---

## ALTA PRIORIDAD

_(vacio - ultima deuda de alta prioridad fue G67, cerrada en R17)_

---

## MEDIA PRIORIDAD

### G68 — Job `procesar_viajes_huerfanos` corre cada 1h

Bajar a 15 min si en produccion se ve friccion.

### G70 — Confusion de paths public/viajes

Existen tres (backend publico, proxy dashboard, helper dashboard), uno
huerfano. Renombrar o documentar.

### G72 — Regla de pegado sin tildes desde chat

Refuerza N10. Nunca pegar bloques con tildes/emojis desde el chat al
editor. Comentarios en codigo pegado: ASCII puro.

### G76 — Worker de uvicorn a veces carga version vieja

Tras un cambio en un archivo que importa otro modulo modificado.
Verificar `LastWriteTime` vs `StartTime` del proceso Python.

### G81 — DB y modelos ORM desincronizados silenciosamente

Sintoma: INSERTs fallan por columna inexistente, sin error visible.

### F5 — `ViajeSolicitado.origen_lat/lng` vs `ViajeActivo.origen`

Numeros sueltos vs Coordenada. Mapear en el store al conectar el WS.

### F6 — `auth.codigo_metadatos` es tabla separada

El INSERT en `codigo_verificacion` solo no alcanza. Documentar en flujo
del propietario.

### J15 — No hay deteccion de viaje activo al abrir la app

Plan: endpoint `GET /api/chofer/viaje-activo` + chequeo en
`(app)/_layout.tsx`.

### metodo_pago.recaudacion

`schemas/recaudacion_schemas.py:22`. Alinear comment cuando se toque
ese modulo.

### metodo_pago.ingreso_turno

`fleet.ingreso_turno.medio_pago`:
- Comment en DB: 6 valores. Sin CHECK.
- Datos reales: solo 2 valores (efectivo=57, debito=16).
- ORM: comment divergente, 4 valores.

Alinear comment del ORM con DB.

### flujo_caja.ingreso_turno

Comments de `tipo_ingreso`, `medio_pago`, `origen` mezclan vocabularios.
`medio_pago` con espacio final en el comment.

Alinear comment del ORM con DB y canonizar vocabulario.

### orm.alembic_check_categoria_b

`alembic check` reporta ~35 items por FKs con `ondelete` distinto
entre ORM y DB. El ORM declara `ondelete` en `ForeignKey(...)`, la DB
no lo tiene aplicado.

**Decision pendiente** por cada FK: aplicar `ondelete` en DB, quitar
del ORM, o dejar como deuda aceptada.

### orm.foto_viaje_out_of_scope

El item `foto_viaje.created_at` nullable desalineado NO esta en
`trip.py`, esta en `app/models/foto_viaje.py`. Pendiente Fase 4d.

### orm.snapshot_orm_stale

El `orm_snapshot.json` puede quedar desactualizado si se editan
archivos del ORM sin regenerarlo. El diff entonces reporta falsos
positivos.

**Mitigacion actual:** regenerar siempre antes de comparar.

### orm.diff_falsos_positivos_tipo_cambio

Cuando se cambia el tipo o nullable de una columna, `diff.py` puede
reportarla como `columna_falta` en el proximo diff.

### rentabilidad.comision_credito_corporativo

`tenant.configuracion_tenant.comision_credito` (default 3.50%) existe
y es real. Aplica al **flujo corporativo** (Momento 2): empresas
pueden pagar viajes con tarjeta de credito.

**R18:** `empresa_dashboard.py:791` actualizado a `tarjeta_credito`.
`rentabilidad.py` usa `tarjeta_debito` y `tarjeta_credito`.

**Accion futura:** documentar en la UI del dashboard empresa que la
comision del 3.50% aplica a tarjeta_credito.

---

## BAJA PRIORIDAD

### Backend heredadas

- **A2** — Schemas legacy snake_case mezclados en viajes/schemas.py.

### Frontend

- **D2** — tsconfig.json con ignoreDeprecations "6.0".
- **D6** — splash.tsx "paso 2 veces la pantalla" (no reproducible).
- **E2** — MetodoPago limitado a 4 valores (viajes comunes).

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
- **J4** — Extension de viaje.
- **J5** — "Siga ese auto".
- **J14** — viaje.store construye ViajeActivo a mano desde ViajeSolicitado.
- **J19** — Recargos: iniciado_en vs now().

### Nuevas Ronda 4

- **metodo_pago.billetera_futuro** — Cuando se implemente la wallet TaxIP
  (Momento 3), agregar `billetera` al CHECK de `viaje_solicitado.metodo_pago`
  y al catalogo `payment.metodo_pago`.
- **orm_viaje.fk_comercio_schema** — FK de `viaje_solicitado.comercio_id`
  apunta a `comercio(id)` sin schema.

### Otras

- **datos.turno_chofer_km_final_outlier** — `fleet.turno_chofer.km_final`
  tiene un valor maximo de 1.523.999,00 km, irreal para un taxi urbano.
- **orm.comercio_indice_redundante** — `public.comercio.idx_comercio_codigo_qr`
  es redundante con el UNIQUE constraint `comercio_codigo_qr_key`.
- **orm.alembic_check_categoria_a** — `alembic check` reporta ~15 falsos
  positivos por naming divergente entre UNIQUE constraints y UNIQUE indexes.
  El `diff.py` los considera equivalentes. NO tocar.

---

## TOCAR FRONTEND

### G63.frontend_propietario

Backend de G63 completo (contadores + audit + 2 endpoints), pero
**falta el frontend del propietario**.

El propietario deberia ver en el dashboard:
- Badge con total de fallbacks.
- Listado de viajes afectados.
- Detalle de cada fallback (precio estimado, motivo, fecha, vehiculo).

Endpoint disponible: `GET /api/propietario/metricas/fallbacks`.

### G67.frontend_chofer

Backend de G67 completo (2 endpoints + notificaciones), pero **falta el
frontend del chofer** para que pueda usar la funcionalidad.

El chofer deberia ver en la app:
- Mensaje al intentar cerrar turno con viajes huerfanos.
- Pantalla con el listado de viajes huerfanos.
- Modal para elegir motivo + notas al cerrar cada uno.
- Habilitar el check-out normal una vez cerrados todos.

Endpoints disponibles:
- `GET /api/chofer/turno/viajes-huerfanos`
- `POST /api/chofer/turno/viajes-huerfanos/{viaje_id}/cerrar`

### G80

La app en el celular apunta a 192.168.1.14:8081 (Metro dev). Para
pruebas en terreno: build preview o production apuntando al backend
publico.

**Bloqueada por:** falta definir URL del backend publico (deploy a
produccion).

---

## VIA MUERTA (NO HACER)

### metodo_pago.fk_catalogo

**Evaluada en R18.** Analisis empirico:
- 53 viajes, 100% dentro del vocabulario canonico.
- 71 usos del string en el codigo, todos coherentes.
- CHECK en `viaje_solicitado` ya garantiza integridad.
- El refactor a FK rompe la API del frontend sin aportar valor claro.

**Decision:** NO HACER.

### orm.alembic_check_ruidoso

`alembic check` reporta cientos de operaciones de upgrade pendientes
porque la DB y el ORM representan constraints de forma distinta
(UNIQUE constraint vs index, nombres de FK, ondelete).

**Accion:** NO usar `alembic check` como gate. Usar `diff.py`.

**NUNCA correr `alembic revision --autogenerate`.**

---

## DEUDAS DE EXPO-ROUTER CON REACT 19 (workaround activo)

- **G77** — Bug de expo-router 57.0.24 con React 19 (2 useEffect sin deps).
- **G78** — Workaround: 2 parches en `patches/expo-router+57.0.24.patch`.
- **G79** — Workflow de compilacion migrado a EAS Build.

Cuenta: megarcia34. Proyecto: @megarcia34/taxip-chofer.
projectId: b54c9f37-bdd0-4845-8c78-9628a3cda6a2.
**No tocar hasta que expo saque fix upstream.**

---

## RECUENTO

| Categoria | Cantidad |
|---|---|
| Alta prioridad | 0 |
| Media prioridad | ~16 |
| Baja prioridad | ~25 |
| Tocar Frontend | 2 |
| Expo-router / EAS | 3 |
| **TOTAL PENDIENTES** | **~46 items** |

**Nota:** el recuento es aproximado. Los items se reagrupan a medida
que se cierran.

---

## REFERENCIAS

- **Reglas de alineacion BD <-> ORM:** `docs/REGLAS_ALINEACION_BD_ORM.md`
- **Historico de rondas cerradas:** `docs/HISTORICO_CERRADAS.md`
- **Contexto de negocio:** `docs/RESUMEN_EJECUTIVO_2026-10-13.md`
- **Decisiones tecnicas ORM:** `docs/orm_sync/orm_decisiones.md`
- **Snapshots:** `docs/orm_sync/`
- **Reporte diff:** `docs/orm_sync/orm_diff_reporte.md`
- **Handoffs historicos:** `docs/historico/handoffs/`
- **Backups:** `docs/backups/`
- **Bitacoras:** `E:\Taxip\app chofer\BITACORA_M1.md`, `M2`, `M3`.

---

**FIN DEL DOCUMENTO**