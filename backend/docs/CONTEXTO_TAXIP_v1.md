# CONTEXTO TAXIP 2.0 — Estado y Deuda Pendiente

**Ultima actualizacion:** 2026-10-21 (post R21)
**Alembic head:** m3_025
**Diff BD <-> ORM:** 1 item (indice preexistente en payment.py — deuda aceptada)
**Tag activo:** ronda20-completa
**Repo:** github.com/megarcia34/TaxIP (main)

**Reglas de alineacion BD <-> ORM:** ver `docs/REGLAS_ALINEACION_BD_ORM.md`.
**Historico de rondas:** ver `docs/HISTORICO_CERRADAS.md`.
**Contexto de negocio:** ver `docs/RESUMEN_EJECUTIVO_2026-10-13.md` (pendiente actualizar a R20).
**Decisiones tecnicas ORM:** ver `docs/orm_sync/orm_decisiones.md`.

---

## Resumen ejecutivo

- **Alineacion estructural BD <-> ORM:** 1 item pendiente (preexistente, deuda aceptada).
- **Deuda alta prioridad:** 0 items.
- **Deuda media prioridad:** ~18 items (3 nuevas de R20).
- **Deuda baja prioridad:** ~25 items.
- **Tocar Frontend:** 2 items (deuda historica).
- **Expo-router / EAS:** 3 items (workaround activo, no tocar).

**Ultimas rondas cerradas:**

- **R14:** alineacion estructural BD <-> ORM completada.
- **R15:** limpieza de `metodo_pago` (12 -> 4 filas) + `alembic check` categorias C y D.
- **R16:** quick wins (G82, A5, G74, tooling, indices redundantes).
- **R17:** G63 (alerta fallback precios) + G67 (forzar cierre turno).
- **R18:** `metodo_pago` completo (flujo_propietario, flujo_empresa, billetera, fk_catalogo via muerta).
- **R19:** backend completo de ciclo de vida de vehiculo (`m3_021`), perfil propietario + cuentas de cobro (`m3_022`), notificacion antiguedad taxi (`m3_023`).
- **R20:** frontend completo del dashboard propietario (perfil, cuentas, chofer, vehiculos, contratos con codigo de 6 digitos).

---

## ALTA PRIORIDAD

_(vacio)_

---

## MEDIA PRIORIDAD

### storage.unificar_cloudinary_local

**Titulo:** Unificar storage: `storage_service` (local) vs `cloudinary_storage`

**Estado:** Deuda abierta. Mitigada parcialmente en R20.

**Contexto:**

Hay dos servicios de storage conviviendo:

| Servicio | Archivo | Destino | Uso actual |
|---|---|---|---|
| `storage_service` | `app/services/storage.py` | Filesystem local (`./uploads/...`) | Endpoints legacy |
| `cloudinary_storage` | `app/services/cloudinary_storage.py` | Cloudinary | Endpoints nuevos |

**En R20:** el endpoint `POST /api/chofer/subir-documento` fue migrado a Cloudinary. Ahora ambos endpoints del chofer usan `cloudinary_storage.upload_documento_chofer()`.

**Deuda pendiente:** auditar los demas usos de `storage_service.save_document()` y `save_photo()` para determinar si conviene migrarlos.

**Archivos referenciados:**
- `app/services/storage.py`
- `app/services/cloudinary_storage.py`
- `app/routers/chofer_documentos.py` (migrado)

### apiClient.duplicado_legacy_modular

**Titulo:** Dos `apiClient` convivendo (legacy vs modular)

**Estado:** Deuda abierta. Detectada en R20.

**Contexto:**

Hay dos instancias de axios:

1. **`lib/api.ts`** (legacy):
   - `baseURL: http://localhost:8000` (sin `/api`).
   - Rutas: incluyen `/api/...` manualmente.
   - Interceptor: cache de token + refresh + cola.
   - Usado por: `propietarioAPI`, `authAPI`, `adminAPI`, `controlBaseAPI`.

