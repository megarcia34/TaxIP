# Decisiones de reconciliacion ORM - DB

**Iniciado:** 2026-09-30 (Ronda 5, Fase 0)
**Head Alembic:** m3_010
**Commit baseline:** 4c77f3a
**Tag baseline:** ronda5-baseline-pre
**Backup DB:** docs/backups/taxip_db_2026-09-30.dump (546 KB)
**Responsable:** megarcia34
**Ultima actualizacion:** 2026-10-04 (Ronda 7, Fase 4b, Paso 7)

## Proposito

Registrar cada decision tomada durante la reconciliacion del ORM con la DB.
Cada entrada debe incluir:

- Item (schema.tabla.columna o schema.tabla)
- Clasificacion (orm_falta, orm_sobra, tipo_desalineado, etc.)
- Decision tomada
- Justificacion
- Fecha

---

## Contexto del entorno (Fase 0)

### Entorno real verificado

- **Python:** 3.12.10 (el traspaso decia 3.11, discrepancia documental)
- **PostgreSQL server:** 17.0 on x86_64-windows
- **PostGIS:** 3.6 USE_GEOS=1 USE_PROJ=1 USE_STATS=1
- **pg_dump / psql:** 17.0
- **Alembic head:** m3_010
- **Git root:** D:/aTaxip
- **Branch:** main
- **Commit:** 4c77f3a

### Inventario de schemas (12) y tablas base (90)

| Schema | Tablas |
|---|---|
| audit | 4 |
| auth | 16 |
| comunicacion | 3 |
| corporate | 4 |
| fleet | 31 |
| geo | 3 |
| notification | 1 |
| payment | 9 |
| public | 4 |
| rentabilidad | 3 |
| tenant | 4 |
| trip | 8 |

### Inventario detallado de public (4 tablas)

- alembic_version (de Alembic)
- comercio (usada por viaje_solicitado.comercio_id sin schema)
- escaneo_qr (nueva, no estaba en el mapa original)
- spatial_ref_sys (de PostGIS)

### Inventario detallado de schemas nuevos (no estaban en el mapa original)

- geo: pais, provincia, ciudad
- notification: notificacion
- audit: alerta_desvio, alertas_vencimiento, log_acciones, log_gps
- comunicacion: conversacion, email_enviado, mensaje
- corporate: cuenta_corriente, factura_corporativa, movimiento_cuenta, pago_corporativo
- rentabilidad: analisis_medios_pago, rentabilidad_diaria_vehiculo, rentabilidad_mensual_vehiculo

---

## Decisiones tomadas (Fase 0)

### D-001: Head de Alembic

- **Item:** migrations
- **Clasificacion:** n/a
- **Decision:** head actual = m3_010
- **Justificacion:** alembic current y alembic heads confirman m3_010 (head). Git tiene el archivo m3_010_metodo_pago_canonico.py. Git y DB estan sincronizados.
- **Fecha:** 2026-09-30

### D-002: Python version

- **Item:** entorno
- **Clasificacion:** n/a (documental)
- **Decision:** Python real es 3.12.10, no 3.11 como decia el traspaso
- **Justificacion:** python --version confirma 3.12.10 en el venv
- **Accion:** actualizar documentacion al cierre de Ronda 5
- **Fecha:** 2026-09-30

### D-003: Tablas backup huerfanas

- **Item:** auth.*_backup_*
- **Clasificacion:** basura (ya eliminada)
- **Decision:** ya dropeadas en Ronda 4. No aparecen en inventario actual.
- **Justificacion:** consulta information_schema.tables WHERE table_name LIKE '%backup%' no las encuentra
- **Fecha:** 2026-09-30

### D-004: trip.reserva

- **Item:** trip.reserva
- **Clasificacion:** orm_sobra - Tier 4 (muerte) -> RECLASIFICADO
- **Decision original:** borrar el modelo Reserva del ORM.
- **Decision actualizada (2026-10-02):** NO borrar el modelo. Postergar a
  Fase 4d. El modulo de reservas corporativas esta previsto para uso
  posterior. Ver deuda `orm.reserva_modulo_activo`.
- **Justificacion original:** la tabla no existe en DB. A1 de la deuda
  confirma que es modelo huerfano. El modulo corporativo no la usa.
