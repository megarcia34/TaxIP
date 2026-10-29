# CONTEXTO TAXIP 2.0 — Estado y Deuda Pendiente

**Ultima actualizacion:** 2026-10-29 (post R23.1)
**Alembic head:** m3_025
**Diff BD <-> ORM:** 1 item (indice preexistente en payment.py — deuda aceptada)
**Tag activo:** ronda23.1-fix-coordenadas-websocket
**Repo:** github.com/megarcia34/TaxIP (main)

**Reglas de alineacion BD <-> ORM:** ver `docs/REGLAS_ALINEACION_BD_ORM.md`.
**Historico de rondas cerradas:** ver `docs/HISTORICO_CERRADAS.md`.
**Contexto de negocio:** ver `docs/RESUMEN_EJECUTIVO_2026-10-13.md` (pendiente actualizar a R21).
**Decisiones tecnicas ORM:** ver `docs/orm_sync/orm_decisiones.md`.

---

## Resumen ejecutivo

- **Alineacion estructural BD <-> ORM:** 1 item pendiente (preexistente, deuda aceptada).
- **Deuda alta prioridad:** 0 items.
- **Deuda media prioridad:** ~13 items.
- **Deuda baja prioridad:** ~21 items.
- **Tocar Frontend:** 1 item (G80).
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
- **R23:** **Fix de mapas y coordenadas.** Corrección transversal de `ST_X`/`ST_Y` invertidos en 5 archivos del backend (`public_routes.py`, `routes.py`, `routes_dashboard.py`, `routes_historial.py`, `services.py`). Fix de sintaxis SQL en `SELECT` (comas sobrantes). Verificación exitosa de reconexión WebSocket (CloseCode 1006). Flujo Landing -> Chofer -> GPS verificado.
- **R23.1:** **Fix de WebSocket, Viajes Huérfanos y UX.** Montaje global del hook `useWebSocket` en `App.tsx` para evitar desconexiones. Implementación del `ModalViajesHuerfanos` para cierre de turnos bloqueados. Envío de `distancia_metros` y `tiempo_estimado_segundos` reales desde la landing al WebSocket. Nuevo job en el scheduler que cancela viajes pendientes huérfanos a los 5 minutos con mensaje UX personalizado.

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

### token.dashboard.expirado
**Síntoma:** El dashboard del propietario muestra `Token expirado` cada ~30 minutos y se re-loguea solo.
**Impacto:** Bajo.
**Acción futura:** Revisar `ACCESS_TOKEN_EXPIRE_MINUTES` en `app/core/security.py` o el interceptor de refresh del dashboard.

### turno.huerfano_turno_anterior
**Síntoma:** Si un viaje queda en estado `aceptado` o `en_curso` de un turno que se cerró (por error o corte), el nuevo turno no puede cerrarlo forzadamente porque el `turno_id` no coincide. El backend devuelve "El viaje no pertenece a este turno".
**Acción futura:** Permitir cerrar viajes de turnos anteriores o reasignarlos automáticamente al turno activo.

### dashboard.estado_inconsistente
**Síntoma:** El dashboard del propietario muestra contratos "Finalizados" pero los turnos en `fleet.turno_chofer` siguen `ACTIVO`, dejando vehículos bloqueados.
**Acción futura:** Sincronizar el cierre de contratos con el cierre de turnos en el backend.

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

## DEUDAS SALDADAS EN R23

- **`mapa.lat_lng_invertidos_landing`** — Saldada. Se corrigió la inversión de `ST_X`/`ST_Y` en `public_routes.py`, `routes_dashboard.py`, `routes_historial.py` y `services.py`. La landing ahora calcula la ruta correctamente.
- **`mapa.invertido_al_retomar_viaje`** — Saldada. Corregido en `routes.py` (endpoint `/api/viajes/activo`). La app chofer ahora muestra el mapa correcto al retomar un viaje.
- **`websocket.reconexion_bucle`** — Saldada (verificada). Se forzó un cierre abrupto (CloseCode 1006) y el `websocketService` de la app chofer se reconectó automáticamente sin intervención. El backend limpió la conexión caída correctamente.
- **Bug 2 (GPS no envía coordenadas)** — Descartado. La migración a React Navigation (R21) ya había eliminado el `_layout.tsx` que borraba el AsyncStorage. Los logs confirman que el GPS envía coordenadas cada 15 segundos sin problemas.

---

## DEUDAS SALDADAS EN R23.1

- **`viaje.distancia_tiempo_websocket`** — Saldada. El backend ahora envía `distancia_metros` y `tiempo_estimado_segundos` en el payload del WebSocket y los guarda en la DB. La landing los calcula con Google Maps y los envía.
- **`barrido.duracion_corta`** — Saldada. Se agregó un job en el scheduler que cancela viajes en estado `pendiente` después de 5 minutos sin chofer asignado. La landing muestra el mensaje "No hay móviles en la zona".
- **`G67.frontend_chofer`** — Saldada. Se creó el `ModalViajesHuerfanos` y se integró en `TurnosScreen` para forzar el cierre de viajes colgados.
- **`websocket.reconexion_bucle` (fix global)** — Saldada. El hook `useWebSocket` ahora se monta globalmente en `App.tsx`, manteniendo la conexión estable.
- **`turno.mensaje_error_generico`** — Saldada. El backend ahora devuelve un mensaje claro indicando qué chofer tiene el vehículo ocupado y desde cuándo.

---

## DEUDAS NUEVAS (R24)

### viaje.finalizar_antes_de_tiempo
**Síntoma:** En la pantalla de viaje en curso, el chofer no tiene un botón para finalizar el viaje antes de llegar al destino (ej. si el pasajero se baja antes).
**Acción futura:** Agregar un botón de "Finalizar viaje aquí" que calcule el precio hasta la ubicación actual o permita ingresar un monto manual.

*(Las deudas `turno.huerfano_turno_anterior` y `dashboard.estado_inconsistente` ya fueron agregadas a MEDIA PRIORIDAD).*

---

## RECUENTO

| Categoria | Cantidad |
|---|---|
| Alta prioridad | 0 |
| Media prioridad | ~16 |
| Baja prioridad | ~21 |
| Tocar Frontend | 1 (G80) |
| Expo-router / EAS | 0 |
| **TOTAL PENDIENTES** | **~38 items** |

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