# DEUDA TECNICA ACTUAL — TaxIP 2.0

**Ultima actualizacion:** 2026-10-11 (cierre Ronda 15)
**Ronda activa:** 15 cerrada (`ronda15-fase15-completa`)
**Total items pendientes:** 0 (diff BD <-> ORM alineado)
**Total criticos:** 0
**Alembic head:** m3_017

---
---
## RESUMEN DE RONDA 15 (2026-10-11)

**Objetivo:** resolver deuda tecnica FUNCIONAL (no estructural).
La alineacion estructural BD <-> ORM quedo completa en R14; R15 ataca
las deudas funcionales y de proceso que el diff no captura.

**Resultado:**
- **P1 - metodo_pago catalogo sucio: CERRADO.**
- **P2 - alembic check categorias C y D: CERRADO.**
- **P3 - tooling: documentado (no resuelto).**
- **P4 - documentacion: este documento.**

**Fixes aplicados:**

1. **P1 - Migracion `m3_016` limpiar catalogo metodo_pago** (commit `44c5147`):
   - Catalogo `payment.metodo_pago` limpiado de 12 a 4 filas.
   - Vocabulario canonico Momento 1: efectivo, tarjeta_debito, qr, transferencia.
   - Filas eliminadas: efectivo duplicado, tarjeta_credito, billetera,
     wallet, credito, debito, mercadopago x2.
   - Agregado UNIQUE sobre nombre (`uq_metodo_pago_nombre`).
   - Agregado CHECK con vocabulario canonico (`ck_metodo_pago_nombre`).
   - Comment de tabla actualizado.
   - ORM: `MetodoPago.__table_args__` actualizado con UniqueConstraint,
     CheckConstraint y comment.
   - Fix adicional: `payment_schemas.py:20` default `mercadopago` -> `efectivo`.
   - Deuda documentada: `pagos.py:203` referencia `billetera` (Momento 3).

