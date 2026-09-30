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

**FIN DEL DOCUMENTO**