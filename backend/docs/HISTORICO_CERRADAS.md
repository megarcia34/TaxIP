# HISTORICO DE RONDAS CERRADAS — TaxIP 2.0

**Ultima actualizacion:** 2026-10-12
**Proposito:** registro historico de rondas cerradas, fixes aplicados,
migraciones y commits. NO contiene deuda pendiente.

**Deuda pendiente:** ver `docs/DEUDA_TECNICA_ACTUAL.md`.
**Decisiones tecnicas ORM:** ver `docs/orm_sync/orm_decisiones.md`.

---

## Indice

- [Ronda 16 (2026-10-12)](#ronda-16-2026-10-12)
- [Ronda 15 (2026-10-11)](#ronda-15-2026-10-11)
- [Ronda 14 (2026-10-11)](#ronda-14-2026-10-11)
- [Ronda 13 (2026-10-10)](#ronda-13-2026-10-10)
- [Ronda 12 (2026-10-10)](#ronda-12-2026-10-10)
- [Ronda 11 (2026-10-08)](#ronda-11-2026-10-08)
- [Ronda 10 (2026-10-06)](#ronda-10-2026-10-06)
- [Ronda 9 (2026-10-06)](#ronda-9-2026-10-06)
- [Ronda 8 (2026-10-05)](#ronda-8-2026-10-05)
- [Ronda 7 (2026-10-03)](#ronda-7-2026-10-03)
- [Ronda 6 (2026-10-02)](#ronda-6-2026-10-02)
- [Ronda 5 (2026-10-01)](#ronda-5-2026-10-01)

---

## Ronda 16 (2026-10-12)

**Objetivo:** quick wins de deuda tecnica. Bajar ~10 items en ~5 horas
con bajo riesgo, atacando cosmeticos, indices redundantes, tooling y
codigo legacy.

**Resultado:**
- Bloque A - Cosmeticos + config: CERRADO.
- Bloque B - DB limpia: CERRADO.
- Bloque C - Tooling: CERRADO.
- Bloque D - Codigo limpio: CERRADO.

**Fixes aplicados:**

1. **Bloque A - G82 + A5** (commit `4182613`):
   - G82: `run.py` reload controlado por env var (`RELOAD=true/false`).
   - A5: eliminado include_router duplicado de neumaticos en `main.py`.
     Baja los 22 warnings `Duplicate Operation ID` a 0.

2. **Bloque B - Migracion `m3_018`** (commit `284d0ac`):
   - Eliminado `trip.ix_viaje_estado` (redundante con `idx_viaje_estado`).
   - Eliminado `public.idx_comercio_codigo_qr` (redundante con
     `comercio_codigo_qr_key` UNIQUE).
   - `orm.constraint_nombres_numericos`: falso positivo (no existen).
   - ORM: quitados los 2 Index en `app/models/trip.py` y `app/models/public.py`.

3. **Bloque C - Tooling** (commit `cc93fed`):
   - `orm.ids_diff_no_estables`: IDs ahora son hash estable
     `D-<hash8>` basado en `(schema, tabla, columna, clasificacion,
     tipo_constraint, nombre)`. Deterministico entre corridas.
   - `orm.diff_clasifica_mal_columnas_ausentes`: falso positivo.

4. **Bloque D - Codigo limpio** (commit `8f08e24`):
   - G74: eliminado endpoint legacy `POST /api/viajes/solicitar` (0
     clientes reales).
   - `logs.auth_prints`: 35 `print` con emoji convertidos a
     `logger.info/warning/error`. Emojis mantenidos.
   - `main.py`: `reconfigure(encoding='utf-8')` en stdout/stderr.

**Migraciones aplicadas:**

- `m3_018`: drop indices redundantes (`ix_viaje_estado`,
  `idx_comercio_codigo_qr`).

**Commits de la ronda:** `4182613`, `284d0ac`, `cc93fed`, `8f08e24`.

**Tag:** `ronda16-fase16-completa`.

---

## Ronda 15 (2026-10-11)

**Objetivo:** resolver deuda tecnica FUNCIONAL (no estructural).
La alineacion estructural BD <-> ORM quedo completa en R14; R15 ataca
las deudas funcionales y de proceso que el diff no captura.

**Resultado:**
- P1 - metodo_pago catalogo sucio: CERRADO.
- P2 - alembic check categorias C y D: CERRADO.
- P3 - tooling: documentado (no resuelto).
- P4 - documentacion: cerrada.

**Fixes aplicados:**

1. **P1 - Migracion `m3_016` limpiar catalogo metodo_pago** (commit `44c5147`):
   - Catalogo `payment.metodo_pago` limpiado de 12 a 4 filas.
   - Vocabulario canonico Momento 1: efectivo, tarjeta_debito, qr, transferencia.
   - Filas eliminadas: efectivo duplicado, tarjeta_credito, billetera,
     wallet, credito, debito, mercadopago x2.
   - Agregado UNIQUE sobre nombre (`uq_metodo_pago_nombre`).
   - Agregado CHECK con vocabulario canonico (`ck_metodo_pago_nombre`).
   - Fix adicional: `payment_schemas.py:20` default `mercadopago` -> `efectivo`.

2. **P2 - Migracion `m3_017` drop indice redundante + comments de tabla**
   (commit `ad24c66`):
   - Eliminado `payment.ix_qr_cobro_token` (redundante con `uq_qr_cobro_token`).
   - 5 comments de tabla agregados al ORM y actualizados en DB.

**Migraciones aplicadas:**

- `m3_016`: limpiar catalogo metodo_pago + UNIQUE + CHECK.
- `m3_017`: drop ix_qr_cobro_token + 5 comments de tabla.

**Deudas cerradas:**

- `metodo_pago.catalogo_sucio`.
- `orm.alembic_check_categoria_c`.
- `orm.alembic_check_categoria_d`.
- `orm.comment_mojibake` (3 residuales).

**Tag:** `ronda15-fase15-completa`.

---

## Ronda 14 (2026-10-11)

**Objetivo:** cerrar los 21 items restantes del diff (16 CHECKs G2a +
5 FKs huerfanas) y alcanzar la alineacion completa BD <-> ORM.

**Resultado:**
- Diff total: 21 -> 0 (-21, -100%).
- Tier 1: 6 -> 0.
- Tier 2: 15 -> 0.
- LA ALINEACION BD <-> ORM ESTA COMPLETA.

**Fixes aplicados:**

1. **Fase R14.3 - Declarar 5 FKs en ORM** (commit `17f4d6d`).
2. **Fase R14.1 - Migracion `m3_015`** (commit `3db3e7b`):
   16 CHECKs renombrados al naming canonico.
3. **Fase R14.2 - Declarar 16 CHECKs en ORM** (commits `0f4434c`,
   `f7c7413`, `60bd195`, `80c030b`, `ed589a6`).

**Migracion aplicada:** `m3_015`.

**Deudas cerradas:**

- `orm.naming_convention_check_divergente` (Grupo 2).
- `orm.paso4_check_constraints_residual`.

**Tag:** `ronda14-fase14-completa`.

---

## Ronda 13 (2026-10-10)

**Objetivo:** cerrar 6 items del diff + refactor del router `/api/reservas`.

**Resultado:**
- Diff total: 27 -> 21 (-6, -22%).

**Fixes aplicados:**

1. **Deprecar `trip.reserva`**: eliminada la clase `Reserva`, metodos
   huerfanos, `app/models/trip_service.py`. Reescrito `reservas.py`
   sobre `trip.viaje_solicitado`.
2. **Eliminar `usuario_rol.control_base_id`**: columna huerfana.
3. **Eliminar `ix_contrato_vehiculo_estado_contrato`**: indice redundante.
4. **Quitar `unique=True` de `payment.metodo_pago.nombre`**.
5. **Agregar `comment=` a `fleet.turno_chofer.snapshot_dia_contractual`**.

**Migracion aplicada:** `m3_014`.

**Tag:** `ronda13-fase13-completa`.

---

## Ronda 12 (2026-10-10)

**Objetivo:** migracion m3_013 + CHECKs Grupo 1 (doble prefijo) +
comments residuales + fix de tooling (UNIQUE INDEX vs Index) + FK.

**Resultado:**
- Diff total: 71 -> 27 (-44, -62%).

**Fixes aplicados:**

1. `m3_013`: 5 UNIQUEs Caso C agregados a DB.
2. Fix de tooling `diff.py` (`_orm_unique_cols` extendido).
3. Fix de ORM: `unique=True` faltante en `propietario_vehiculo`.
4. CHECKs Grupo 1 (doble prefijo) declarados en ORM.
5. Comments residuales (mojibake + tilde).
6. FK `corporate.movimiento_cuenta.created_by` declarada.

**Migracion aplicada:** `m3_013`.

**Tag:** `ronda12-fase12-completa`.

---

## Ronda 11 (2026-10-08)

**Objetivo:** fix de tooling (`diff.py`) + Paso 6 residual + Fase 4c +
nullable_desalineado + comments Tipo A.

**Resultado:**
- Diff total: 114 -> 71 (-43, -38%).

**Fixes aplicados:**

1. `diff.py`: helper `_orm_unique_cols()` + `_is_partial_index()`.
2. Paso 6 residual (9 indices B-tree).
3. Fase 4c: 10 tablas + 2 schemas nuevos.
4. nullable_desalineado: 4 columnas alineadas.
5. comments Tipo A: 7 comentarios movidos de `comment=` a `doc=`.

**Tag:** `ronda11-fase11-completa`.

---

## Ronda 10 (2026-10-06)

**Objetivo:** corregir bugs de tooling (introspector + diff), aplicar
migraciones DDL basicas, limpiar redundancias en ORM.

**Resultado:**
- Diff total: 332 -> 114 (-218, -66%).

**Descubrimientos clave:**

1. `introspect_db.py` bug: `psycopg2` no adaptaba arrays.
2. `diff.py` comparaba nombres de PKs y FKs.
3. GeoAlchemy2 auto-genera GIST sobre Geography.

**Migraciones aplicadas:** `m3_011`, `m3_012`.

**Tag:** `ronda10-fase10-completa`.

---

## Ronda 9 (2026-10-06)

**Objetivo:** fix de `diff.py` (PKs) + limpieza de `indice_sobra`.

**Resultado:**
- Diff total: 404 -> 332 (-72, -17.8%).

**Fixes aplicados:**

1. Excluir PKs de `indice_falta` en `diff.py` (`1ac1294`).
2. Eliminar B-tree redundante en `fleet.chofer_vehiculo.ubicacion`
   (`158e594`).

**Tag:** `ronda9-fase9-completa`.

---

## Ronda 8 (2026-10-05)

**Objetivo:** fix de `diff.py` + Fase 6 (indices reales).

**Resultado:**
- Diff total: 877 -> 404 (-473, -54%).
- `fleet` schema 100% reconciliado.

**Fixes aplicados:**

1. Geography case-insensitive en `diff.py` (`6927f08`).
2. Exclusion de `*_not_null` autogenerados (`d3692f1`).
3. Doble prefijo `ck_` en `trip.py` (`b2edb4e`).
4. Fase 6: todos los indices reales aplicados (~98).

**Tag:** `ronda8-fase6-completa`.

---

## Ronda 7 (2026-10-03)

**Objetivo:** Fase 4b (fleet.py).

**Resultado:** `fleet.py` items reducidos significativamente.

**Tag:** `ronda7-fase4b-completa`.

---

## Ronda 6 (2026-10-02)

**Objetivo:** Fase 2 (Sesion 1). Modelos `viaje_solicitado`,
`chofer_vehiculo`, `turno_chofer`, `control_base`, `ingreso_turno`.

**Resultado:** B5 tecnicamente desbloqueado.

---

## Ronda 5 (2026-10-01)

**Objetivo:** diagnostico estructurado (Fase 1). Scripts de introspeccion
y diff.

**Resultado:** baseline del diff (~1280 items).

**Tag:** `ronda5-baseline-pre`.

---

## Referencias

- **Deuda pendiente:** `docs/DEUDA_TECNICA_ACTUAL.md`
- **Decisiones tecnicas:** `docs/orm_sync/orm_decisiones.md`
- **Handoffs:** `docs/CONTEXTO_RONDA_N a N+1.md`
- **Snapshots:** `docs/orm_sync/`

---

**FIN DEL DOCUMENTO**