2. **P2 - Migracion `m3_017` drop indice redundante + comments de tabla**
   (commit `ad24c66`):
   - Eliminado `payment.ix_qr_cobro_token` (redundante con `uq_qr_cobro_token`).
   - 5 comments de tabla agregados al ORM y actualizados en DB:
     - `auth.autorizacion_inicio`
     - `auth.turno_empleado`
     - `auth.usuario_rol`
     - `fleet.contrato_qr` (texto corregido: "QRs generados para pagos
       y trazabilidad de viajes")
     - `fleet.documentos_chofer`
   - Deuda `orm.comment_mojibake` cerrada (3 comments con mojibake
     corregidos).

3. **P3 - Documentacion de tooling** (este documento):
   - 4 deudas de tooling documentadas (postergadas a R16+).
   - Deuda nueva `orm.naming_convention_check_doble_prefijo` documentada
     como resuelta.

**Migraciones aplicadas:**

- `m3_016` (commit `44c5147`): limpiar catalogo metodo_pago + UNIQUE + CHECK.
- `m3_017` (commit `ad24c66`): drop ix_qr_cobro_token + 5 comments de tabla.

**Deudas cerradas en R15:**

- `metodo_pago.catalogo_sucio` (P1).
- `orm.alembic_check_categoria_c` (ix_qr_cobro_token redundante).
- `orm.alembic_check_categoria_d` (5 comments de tabla).
- `orm.comment_mojibake` (3 comments residuales de R12).
- `orm.naming_convention_check_doble_prefijo` (documentada como resuelta).

**Deudas nuevas identificadas en R15:**

- `orm.naming_convention_check_doble_prefijo` (RESUELTA).
- `orm.alembic_check_categoria_a` (naming divergente, ~15 falsos positivos).
- `orm.alembic_check_categoria_b` (FKs con ondelete distinto, ~35 items).
- `pagos.py_203_billetera` (referencia a fila eliminada del catalogo).

**Plan R16 (recomendado):**

- Fix de tooling: `orm.ids_diff_no_estables`.
- Decision de `ondelete` por FK (`orm.alembic_check_categoria_b`).
- Deuda funcional heredada: G63, G67, G80.
- Refactor funcional: `metodo_pago.fk_catalogo`,
  `metodo_pago.flujo_propietario`, `metodo_pago.flujo_empresa`.

**Ver:** `docs/CONTEXTO_RONDA_15.md` (este documento).

---
---
## RESUMEN DE RONDA 14 (2026-10-11)

**Objetivo:** cerrar los 21 items restantes del diff (16 CHECKs G2a +
5 FKs huerfanas) y alcanzar la alineacion completa BD <-> ORM.

**Resultado:**
- **Diff total: 21 -> 0** (-21, -100%).
- Tier 1: 6 -> **0**.
- Tier 2: 15 -> **0**.
- `constraint_falta / check`: 16 -> **0**.
- `constraint_falta / fk`: 5 -> **0**.

**LA ALINEACION BD <-> ORM ESTA COMPLETA.**

**Fixes aplicados:**

1. **Fase R14.3 - Declarar 5 FKs en ORM** (commit `17f4d6d`):
   - `corporate.cuenta_corriente.propietario_id` -> `auth.usuario.id`
   - `trip.viaje_solicitado.empleado_id` -> `auth.usuario.id`
   - `trip.viaje_solicitado.movimiento_cc_id` -> `corporate.movimiento_cuenta.id`
   - `trip.viaje_solicitado.turno_empleado_id` -> `auth.turno_empleado.id`
   - `trip.viaje_solicitado.cuenta_corriente_id` -> `corporate.cuenta_corriente.id`
   - Correccion: `turno_empleado_id` apuntaba a `auth.usuario.id` en vez
     de `auth.turno_empleado.id`.

2. **Fase R14.1 - Migracion `m3_015`** (commit `3db3e7b`):
   - Renombra 16 CHECKs al naming canonico `ck_<tabla>_<col>`.
   - Aplicada en R14.
   - Deuda `orm.naming_convention_check_divergente` cerrada.

3. **Fase R14.2 - Declarar 16 CHECKs en ORM** (commits `0f4434c`, `f7c7413`,
   `60bd195`, `80c030b`, `ed589a6`):
   - `auth.py`: `ck_turno_empleado_estado`, `ck_codigo_verificacion_tipo`.
   - `fleet.py`: 9 CHECKs en `contrato_vehiculo`.
   - `payment.py`: `ck_pago_empresa_estado`, `ck_pago_empresa_monto`.
   - `public.py`: `ck_escaneo_qr_resultado`, `ck_escaneo_qr_tipo`.
   - `trip.py`: `ck_calificacion_puntaje`.

**Migracion aplicada:**

`m3_015` (commit `3db3e7b`):
- 16 `ALTER TABLE ... RENAME CONSTRAINT`.

**Deudas cerradas en R14:**

- `orm.naming_convention_check_divergente` (Grupo 2).
- `orm.paso4_check_constraints_residual`.

**Deudas residuales (no-diff, funcionales):**

- `metodo_pago.catalogo_sucio` (12 filas, refactor funcional).
- `metodo_pago.fk_catalogo`.
- `metodo_pago.frontend_e2`.
- `metodo_pago.flujo_propietario` / `flujo_empresa`.
- `metodo_pago.ingreso_turno`.
- `flujo_caja.ingreso_turno`.
- `orm.snapshot_orm_stale` (proceso).
- `orm.ids_diff_no_estables` (tooling).
- `orm.diff_clasifica_mal_columnas_ausentes` (tooling).
- `orm.diff_falsos_positivos_tipo_cambio` (tooling).
- `orm.alembic_check_ruidoso` (proceso).
- `orm.modulo_duplicado_trip_service` (documentar).
- `orm.ciclo_fk_usuario_control_base` (documentar).
- Las deudas de Alta/Media/Baja prioridad ya documentadas en R12.

**Plan R15 (recomendado):**

- Refactor funcional de `metodo_pago` (catalogo sucio).
- Verificacion de `alembic check` (¿ahora si es util?).
- Limpieza de tooling (`orm.ids_diff_no_estables`, `orm.snapshot_orm_stale`).
- Documentacion de deudas residuales.

**Ver:** `docs/CONTEXTO_RONDA_14 a 15.md` (handoff, a crear).

## RESUMEN DE RONDA 13 (2026-10-10)

**Objetivo:** cerrar 6 items del diff (tabla_sobra, columna_falta, indice_falta,
comment_desalineado, constraint_sobra, constraint_falta/fk) + refactor
del router /api/reservas.

**Resultado:**
- Diff total: 27 -> **21** (-6, -22%).
- Tier 1: 7 -> **6**.
- Tier 2: 19 -> **15**.
- Tier 4: 1 -> **0**.
- `tabla_sobra`: 1 -> **0**.
- `columna_falta`: 1 -> **0**.
- `indice_falta`: 1 -> **0**.
- `comment_desalineado`: 1 -> **0**.
- `constraint_sobra`: 1 -> **0**.
- `constraint_falta / fk`: 6 -> **5** (1 resuelto).
- `constraint_falta / check`: 16 -> **16** (sin cambios).

**Fixes aplicados:**

1. **Item 1 - Deprecar `trip.reserva`** (tabla_sobra, D-0001).
   - Eliminada la clase `Reserva` de `app/models/trip.py` (68 lineas).
   - Eliminados los metodos huerfanos `crear_reserva` y `procesar_reserva`
     de `app/services/trip_service.py` (89 lineas).
   - Eliminado `app/models/trip_service.py` (modulo duplicado, roto,
     sin uso).
   - Reescrito `app/routers/reservas.py` sobre `trip.viaje_solicitado`
     (+215/-79 lineas).
   - Mapeo de estados visibles (reservado, despachado, vehiculo_llego,
     pasajero_a_bordo, completado, cancelado) a la maquina canonica de
     `viaje_solicitado` (estado + subestado_despacho).
   - Impacto: -1 item.

2. **Item 2 - Eliminar `usuario_rol.control_base_id`** (columna_falta +
   FK, D-0004 + D-0005).
   - Columna huerfana en DB: 0 filas con valor, 0 referencias en codigo.
   - Comentario en ORM confirma decision previa (commit 2f93716,
     26 Ago 2026).
   - Migracion `m3_014` elimina la columna y su FK.
   - Impacto: -2 items.

3. **Item 3 - Eliminar `ix_contrato_vehiculo_estado_contrato`**
   (indice_falta, D-0016).
   - Indice redundante con `idx_contrato_estado` (misma columna, mismo
     tipo, mismo partial=false).
   - Creado por error en migracion `182d55b83b69` (17 Ago 2026).
   - ORM declara `idx_contrato_estado` como canonico (commit 58a47f0,
     R11).
   - Migracion `m3_014` elimina el indice.
   - Impacto: -1 item.

4. **Item 4 - Quitar `unique=True` de `payment.metodo_pago.nombre`**
   (constraint_sobra, D-0018).
   - La DB no tiene UNIQUE sobre `nombre`.
   - Catalogo sucio (2 duplicados literales, 2 sinonimos, 0 uso real).
   - La limpieza funcional del catalogo queda para R14+.
   - Impacto: -1 item.

5. **Item 5 - Agregar `comment=` a `fleet.turno_chofer.snapshot_dia_contractual`**
   (comment_desalineado, D-0017).
   - Comment en DB: "Dia contractual al inicio del turno (ej. LUNES,
     MARTES). Snapshot inmutable."
   - El ORM no lo declaraba.
   - Impacto: -1 item.

**Migracion aplicada:**

`m3_014` (commit `832ad7b`, aplicada en R13):
- `ALTER TABLE auth.usuario_rol DROP CONSTRAINT fk_usuario_rol_control_base_id_control_base`.
- `ALTER TABLE auth.usuario_rol DROP COLUMN control_base_id`.
- `DROP INDEX fleet.ix_contrato_vehiculo_estado_contrato`.

**Deudas cerradas en R13:**

- `orm.reserva_modulo_activo` (D-0001).
- `orm.unique_constraints_caso_c` (D-0018, ultimo item).
- `orm.indice_redundante_contrato_vehiculo` (D-0016).
- `orm.comment_mojibake` (D-0017, ultimo item).
- `orm.ciclo_fk_usuario_control_base` (parcial: `usuario_rol.control_base_id`).

**Deudas nuevas identificadas en R13:**

- `orm.modulo_duplicado_trip_service`: `app/models/trip_service.py`
  era un duplicado de `app/services/trip_service.py`, roto (importaba
  `Reserva`), sin uso. Eliminado en R13.
- `metodo_pago.catalogo_sucio` (revisada): 12 filas, 2 duplicados
  literales (`efectivo` x2, `mercadopago` x2), 2 sinonimos
  (`billetera`/`wallet`), 2 duplicados semanticos (`credito`/`tarjeta_credito`,
  `debito`/`tarjeta_debito`), 1 valor que es pasarela (`mercadopago`).
  0 transacciones la referencian. La FK `fk_transaccion_metodo_pago_id`
  existe pero esta vacia. Refactor funcional programado para R14+.

