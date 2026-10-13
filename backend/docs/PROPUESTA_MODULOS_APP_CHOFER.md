# PROPUESTA DE MODULOS APP CHOFER — TaxIP 2.0

**Ultima actualizacion:** 2026-10-13
**Estado:** Propuesta preliminar (borrador para revision)
**Alembic head:** m3_020
**Diff BD <-> ORM:** 0 items

---

## Contexto

Documento de planificacion de la **app chofer** (Expo SDK 57 +
React Native 0.86 + React 19 + expo-router 57.0.24).

**Basado en:**
- Backend actual (m3_020, alineado).
- Investigacion del codigo real (ver seccion "Hallazgos tecnicos previos").
- Estado de deuda pendiente (`docs/CONTEXTO_TAXIP_v1.md`).
- Contexto de negocio (`docs/RESUMEN_EJECUTIVO_2026-10-13.md`).

**Nota:** este documento corrige inconsistencias del borrador original
(Expo SDK 53 -> 57, endpoint `/api/usuarios/login` -> `/api/auth/login`,
etc.). Ver seccion "Correcciones respecto al borrador".

---

## Hallazgos tecnicos previos

Investigacion del codigo real antes de planificar los modulos.

### H1. La vinculacion chofer-vehiculo NO ocurre en la app del chofer

- La creacion de `fleet.contrato_vehiculo` ocurre en:
  - `app/routers/propietario/contratos.py:195` (dashboard propietario).
  - `app/routers/chofer_turnos.py:594` (durante check-in, excepcional).
  - `app/services/contrato_service.py:94` (logica de servicio).
- El propietario crea el contrato desde su dashboard.
- El chofer aprobado **espera a que un propietario lo vincule**.
- El QR (`fleet.contrato_qr`) es **operativo** (para iniciar turno), no
  para vinculacion inicial.

**Implicancia para el modulo 1:** el wizard de registro **NO debe
intentar vincular vehiculo**. La vinculacion es posterior, desde el
dashboard del propietario.

### H2. Estado de aprobacion vive en `fleet.chofer_vehiculo`

- Campo: `estado_aprobacion` (default `pendiente`).
- Valores: `pendiente` -> `completo` (docs subidos) -> `aprobado` /
  `rechazado`.
- **NO vive en `auth.usuario`** (como proponia el borrador original).

**Implicancia para el modulo 1:** el bloqueo post-registro depende de
`fleet.chofer_vehiculo.estado_aprobacion`, no de `auth.usuario`.

### H3. Storage de documentos: hoy en disco local

- `app/services/storage.py` guarda en `./uploads/` (disco local).
- Tiene `TODO: Implement S3 or Cloudinary` (no implementado).
- El borrador original proponia subida directa a Cloudinary desde la app.

**Implicancia para el modulo 1:** hay que decidir:
- **Opcion A:** implementar Cloudinary en `storage_service` (backend
  maneja la subida).
- **Opcion B:** crear endpoint de firma (`/api/cloudinary/signature`) y
  la app sube directo.

**Recomendacion:** Opcion B (la app sube directo, backend solo firma).
Menos carga en el backend.

### H4. El `control_base_id` del chofer

- El registro de chofer asigna `control_base_id` en `auth.usuario` y
  `fleet.chofer_vehiculo`.
- El flujo usa un **codigo OTP** que incluye el tenant (linea 191-206 de
  `app/routers/chofer_registro.py`).

**Implicancia para el modulo 1:** el wizard debe pedir el **codigo OTP**
al chofer para vincularlo al tenant correcto.

### H5. El caso "propietario-chofer" ya existe parcialmente

- `auth.py:150-351`: cuando un propietario se registra con
  `registrar_como_conductor=True`, se crea un `usuario_rol` de tipo
  chofer.
- **NO se crea `fleet.chofer_vehiculo`**.
- **NO se completa el wizard de documentos**.

**Implicancia para el modulo 1:** el propietario-chofer **necesita
completar el wizard de documentos** para ser aprobado como chofer. El
`usuario_rol` no alcanza.

---

## Modulos

### Modulo 1: Fundacion y Autenticacion

**Objetivo:** setup del proyecto, sistema de auth completo y wizard de
registro de chofer.

**Funcionalidades incluidas:**

- Setup Expo SDK 57+ con TypeScript, Expo Router, Zustand, Axios, React
  Native Paper.
- Configuracion de variables de entorno (`.env`).
- Cliente HTTP con interceptores JWT (access + refresh token).
- Store global de autenticacion (Zustand + persistencia AsyncStorage).
- Login (`POST /api/auth/login`) con deteccion de rol.
- Wizard de registro de 4 pasos:
  - **Paso 1:** Datos de cuenta (validacion con Zod) + **codigo OTP**
    del tenant.
  - **Paso 2:** Datos del vehiculo (patente auto-mayusculas) — *opcional,
    puede quedar NULL si el chofer espera vinculacion*.
  - **Paso 3:** Carga documental (camara/galeria -> Cloudinary con firma
    -> envio de URLs al backend).
  - **Paso 4:** Pantalla de bloqueo con polling de
    `GET /api/chofer/estado-aprobacion`.