- **Justificacion actualizada:** verificado en Fase 4a (Ronda 6) que el
  modulo SI esta referenciado activamente en 6 lugares (trip_service.py
  x2, reservas.py, operativo.py, main.py, reserva_schemas.py). Borrar
  el modelo rompe el backend. Requiere decision funcional previa.
- **Accion:** documentar en DEUDA_TECNICA_ACTUAL.md como
  `orm.reserva_modulo_activo`. Resolver en Fase 4d o ronda especifica.
- **Fecha:** 2026-09-30 (actualizado 2026-10-02)

### D-007: tenant.control_base.latitud/longitud

- **Item:** tenant.control_base.latitud, tenant.control_base.longitud
- **Clasificacion:** tipo_desalineado + requiere_decision + orm_mal_db_bien
- **Decision:** el ORM debe cambiar de String(50) a Numeric(10,8) (latitud) y Numeric(11,8) (longitud)
- **Justificacion:** la DB tiene numeric(10,8) y numeric(11,8) que es lo correcto para coordenadas. El ORM con String(50) es un error grave. Excepcion explicita a la regla de oro.
- **Fecha:** 2026-09-30

### D-008: fleet.* timestamps naive

- **Item:** fleet.<tabla>.<columna>
- **Clasificacion:** tipo_desalineado + requiere_decision (arquitectura)
- **Decision:** PENDIENTE (ver D-012 para la resolucion acotada de los 19 items
  del modulo neumatico_*). D-008 como estimacion de Fase 0 decia 70 columnas
  en 30 tablas; el diff real de Fase 1 identifico 19 columnas desalineadas
  en 7 tablas neumatico_*.
- **Justificacion:** Fase 0 estimo 70 columnas. Fase 1 las acoto a 19 (las
  unicas con razon_decision=timestamp_naive_vs_tz). El resto de las columnas
  timestamp de fleet (68/68 segun conteo empirico) ya estan coherentes
  (naive en ambos lados).
- **Fecha:** 2026-09-30 (actualizado 2026-10-01)

### D-009: public.comercio y orm_viaje.fk_comercio_schema

- **Item:** trip.viaje_solicitado.comercio_id
- **Clasificacion:** constraint_desalineada + requiere_decision
- **Decision:** PENDIENTE. La FK apunta a comercio(id) sin schema. public.comercio existe. Hay que decidir si: (a) la FK se especifica como public.comercio(id), o (b) comercio se mueve a otro schema.
- **Justificacion:** item orm_viaje.fk_comercio_schema de la deuda. La FK sin schema depende de search_path.
- **Fecha:** 2026-09-30

### D-010: Ciclo de FKs auth.usuario <-> tenant.control_base

- **Item:** auth.usuario, tenant.control_base
- **Clasificacion:** constraint_desalineada + item nuevo
- **Decision:** PENDIENTE. Hay un ciclo de FKs mutuas que SQLAlchemy no puede resolver. Requiere use_alter=True en las FKs o deferrable.
- **Justificacion:** warning explicito de Alembic: "Cannot correctly sort tables; there are unresolvable cycles between tables auth.usuario, tenant.control_base"
- **Accion:** agregar a DEUDA_TECNICA_ACTUAL.md
- **Fecha:** 2026-09-30

### D-011: Esquema de trabajo Fase 1

- **Item:** scripts/orm_sync, docs/orm_sync
- **Clasificacion:** n/a
- **Decision:** crear 3 scripts (introspect_db.py, introspect_orm.py, diff.py) + archivos de salida JSON + reporte markdown
- **Justificacion:** plan de Fase 1 del traspaso
- **Fecha:** 2026-09-30

---

## Decisiones tomadas en Fase 2 (Ronda 6, Sesion 1)

### D-005: Vocabulario de metodo_pago (grupo D)

- **Item:** trip.viaje_solicitado.metodo_pago, fleet.ingreso_turno.medio_pago,
  payment.metodo_pago
- **Clasificacion:** requiere_decision (negocio) - Tier 1
- **Decision (Fase 2):** fijar como canonico el vocabulario del CHECK
  actual de trip.viaje_solicitado.metodo_pago:
  efectivo | tarjeta_debito | qr | transferencia.
  NO migrar DB en Fase 2. NO tocar CHECK. NO unificar con catalogo.