**Plan R14:**

- P1: migracion `m3_015` - CHECKs G2a (16 items, ~16 CHECKs sin
  convention). Requiere backup DB + decision de naming
  (`ck_<tabla>_<col>`).
- P2: FKs huerfanas de `trip.viaje_solicitado` (~4 items restantes):
  `empleado_id`, `movimiento_cc_id`, `turno_empleado_id`,
  `cuenta_corriente_id`. Requieren declarar las columnas con
  `ForeignKey` en el ORM (las columnas ya existen, falta la FK).
- P3: refactor funcional de `metodo_pago` (catalogo sucio).

**Ver:** `docs/CONTEXTO_RONDA_13 a 14.md` (handoff, a crear).

## RESUMEN DE RONDA 12 (2026-10-10)

**Objetivo:** migracion m3_013 + CHECKs Grupo 1 (doble prefijo) +
comments residuales + fix de tooling (UNIQUE INDEX vs Index) + FK.

**Resultado:**
- Diff total: 71 -> **27** (-44, -62%).
- Tier 1: 17 -> **7**.
- Tier 2: 46 -> **19**.
- Tier 3: 7 -> **0**.
- Tier 4: 1 -> **1**.
- `constraint_sobra`: 6 -> **1**.
- `comment_desalineado`: 13 -> **1**.
- `constraint_falta`: 49 -> **22**.

**Fixes aplicados:**

1. `m3_013` - agregar 5 UNIQUEs Caso C del ORM a la DB
   (`auth.perfil_general`, `auth.reset_token`, `fleet.vehiculo`,
   `tenant.configuracion_tenant`, `trip.calificacion`). Impacto: -5.

2. Fix de tooling `diff.py` (`_orm_unique_cols` extendido):
   matchea `UniqueConstraint` (DB) contra `Index(unique=True)` (ORM),
   no solo contra `UniqueConstraint`. Impacto: -7 items.

3. Fix de ORM: `unique=True` faltante en
   `fleet.propietario_vehiculo.unique_propietario_vehiculo_activo`.
   Impacto: -1.

4. CHECKs Grupo 1 (doble prefijo) declarados en ORM:
   - `corporate.py`: 2 CHECKs.
   - `fleet.py`: 16 CHECKs (vehiculo, chofer_vehiculo,
     contrato_vehiculo, notificacion_vencimiento, neumaticos).
   Impacto: -18.

5. Comments residuales:
   - Mojibake en `fleet.ingreso_turno` (2 columnas).
   - Tilde faltante en `trip.viaje_solicitado.solicitado_en`.
   - `comment=` agregado a 9 columnas (payment, trip).
   Impacto: -12.

6. FK `corporate.movimiento_cuenta.created_by` declarada en ORM.
   Impacto: -1.

**Deudas cerradas en R12:**
- `orm.unique_constraints_caso_c` (parcial: quedan 2, ver abajo).
- `orm.naming_convention_check_divergente` (parcial: G1).
- `orm.comment_mojibake` (parcial: quedan 1).
- `orm.diff_check_constraints_duplicados` (parcial).
- `orm.unique_constraint_vs_unique_index` (parcial).
- `orm.indice_redundante_contrato_vehiculo` (sigue, ver P4).

**Deudas nuevas identificadas en R12:**
- `orm.ids_diff_no_estables`: los IDs `D-XXXX` de `orm_diff.json` se
  regeneran en cada corrida de `diff.py`. No sirven como identificador
  persistente. Usar `(schema, tabla, columna, clasificacion,
  tipo_constraint, nombre)`.
- `orm.snapshot_orm_stale`: el `orm_snapshot.json` puede quedar
  desactualizado sin que el diff lo detecte. Regenerar siempre antes
  de comparar.
- `orm.columnas_snapshot_turno_faltantes`: 6 columnas `snapshot_*` de
  `fleet.turno_chofer` existen en DB y no en ORM
  (`snapshot_hora_inicio`, `snapshot_hora_fin`,
  `snapshot_duracion_minima_horas`, `snapshot_permite_extension`,
  `snapshot_hora_fin_extension`, `snapshot_dia_contractual`). El diff
  solo reporta 1 (la que tiene COMMENT ON COLUMN).
- `orm.diff_clasifica_mal_columnas_ausentes`: cuando una columna existe
  en DB y no en ORM, el diff la clasifica como `comment_desalineado`
  (no como `columna_falta`) si la DB tiene comment.

**Plan R13:**
- P1: m3_014 - CHECKs Grupo 2 (sin convention, ~16 items). Requiere
  backup DB + decision de naming (`ck_<tabla>_<col>`).
- P2: P4 - decisiones funcionales:
  - `trip.reserva` (tabla_sobra): decidir crear en DB o deprecar.
  - `usuario_rol.control_base_id` (columna_falta): decidir agregar
    en ORM o quitar de DB.
  - `contrato_vehiculo` redundancia (indice_falta): decidir declarar
    en ORM o eliminar en DB.
  - `metodo_pago` (constraint_sobra): limpiar catalogo sucio antes
    de agregar UNIQUE.
  - `snapshot_dia_contractual` y las 5 columnas snapshot restantes:
    decidir declarar en ORM (columna + comment) o deprecar.
- P3: 6 FKs huerfanas de `trip.viaje_solicitado` y `auth.usuario_rol`:
  requieren declarar las columnas primero (depende de P2).

**Ver:** `docs/CONTEXTO_RONDA_12 a 13.md` (handoff).

## RESUMEN DE RONDA 11 (2026-10-08)

**Objetivo:** fix de tooling (diff.py) + Paso 6 residual + Fase 4c +
nullable_desalineado + comments Tipo A. Todo SIN tocar DB.

**Resultado:**
- Diff total: 114 -> **71** (-43, -38%).
- Tier 1: 20 -> **17**.
- Tier 2: 79 -> **46**.
- Tier 3: 14 -> **7**.
- `indice_falta`: 22 -> **1**.
- `tabla_falta`: 10 -> **0**.
- `schema_falta`: 2 -> **0**.
- `nullable_desalineado`: 4 -> **0**.
- `comment_desalineado`: 20 -> **13** (los 13 restantes son mojibake, R12).

**Fixes aplicados:**