- Recuperacion de contrasena.
- Pantalla de bloqueo post-registro: modo kiosk hasta aprobacion
  municipal.

**Entregable:** app instalable que permite registrarse, subir documentos
y quedar en espera de aprobacion.

**Pendiente de decision:**
- Cloudinary: opcion A o B (ver H3).
- El paso 2 (vehiculo): obligatorio u opcional.

---

### Modulo 2: Turno y Estado Laboral

**Objetivo:** gestion completa del turno del chofer, requisito para todo
lo demas.

**Funcionalidades incluidas:**

- Home del chofer con mapa (ubicacion actual).
- Toggle de estado laboral: `fuera_servicio` -> `libre` (solo si hay
  turno activo).
- **Check-in de turno:**
  - Ingreso de **codigo de validacion** (NO escaneo QR — cambio respecto
    al borrador original).
  - Ingreso de km inicial.
  - Ingreso de nivel de combustible.
  - `POST /api/chofer/turno/check-in` para crear turno.
- **Check-out de turno:**
  - Ingreso de km final.
  - Ingreso de combustible final.
  - Ingreso de monto de ticketera (efectivo recaudado en calle).
  - Confirmacion de cierre y visualizacion de liquidacion.
- **Validacion:** no permite operar (recibir viajes, registrar gastos)
  sin turno activo.
- **Forzar cierre (R17 - G67):** si hay viajes huerfanos, permite
  cerrarlos uno por uno con motivo.

**Entregable:** chofer puede iniciar y cerrar turno, y el sistema
bloquea operaciones si no hay turno activo.

**Endpoints backend disponibles:**
- `POST /api/chofer/turno/check-in`
- `POST /api/chofer/turno/check-out`
- `GET /api/chofer/turno/estado`
- `GET /api/chofer/turno/activo`
- `GET /api/chofer/turno/viajes-huerfanos` (R17)
- `POST /api/chofer/turno/viajes-huerfanos/{id}/cerrar` (R17)

---

### Modulo 3: Viajes desde la Plataforma (App / QR / Empresa)

**Objetivo:** recibir, aceptar y completar viajes que vienen de otros
canales.

**Funcionalidades incluidas:**

- **WebSocket:** conexion persistente a `ws://.../ws/{user_id}`.
- **Pantalla de solicitudes cercanas:** lista en tiempo real de viajes
  entrantes.
- **Aceptar solicitud:** `POST /api/viajes/{id}/aceptar`.
- **Pantalla de viaje en curso (tracking chofer):**
  - Mapa con ruta al destino del pasajero.
  - Datos del pasajero (nombre, telefono).
  - Boton "Iniciar viaje" (pasajero a bordo).
  - Boton "Finalizar viaje".
  - Boton "Cancelar viaje" (con motivo).
  - Boton "Navegar con Google Maps / Waze".
- **Actualizacion GPS periodica:** envio de ubicacion al backend cada X
  segundos.
- **Boton de panico:** confirmacion + envio WS de alerta.

**Entregable:** chofer puede operar el ciclo completo de un viaje
solicitado por pasajero/empresa/QR.

**Endpoints backend disponibles:**
- `POST /api/viajes/{id}/aceptar`
- `POST /api/viajes/{id}/llegar`
- `POST /api/viajes/{id}/iniciar`
- `POST /api/viajes/{id}/finalizar`
- `POST /api/viajes/{id}/cancelar`
- `POST /api/viajes/{id}/rechazar`

---

### Modulo 4: Viaje de Calle (Via Publica)

**Objetivo:** permitir al chofer registrar y cobrar viajes tomados en la
calle.

**Funcionalidades incluidas:**

- **Pantalla "Nuevo viaje de calle":**
  - Origen: posicion GPS actual (automatico, no editable).
  - Destino: input con autocompletado Google Places.
  - Selector de metodo de pago: `efectivo` (default), `qr`,
    `transferencia` (vocabulario canonico Momento 1).
- **Calculo de estimado:** `POST /api/viajes/solicitar-viaje-calle` (o
  endpoint especifico para chofer).
- **Confirmacion:** muestra distancia, tiempo y monto estimado.
- **Inicio de viaje:** crea viaje manual en backend con
  `origen_tipo = 'via_publica'`.
- **Tracking del viaje:** igual que el modulo 3, pero sin datos de
  pasajero.
- **Finalizacion:**
  - Si `efectivo`: registra cobro en mano, suma a ticketera del turno.
  - Si `qr` / `transferencia`: backend genera QR de cobro -> app lo
    muestra en pantalla fullscreen para que el pasajero escanee.
- **Registro en liquidacion:** el viaje impacta automaticamente en el
  turno activo.