- **Justificacion:**
  - Hay 5 vocabularios en juego (ver detalle abajo). Unificarlos es
    refactor grande que no cabe en Fase 2.
  - El CHECK de trip.viaje_solicitado es el unico enforceado. Ya cerro
    parcialmente B7 en Ronda 4.
  - El frontend (E2 de la deuda) esta limitado a 4 valores. Ampliar el
    CHECK sin tocar frontend rompe E2.
  - payment.metodo_pago es catalogo sucio (2 duplicados, 1 sinonimo,
    1 pasarela mezclada). Limpiarlo es deuda aparte.
  - Regla de oro del traspaso: la DB es la fuente de verdad. El CHECK
    actual define el vocabulario de facto para viajes.
- **Vocabularios documentados (estado actual):**
  1. trip.viaje_solicitado.metodo_pago (CHECK):
     efectivo | tarjeta_debito | qr | transferencia
  2. fleet.ingreso_turno.medio_pago (comment DB, sin CHECK):
     efectivo | debito | credito | qr | transferencia | billetera
  3. fleet.ingreso_turno.medio_pago (datos reales):
     debito (16 filas), efectivo (57 filas)
  4. payment.metodo_pago (catalogo, 12 filas con duplicados):
     billetera, mercadopago x2, wallet, tarjeta_debito,
     tarjeta_credito, transferencia, qr, efectivo x2, debito, credito
  5. schemas/recaudacion_schemas.py:22 (sin CHECK):
     efectivo | debito | credito | qr | transferencia | billetera
- **Accion en Fase 4 (deuda nueva, ver seccion Deudas Fase 2):**
  - metodo_pago.catalogo_sucio
  - metodo_pago.fk_catalogo
  - metodo_pago.ingreso_turno
  - metodo_pago.frontend_e2
- **Migracion DB en Fase 2:** ninguna.
- **Archivos ORM a tocar en Fase 4:** app/models/fleet.py (comment de
  IngresoTurno.medio_pago).
- **Fecha:** 2026-09-30 (actualizado 2026-10-01)
- **Estado:** APROBADA (con alcance acotado).

### D-006: auth.codigo_verificacion + auth.codigo_metadatos (J9)

- **Item:** auth.codigo_verificacion, auth.codigo_metadatos
- **Clasificacion:** orm_falta - Tier 2
- **Decision (Fase 2):** declarar AMBAS tablas en el ORM. NO unificar.
  J9 es un falso positivo documental.
- **Justificacion:**
  - J9 original decia "dos fuentes de verdad para codigos de turno" y
    "el handler validar_codigo_turno lee de codigo_metadatos".
  - Verificado en Fase 2: J9 es un FALSO POSITIVO documental.
  - FK real: codigo_metadatos.codigo_id -> codigo_verificacion.id
    (ON DELETE CASCADE). codigo_metadatos es tabla SATELITE, no
    fuente alternativa.
  - Handler validar_codigo_turno (app/routers/chofer_turnos.py:233)
    lee de codigo_verificacion (linea 282), NO de codigo_metadatos.
  - El dominio de codigo_metadatos es contrato/vehiculo/propietario
    (FKs a fleet.contrato_vehiculo, fleet.vehiculo, auth.usuario).
    Es metadata ESTRUCTURADA, no jsonb generico.
  - codigo_verificacion tiene su propio campo metadata (jsonb),
    ortogonal a codigo_metadatos. Conviven sin conflicto.
  - No hay ambiguedad funcional que resolver. No hay que unificar.
- **Columnas codigo_verificacion (9):** id, usuario_id, codigo, tipo,
  usado, intentos, creado_en, expira_en, metadata.
- **Columnas codigo_metadatos (6):** id, codigo_id, contrato_id,
  vehiculo_id, propietario_id, created_at.
- **Filas actuales:** codigo_verificacion=29, codigo_metadatos=11.
- **FKs de codigo_metadatos:**
  - codigo_id -> auth.codigo_verificacion(id) ON DELETE CASCADE
  - contrato_id -> fleet.contrato_vehiculo(id) ON DELETE CASCADE
  - propietario_id -> auth.usuario(id) ON DELETE CASCADE
  - vehiculo_id -> fleet.vehiculo(id) ON DELETE CASCADE
- **Migracion DB:** ninguna.
- **Archivos ORM a tocar en Fase 4:** app/models/auth.py (agregar ambas clases).
- **Accion adicional:** marcar J9 en DEUDA_TECNICA_ACTUAL.md como FALSO
  POSITIVO (resuelto).
