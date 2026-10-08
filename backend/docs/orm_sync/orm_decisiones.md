# Decisiones de reconciliacion ORM - DB

**Iniciado:** 2026-09-30 (Ronda 5, Fase 0)
**Head Alembic:** m3_010
**Commit baseline:** 4c77f3a
**Tag baseline:** ronda5-baseline-pre
**Backup DB:** docs/backups/taxip_db_2026-09-30.dump (546 KB)
**Responsable:** megarcia34
**Ultima actualizacion:** 2026-10-06 (Ronda 9, cierre)

## Proposito

Registrar cada decision tomada durante la reconciliacion del ORM con la DB.
Cada entrada debe incluir: item, clasificacion, decision, justificacion, fecha.

**Historico de decisiones cerradas (D-001 a D-013):** ver
`docs/orm_sync/orm_decisiones_historico.md`.

---

## Decisiones tomadas en Ronda 9 (2026-10-06)

### D-022: Excluir PKs de indice_falta en diff.py

- **Item:** `RE_PK_INDEX` + filtro en `diff_indexes` de `scripts/orm_sync/diff.py`.
- **Clasificacion:** fix de tooling.
- **Decision (2026-10-06):** filtrar indices cuyo nombre matchea
  `^(pk_.+|.+_pkey)$` antes de comparar. Aplicar a DB y ORM.
- **Justificacion:**
  - SQLAlchemy declara la PK via `primary_key=True`, no como `Index`.
  - El introspector de DB si incluye `pk_<tabla>` / `<tabla>_pkey` en indexes.
  - `diff.py` los reportaba como `indice_falta` (72 falsos positivos).
- **Impacto:** −72 items (`indice_falta: 86 → 14`). Diff total: 404 → 332.
- **Commit:** `1ac1294`.
- **Fecha:** 2026-10-06.

### D-023: Eliminar B-tree redundante sobre Geography en fleet.chofer_vehiculo

- **Item:** `index=True` en `fleet.chofer_vehiculo.ubicacion`.
- **Clasificacion:** bug del ORM.
- **Decision (2026-10-06):** eliminar `index=True`. El B-tree que genera
  es inutil sobre Geography (queries espaciales requieren GIST).
  GeoAlchemy2 ya declara un GIST equivalente via `spatial_index=True`.
- **Justificacion:**
  - Postgres no usa B-tree para operadores espaciales (`&&`, `ST_DWithin`, etc.).
  - El GIST auto-generado por GeoAlchemy2 lo cubre.
  - DB no tenia ningun indice (solo `chofer_vehiculo_pkey`).
- **Impacto:** cleanup real, aunque el diff no bajo (bug de colapso
  de `diff_indexes`).
- **Commit:** `158e594`.
- **Fecha:** 2026-10-06.

### D-024: Indices GIST de GeoAlchemy2 — pendiente migracion Alembic

- **Item:** 3 indices GIST auto-generados por GeoAlchemy2, ausentes en DB:
  - `fleet.chofer_vehiculo.idx_chofer_vehiculo_ubicacion`
  - `trip.panico.idx_panico_ubicacion`
  - `trip.viaje_solicitado.idx_viaje_solicitado_destino`
- **Clasificacion:** decision funcional.
- **Decision (2026-10-06):** crear migracion Alembic en R10 para
  aplicar los 3 en DB. Son utiles para queries espaciales.
- **Alternativa descartada:** desactivar `spatial_index` en las columnas.
  Se descarta porque los indices son utiles en produccion.
- **Impacto:** queries espaciales eficientes (proximidad de choferes,
  busqueda por destino).
- **Deuda:** `orm.geoalchemy2_indices_no_aplicados`.
- **Fecha:** 2026-10-06.

### D-025: Fix de diff_indexes — matchear por (nombre, columnas)

- **Item:** `diff_indexes` en `scripts/orm_sync/diff.py`.
- **Clasificacion:** fix de tooling.
- **Decision (2026-10-06):** cambiar el matching de indices para que
  use `(nombre_normalizado, columnas)` en vez de solo `columnas`.