**Entregable:** chofer puede tomar un pasajero de la calle, calcular
tarifa, ejecutar el viaje y cobrar (efectivo o QR electronico).

**Anexo:** ver `docs/ANEXO_MEDIOS_PAGO_ARGENTINA.md` para el analisis de
preautorizaciones y cobros electronicos.

---

### Modulo 5: Gastos de Turno

**Objetivo:** registrar gastos operativos con foto obligatoria.

**Funcionalidades incluidas:**

- **Pantalla "Nuevo gasto":**
  - Selector de tipo de gasto (catalogo cerrado: `COMBUSTIBLE`, `PEAJE`,
    `LAVADO`, `ESTACIONAMIENTO`, `MULTA`, `OTRO`).
  - Monto (ARS/USD).
  - Descripcion opcional.
  - Fecha del gasto (default: hoy).
  - Km del vehiculo (opcional).
  - Foto del comprobante: camara o galeria, subida directa a Cloudinary.
- **Validaciones:**
  - Solo si hay turno activo.
  - Foto obligatoria (sin foto no se envia).
  - Monto > 0.
  - Fecha no futura.
- **Listado "Mis gastos":**
  - Filtros por estado: `PENDIENTE`, `APROBADO`, `RECHAZADO`.
  - Si es rechazado, muestra motivo completo.
  - No permite editar gastos enviados.

**Entregable:** chofer puede registrar gastos con foto, ver historial y
estados de aprobacion.

**Endpoints backend disponibles:**
- `POST /api/chofer/turno/gastos` (a verificar)

---

### Modulo 6: Perfil y Utils

**Objetivo:** pantallas secundarias y optimizaciones finales.

**Funcionalidades incluidas:**

- **Perfil del chofer:**
  - Foto de perfil (camara/galeria -> Cloudinary).
  - Datos personales editables.
  - Datos del vehiculo (solo lectura).
  - Calificacion promedio.
- **Historial de viajes:**
  - Lista de viajes completados (fecha, origen, destino, monto, metodo
    de pago).
  - Detalle de viaje individual.
- **Ingresos:**
  - Resumen de hoy / semana / mes.
  - Desglose: viajes app + viajes calle + ticketera.
- **Configuracion:**
  - Cambiar contrasena.
  - Notificaciones push (Expo Notifications).
  - Cerrar sesion.
- **Emergencias:**
  - Boton de panico accesible desde cualquier pantalla (overlay).
  - Confirmacion antes de enviar alerta.
- **Optimizaciones:**
  - Manejo de errores global (toasts).
  - Skeleton loaders.
  - Pull-to-refresh en listas.
  - Deep linking (para compartir viaje).
- **Build configurado para Android (APK/AAB).**

**Entregable:** app completa, produccion-ready, con todas las pantallas
secundarias y optimizaciones.

---

## Roadmap (orden de dependencias)

Modulo 1 (Auth + Registro)
|
v
Modulo 2 (Turno y Estado Laboral)
|
+-----> Modulo 3 (Viajes desde Plataforma)
|
+-----> Modulo 4 (Viaje de Calle)
|
+-----> Modulo 5 (Gastos de Turno)
|
v
Modulo 6 (Perfil y Utils)

**Notas:**
- Modulo 1: base, sin el no hay usuario.
- Modulo 2: sin turno activo no se opera.
- Modulos 3 y 4: paralelos (viajes de plataforma vs. calle).
- Modulo 5: depende de turno activo.
- Modulo 6: ultimo, consolida todo.

---

## Correcciones respecto al borrador original

| Aspecto | Borrador original | Correccion |
|---------|-------------------|------------|
| Expo SDK | 53+ | **57.0.24** |
| Endpoint login | `/api/usuarios/login` | **`/api/auth/login`** |
| Check-in | Escaneo QR | **Codigo de validacion** |
| Estado aprobacion | En `auth.usuario` | **En `fleet.chofer_vehiculo`** |
| Selfie | `selfie_url` (nuevo) | **`foto_perfil_url`** (existente) |
| Ubicacion | "Agregar campos" | **Ya existe en `perfil_general`** |
| Vinculacion | "Chofer escanea QR" | **Desde dashboard del propietario** |
| Control base | "Elige ciudad" | **Codigo OTP del tenant** |
| Cloudinary | "Subida directa" | **A decidir (opcion A o B)** |

---

## Anexos

- **Medios de pago Argentina:** `docs/ANEXO_MEDIOS_PAGO_ARGENTINA.md`

---

## Pendientes / decisiones abiertas

- **Cloudinary:** opcion A (backend sube) u opcion B (endpoint de firma).
- **Paso 2 (vehiculo):** obligatorio u opcional en el wizard.
- **Vinculacion chofer-vehiculo:** documentar el flujo exacto para la app.
- **Modo kiosk:** especificar implementacion (bloqueo de navegacion).
- **Notificaciones push:** implementar (deuda pendiente).

---

**FIN DEL DOCUMENTO**