1. `diff.py` — nuevo helper `_orm_unique_cols()` + `_is_partial_index()`.
   Matchea `CREATE UNIQUE INDEX` (DB) contra `UniqueConstraint` (ORM) por
   columnas, excluyendo partial indexes. Impacto: -12 items.

2. Paso 6 residual (indices B-tree): declarados 9 indices + UNIQUEs
   compuestos en auth, corporate, fleet y payment.

3. Fase 4c (tablas faltantes): 10 tablas + 2 schemas nuevos
   (comunicacion, rentabilidad). 11 tablas efectivas + 3 tablas nuevas.
   Impacto: -11 items.

4. nullable_desalineado: 4 columnas alineadas a `nullable=False`
   (la DB ya tenia NOT NULL).

5. comments Tipo A: 7 comentarios movidos de `comment=` a `doc=`
   (documentacion interna, no persistida).

**Deudas cerradas en R11:**
- `orm.diff_indexes_colapsa_por_columnas`.
- `orm.geoalchemy2_indices_no_aplicados`.
- `orm.indice_falta` (parcial: 22 -> 1).
- `orm.tabla_falta_ampliada` (10 -> 0).
- `orm.schema_falta` (2 -> 0).
- `orm.nullable_desalineado` (4 -> 0).
- `orm.comment_tipo_a` (7 -> 0).

**Ver:** `docs/CONTEXTO_RONDA_11 a 12.md` (handoff).

---

## RESUMEN DE RONDA 10 (2026-10-06)

**Objetivo:** corregir bugs de tooling (introspector + diff), aplicar
migraciones DDL basicas, limpiar redundancias en ORM.

**Resultado:**
- Diff total: 332 → **114** (−218, −66%).
- Tier 1: 62 → **20**.
- Tier 2: 158 → **79**.
- Tier 3: 111 → **14**.
- `constraint_desalineada`: 72 → **0**.
- `constraint_nombre_desalineado`: 124 → **0**.
- `indice_falta_en_db`: 3 → **0**.

**Descubrimientos clave:**
1. `introspect_db.py` tenia un bug grave: `psycopg2` no adaptaba los
   arrays de `information_schema` a list de Python. Los PKs y UNIQUEs
   del `db_snapshot.json` tenian columnas corruptas
   (`['{','t','o','k','e','n','}']` en vez de `['token']`). Eso generaba
   ~100 falsos positivos en el diff.
2. `diff.py` comparaba nombres de PKs y FKs. La DB tiene dos
   convenciones mezcladas (`<tabla>_pkey` autogenerados + `pk_<tabla>`
   explicitos). El nombre de un PK/FK no tiene semantica funcional.
   Generaba 176 falsos positivos.
3. GeoAlchemy2 auto-genera GIST sobre Geography con `spatial_index=True`
   (default). El ORM los declara implicitamente. La DB no los tenia.

**Fixes aplicados:**
1. `diff_indexes` matchea por `(nombre_normalizado, columnas)` en vez de
   solo columnas (`113f324`).
2. Nueva clasificacion `indice_falta_en_db` para GIST de GeoAlchemy2
   (`113f324`).
3. `trip.py`: restaurar `idx_viaje_origen_gist` + `spatial_index=False`
   en `origen` (`1d4debd`).
4. `auth.py` + `fleet.py`: eliminar `index=True` redundante en columnas
   UNIQUE (`ccead93`).
5. `gasto_turno.py`: alinear nombre de CHECK a la convention (`1af08de`).
6. `diff_constraints`: PKs y FKs matchean por columnas, no por nombre
   (`9520129`).
7. `introspect_db.py`: cast `::text[]` en `array_agg` de
   `information_schema` (`783363b`).

**Migraciones aplicadas:**
- `m3_011` (`783363b`): 3 GIST sobre Geography
  (`fleet.chofer_vehiculo`, `trip.panico`, `trip.viaje_solicitado.destino`).
- `m3_012` (`b8ffd5a`): rename CHECK `gasto_turno_monto_check` →
  `ck_gasto_turno_monto_check`.

**Ver:** `docs/CONTEXTO_RONDA_10 a 11.md` (handoff).

---

## RESUMEN DE RONDA 9 (2026-10-06)

**Objetivo:** fix de `diff.py` (PKs) + limpieza de `indice_sobra`.

**Resultado:**
- Diff total: 404 → **332** (−72, −17.8%).
- `indice_falta`: 86 → **14**.
- Se descubrio que GeoAlchemy2 auto-genera indices GIST sobre columnas
  Geography.

**Fixes aplicados:**
1. Excluir PKs de `indice_falta` en `diff.py` (`1ac1294`).
2. Eliminar B-tree redundante en `fleet.chofer_vehiculo.ubicacion`
   (`158e594`).

**Tag:** `ronda9-fase9-completa` en `a887cc3`.

---

## RESUMEN DE RONDA 8 (2026-10-05)

**Objetivo:** fix de `diff.py` + Fase 6 (indices reales).

**Resultado:**
- Diff total: 877 → **404** (−473, −54%).
- `fleet` schema 100% reconciliado.

**Fixes aplicados:**
1. Fix 1 — Geography case-insensitive en `diff.py` (`6927f08`).
2. Fix 2 — Exclusion de `*_not_null` autogenerados (`d3692f1`).
3. Fix 3 — Doble prefijo `ck_` en `trip.py` (`b2edb4e`).
4. Fase 6 — Todos los indices reales aplicados (~98).

**Tag:** `ronda8-fase6-completa` en `c5bd634`.

---

## BLOQUEANTE PARA PRODUCCION

### B5 — Modelo ViajeSolicitado desactualizado

**Estado:** TECNICAMENTE DESBLOQUEADO. Fase 4a completada en R6.
**Pendiente:** verificacion formal del cierre (Fase 5).

**Ver:** `docs/orm_sync/orm_diff_reporte.md`.

---

## CRITICO

### orm.db_desalineados — ACTUALIZADO 2026-10-06

### orm.db_desalineados — ACTUALIZADO 2026-10-08

**Estado:** CERRADO en R14. Diff BD <-> ORM en 0.

**Datos historicos (post R11):**

| Metrica | Original | R5 | R8 | R9 | R10 | R11 | R14 |
|---|---|---|---|---|---|---|---|
| Tablas faltantes | ~40 | 17 | ~16 | ~16 | 12 (10+2 schemas) | **0** | **0** |
| Columnas faltantes | ~150 | 227 | 1 | 1 | 1 | **1** | **0** |
| Indices faltantes | ~80 | 251 | 86 | 14 | 22 | **1** | **0** |
| Constraints faltantes | ? | 541 | 274 | 61 | 48 | **49** | **0** |
| Diferencias totales | ~500 | 1,280 | 404 | 332 | 114 | **71** | **0** |