- **Justificacion:**
  - Si el ORM declara dos indices sobre la misma columna (ej: B-tree + GIST
    sobre `ubicacion`), el dict `orm_idx` colapsa a uno solo.
  - El otro queda invisible al diff.
  - Esto enmascaro el fix de D-023 (el diff no bajo en Paso 9.2).
- **Impacto esperado:** el diff reflejara correctamente los 332 items.
  Probablemente baje a 331 (el B-tree eliminado en D-023 ya no aparece).
- **Estado:** pendiente (R10).
- **Fecha:** 2026-10-06.

---

## Decisiones tomadas en Ronda 8 (2026-10-05)

### D-014: Fix Geography case-insensitive en diff.py

- **Item:** `_types_equivalent()` en `scripts/orm_sync/diff.py`.
- **Clasificacion:** fix de tooling.
- **Decision (2026-10-05):** comparar tipos Geography/Geometry case-insensitive
  (lowercase ambos lados). Resto de tipos: exacto.
- **Justificacion:**
  - GeoAlchemy2 normaliza `geometry_type` a lowercase internamente.
  - La DB tiene `Point`/`MultiPolygon` con mayuscula (PostGIS nativo).
  - `diff.py` los reportaba como `tipo_desalineado` (4 falsos positivos).
- **Impacto:** −4 items (`tipo_desalineado: 4 → 0`).
- **Commit:** `6927f08`.
- **Fecha:** 2026-10-05.

### D-015: Excluir `*_not_null` autogenerados de `constraint_falta`

- **Item:** `RE_NOT_NULL_AUTOGEN` en `scripts/orm_sync/diff.py`.
- **Clasificacion:** fix de tooling.
- **Decision (2026-10-05):** excluir CHECKs con patron `^\d+_\d+_\d+_not_null$`
  de la comparacion de constraints.
- **Justificacion:**
  - Alembic genera CHECKs `<oid1>_<oid2>_<ordinal>_not_null` en cada
    `ALTER TABLE ... SET NOT NULL`.
  - El ORM no los declara (son artefactos de Postgres/Alembic).
  - `diff.py` los reportaba como `constraint_falta` (~400 falsos positivos).
- **Impacto:** −358 items (`constraint_falta: 427 → 69`).
- **Commit:** `d3692f1`.
- **Fecha:** 2026-10-05.

### D-016: Fix doble prefijo `ck_` en trip.viaje_solicitado

- **Item:** 8 `CheckConstraint` de `trip.viaje_solicitado` en `app/models/trip.py`.
- **Clasificacion:** bug del ORM.
- **Decision (2026-10-05):** los `name=` declarados tenian el prefijo
  `ck_viaje_solicitado_` **ya incluido**. La convention de `app/database.py`
  (`ck_%(table_name)s_%(constraint_name)s`) lo agregaba **otra vez**.
  Resultado: nombre final con doble prefijo.
  Se removio el prefijo de los 8 `name=`.
- **Justificacion:**
  - Declaracion original: `name="ck_viaje_solicitado_ck_viaje_calidad_min"`.
  - Nombre final ORM: `ck_viaje_solicitado_ck_viaje_solicitado_ck_viaje_calidad_min`.
  - Nombre DB: `ck_viaje_solicitado_ck_viaje_calidad_min`.
  - No matcheaban.
  - Fix: `name="ck_viaje_calidad_min"`.
  - Resultado con convention: `ck_viaje_solicitado_ck_viaje_calidad_min`.
- **Impacto:** −16 items (`constraint_sobra` −8, `constraint_falta` −8).
- **Commit:** `b2edb4e`.
- **Fecha:** 2026-10-05.

### D-017: `Index(unique=True)` para UNIQUEs que la DB tiene como INDEX

- **Item:** `uq_neumatico_codigo_interno` en `fleet.neumatico_vehiculo`.
- **Clasificacion:** semantica ORM vs DB.
- **Decision (2026-10-05):** la DB tiene `CREATE UNIQUE INDEX` (no
  `UNIQUE CONSTRAINT`). El ORM debe reflejar eso con `Index(..., unique=True)`,
  no con `UniqueConstraint(...)`.