2. **`lib/api/client.ts`** (modular):
   - `baseURL: http://localhost:8000/api`.
   - Rutas: sin `/api`.
   - Interceptor: token desde NextAuth.
   - Usado por: `neumaticos.ts`, `propietario.ts`, `perfil.ts`, `cuentasCobro.ts`, `postulacionChofer.ts`, etc.

**Riesgos:** comportamiento distinto ante 401, rutas inconsistentes, duplicacion.

**Accion futura:** migrar `lib/api.ts` a `lib/api/client.ts`, unificar interceptor de refresh.


### documentos.duplicados_en_db
**Estado:** ✅ Cerrada en R21.
**Contexto:** Se implementó UPSERT en `crear_documento_vehiculo` (actualiza si existe, inserta si no). Ya no se duplican documentos por tipo.

### vehiculos.habilitacion_obligatoria

**Titulo:** `HABILITACION` es obligatorio para `documentacion_completa`

**Estado:** Deuda abierta. Detectada en R20.

**Contexto:** el backend exige 4 documentos obligatorios: `SEGURO`, `VTV`, `CEDULA_VERDE`, `HABILITACION`. Si un tenant no requiere habilitacion municipal, no puede operar sin cambiar el codigo.

**Accion futura:** parametrizar la lista de documentos obligatorios por tenant (`tenant.configuracion_tenant`).

### G68 — Job `procesar_viajes_huerfanos` corre cada 1h

Bajar a 15 min si en produccion se ve friccion.

### G70 — Confusion de paths public/viajes

Existen tres (backend publico, proxy dashboard, helper dashboard), uno huerfano. Renombrar o documentar.

### G72 — Regla de pegado sin tildes desde chat

Refuerza N10. Nunca pegar bloques con tildes/emojis desde el chat al editor. Comentarios en codigo pegado: ASCII puro.

### G76 — Worker de uvicorn a veces carga version vieja

Tras un cambio en un archivo que importa otro modulo modificado. Verificar `LastWriteTime` vs `StartTime` del proceso Python.

### G81 — DB y modelos ORM desincronizados silenciosamente

Sintoma: INSERTs fallan por columna inexistente, sin error visible.

### F5 — `ViajeSolicitado.origen_lat/lng` vs `ViajeActivo.origen`

Numeros sueltos vs Coordenada. Mapear en el store al conectar el WS.

### F6 — `auth.codigo_metadatos` es tabla separada

El INSERT en `codigo_verificacion` solo no alcanza. Documentar en flujo del propietario.

### J15 — No hay deteccion de viaje activo al abrir la app

Plan: endpoint `GET /api/chofer/viaje-activo` + chequeo en `(app)/_layout.tsx`.

### metodo_pago.recaudacion

`schemas/recaudacion_schemas.py:22`. Alinear comment cuando se toque ese modulo.

### metodo_pago.ingreso_turno

`fleet.ingreso_turno.medio_pago`:
- Comment en DB: 6 valores. Sin CHECK.
- Datos reales: solo 2 valores (efectivo=57, debito=16).
- ORM: comment divergente, 4 valores.

Alinear comment del ORM con DB.

### flujo_caja.ingreso_turno

Comments de `tipo_ingreso`, `medio_pago`, `origen` mezclan vocabularios. `medio_pago` con espacio final en el comment.

Alinear comment del ORM con DB y canonizar vocabulario.

### orm.alembic_check_categoria_b

`alembic check` reporta ~35 items por FKs con `ondelete` distinto entre ORM y DB. Decision pendiente por cada FK.

### orm.foto_viaje_out_of_scope

El item `foto_viaje.created_at` nullable desalineado NO esta en `trip.py`, esta en `app/models/foto_viaje.py`. Pendiente Fase 4d.

### orm.snapshot_orm_stale

El `orm_snapshot.json` puede quedar desactualizado si se editan archivos del ORM sin regenerarlo. Mitigacion: regenerar siempre antes de comparar.

### orm.diff_falsos_positivos_tipo_cambio

Cuando se cambia el tipo o nullable de una columna, `diff.py` puede reportarla como `columna_falta` en el proximo diff.