**Distribucion por clasificacion (post R14):**
- Todas las clasificaciones en 0.

**Riesgo:** cualquier `alembic revision --autogenerate` es DESTRUCTIVA.
Verificado: ninguna migracion historica uso autogenerate.

**Ver:**
- `docs/orm_sync/orm_diff_reporte.md`
- `docs/orm_sync/db_snapshot.json`
- `docs/orm_sync/orm_snapshot.json`
- `docs/orm_sync/orm_decisiones.md`

## NUEVOS — Ronda 15 (2026-10-11)

### orm.ids_diff_no_estables — NUEVA 2026-10-11

Los IDs `D-XXXX` de `orm_diff.json` se regeneran en cada corrida de
`diff.py`. No sirven como identificador persistente entre rondas.

**Ejemplo:** un mismo item puede ser `D-0001` en una corrida y `D-0042`
en la siguiente.

**Accion futura:** cambiar el generador de IDs en `diff.py` para usar
tuplas estables `(schema, tabla, columna, clasificacion,
tipo_constraint, nombre)`.

**Tier 2.** Toca `diff.py`. Postergado a R16+.

### orm.snapshot_orm_stale — NUEVA 2026-10-11

El `orm_snapshot.json` puede quedar desactualizado si se editan
archivos del ORM sin regenerarlo. El diff entonces reporta falsos
positivos.

**Mitigacion actual:** regenerar siempre antes de comparar (los scripts
`introspect_db.py` + `introspect_orm.py` corren al inicio de cada paso).

**Accion futura:** agregar un timestamp en el snapshot y avisar si
tiene mas de X horas.

**Tier 3.** Postergado.

### orm.diff_clasifica_mal_columnas_ausentes — NUEVA 2026-10-11

Cuando una columna existe en DB y no en ORM, `diff.py` la clasifica
como `comment_desalineado` (no como `columna_falta`) si la DB tiene
comment en esa columna.

**Impacto:** falsos positivos en el reporte.

**Accion futura:** corregir la logica de clasificacion en `diff.py`.

**Tier 3.** Postergado.

### orm.diff_falsos_positivos_tipo_cambio — NUEVA 2026-10-11

Cuando se cambia el tipo o nullable de una columna, `diff.py` puede
reportarla como `columna_falta` en el proximo diff (en vez de
`tipo_desalineado` o `nullable_desalineado`).

**Accion futura:** corregir la deteccion de cambios de tipo en
`diff.py`.

**Tier 3.** Postergado.

### orm.naming_convention_check_doble_prefijo — RESUELTA 2026-10-11

La naming convention de `app/database.py` para CHECKs es
`ck_%(table_name)s_%(constraint_name)s`. Al declarar:

    CheckConstraint("...", name="ck_metodo_pago_nombre")

SQLAlchemy genera `ck_metodo_pago_ck_metodo_pago_nombre` (doble
prefijo).

**Fix:** declarar `CheckConstraint("...", name="nombre")` para que
la convencion genere `ck_metodo_pago_nombre`.

**Documentado en:** este archivo + `m3_016`.

**Estado:** RESUELTA. Aplicar en todos los CHECKs nuevos.

### orm.alembic_check_categoria_a — NUEVA 2026-10-11

`alembic check` reporta ~15 falsos positivos por naming divergente
entre UNIQUE constraints y UNIQUE indexes:

- `comercio_codigo_qr_key` (DB) vs `uq_comercio_codigo_qr` (ORM).
- `usuario_email_key` (DB) vs `uq_usuario_email` (ORM).
- `vehiculo_patente_key` (DB) vs `uq_vehiculo_patente` (ORM).
- `marca_nombre_key` (DB) vs `uq_marca_nombre` (ORM).
- `tipo_usuario_nombre_key` (DB) vs `uq_tipo_usuario_nombre` (ORM).
- `factura_numero_factura_key` (DB) vs `uq_factura_numero_factura` (ORM).
- ~9 mas.

El `diff.py` los considera equivalentes. `alembic check` no.

**Accion:** documentar. NO tocar. Usar `diff.py` como fuente de verdad.

**Tier 3.** Postergado.

### orm.alembic_check_categoria_b — NUEVA 2026-10-11

`alembic check` reporta ~35 items por FKs con `ondelete` distinto
entre ORM y DB. El ORM declara `ondelete` en `ForeignKey(...)`, la DB
no lo tiene aplicado.

Tablas afectadas: log_acciones, log_gps, autorizacion_inicio,
perfil_general, usuario, usuario_rol, chofer_vehiculo, gasto_turno,
gasto_vehiculo, mantenimiento_vehiculo, neumatico_* (7 tablas),
turno_chofer, vehiculo, ciudad, provincia, configuracion_tarifa,
transaccion, configuracion_tenant, control_base, calificacion,
historial_estado_viaje, objeto_olvidado, panico, viaje_solicitado.

**Accion futura:** decidir por cada FK si:
  (a) aplicar ondelete en DB, o
  (b) quitar ondelete del ORM, o
  (c) dejar como deuda aceptada.

**Tier 2.** Postergado a R16+.

### pagos.py_203_billetera — NUEVA 2026-10-11

`app/routers/pagos.py:203` referencia `payment.metodo_pago WHERE
nombre = 'billetera'`. La fila `billetera` fue eliminada del catalogo
en `m3_016` (pertenece al Momento 3 - billetera TaxIP futura).

**Impacto:** el TOP_UP de wallet queda deshabilitado silenciosamente
(0 transacciones afectadas al momento del cambio).

**Accion futura:** implementar la billetera TaxIP, agregar `billetera`
al CHECK de `metodo_pago` y al flujo de pagos.

**Documentado en:** `m3_016` + comentario in-line en `pagos.py:203`.

**Tier 2.** Postergado a cuando se implemente la billetera.

## NUEVOS — Ronda 10 (Fase 10)

### orm.introspect_db_arrays_corruptos — CERRADA 2026-10-06

`psycopg2` no adaptaba arrays de `information_schema` a `list`. El
`db_snapshot.json` tenia PKs y UNIQUEs con columnas corruptas.

**Fix:** `783363b` — cast `::text[]` en `array_agg`.

### orm.diff_nombres_pk_fk — CERRADA 2026-10-06

`diff_constraints` comparaba nombre de PKs y FKs. La DB tiene dos
convenciones mezcladas. 176 falsos positivos.

