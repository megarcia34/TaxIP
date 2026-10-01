# Decisiones de reconciliacion ORM - DB

**Iniciado:** 2026-09-30 (Ronda 5, Fase 0)
**Head Alembic:** m3_010
**Commit baseline:** 4c77f3a
**Tag baseline:** ronda5-baseline-pre
**Backup DB:** docs/backups/taxip_db_2026-09-30.dump (546 KB)
**Responsable:** megarcia34

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
- **Clasificacion:** orm_sobra - Tier 4 (muerte)
- **Decision:** borrar el modelo Reserva del ORM
- **Justificacion:** la tabla no existe en DB. A1 de la deuda confirma que es modelo huerfano. El modulo corporativo no la usa.
- **Fecha:** 2026-09-30

### D-005: fleet.ingreso_turno

- **Item:** fleet.ingreso_turno
- **Clasificacion:** tipo_desalineado (comment) + orm_falta (comment)
- **Decision:** existe en DB. Alinear comment del ORM con DB y canonizar vocabulario de medio_pago (conecta con metodo_pago.catalogo)
- **Justificacion:** SELECT EXISTS(...) confirma true. El comment en DB tiene 6 valores, el ORM tiene 4.
- **Fecha:** 2026-09-30

### D-006: auth.codigo_verificacion + auth.codigo_metadatos

- **Item:** auth.codigo_verificacion, auth.codigo_metadatos
- **Clasificacion:** orm_falta + requiere_decision (funcional)
- **Decision:** PENDIENTE. Ambas tablas existen en DB, ORM no las declara. J9 dice que hay ambiguedad de negocio (dos fuentes de verdad para codigos de turno). Requiere analisis del handler validar_codigo_turno.
- **Justificacion:** ambas tablas confirmadas en DB. Decidir: (a) declarar ambas en ORM y documentar cual es la fuente de verdad, o (b) unificar en una sola (migracion + refactor).
- **Fecha:** 2026-09-30

### D-007: tenant.control_base.latitud/longitud

- **Item:** tenant.control_base.latitud, tenant.control_base.longitud
- **Clasificacion:** tipo_desalineado + requiere_decision + orm_mal_db_bien
- **Decision:** el ORM debe cambiar de String(50) a Numeric(10,8) (latitud) y Numeric(11,8) (longitud)
- **Justificacion:** la DB tiene numeric(10,8) y numeric(11,8) que es lo correcto para coordenadas. El ORM con String(50) es un error grave. Excepcion explicita a la regla de oro.
- **Fecha:** 2026-09-30

### D-008: fleet.* timestamps naive

- **Item:** fleet.<tabla>.<columna> (70 columnas timestamp en 30 tablas)
- **Clasificacion:** tipo_desalineado + requiere_decision (arquitectura)
- **Decision:** PENDIENTE. DB tiene timestamp without time zone, ORM probablemente DateTime(timezone=True). Decision arquitectonica: (a) ORM se adapta a naive, (b) DB migra a timestamptz, (c) ignorar.
- **Justificacion:** 70 columnas timestamp en fleet son naive. Decision afecta semantica de turnos, liquidaciones, etc. Fuera de alcance de Fase 1, se documenta como deuda.
- **Fecha:** 2026-09-30

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

## Decisiones pendientes (se resolveran en Fase 2)

- D-006: auth.codigo_verificacion + auth.codigo_metadatos (decision funcional)
- D-008: fleet.* timestamps (decision arquitectonica)
- D-009: public.comercio FK (decision de schema)
- D-010: ciclo de FKs (decision tecnica)

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
- **Accion:** definir vocabulario canonico antes de tocar el ORM. Requiere input de negocio.
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

**FIN DEL DOCUMENTO**