- **Justificacion:**
  - En Postgres, `CREATE UNIQUE INDEX` y `ALTER TABLE ... ADD CONSTRAINT UNIQUE`
    son cosas distintas.
  - El introspector de DB clasifica los UNIQUE INDEX como indices (no constraints).
  - Si el ORM declara `UniqueConstraint`, el diff lo ve como `constraint_sobra`.
  - Si el ORM declara `Index(unique=True)`, el diff lo ve como indice y matchea.
- **Impacto:** −1 `indice_falta` + −1 `constraint_sobra`.
- **Commit:** `d133472`.
- **Deuda asociada:** `orm.unique_constraint_vs_unique_index` (14 items
  preexistentes con el mismo patron, no resueltos en R8).
- **Fecha:** 2026-10-05.

### D-018: Fase 6 (indices reales) cerrada — 100% aplicado

- **Item:** Paso 6 del plan (indices reales).
- **Clasificacion:** cierre de fase.
- **Decision (2026-10-05):** todos los indices reales del diff aplicados.
  No quedan `indice_falta` con prefijo `ix_`/`idx_` pendientes.
- **Indices aplicados (98 total):**
  - `audit.py`: 8
  - `corporate.py`: 7
  - `tenant.py`: 5
  - `public.py`: 6
  - `payment.py`: 4
  - `geo.py`: 1
  - `foto_viaje.py`: 1
  - `fleet.py`: 60 (+2 UNIQUEs)
  - `turno.py`: 4
  - `gasto_turno.py`: 2
- **Commits:** `b04a2fb`, `f6c9fe1`, `e120b55`, `f6226f2`, `973dda9`,
  `a2010f2`, `824d770`, `ce55835`, `44daf51`, `c5bd634`.
- **Impacto acumulado:** `indice_falta: 180 → 86` (−94).
- **Deuda residual:** los 86 `indice_falta` restantes son 72 PKs (ruido
  de diff.py) + 14 UNIQUE INDEX cosmeticos.
- **Fecha:** 2026-10-05.

### D-019: fleet schema 100% reconciliado

- **Item:** schema `fleet` en el diff.
- **Clasificacion:** cierre de schema.
- **Decision (2026-10-05):** los 60 indices reales del schema `fleet`
  (mas `turno.py` y `gasto_turno.py`) aplicados. Los items residuales
  son:
  - PKs ruidosas (ruido de diff.py).
  - UNIQUE INDEX cosmeticos (`uq_*`, `unique_*`, `*_key`).
  - `constraint_nombre_desalineado` (124 items global, cosmetico).
  - `constraint_desalineada` (72 items global, PKs con nombre distinto).
  - `constraint_falta` residual (CHECKs reales sin resolver).
- **Impacto:** `fleet.py` items: 303 → 118 (−61%).
- **Fecha:** 2026-10-05.

---

## Decisiones pendientes (R10)

- **D-009:** `public.comercio` FK sin schema. Decidir `public.comercio` o
  cambiar schema.
- **D-010:** ciclo de FKs `auth.usuario` <-> `tenant.control_base`. Requiere
  `use_alter=True` o `deferrable`.
- **D-026** (nueva): `orm.unique_constraint_vs_unique_index`. 14 items con
  patron D-017 sin resolver. Decision: aplicar `Index(unique=True)` en masa
  o dejar cosmetico.
- **D-027** (nueva): `orm.naming_convention_check_divergente`. Politica
  de naming de CHECKs: cambiar convention global o matchear por definicion
  en `diff.py`. Bloqueante del Paso 4 residual.
- **D-028** (nueva): `orm.indice_sobra_ambiguo`. Distinguir en `diff.py`
  entre ruido real (B-tree sobre Geography) y GIST util de GeoAlchemy2.
  Requiere heuristica o lista blanca de patrones.

---

## Deudas nuevas detectadas en Ronda 9

(Ver `DEUDA_TECNICA_ACTUAL.md` para detalle completo.)