- **Fecha:** 2026-10-01 (actualizado 2026-10-04)
- **Estado:** CERRADA 2026-10-04 (Fase 4b, Paso 7). 19 timestamps migrados
  en 7 clases Neumatico* de `app/models/fleet.py`. Commits d00dec7..56570fa.
  Diff: 906 -> 887.

### D-012: Timestamps naive en fleet.neumatico_* (grupo A, 19 items)

- **Item:** fleet.neumatico_*.<columna> (19 columnas en 7 tablas)
- **Clasificacion:** tipo_desalineado + timestamp_naive_vs_tz - Tier 2
- **Decision:** ORM se adapta a DB (opcion a). Cambiar DateTime(timezone=True)
  a DateTime(timezone=False). Reemplazar default=datetime.now por
  server_default=func.now() (quitar default de Python).
- **Justificacion:**
  - La DB tiene timestamp without time zone con default now().
  - El ORM declara DateTime(timezone=True) con default datetime.now (naive).
  - Incoherencia detectada: el default Python es naive pero la columna ORM
    es tz-aware. PostgreSQL interpreta el naive con el timezone del server.
  - Verificado empiricamente: 68/68 columnas timestamp en fleet son
    timestamp without time zone. La convencion del schema es naive.
  - Volumen de datos: 41 filas en total (todas simulacion de prueba,
    modulo en desarrollo). Migrar la DB a timestamptz no tiene justificacion.
  - Regla de oro del traspaso original: la DB es la fuente de verdad,
    el ORM se adapta.
  - Opcion (b) descartada: 41 filas no justifican migracion de schema;
    rompe coherencia de fleet; riesgo de interpretacion de zona.
  - Opcion (c) descartada: el bug del default sigue activo; costo de
    arreglar (a) es bajisimo (19 lineas en 1 archivo).
- **Items del diff:** D-0608, D-0610, D-0611, D-0631, D-0632, D-0649, D-0650,
  D-0665, D-0666, D-0667, D-0684, D-0696, D-0697, D-0698, D-0699, D-0719,
  D-0720, D-0721, D-0722.
- **Tablas afectadas:**
  - fleet.neumatico_historial_posicion (3): created_at, fecha_desmontaje, fecha_montaje
  - fleet.neumatico_imagen (2): created_at, fecha_subida
  - fleet.neumatico_medicion (2): created_at, fecha_medicion
  - fleet.neumatico_operacion (3): created_at, fecha_operacion, updated_at
  - fleet.neumatico_operacion_detalle (1): created_at
  - fleet.neumatico_sugerencia (4): created_at, fecha_atendida, fecha_generacion, updated_at
  - fleet.neumatico_vehiculo (4): created_at, fecha_alta, fecha_baja, updated_at
- **Datos afectados:** 41 filas (simulacion de prueba).
- **Migracion DB:** ninguna.
- **Archivos ORM a tocar en Fase 4:** app/models/fleet.py (modulo de neumaticos).
- **Fecha:** 2026-10-01
- **Estado:** APROBADA.

---

## Decisiones pendientes (se resolveran en Fase 4 o rondas siguientes)

- D-009: public.comercio FK (decision de schema).
- D-010: ciclo de FKs auth.usuario <-> tenant.control_base (decision tecnica).
- D-011: esquema de trabajo Fase 1 (cerrado en Ronda 5).

---

## Items nuevos detectados en Fase 0

- audit.alerta_desvio y audit.log_gps: tablas de auditoria GPS no documentadas
- public.escaneo_qr: tabla nueva en public
- geo.pais, geo.provincia, geo.ciudad: schema geo no documentado
- notification.notificacion: schema notification no documentado
- Ciclo de FKs auth.usuario <-> tenant.control_base
- comunicacion.email_enviado: tabla entera sin ORM

---

## Snapshot de referencia

- docs/orm_sync/alembic_check_baseline_2026-09-30.txt (849 KB, 2.611 lineas)
- docs/backups/taxip_db_2026-09-30.dump (546 KB)

---

## Hallazgos de Fase 1 - Sesion 1 (introspect_db.py)

### H-001: trip.viaje_solicitado tiene 66 columnas

- **Item:** trip.viaje_solicitado
- **Clasificacion:** orm_falta (masivo) - Tier 1
- **Descripcion:** la DB tiene 66 columnas. El ORM declara ~37 (29 faltantes). Confirmado con introspect_db.py.
- **Accion:** declarar las 29 faltantes en ORM (B5).
- **Fecha:** 2026-10-01