**Fix:** `9520129` — PK/FK matchean por columnas, no por nombre.

### orm.indice_falta_en_db — CERRADA 2026-10-06

3 GIST de GeoAlchemy2 sin aplicar en DB.

**Fix:** `m3_011` (`783363b`).

### orm.gasto_turno_check_nombre — CERRADA 2026-10-06

CHECK de `fleet.gasto_turno` con nombre divergente entre ORM y DB.

**Fix:** `m3_012` (`b8ffd5a`).

### orm.unique_constraints_caso_c — CERRADA 2026-10-10

5 UNIQUEs que el ORM declaraba y la DB no tenia:
- `auth.perfil_general.usuario_id`
- `auth.reset_token.token`
- `fleet.vehiculo.qr_uuid`
- `tenant.configuracion_tenant.control_base_id`
- `trip.calificacion.viaje_id`

**Fix:** migracion `m3_013` (aplicada en R12).

**Tier 2.**

### metodo_pago.catalogo_sucio — CERRADA 2026-10-11

`payment.metodo_pago` tenia 12 filas con 2 pares de duplicados
(`efectivo` x2, `mercadopago` x2) y valores de otros dominios.

**Fix:** migracion `m3_016` (aplicada en R15). Catalogo limpiado a
4 filas (efectivo, tarjeta_debito, qr, transferencia). UNIQUE + CHECK
agregados.

**Tier 2.**

---

## NUEVOS — Ronda 5 (Fase 1)

### orm.nullable_desalineado — 2026-10-01

4 columnas con nullable divergente entre ORM y DB.
Bug potencial activo: si ORM declara nullable=True pero DB tiene NOT NULL,
los INSERTs del ORM pueden fallar silenciosamente.

**Tier 2.**

**Ver:** `docs/orm_sync/orm_diff_reporte.md`.

### orm.constraint_nombres_numericos — 2026-10-01

2 constraints con nombres autogenerados por Alembic:
- `63669_63825_1_not_null` (trip.viaje_solicitado).
- `63669_63825_38_not_null` (trip.viaje_solicitado).

**Tier 3.** Renombrar en Fase 4.

**Ver:** `docs/orm_sync/orm_decisiones.md` (H-004).

### orm.indices_duplicados — 2026-10-01

Indices duplicados funcionales:
- `idx_viaje_estado` + `ix_viaje_estado` (trip.viaje_solicitado).

**Tier 3.** Eliminar uno en Fase 4.

### orm.system_tables_whitelist — 2026-10-01

`public.alembic_version` y `public.spatial_ref_sys` son tablas de sistema.
No deben considerarse parte del diff.

**Accion:** whitelist en `diff.py` (ya implementado).

---

## NUEVOS — Ronda 6 (Fase 2, Sesion 1)

### orm.reserva_modulo_activo — CERRADA 2026-10-10

La tabla `trip.reserva` NO existia en DB, pero el modulo de reservas
corporativas la usaba. Los endpoints `/api/reservas` estaban rotos.

**Fix:** migracion y refactor en R13. Modulo reescrito sobre
`trip.viaje_solicitado`.

### orm.foto_viaje_out_of_scope — NUEVA 2026-10-02

El item D-1125 (`foto_viaje.created_at` nullable desalineado) NO esta en
`trip.py`, esta en `app/models/foto_viaje.py`. Pendiente Fase 4d.

**Tier 2.**

### metodo_pago.fk_catalogo — NUEVA 2026-10-01

Refactor estructural: evaluar FK por `metodo_pago_id` en
`trip.viaje_solicitado` y `fleet.ingreso_turno` (en vez de string).

**Tier 2.** Refactor grande.

### metodo_pago.ingreso_turno — NUEVA 2026-10-01

`fleet.ingreso_turno.medio_pago`:
- Comment en DB: 6 valores. Sin CHECK.
- Datos reales: solo 2 valores (efectivo=57, debito=16).
- ORM: comment divergente, 4 valores.

**Tier 2.** Alinear comment del ORM con DB en Fase 4.

### metodo_pago.frontend_e2 — NUEVA 2026-10-01

MetodoPago del frontend limitado a 4 valores (deuda E2 original).

**Tier 3.** Resolver si se decide ampliar vocabulario.

---

## NUEVOS — Ronda 7 (Fase 4b)

### datos.turno_chofer_km_final_outlier — NUEVA 2026-10-03

`fleet.turno_chofer.km_final` tiene un valor maximo de 1.523.999,00 km,
irreal para un taxi urbano.

**Tier 3.** Revisar registros con `km_final > 500000` en ronda de limpieza.

### orm.snapshot_desactualizado — NUEVA 2026-10-03

Practica preventiva: el `orm_snapshot.json` puede quedar desactualizado
si se editan archivos del ORM sin regenerarlo.

**Tier 2.** Regenerar snapshots al inicio de cada paso.

### orm.diff_falsos_positivos_tipo_cambio — NUEVA 2026-10-03

Cuando se cambia el tipo o nullable de una columna, `diff.py` puede
reportarla como `columna_falta` en el proximo diff.

**Tier 2.** Postergado.

### orm.diff_check_constraints_duplicados — NUEVA 2026-10-03

`diff.py` compara CHECKs por nombre. Cuando el ORM declara un CHECK con
`name="X"` y la DB lo tiene con `name="ck_<tabla>_X"`, el diff los cuenta
como 2 items distintos.

**Tier 2.** Parcialmente mitigado por Fix 2 de R8.

### orm.naming_convention_check_divergente — CERRADA 2026-10-11

La naming convention de `app/database.py` para CHECKs es
`ck_%(table_name)s_%(constraint_name)s`. La DB tenia CHECKs con nombres
que NO seguian esa convention.

**Fix:** migracion `m3_015` (aplicada en R14). 16 CHECKs renombrados
al naming canonico.

**Tier 2.**

### orm.paso4_check_constraints_residual — CERRADA 2026-10-11

Los 8 CHECKs de `trip.viaje_solicitado` alineados en R8.
`gasto_turno_monto_check` alineado en R10.
16 CHECKs G2a alineados en R14.

**Fix:** migracion `m3_015` (R14).

**Tier 2.**

### orm.alembic_check_ruidoso — ACTUALIZADO 2026-10-11

`alembic check` reporta cientos de operaciones de upgrade pendientes
porque la DB y el ORM representan constraints de forma distinta
(UNIQUE constraint vs index, nombres de FK, ondelete).

