# DEUDA TECNICA ACTUAL — TaxIP 2.0

**Ultima actualizacion:** 2026-10-12 (cierre Ronda 16)
**Ronda activa:** 16 cerrada (`ronda16-fase16-completa`)
**Alembic head:** m3_018
**Diff BD <-> ORM:** 0 items (alineado desde R14)

---

## Como leer este documento

**Este documento contiene SOLO deuda tecnica PENDIENTE.**

- **Historico de rondas cerradas:** ver `docs/HISTORICO_CERRADAS.md`.
- **Decisiones tecnicas ORM (D-XXX):** ver `docs/orm_sync/orm_decisiones.md`.
- **Handoffs entre rondas:** ver `docs/CONTEXTO_RONDA_N a N+1.md`.

**Ultima limpieza:** 2026-10-12 (R16). Refactor: se movio el historico
de rondas a `HISTORICO_CERRADAS.md`. El archivo baja de ~950 a ~400
lineas.

---

## Resumen ejecutivo

- **Diff BD <-> ORM:** 0 items. Alineacion estructural completa (R14).
- **Deuda pendiente:** ~110 items no-diff.
- **Prioridad alta:** 3 items (G63, G67, G80).
- **Prioridad media:** ~15 items.
- **Prioridad baja:** ~21 items.
- **Expo-router / EAS:** 3 items (workaround activo, no tocar).

---

## ALTA PRIORIDAD

### G63 — Alerta si el motor de precios cae a fallback

`precio_final` puede caer a `precio_estimado` si el motor unificado falla.
Requiere infra de monitoreo (Sentry, Grafana o similar). Fase 2.

### G67 — `check_out_turno` sin escapatoria si hay viajes huerfanos

El chofer queda atrapado sin poder cerrar turno. Requiere decision de
negocio: auto-cancelar huerfanos con motivo, o boton "forzar cierre".

### G80 — App apunta a Metro (no funciona fuera de WiFi dev)

La app en el celular apunta a 192.168.1.14:8081. Para pruebas en terreno:
build preview o production apuntando al backend publico.

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

### metodo_pago.flujo_propietario

`liquidacion.py:329`, `fleet.py:875/880` (comments de `IngresoTurno`).
Dominio: como el propietario le paga al chofer.
Vocabulario propio por definir.

### metodo_pago.flujo_empresa

`empresa_dashboard.py:790`. Dominio: como la empresa le paga a TaxIP.
Requiere vocabulario propio.

### metodo_pago.recaudacion

`schemas/recaudacion_schemas.py:22`. Alinear cuando se toque ese modulo.

### metodo_pago.fk_catalogo

Refactor estructural: evaluar FK por `metodo_pago_id` en
`trip.viaje_solicitado` y `fleet.ingreso_turno` (en vez de string).

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

Tablas afectadas: log_acciones, log_gps, autorizacion_inicio,
perfil_general, usuario, usuario_rol, chofer_vehiculo, gasto_turno,
gasto_vehiculo, mantenimiento_vehiculo, neumatico_* (7 tablas),
turno_chofer, vehiculo, ciudad, provincia, configuracion_tarifa,
transaccion, configuracion_tenant, control_base, calificacion,
historial_estado_viaje, objeto_olvidado, panico, viaje_solicitado.

**Decision pendiente** por cada FK: aplicar `ondelete` en DB, quitar
del ORM, o dejar como deuda aceptada.

### pagos.py_203_billetera

`app/routers/pagos.py:203` referencia `payment.metodo_pago WHERE
nombre = 'billetera'`. La fila `billetera` fue eliminada del catalogo
en `m3_016` (pertenece al Momento 3 - billetera TaxIP futura).

**Impacto:** el TOP_UP de wallet queda deshabilitado silenciosamente
(0 transacciones afectadas al momento del cambio).

**Accion futura:** implementar la billetera TaxIP, agregar `billetera`
al CHECK de `metodo_pago` y al flujo de pagos.

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
reportarla como `columna_falta` en el proximo diff (en vez de
`tipo_desalineado` o `nullable_desalineado`).

### orm.alembic_check_ruidoso

`alembic check` reporta cientos de operaciones de upgrade pendientes
porque la DB y el ORM representan constraints de forma distinta
(UNIQUE constraint vs index, nombres de FK, ondelete).

**Accion:** documentar. NO usar `alembic check` como gate. Usar
`diff.py` como fuente de verdad.

---

## BAJA PRIORIDAD

### Backend heredadas

- **A2** — Schemas legacy snake_case mezclados en viajes/schemas.py.

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
| Alta prioridad | 3 |
| Media prioridad | ~20 |
| Baja prioridad | ~35 |
| Expo-router / EAS | 3 |
| **TOTAL PENDIENTES** | **~60 items** |

**Nota:** el recuento es aproximado. Los items se reagrupan a medida
que se cierran. Las deudas nuevas se agregan en su seccion de prioridad.

---

## REFERENCIAS

- **Historico de rondas cerradas:** `docs/HISTORICO_CERRADAS.md`
- **Decisiones tecnicas ORM:** `docs/orm_sync/orm_decisiones.md`
- **Plan de reconciliacion:** `docs/orm_reconciliacion_plan.md`
- **Snapshots:** `docs/orm_sync/`
- **Reporte diff:** `docs/orm_sync/orm_diff_reporte.md`
- **Handoffs:** `docs/CONTEXTO_RONDA_N a N+1.md`
- **Backups:** `docs/backups/`
- **Bitacoras:** `E:\Taxip\app chofer\BITACORA_M1.md`, `M2`, `M3`.

---

**FIN DEL DOCUMENTO**