### H-002: trip.viaje_solicitado tiene 10 CHECK constraints

- **Item:** trip.viaje_solicitado.constraints.check
- **Clasificacion:** orm_falta - Tier 1
- **Descripcion:** 10 CHECK constraints en DB, 0 en ORM.
- **Lista:**
  - ck_viaje_solicitado_metodo_pago (efectivo, tarjeta_debito, qr, transferencia)
  - ck_viaje_solicitado_ck_viaje_calidad_min (regular, bueno, excelente)
  - ck_viaje_solicitado_ck_viaje_cc_obligatoria
  - ck_viaje_solicitado_ck_viaje_centro_costo_despacho
  - ck_viaje_solicitado_ck_viaje_estado_cobro (pendiente, cobrado, facturado, pagado)
  - ck_viaje_solicitado_ck_viaje_origen_tipo (plataforma, via_publica, qr_comercio, corporativo, despacho_manual)
  - ck_viaje_solicitado_ck_viaje_responsable_cobro (chofer, propietario, tenant, comercio, empresa)
  - ck_viaje_solicitado_ck_viaje_subestado_despacho (reservado, despachado, vehiculo_llego, pasajero_a_bordo, completado)
  - 63669_63825_1_not_null (autogenerado, renombrar)
  - 63669_63825_38_not_null (autogenerado, renombrar)
- **Accion:** declarar en ORM + renombrar los 2 autogenerados.
- **Fecha:** 2026-10-01

### H-003: Vocabularios de metodo_pago siguen divergentes

- **Item:** trip.viaje_solicitado.metodo_pago + fleet.ingreso_turno.medio_pago + payment.metodo_pago
- **Clasificacion:** requiere_decision (negocio) - Tier 1
- **Descripcion:** B7 cerro parcialmente, pero los vocabularios siguen divergentes:
  - CHECK en trip.viaje_solicitado.metodo_pago: efectivo, tarjeta_debito, qr, transferencia
  - Comment en fleet.ingreso_turno.medio_pago: efectivo, debito, credito, qr, transferencia, billetera
  - payment.metodo_pago (catalogo): duplicados (efectivo x2, mercadopago x2)
- **Accion:** definido en D-005 (Fase 2). Vocabulario canonico = CHECK actual.
- **Fecha:** 2026-10-01

### H-004: Constraints autogenerados con nombres numericos

- **Item:** trip.viaje_solicitado.constraints.check.63669_63825_*
- **Clasificacion:** constraint_desalineada - Tier 3
- **Descripcion:** 2 constraints tienen nombres autogenerados por Alembic con numeros. No descriptivos.
- **Accion:** renombrar en DB + ORM.
- **Fecha:** 2026-10-01

### H-005: Indices duplicados en trip.viaje_solicitado

- **Item:** idx_viaje_estado + ix_viaje_estado
- **Clasificacion:** indice_duplicado - Tier 3
- **Descripcion:** dos indices sobre la misma columna estado. Uno custom (idx_), uno autogenerado (ix_).
- **Accion:** eliminar uno. Decidir cual.
- **Fecha:** 2026-10-01

### H-006: public.comercio tiene 13 columnas

- **Item:** public.comercio
- **Clasificacion:** orm_falta - Tier 2
- **Descripcion:** 13 columnas: id, nombre, rubro, direccion, latitud, longitud, codigo_qr, email_contacto, telefono, activo, created_at, updated_at, control_base_id.
- **Accion:** declarar en ORM. Conecta con D-009 (FK sin schema).
- **Fecha:** 2026-10-01

### H-007: auth.codigo_verificacion tiene 9 columnas

- **Item:** auth.codigo_verificacion
- **Clasificacion:** orm_falta - Tier 2
- **Descripcion:** 9 columnas: id, usuario_id, codigo, tipo, usado, intentos, creado_en, expira_en, metadata.
- **Accion:** declarar en ORM. Conecta con D-006 (J9).
- **Fecha:** 2026-10-01

### H-008: trip.viaje_solicitado tiene 19 indices

- **Item:** trip.viaje_solicitado.indexes
- **Clasificacion:** indice_falta - Tier 1
- **Descripcion:** 19 indices en DB: 1 PK, 9 idx_ (custom), 9 ix_ (autogenerados), 1 gist (PostGIS).
- **Accion:** declarar los custom en ORM. Decidir sobre los autogenerados.
- **Fecha:** 2026-10-01

---