**Estado R15:** las categorias C (indice faltante) y D (comments de
tabla) fueron cerradas. Las categorias A (naming divergente) y B
(ondelete) quedan como deuda aceptada.

**Accion:** documentar. NO usar `alembic check` como gate. Usar
`diff.py` como fuente de verdad.

**Tier 2.** Investigado en R15, no resuelto (postergado).

---

## NUEVOS — Ronda 8 (Fase 6 + fixes)

### orm.unique_constraint_vs_unique_index — CERRADA 2026-10-11

El ORM declaraba `UniqueConstraint` y la DB tenia `CREATE UNIQUE INDEX`.
Funcionalmente equivalentes.

**Fix:** resuelto via `diff.py` matcheando por columnas + `m3_013` para
los UNIQUEs faltantes + `m3_016` para el catalogo sucio.

**Tier 2.**

### orm.comercio_indice_redundante — NUEVA 2026-10-05

`public.comercio.idx_comercio_codigo_qr` es redundante con el UNIQUE
constraint `comercio_codigo_qr_key`.

**Tier 3.** Evaluar eliminacion en ronda de optimizacion.

### orm.tabla_falta_ampliada — CERRADA 2026-10-08

Tablas faltantes (~16) creadas en R11 (Fase 4c):
- `comunicacion.conversacion`, `comunicacion.email_enviado`,
  `comunicacion.mensaje`.
- `rentabilidad.analisis_medios_pago`,
  `rentabilidad.rentabilidad_diaria_vehiculo`,
  `rentabilidad.rentabilidad_mensual_vehiculo`.
- `auth.codigo_metadatos`, `auth.codigo_verificacion`,
  `auth.plantilla_viaje`, `auth.prestadora_telefonica`.
- `payment.qr_cobro`, `payment.configuracion_pasarela`.
- `audit.alertas_vencimiento`.
- `trip.broadcast_log`.
- `fleet.historial_chofer_vehiculo`,
  `fleet.relacion_propietario_vehiculo`.

**Tier 2.**

### metodo_pago.pasarela — CERRADA 2026-10-08

Las tablas `payment.qr_cobro` y `payment.configuracion_pasarela`
estaban en DB pero no en ORM.

**Fix:** R11 (Fase 4c).

**Tier 2.**

---

## NUEVOS — Ronda 9 (Paso 9)

### orm.indice_sobra_ambiguo — RESUELTA 2026-10-06

`diff.py` clasificaba como `indice_sobra` GIST auto-generados por
GeoAlchemy2. Reclasificados como `indice_falta_en_db` y aplicados via
`m3_011`.

### orm.geoalchemy2_indices_no_aplicados — CERRADA 2026-10-06

3 GIST declarados por ORM (via GeoAlchemy2), ausentes en DB.

**Fix:** `m3_011` (`783363b`).

### orm.diff_indexes_colapsa_por_columnas — CERRADA 2026-10-06

`diff.py` matcheaba indices por `tuple(columns)`. Si el ORM declaraba
dos indices sobre la misma columna, solo uno aparecia.

**Fix:** `113f324` — matching por `(nombre_normalizado, columnas)`.

---

## ALTA PRIORIDAD

### G63 — Alerta si el motor de precios cae a fallback

`precio_final` puede caer a `precio_estimado` si el motor unificado falla.
Requiere infra de monitoreo (Sentry, Grafana o similar). Fase 2.

### G67 — check_out_turno sin escapatoria si hay viajes huerfanos

El chofer queda atrapado sin poder cerrar turno. Requiere decision de
negocio: auto-cancelar huerfanos con motivo, o boton "forzar cierre".

### G80 — App apunta a Metro (no funciona fuera de WiFi dev)

La app en el celular apunta a 192.168.1.14:8081. Para pruebas en terreno:
build preview o production apuntando al backend publico.

---

## MEDIA PRIORIDAD

### F5 — ViajeSolicitado.origen_lat/lng vs ViajeActivo.origen

Numeros sueltos vs Coordenada. Mapear en el store al conectar el WS.

### F6 — auth.codigo_metadatos es tabla separada

El INSERT en codigo_verificacion solo no alcanza. Documentar en flujo
del propietario.

### G68 — Job procesar_viajes_huerfanos corre cada 1h

Bajar a 15 min si en produccion se ve friccion.

### G70 — Confusion de paths public/viajes

Existen tres (backend publico, proxy dashboard, helper dashboard), uno
huerfano. Renombrar o documentar.

### G72 — Regla de pegado sin tildes desde chat

Refuerza N10. Nunca pegar bloques con tildes/emojis desde el chat al
editor. Comentarios en codigo pegado: ASCII puro.

### G74 — Endpoint /api/viajes/solicitar deprecado

Sigue en codigo. Eliminar en Fase 2.

### G76 — Worker de uvicorn a veces carga version vieja

Tras un cambio en un archivo que importa otro modulo modificado.
Verificar LastWriteTime vs StartTime del proceso Python.

### G81 — DB y modelos ORM desincronizados silenciosamente

Sintoma: INSERTs fallan por columna inexistente, sin error visible.
**Relacionado con:** `orm.db_desalineados` (cerrado en R14).

### J15 — No hay deteccion de viaje activo al abrir la app

Plan: endpoint GET /api/chofer/viaje-activo + chequeo en
`(app)/_layout.tsx`.

### metodo_pago.flujo_propietario — 2026-09-30

`liquidacion.py:329`, `fleet.py:875/880` (comments de IngresoTurno).
Dominio: como el propietario le paga al chofer.
Vocabulario propio por definir.

### metodo_pago.flujo_empresa — 2026-09-30

`empresa_dashboard.py:790`. Dominio: como la empresa le paga a TaxIP.
Requiere vocabulario propio.

### metodo_pago.recaudacion — 2026-09-30

`schemas/recaudacion_schemas.py:22`. Alinear cuando se toque ese modulo.

### flujo_caja.ingreso_turno — ACTUALIZADO 2026-10-01

Comments de `tipo_ingreso`, `medio_pago`, `origen` mezclan vocabularios.
`medio_pago` con espacio final en el comment.

**Accion:** alinear comment del ORM con DB y canonizar vocabulario.

### G82 — 2026-09-30

`run.py` tiene `reload=True` hardcodeado. Contradice N14.
Propuesta: `reload=os.getenv("RELOAD", "false").lower() == "true"`.

---

## BAJA PRIORIDAD

### Backend heredadas

