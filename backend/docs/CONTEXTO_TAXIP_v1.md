# CONTEXTO TAXIP 2.0 — Estado y Deuda Pendiente

**Ultima actualizacion:** 2026-10-27 (post R22)
**Alembic head:** m3_025
**Diff BD <-> ORM:** 1 item (indice preexistente en payment.py — deuda aceptada)
**Tag activo:** ronda22-completa
**Repo:** github.com/megarcia34/TaxIP (main)

**Reglas de alineacion BD <-> ORM:** ver `docs/REGLAS_ALINEACION_BD_ORM.md`.
**Historico de rondas cerradas:** ver `docs/HISTORICO_CERRADAS.md`.
**Contexto de negocio:** ver `docs/RESUMEN_EJECUTIVO_2026-10-13.md` (pendiente actualizar a R21).
**Decisiones tecnicas ORM:** ver `docs/orm_sync/orm_decisiones.md`.

---

## Resumen ejecutivo

- **Alineacion estructural BD <-> ORM:** 1 item pendiente (preexistente, deuda aceptada).
- **Deuda alta prioridad:** 0 items.
- **Deuda media prioridad:** ~18 items.
- **Deuda baja prioridad:** ~21 items.
- **Tocar Frontend:** 1 item (G67).
- **Expo-router / EAS:** 0 items (migracion completada).

**Ultimas rondas cerradas:**

- **R14:** alineacion estructural BD <-> ORM completada.
- **R15:** limpieza de `metodo_pago` (12 -> 4 filas) + `alembic check` categorias C y D.
- **R16:** quick wins (G82, A5, G74, tooling, indices redundantes).
- **R17:** G63 (alerta fallback precios) + G67 (forzar cierre turno).
- **R18:** `metodo_pago` completo (flujo_propietario, flujo_empresa, billetera, fk_catalogo via muerta).
- **R19:** backend completo de ciclo de vida de vehiculo (`m3_021`), perfil propietario + cuentas de cobro (`m3_022`), notificacion antiguedad taxi (`m3_023`).
- **R20:** frontend completo del dashboard propietario (perfil, cuentas, chofer, vehiculos, contratos con codigo de 6 digitos).
- **R21:** Dashboard Tenant (solicitudes pendientes, aprobación/rechazo). **Migración completa de `expo-router` a React Navigation** (por bug de React 19). Actualización a **Expo SDK 58**. Implementación de **autocompletado real** con Google Places y `locationBias` por GPS. Fix de historial de viajes (LEFT JOIN). Flujo completo del chofer validado en iOS y Android.
- **R22:** **Nuevas funcionalidades:** Módulo Finanzas del Chofer (resumen, gastos con Cloudinary, integración dual write). Módulo Perfil del Chofer (datos, documentos, reporte de actividad, cambio de contraseña). Gestión de Viajes del Chofer (publicación por radio 1-5km, aceptación, ciclo de vida completo). GPS en tiempo real desde la app del chofer vía WebSocket. Contratos editables con horarios flexibles y extensión.

---

## ALTA PRIORIDAD

_(vacio)_

---

## MEDIA PRIORIDAD

### apiClient.duplicado_legacy_modular

**Titulo:** Dos `apiClient` conviviendo (legacy vs modular)

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

### F6 — `auth.codigo_metadatos` es tabla separada

El INSERT en `codigo_verificacion` solo no alcanza. Documentar en flujo del propietario.

### J15 — No hay deteccion de viaje activo al abrir la app

**Estado:** Implementado en R21 (endpoint `GET /api/viajes/activo` + `useEffect` en `HomeScreen`), pero **revertido temporalmente** por conflicto con la serialización de `POST /api/viajes/calle`. **Pendiente de reintentar.**

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

### mapa.invertido_al_retomar_viaje

**Estado:** Deuda abierta. No saldada en R22.

**Sintoma:** Cuando el chofer cierra la app con un viaje en curso y la vuelve a abrir, el endpoint `GET /api/viajes/activo` detecta el viaje, pero el mapa estático se genera con las coordenadas invertidas (`origen_lat` = longitud, `origen_lng` = latitud). Google Directions devuelve `ZERO_RESULTS` y el mapa queda en blanco. El viaje se crea, finaliza y registra correctamente en la base de datos (solo el mapa no se muestra).

**Accion futura:** Revisar `public_routes.py` y `routes_geocode.py` (backend) o el `MapPicker` (landing) para corregir la inversión de coordenadas.

### websocket.reconexion_bucle
**Síntoma:** El WebSocket del chofer se reconecta cada ~15-20s con código 1000 (cierre normal) o 1006 (abnormal). El servicio `websocketService` reconecta automáticamente, pero el ciclo es molesto.
**Impacto:** Bajo. El GPS se envía y la app sigue funcionando.
**Acción futura:** Investigar por qué el frontend cierra la conexión (posible `useEffect` que dispara `desconectar/conectar`).
**Ref:** `services/websocket.service.ts`, `HomeScreen.tsx`.