## Hallazgos de Fase 1 - Sesion 2 (introspect_orm.py)

### H-009: El ORM tiene 73 tablas, la DB tiene 90

- **Item:** Base.metadata vs DB
- **Clasificacion:** orm_falta (masivo) - Tier 2
- **Descripcion:** El ORM declara 73 tablas, la DB tiene 90. Faltan 17 tablas de negocio (18 contando system tables).
- **Accion:** declarar las 17 faltantes en ORM (ver H-012, H-013 y lista en db_snapshot vs orm_snapshot).
- **Fecha:** 2026-10-01

### H-010: El ORM tiene 29 indices, la DB tiene 280

- **Item:** Base.metadata.indexes vs DB
- **Clasificacion:** indice_falta (masivo) - Tier 1
- **Descripcion:** El ORM declara 29 indices, la DB tiene 280. Falta el 90%.
- **Riesgo:** si alguien corre alembic autogenerate, dropearia 251 indices.
- **Accion:** declarar los 251 faltantes en ORM. Priorizar los de viaje_solicitado, turno_chofer, control_base.
- **Fecha:** 2026-10-01

### H-011: El ORM tiene 243 constraints, la DB tiene 784

- **Item:** Base.metadata.constraints vs DB
- **Clasificacion:** constraint_desalineada (masivo) - Tier 1
- **Descripcion:** El ORM declara 243 constraints, la DB tiene 784. Falta el 69%.
- **Distribucion probable:** PKs (73 en ORM vs 90 en DB), FKs (menos en ORM), UNIQUEs, CHECKs (10 en viaje_solicitado solo, 0 en ORM).
- **Accion:** declarar los faltantes en ORM. Incluye CHECK constraints de viaje_solicitado (H-002).
- **Fecha:** 2026-10-01

### H-012: Schema comunicacion completo no esta en ORM

- **Item:** comunicacion.*
- **Clasificacion:** orm_falta (schema completo) - Tier 2
- **Descripcion:** El schema comunicacion tiene 3 tablas (conversacion, email_enviado, mensaje) en DB. Ninguna esta en ORM.
- **Accion:** crear app/models/comunicacion.py con las 3 tablas. Registrar en app/models/__init__.py.
- **Fecha:** 2026-10-01

### H-013: Schema rentabilidad completo no esta en ORM

- **Item:** rentabilidad.*
- **Clasificacion:** orm_falta (schema completo) - Tier 2
- **Descripcion:** El schema rentabilidad tiene 3 tablas (analisis_medios_pago, rentabilidad_diaria_vehiculo, rentabilidad_mensual_vehiculo) en DB. Ninguna esta en ORM.
- **Accion:** crear app/models/rentabilidad.py con las 3 tablas. Registrar en app/models/__init__.py.
- **Fecha:** 2026-10-01

### H-014: public.alembic_version y public.spatial_ref_sys son system tables

- **Item:** public.alembic_version, public.spatial_ref_sys
- **Clasificacion:** ignorar en diff
- **Descripcion:** Estas 2 tablas no son de negocio. Una la maneja Alembic, otra PostGIS.
- **Accion:** whitelist en diff.py para excluirlas.
- **Fecha:** 2026-10-01

### H-015: trip.reserva es la unica tabla sobrante en ORM

- **Item:** trip.reserva
- **Clasificacion:** orm_sobra - Tier 4 (muerte)
- **Descripcion:** 29 columnas declaradas en ORM, tabla no existe en DB.
- **Accion:** borrar el modelo Reserva de app/models/trip.py. Verificar que no haya FKs ni relationships apuntando a el.
- **Fecha:** 2026-10-01

### H-016: Indices de trip.viaje_solicitado (6 en ORM vs 19 en DB)