- **A1** — Modelo Reserva apunta a tabla dropeada (trip.reserva).
  **RESUELTA en R13** (modulo deprecado).
- **A2** — Schemas legacy snake_case mezclados en viajes/schemas.py.
- **A5** — ~22 warnings Duplicate Operation ID en neumaticos OpenAPI.

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
- **logs.auth_prints** — `routers/auth.py:289` con print con emoji.
- **orm_viaje.fk_comercio_schema** — FK de `viaje_solicitado.comercio_id`
  apunta a `comercio(id)` sin schema.

---

## DEUDAS DE EXPO-ROUTER CON REACT 19 (workaround activo)

- **G77** — Bug de expo-router 57.0.24 con React 19 (2 useEffect sin deps).
- **G78** — Workaround: 2 parches en `patches/expo-router+57.0.24.patch`.
- **G79** — Workflow de compilacion migrado a EAS Build.

Cuenta: megarcia34. Proyecto: @megarcia34/taxip-chofer.
projectId: b54c9f37-bdd0-4845-8c78-9628a3cda6a2.
**No tocar hasta que expo saque fix upstream.**

---

## CERRADAS EN RONDA 15 (2026-10-11)

### Deuda tecnica funcional — P1 (metodo_pago)

- **metodo_pago.catalogo_sucio** — CERRADA. Catalogo limpiado de 12 a
  4 filas (efectivo, tarjeta_debito, qr, transferencia). UNIQUE + CHECK
  agregados. Migracion `m3_016`. Commit `44c5147`.

### Deuda tecnica — P2 (alembic check)

- **orm.alembic_check_categoria_c** (ix_qr_cobro_token) — CERRADA.
  Indice redundante eliminado. Migracion `m3_017`. Commit `ad24c66`.
- **orm.alembic_check_categoria_d** (5 comments de tabla) — CERRADA.
  Comments declarados en ORM + corregidos en DB. Migracion `m3_017`.
  Commit `ad24c66`.
- **orm.comment_mojibake** — CERRADA (los 3 residuales de R12).
  Comments de `fleet.contrato_qr` y `fleet.documentos_chofer`
  corregidos.

### Deuda tecnica — P3 (tooling)

- **orm.ids_diff_no_estables** — documentada. Postergada.
- **orm.snapshot_orm_stale** — documentada. Postergada.
- **orm.diff_clasifica_mal_columnas_ausentes** — documentada.
  Postergada.
- **orm.diff_falsos_positivos_tipo_cambio** — documentada.
  Postergada.

### Deuda nueva descubierta en R15

- **orm.naming_convention_check_doble_prefijo** — RESUELTA.
  Documentada para evitar reaparicion.
- **orm.alembic_check_categoria_a** — documentada. Postergada.
- **orm.alembic_check_categoria_b** — documentada. Postergada.
- **pagos.py_203_billetera** — documentada. Postergada a cuando
  se implemente la billetera.

---

## CERRADAS EN RONDA 10 (2026-10-06)

### Fixes de tooling

- **orm.introspect_db_arrays_corruptos** — CERRADA. Cast `::text[]` en
  `array_agg` de `information_schema` (`783363b`).
- **orm.diff_nombres_pk_fk** — CERRADA. PK/FK matchean por columnas
  (`9520129`).
- **orm.diff_indexes_colapsa_por_columnas** — CERRADA. Matching por
  `(nombre, columnas)` (`113f324`).

### Fixes del ORM

- **trip.py** — Restaurado `idx_viaje_origen_gist` + `spatial_index=False`
  en `origen` (`1d4debd`).
- **auth.py + fleet.py** — Eliminado `index=True` redundante (`ccead93`).
- **gasto_turno.py** — Alineado CHECK a la convention (`1af08de`).

### Migraciones

- **m3_011** — 3 GIST sobre Geography (`783363b`).
- **m3_012** — Rename CHECK `gasto_turno` (`b8ffd5a`).

---

## RECUENTO

| Categoria | Cantidad |
|---|---|
| Bloqueante | 1 |
| Critico | 1 |
| Nuevos Ronda 5 | 5 |
| Nuevos Ronda 6 (Fase 2) | 4 |
| Nuevos Ronda 7 (Fase 4b) | 7 |
| Nuevos Ronda 8 (Fase 6) | 3 |
| Nuevos Ronda 9 (Paso 9) | 3 (2 cerradas, 1 resuelta) |
| Nuevos Ronda 10 (Fase 10) | 5 (4 cerradas, 1 nueva) |
| **Nuevos Ronda 15** | **8 (1 resuelta, 7 documentadas)** |
| Alta prioridad | 3 |
| Media prioridad | 15 |
| Baja prioridad | 21 |
| Expo-router / EAS | 3 |
| **TOTAL PENDIENTES** | **~114 (items del diff) + deudas no-diff** |

**Notas:**
- El diff BD <-> ORM esta en 0 desde R14. R15 se enfoco en deuda
  funcional (metodo_pago) y de proceso (alembic check, tooling).
- Las deudas no-diff (G63, G67, etc.) son items aparte que no entran
  en el diff pero estan pendientes de resolucion.
- Las 8 deudas de R15 son todas de tooling/documentacion, excepto
  `metodo_pago.catalogo_sucio` que ya fue cerrada (P1).

---

## REFERENCIAS

- **Plan de reconciliacion:** `docs/orm_reconciliacion_plan.md`
- **Snapshots:** `docs/orm_sync/`
- **Reporte diff:** `docs/orm_sync/orm_diff_reporte.md`
- **Decisiones:** `docs/orm_sync/orm_decisiones.md`
- **Historico:** `docs/HISTORICO_CERRADAS.md`
- **Baseline:** `docs/orm_sync/baseline_info.md`
- **Handoff R9→R10:** `docs/CONTEXTO_RONDA_9 a 10.md`
- **Handoff R10→R11:** `docs/CONTEXTO_RONDA_10 a 11.md`
- **Handoff R14→R15:** `docs/CONTEXTO_RONDA_14 a 15.md`
- **Contexto R15:** `docs/CONTEXTO_RONDA_15.md`
- **Alembic check cierre R8:** `docs/orm_sync/alembic_check_cierre_r8_2026-10-05.txt`
- **Alembic check R15:** `docs/orm_sync/alembic_check_r15_2026-10-11.txt`
- **Backups:** `docs/backups/`
- **Bitacoras:** `E:\Taxip\app chofer\BITACORA_M1.md`, `M2`, `M3`.

---

**FIN DEL DOCUMENTO**