### payment.indice_falta (preexistente)

`diff.py` reporta 1 item `indice_falta` en `app/models/payment.py`. **Deuda aceptada** en R20. No es critica.

### rentabilidad.comision_credito_corporativo

`tenant.configuracion_tenant.comision_credito` (default 3.50%) existe y es real. Aplica al flujo corporativo (Momento 2). Documentar en la UI del dashboard empresa.

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
- **G42** — Duplicacion de calculo de precio entre calcular_costo y solicitar_viaje_calle.
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
- **metodo_pago.billetera_futuro** — Cuando se implemente la wallet TaxIP (Momento 3), agregar `billetera` al CHECK de `viaje_solicitado.metodo_pago` y al catalogo `payment.metodo_pago`.
- **orm_viaje.fk_comercio_schema** — FK de `viaje_solicitado.comercio_id` apunta a `comercio(id)` sin schema.

### Otras
- **datos.turno_chofer_km_final_outlier** — `fleet.turno_chofer.km_final` tiene un valor maximo de 1.523.999,00 km, irreal para un taxi urbano.
- **orm.comercio_indice_redundante** — `public.comercio.idx_comercio_codigo_qr` es redundante con el UNIQUE constraint `comercio_codigo_qr_key`.
- **orm.alembic_check_categoria_a** — `alembic check` reporta ~15 falsos positivos por naming divergente entre UNIQUE constraints y UNIQUE indexes. NO tocar.

---

## TOCAR FRONTEND

### G63.frontend_propietario
Backend de G63 completo (contadores + audit + 2 endpoints), pero falta el frontend del propietario. **En R20 se agrego la pantalla `/dashboard-propietario/metricas-fallbacks`.** ✅ Cerrada.

### G67.frontend_chofer
Backend de G67 completo (2 endpoints + notificaciones), pero falta el frontend del chofer para que pueda usar la funcionalidad. **Pendiente para R21+ (app chofer).**

### G80
La app en el celular apunta a 192.168.1.14:8081 (Metro dev). Para pruebas en terreno: build preview o production apuntando al backend publico. **Bloqueada por deploy a produccion.**

---

## VIA MUERTA (NO HACER)

### metodo_pago.fk_catalogo
**Decision (R18):** NO HACER. Analisis empirico: 53 viajes, 100% dentro del vocabulario canonico. El refactor a FK rompe la API del frontend sin aportar valor claro.

### orm.alembic_check_ruidoso
**Accion:** NO usar `alembic check` como gate. Usar `diff.py`. **NUNCA correr `alembic revision --autogenerate`.**

---

## DEUDAS DE EXPO-ROUTER CON REACT 19 (workaround activo)

- **G77** — Bug de expo-router 57.0.24 con React 19.
- **G78** — Workaround: 2 parches en `patches/expo-router+57.0.24.patch`.
- **G79** — Workflow de compilacion migrado a EAS Build.

Cuenta: megarcia34. Proyecto: @megarcia34/taxip-chofer.
**No tocar hasta que expo saque fix upstream.**

---

## RECUENTO

| Categoria | Cantidad |
|---|---|
| Alta prioridad | 0 |
| Media prioridad | ~18 |
| Baja prioridad | ~25 |
| Tocar Frontend | 1 (G67) |
| Expo-router / EAS | 3 |
| **TOTAL PENDIENTES** | **~47 items** |

---

## REFERENCIAS

- **Reglas de alineacion BD <-> ORM:** `docs/REGLAS_ALINEACION_BD_ORM.md`
- **Historico de rondas cerradas:** `docs/HISTORICO_CERRADAS.md`
- **Contexto de negocio:** `docs/RESUMEN_EJECUTIVO_2026-10-13.md`
- **Decisiones tecnicas ORM:** `docs/orm_sync/orm_decisiones.md`
- **Snapshots:** `docs/orm_sync/`
- **Reporte diff:** `docs/orm_sync/orm_diff_reporte.md`
- **Backups:** `docs/backups/`

---

**FIN DEL DOCUMENTO**