- **Item:** trip.viaje_solicitado.indexes
- **Clasificacion:** indice_falta + constraint_nombre_desalineado - Tier 1
- **Descripcion:** ORM declara 6 indices, DB tiene 19. Divergencia doble: faltan 13, y los nombres divergen por naming convention.
- **ORM:** ix_trip_viaje_solicitado_origen, idx_viaje_solicitado_origen, idx_viaje_solicitado_destino, ix_trip_viaje_solicitado_destino, ix_trip_viaje_solicitado_codigo_compartido, ix_trip_viaje_solicitado_estado.
- **DB:** idx_viaje_aceptado, idx_viaje_chofer, idx_viaje_comercio, idx_viaje_estado, idx_viaje_fecha_programada, idx_viaje_origen_gist, idx_viaje_pasajero, idx_viaje_reservas_pendientes, idx_viaje_solicitado_chofer_vehiculo, idx_viajes_llegado_en, ix_viaje_centro_costo, ix_viaje_cuenta_corriente_id, ix_viaje_empleado_id, ix_viaje_empresa_id, ix_viaje_estado, ix_viaje_fecha_expiracion_publicado, ix_viaje_qr_cobro_token, ix_viaje_solicitado_turno_id, viaje_solicitado_pkey.
- **Accion:** declarar los 13 faltantes en ORM. Considerar alinear naming convention con DB (o viceversa).
- **Fecha:** 2026-10-01

---

## Hallazgos de Fase 1 - Sesion 3 (diff.py)

### H-017: nullable_desalineado masivo (158 items)

- **Item:** multiples columnas en 10 schemas
- **Clasificacion:** nullable_desalineado - Tier 2
- **Descripcion:** El ORM declara nullable distinto que la DB en 158 columnas.
- **Riesgo:** si ORM declara nullable=True pero DB tiene NOT NULL, los INSERTs del ORM pueden fallar. Bug potencial activo.
- **Accion:** revisar en Fase 2. Puede requerir migracion de nullable en DB o ajuste en ORM.
- **Fecha:** 2026-10-01

### H-018: constraint_nombre_desalineado (124 items)

- **Item:** multiples constraints
- **Clasificacion:** constraint_nombre_desalineado - Tier 3
- **Descripcion:** 124 constraints difieren solo en nombre. Consecuencia del naming convention del ORM (pk_%, fk_%, ck_%, uq_%).
- **Accion:** automatico en Fase 3 (apply.py). Cosmetico pero masivo.
- **Fecha:** 2026-10-01

### H-019: constraint_falta (428 items)

- **Item:** multiples constraints
- **Clasificacion:** constraint_falta - Tier 1-2
- **Descripcion:** 428 constraints en DB que el ORM no declara. FKs, UNIQUEs, CHECKs.
- **Accion:** priorizar por tabla en Fase 2. Declarar en ORM en Fase 4.
- **Fecha:** 2026-10-01

### H-020: tipo_desalineado (114 items)

- **Item:** multiples columnas
- **Clasificacion:** tipo_desalineado - Tier 1-2
- **Descripcion:** 114 columnas con tipo distinto entre ORM y DB. Incluye 19 timestamps naive y 2 control_base lat/lng.
- **Accion:** 21 ya identificados (requieren decision). Los ~93 restantes, revisar en Fase 2.
- **Fecha:** 2026-10-01

### H-021: 24 items requieren decision manual

- **Item:** multiples
- **Clasificacion:** requiere_decision
- **Desglose:**
  - 19 timestamps naive (7 tablas neumatico_*) -> D-012
  - 2 J9 (auth.codigo_metadatos, auth.codigo_verificacion) -> D-006
  - 2 orm_mal_db_bien (tenant.control_base.latitud/longitud) -> D-007
  - 1 vocabulario (fleet.ingreso_turno.medio_pago) -> D-005
- **Accion:** resueltos en Fase 2 (Ronda 6, Sesion 1). 24/24.
- **Fecha:** 2026-10-01

### H-022: Total diferencias del diff

- **Total:** 1280
- **Tier 1:** 247
- **Tier 2:** 912
- **Tier 3:** 120
- **Tier 4:** 1
- **Requieren decision:** 24 (resueltos en Fase 2)
- **Archivos generados:**
  - orm_diff.json (823 KB)
  - orm_diff_reporte.md (21 KB)
  - orm_diff_acciones.csv (115 KB)
- **Fecha:** 2026-10-01

---

## Hallazgos de Fase 2 (Ronda 6, Sesion 1)

### H-023: J9 es un falso positivo documental

- **Item:** J9 (auth.codigo_metadatos vs auth.codigo_verificacion)
- **Clasificacion:** documental (resuelto)
- **Descripcion:** J9 decia "dos fuentes de verdad para codigos de turno"
  y "el handler validar_codigo_turno lee de codigo_metadatos". Verificado:
  la FK codigo_id -> codigo_verificacion.id ON DELETE CASCADE existe;
  el handler lee de codigo_verificacion. NO hay dos fuentes de verdad.
  Es una relacion padre-hijo (codigo_verificacion es padre, codigo_metadatos
  es satelite con metadata estructurada del dominio propietario).