- `orm.indice_sobra_ambiguo` (3 items, mixto ruido/util).
- `orm.geoalchemy2_indices_no_aplicados` (3 indices GIST sin aplicar en DB).
- `orm.diff_indexes_colapsa_por_columnas` (bug de tooling).

---

## Deudas nuevas detectadas en Ronda 8

(Ver `DEUDA_TECNICA_ACTUAL.md` para detalle completo.)

- `orm.unique_constraint_vs_unique_index` (14 items).
- `orm.tabla_falta_auth` (4 tablas: codigo_metadatos, codigo_verificacion,
  plantilla_viaje, prestadora_telefonica).
- `orm.indice_falta_incluye_pks` (72 PKs ruido de `diff.py`). CERRADA en R9.
- `orm.comercio_indice_redundante` (1 item).

---

## Items nuevos detectados en Ronda 8 (no estaban en el diff original)

- `auth.plantilla_viaje` (19 columnas) — tabla real, no en ORM.
- `auth.prestadora_telefonica` (6 columnas) — tabla real, no en ORM.
- Bug del doble prefijo `ck_` — no anticipado.
- Bug del BOM en `fleet.py` — VS Code agrega BOM al guardar en
  ciertas configuraciones. Verificar encoding.

---

## Items nuevos detectados en Ronda 9 (no estaban en el diff original)

- GeoAlchemy2 auto-genera `Index GIST` sobre columnas `Geography` con
  `spatial_index=True` (default). Esto explica los 3 `indice_sobra`
  que parecian ruido y son indices utiles.
- `diff_indexes` colapsa indices por columna: si el ORM tiene dos indices
  sobre la misma columna, solo uno aparece en el diff.

---

## Referencias historicas

- **Decisiones D-001 a D-013:** `docs/orm_sync/orm_decisiones_historico.md`.
- **Hallazgos H-001 a H-026:** mismo archivo historico.

---

## DECISIONES RONDA 11 (2026-10-08)

### D-030 — `diff.py` matchea UNIQUE INDEX (DB) vs UniqueConstraint (ORM) por columnas

**Contexto:** el diff reportaba 22 `indice_falta` que en realidad eran
`UniqueConstraint` del ORM expresados en DB como `CREATE UNIQUE INDEX`.
El ORM los declara en `constraints.unique`, no en `indexes`, por lo que
`diff_indexes` no los veia.

**Decision:** matchear `CREATE UNIQUE INDEX` (DB, no PK, no partial)
contra `UniqueConstraint` (ORM) por columna, sin comparar nombre. Excluye
partial indexes porque SQLAlchemy no puede expresar `WHERE` en
`UniqueConstraint` (los partial siguen apareciendo como `indice_falta`).

**Implementacion:** `scripts/orm_sync/diff.py`, helper `_orm_unique_cols()`
+ `_is_partial_index()`. Commit `6918cb1`.

**Impacto:** -12 items (falsos positivos eliminados).

**Alternativa descartada:** renombrar los UNIQUEs en DB para que coincidan
con los nombres del ORM. Rechazada porque requiere DDL y porque el nombre
de un UNIQUE no tiene semantica funcional.

**Tier 2.**

### D-031 — B-tree declarados en ORM deben matchear el nombre exacto de DB

**Contexto:** en R11 declaramos 9 B-tree + UNIQUEs compuestos que la DB
ya tenia. Todos los nombres matchearon exactos (`idx_*`, `uq_*`,
`unique_*`, `*_key`).

**Decision:** al declarar un `Index` en el ORM, usar el nombre **literal**
de la DB (no normalizar). El diff matchea por `(nombre_normalizado,
columnas)`, por lo que cambiar el nombre genera un `indice_falta` (el de
DB) + `indice_sobra` (el de ORM).

**Excepcion:** `fleet.contrato_vehiculo.ix_contrato_vehiculo_estado_contrato`
se renombro a `idx_contrato_estado` (el nombre de DB) porque eran el mismo
indice con dos nombres distintos. Eso cerro un item pero abrio otro (el
`ix_...` original de DB ahora queda sin par en ORM). Redundancia documentada
en `orm.indice_redundante_contrato_vehiculo`.