### mapa.lat_lng_invertidos_landing
**Síntoma:** El mapa estático en la landing muestra "No se encontró una ruta" porque el backend envía `origen_lat` y `origen_lng` invertidos al endpoint `/api/viajes/mapa-estatico`.
**Impacto:** Cosmético. No bloquea el flujo del chofer ni del pasajero.
**Acción futura:** Revisar `public_routes.py` y `routes_geocode.py` (backend) o el `MapPicker` (landing).

### barrido.duracion_corta
**Síntoma:** El barrido progresivo de viajes dura solo 40s (10s × 4 radios: 1km, 2km, 3km, 5km). Si el chofer no está conectado en ese momento, el viaje queda huérfano en `pendiente`.
**Impacto:** Medio. En producción, extender el barrido o agregar un job de limpieza.
**Acción futura:** Extender a 2-3 minutos, o job que cancele viajes pendientes huérfanos después de X minutos.
**Ref:** `app/routers/viajes/public_routes.py` (función `publicar_viaje_progresivo`).

### viaje.distancia_tiempo_websocket
**Síntoma:** En `ViajeDetalleScreen`, "DISTANCIA" y "TIEMPO" aparecen como `—` porque el backend no envía `distancia_metros` ni `tiempo_estimado_segundos` en el payload del WebSocket (`nuevo_viaje`).
**Impacto:** Cosmético.
**Acción futura:** Agregar esos campos al `viaje_data` en `public_routes.py`.
**Ref:** `app/routers/viajes/public_routes.py`, `types/viaje.types.ts`.

### token.dashboard.expirado
**Síntoma:** El dashboard del propietario muestra `Token expirado` cada ~30 minutos y se re-loguea solo.
**Impacto:** Bajo.
**Acción futura:** Revisar `ACCESS_TOKEN_EXPIRE_MINUTES` en `app/core/security.py` o el interceptor de refresh del dashboard.

---

## BAJA PRIORIDAD

### Backend heredadas
- **A2** — Schemas legacy snake_case mezclados en viajes/schemas.py.

### Frontend
- **D2** — tsconfig.json con ignoreDeprecations "6.0".

### Endpoints faltantes
- **F4** — /cobro-qr, webhooks de pasarela.

### Proceso, encoding, metadata
- **G28** — Posible race en rotacion de logs con --reload.
- **G29** — Consola PowerShell 5.1 con mojibake en logs.
- **G42** — Duplicacion de calculo de precio entre calcular_costo y solicitar_viaje_calle.
- **G54** — Landing usa Haversine en lugar de Directions.
- **G55** — Landing resuelve tenant con SELECT LIMIT 1 sin ORDER BY.
- **G73** — ~29 no-ASCII preexistentes en routes.py.

### Funcional heredada
- **H2** — Home muestra datos mock (resultadosAyer).

### ORM y funcional futuro
- **J1** — pasajero_id nullable en DB pero NOT NULL en ORM.
- **J2** — es_anonimo existe en DB pero no en ORM.
- **J4** — Extension de viaje.
- **J5** — "Siga ese auto".
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

### G67.frontend_chofer
Backend de G67 completo (2 endpoints + notificaciones), pero falta el frontend del chofer para que pueda usar la funcionalidad. **Pendiente para R23+ (app chofer).**

### G80
La app en el celular apunta a 192.168.1.14:8081 (Metro dev). Para pruebas en terreno: build preview o production apuntando al backend publico. **Bloqueada por deploy a produccion.**

---

## VIA MUERTA (NO HACER)

### metodo_pago.fk_catalogo
**Decision (R18):** NO HACER. Analisis empirico: 53 viajes, 100% dentro del vocabulario canonico. El refactor a FK rompe la API del frontend sin aportar valor claro.

### orm.alembic_check_ruidoso
**Accion:** NO usar `alembic check` como gate. Usar `diff.py`. **NUNCA correr `alembic revision --autogenerate`.**

---

## DEUDAS SALDADAS EN R21

- **`documentos.duplicados_en_db`** — Implementado UPSERT en `crear_documento_vehiculo`.
- **`storage.unificar_cloudinary_local`** — Todos los documentos usan Cloudinary.
- **`auth.uso_expo_router`** — Migración completa a React Navigation.
- **`G37` (Warning VirtualizedLists)** — El componente `GooglePlacesAutocomplete` fue reemplazado por autocompletado propio.
- **`F8` (app/_layout.tsx limpia taxip-turno)** — El entry point ahora es `index.js` + `App.tsx`.
- **`G77`, `G78`, `G79` (Deudas de expo-router)** — Obsoletas por migración a React Navigation.

---

## DEUDAS SALDADAS EN R22

### H3 — Home tenía "viajes" y "finanzas" deshabilitados
**Estado:** Saldada.
**Detalle:** Se habilitaron ambos módulos en `HomeScreen.tsx`:
- "Finanzas" → `disabled: false`.
- "Gestión de Viajes" → `disabled: !hayTurnoActivo` (solo requiere turno activo).

---

## RECUENTO

| Categoria | Cantidad |
|---|---|
| Alta prioridad | 0 |
| Media prioridad | ~18 |
| Baja prioridad | ~21 |
| Tocar Frontend | 1 (G67) |
| Expo-router / EAS | 0 |
| **TOTAL PENDIENTES** | **~40 items** |

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