- **Accion:** marcar J9 como FALSO POSITIVO en DEUDA_TECNICA_ACTUAL.md.
- **Fecha:** 2026-10-01

### H-024: fleet tiene 68 columnas timestamp, todas naive

- **Item:** information_schema.columns WHERE table_schema='fleet' AND data_type LIKE 'timestamp%'
- **Clasificacion:** verificacion empirica
- **Descripcion:** Conteo real: 68 columnas, todas timestamp without time zone.
  Cero timestamptz. Confirma que la convencion del schema fleet es naive.
- **Implicacion:** la opcion (a) de D-012 (ORM a naive) es coherente con el schema.
- **Fecha:** 2026-10-01

### H-025: Volumen de datos en neumatico_*

- **Item:** 7 tablas neumatico_*
- **Clasificacion:** verificacion empirica
- **Descripcion:** 41 filas totales (11 + 1 + 3 + 8 + 11 + 0 + 7).
  Todo simulacion de prueba, modulo en desarrollo.
- **Implicacion:** descarta la opcion (b) de D-012 (migrar a timestamptz).
- **Fecha:** 2026-10-01

### H-026: Vocabularios de metodo_pago - 5 variantes documentadas

- **Item:** trip.viaje_solicitado.metodo_pago, fleet.ingreso_turno.medio_pago,
  payment.metodo_pago, schemas/recaudacion_schemas.py, empresa_dashboard.py
- **Clasificacion:** requiere_decision (negocio)
- **Descripcion:** Hay 5 vocabularios en juego. Ver D-005 para el detalle.
  El CHECK de trip.viaje_solicitado es el unico enforceado.
- **Accion:** vocabulario canonico = CHECK actual. Refactor a catalogo
  (FK por metodo_pago_id) va a Fase 4.
- **Fecha:** 2026-10-01

---

## Deudas nuevas detectadas en Fase 2

- **metodo_pago.catalogo_sucio:** payment.metodo_pago tiene 12 filas con
  2 duplicados (efectivo x2, mercadopago x2), 1 sinonimo (wallet=billetera),
  1 pasarela mezclada (mercadopago). Limpiar en Fase 4.
- **metodo_pago.fk_catalogo:** evaluar refactor a FK por metodo_pago_id en
  trip.viaje_solicitado y fleet.ingreso_turno. Toca app, reportes, ORM.
  NO en Fase 2.
- **metodo_pago.ingreso_turno:** alinear comment del ORM con DB y decidir
  si se agrega CHECK a fleet.ingreso_turno.medio_pago.
- **metodo_pago.frontend_e2:** ampliar MetodoPago del frontend cuando se
  decida agregar credito o billetera.

---
---

## Decisiones tomadas en Fase 4b (Ronda 7)

### D-013: Saltear Paso 4 (CHECKs) por conflicto de naming convention

- **Item:** Paso 4 del plan Fase 4b (CHECKs reales).
- **Clasificacion:** n/a (decision operativa).
- **Decision (2026-10-04):** saltear el Paso 4. Documentar el bloqueo
  como deuda (`orm.naming_convention_check_divergente`) y avanzar con
  el Paso 7 (D-012: timestamps naive en neumatico_*).
- **Justificacion:**
  - La convention `ck_%(table_name)s_%(constraint_name)s` en
    `app/database.py` agrega el prefijo `ck_<tabla>_` a todos los
    CHECKs declarados en el ORM.
  - La DB tiene CHECKs con nombres que NO siguen esa convention.
  - `diff.py` matchea CHECKs por nombre exacto, asi que los ~13 CHECKs
    "sin convention" nunca van a matchear.
  - Se probo overridear con `quoted_name(..., quote=True)` (SQLAlchemy
    2.0). NO funciona: la convention se aplica antes del `name` final.
  - De los ~23 CHECKs reales, solo ~8 (trip.viaje_solicitado) se
    alinean solos con la convention actual.
  - El esfuerzo de arreglar `diff.py` o la convention global excede
    el scope de un sub-paso. Mejor diferir y priorizar D-012 (19
    timestamps naive, bug activo).
- **Accion:** documentar en DEUDA_TECNICA_ACTUAL.md. Arrancar Paso 7
  (D-012) inmediatamente despues.
- **Estado:** APROBADA.


  
**FIN DEL DOCUMENTO**