**Tier 2.**

### D-032 — `nullable_desalineado`: alinear siempre el ORM a la DB

**Contexto:** 4 columnas con `nullable=True` en ORM y `NOT NULL` en DB.
Eso significa que el ORM puede intentar insertar `NULL` y la DB lo
rechaza en runtime.

**Decision:** la DB es la fuente de verdad. Cuando el ORM y la DB difieren
en `nullable`, alinear **el ORM a la DB** (no tocar la DB). Cambio
quirurgico: solo `nullable=True` -> `nullable=False`, sin tocar el tipo
Python (`Mapped[Optional[...]]` se puede dejar como esta; no afecta al
diff).

**Cuidado:** verificar que ningun endpoint este pasando `None` a esas
columnas antes de aplicar el cambio. Si la DB ya tiene `NOT NULL`, en
principio no deberia romper (ya fallaba).

**Impacto:** -4 items.

**Tier 2.**

### D-033 — Comments en ORM: usar `doc=` en lugar de `comment=`

**Contexto:** 7 columnas con `comment="..."` en ORM que la DB no tenia
en `pg_description`. Se reportaban como `comment_desalineado` (Tipo A).
Los otros 13 `comment_desalineado` son mojibake en DB y requieren UPDATE.

**Decision:** mover los `comment=` a `doc=`. El `doc=` de SQLAlchemy es
documentacion interna de Python, **NO se persiste** en `pg_description`,
por lo que el diff no lo ve. Esto cierra el item **conservando la
documentacion**.

**Regla para el futuro:** usar `comment=` **solo** cuando el comentario
este tambien en la DB (sincronizado). Para documentacion interna, usar
`doc=`.

**Implementacion:**
- `corporate.py`: factura_corporativa.estado, movimiento_cuenta.tipo_movimiento,
  pago_corporativo.estado.
- `fleet.py`: notificacion_vencimiento.entidad_tipo, notificacion_vencimiento.nivel.
- `public.py`: escaneo_qr.resultado, escaneo_qr.tipo_qr.

**Impacto:** -7 items.

**Tier 3.**

### D-034 — Fase 4c: tablas que existen en DB pero no en ORM

**Contexto:** 10 tablas existian en DB pero no estaban declaradas en ORM.
Ademas, 2 schemas completos (`comunicacion`, `rentabilidad`) tenian
3 tablas cada uno, sin modulo ORM.

**Decision:** declarar **todas** las tablas faltantes en ORM. La DB es la
fuente de verdad; el ORM debe reflejarla. Se crearon 2 modulos nuevos
(`app/models/comunicacion.py`, `app/models/rentabilidad.py`) y se
ampliaron 4 existentes (auth, audit, fleet, payment, trip).

**Implementacion:**
- 8 commits de models (uno por sub-paso o par de tablas relacionadas).
- 2 commits de archivos nuevos.

**Impacto:** -11 items (10 tabla_falta + 2 schema_falta - 1 CHECK residual
de `codigo_verificacion`).

**Nota:** `auth.codigo_verificacion` tiene un CHECK (`chk_codigo_verificacion_tipo`)
cuyo nombre **no matchea** la convention de SQLAlchemy. Queda como
`constraint_falta` residual para R12 (migracion m3_014).

**Tier 2.**

---

## RESUMEN DE DECISIONES R11

| ID | Decision | Impacto | Commit |
|---|---|---|---|
| D-030 | Matchear UNIQUE INDEX vs UniqueConstraint por columnas | -12 | 6918cb1 |
| D-031 | Declarar B-tree con nombre literal de DB | -9 | varios |
| D-032 | Alinear nullable del ORM a la DB | -4 | varios |
| D-033 | Mover `comment=` a `doc=` para comments solo-ORM | -7 | varios |
| D-034 | Declarar tablas faltantes (Fase 4c) | -11 | varios |

**Total cerrado en R11: -43 items.**
---

**FIN DEL DOCUMENTO**