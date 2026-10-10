"""
diff.py - Compara db_snapshot.json vs orm_snapshot.json.

Produce 3 archivos:
- orm_diff.json          : datos estructurados completos.
- orm_diff_reporte.md    : informe humano resumido.
- orm_diff_acciones.csv  : CSV de acciones sugeridas para Fase 2.

Uso:
    python scripts/orm_sync/diff.py
    python scripts/orm_sync/diff.py --db=docs/orm_sync/db_snapshot.json --orm=docs/orm_sync/orm_snapshot.json
    python scripts/orm_sync/diff.py --output-dir=docs/orm_sync
"""

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# Paths absolutos
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_DB = PROJECT_ROOT / "docs" / "orm_sync" / "db_snapshot.json"
DEFAULT_ORM = PROJECT_ROOT / "docs" / "orm_sync" / "orm_snapshot.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "docs" / "orm_sync"


# ============================================================
# Constantes
# ============================================================

SYSTEM_TABLES = {
    ("public", "alembic_version"),
    ("public", "spatial_ref_sys"),
}

TIER_1_TABLES = {
    ("trip", "viaje_solicitado"),
    ("fleet", "turno_chofer"),
    ("fleet", "ingreso_turno"),
    ("fleet", "chofer_vehiculo"),
    ("fleet", "vehiculo"),
    ("tenant", "control_base"),
    ("auth", "usuario"),
    ("auth", "codigo_verificacion"),
    ("auth", "codigo_metadatos"),
    ("trip", "historial_estado_viaje"),
    ("trip", "calificacion"),
    ("payment", "transaccion"),
}

TIER_4_TABLES = {
    ("trip", "reserva"),
}


# Patron de nombres autogenerados por Alembic para NOT NULL.
# Formato: <oid1>_<oid2>_<ordinal>_not_null
# Estos CHECKs no son declarados por el ORM y no representan deuda real.
RE_NOT_NULL_AUTOGEN = re.compile(r"^\d+_\d+_\d+_not_null$")


# Patron de nombres de indices de PRIMARY KEY.
# Postgres los nombra <tabla>_pkey o pk_<tabla>; SQLAlchemy no los declara
# como Index (van via primary_key=True). Excluirlos evita 72 falsos positivos
# de indice_falta (deuda orm.indice_falta_incluye_pks).
RE_PK_INDEX = re.compile(r"^(pk_.+|.+_pkey)$")

# Patron de nombres de indices GIST auto-generados por GeoAlchemy2 sobre
# columnas Geography. Formato: idx_<tabla>_<columna>.
# El ORM los declara implicitamente via spatial_index=True (default);
# la DB no los tiene. NO son indice_sobra (no hay que borrarlos del ORM),
# son indice_falta_en_db (requieren migracion Alembic).
RE_GEOALCHEMY2_INDEX = re.compile(r"^idx_.+_.+$")


def _is_geoalchemy2_gist(idx):
    """True si el indice parece auto-generado por GeoAlchemy2.

    Heuristica: nombre matchea idx_<tabla>_<columna> y el indice usa
    GIST (postgresql_using == 'gist' o definition contiene 'USING gist').
    """
    name = idx.get("name") or ""
    if not RE_GEOALCHEMY2_INDEX.match(name):
        return False
    using = (idx.get("postgresql_using") or "").lower()
    definition = (idx.get("definition") or "").lower()
    return using == "gist" or "using gist" in definition


# ============================================================
# Logging
# ============================================================

VERBOSE = False


def log(msg, level="INFO"):
    print(f"[diff] [{level}] {msg}")


def log_verbose(msg):
    if VERBOSE:
        log(msg, "DEBUG")


# ============================================================
# Carga de snapshots
# ============================================================

def load_json(path):
    log(f"Cargando: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"ERROR cargando {path}: {e}", "ERROR")
        sys.exit(1)


# ============================================================
# Clasificacion y Tier
# ============================================================

def assign_tier(schema, tabla, clasificacion):
    """Asigna Tier a un item del diff."""
    if (schema, tabla) in TIER_1_TABLES:
        return 1
    if (schema, tabla) in TIER_4_TABLES:
        return 4
    if (schema, tabla) in SYSTEM_TABLES:
        return None  # ignorar

    if clasificacion == "schema_falta":
        return 2
    if clasificacion in ("comment_desalineado", "constraint_nombre_desalineado",
                         "indice_nombre_desalineado"):
        return 3
    if clasificacion in ("indice_falta", "indice_sobra", "indice_falta_en_db"):
        return 2
    if clasificacion.startswith("columna_"):
        return 2
    if clasificacion.startswith("constraint_"):
        return 2
    if clasificacion.startswith("tabla_"):
        return 2

    return 2


def detect_requires_decision(schema, tabla, columna, clasificacion, detalle):
    """Detecta si un item requiere decision manual."""
    # Caso 1: tenant.control_base.latitud/longitud
    if (schema, tabla) == ("tenant", "control_base") and columna in ("latitud", "longitud"):
        return True, "orm_mal_db_bien"

    # Caso 2: timestamps naive
    if clasificacion == "tipo_desalineado":
        db_type = (detalle.get("db") or {}).get("type", "") or ""
        orm_type = (detalle.get("orm") or {}).get("type", "") or ""
        if "timestamp without time zone" in db_type.lower() and "timestamp with time zone" in orm_type.lower():
            return True, "timestamp_naive_vs_tz"

    # Caso 3: comment con vocabulario de metodo_pago
    if clasificacion == "comment_desalineado":
        db_comment = ((detalle.get("db") or {}).get("comment") or "")
        if "efectivo" in db_comment.lower() and "qr" in db_comment.lower():
            return True, "vocabulario_metodo_pago"

    # Caso 4: auth.codigo_verificacion + auth.codigo_metadatos (J9)
    if (schema, tabla) in [("auth", "codigo_verificacion"), ("auth", "codigo_metadatos")]:
        return True, "j9_dos_fuentes_de_verdad"

    return False, None


# ============================================================
# Comparacion: schemas
# ============================================================

def diff_schemas(db, orm):
    """Compara schemas de DB vs ORM."""
    diff = []

    db_schemas = set(db["schemas"].keys())
    orm_schemas = set(orm["schemas"].keys())

    solo_db = sorted(db_schemas - orm_schemas)
    solo_orm = sorted(orm_schemas - db_schemas)

    for schema in solo_db:
        if schema in ("public",):  # public solo aporta system tables
            continue
        n_tables = len(db["schemas"][schema]["tables"])
        diff.append({
            "id": None,
            "clasificacion": "schema_falta",
            "schema": schema,
            "tabla": None,
            "columna": None,
            "detalle": {
                "db": {"n_tables": n_tables, "tables": list(db["schemas"][schema]["tables"].keys())},
                "orm": None,
            },
        })

    for schema in solo_orm:
        diff.append({
            "id": None,
            "clasificacion": "schema_sobra",
            "schema": schema,
            "tabla": None,
            "columna": None,
            "detalle": {
                "db": None,
                "orm": {"tables": list(orm["schemas"][schema]["tables"].keys())},
            },
        })

    log(f"  Schemas solo en DB: {solo_db}")
    log(f"  Schemas solo en ORM: {solo_orm}")
    return diff


# ============================================================
# Comparacion: tablas
# ============================================================

def diff_tables(db, orm, schemas_comunes):
    """Compara tablas por schema."""
    diff = []

    for schema in schemas_comunes:
        if schema not in db["schemas"] or schema not in orm["schemas"]:
            continue

        db_tables = set(db["schemas"][schema]["tables"].keys())
        orm_tables = set(orm["schemas"][schema]["tables"].keys())

        solo_db = sorted(db_tables - orm_tables)
        solo_orm = sorted(orm_tables - db_tables)

        for tabla in solo_db:
            if (schema, tabla) in SYSTEM_TABLES:
                log_verbose(f"  Ignorando system table: {schema}.{tabla}")
                continue
            n_cols = len(db["schemas"][schema]["tables"][tabla]["columns"])
            diff.append({
                "id": None,
                "clasificacion": "tabla_falta",
                "schema": schema,
                "tabla": tabla,
                "columna": None,
                "detalle": {
                    "db": {"n_columns": n_cols},
                    "orm": None,
                },
            })

        for tabla in solo_orm:
            if (schema, tabla) in SYSTEM_TABLES:
                continue
            n_cols = len(orm["schemas"][schema]["tables"][tabla]["columns"])
            diff.append({
                "id": None,
                "clasificacion": "tabla_sobra",
                "schema": schema,
                "tabla": tabla,
                "columna": None,
                "detalle": {
                    "db": None,
                    "orm": {"n_columns": n_cols},
                },
            })

    return diff


def _types_equivalent(db_type, orm_type):
    """
    Compara tipos DB vs ORM normalizando casos conocidos.

    - Geography/Geometry: GeoAlchemy2 normaliza a lowercase; la DB puede
      tener 'Point'/'MultiPolygon' con mayuscula. Comparacion case-insensitive.
    - Resto: comparacion exacta (no enmascarar diferencias reales).

    Returns True si son equivalentes, False si hay divergencia real.
    """
    if db_type is None and orm_type is None:
        return True
    if db_type is None or orm_type is None:
        return False

    db_str = str(db_type).strip()
    orm_str = str(orm_type).strip()

    db_low = db_str.lower()
    orm_low = orm_str.lower()

    if db_low.startswith("geography") or db_low.startswith("geometry"):
        return db_low == orm_low

    return db_str == orm_str


# ============================================================
# Comparacion: columnas
# ============================================================

def diff_columns(db_table, orm_table, schema, tabla):
    """Compara columnas de una tabla."""
    diff = []

    db_cols = db_table["columns"]
    orm_cols = orm_table["columns"]

    for col_name in sorted(set(db_cols) - set(orm_cols)):
        diff.append({
            "id": None,
            "clasificacion": "columna_falta",
            "schema": schema,
            "tabla": tabla,
            "columna": col_name,
            "detalle": {"db": db_cols[col_name], "orm": None},
        })

    for col_name in sorted(set(orm_cols) - set(db_cols)):
        diff.append({
            "id": None,
            "clasificacion": "columna_sobra",
            "schema": schema,
            "tabla": tabla,
            "columna": col_name,
            "detalle": {"db": None, "orm": orm_cols[col_name]},
        })

    for col_name in sorted(set(db_cols) & set(orm_cols)):
        db_col = db_cols[col_name]
        orm_col = orm_cols[col_name]

        # Tipo
        if not _types_equivalent(db_col.get("type"), orm_col.get("type")):
            diff.append({
                "id": None,
                "clasificacion": "tipo_desalineado",
                "schema": schema,
                "tabla": tabla,
                "columna": col_name,
                "detalle": {"db": db_col, "orm": orm_col},
            })

        # Nullable
        if db_col.get("nullable") != orm_col.get("nullable"):
            diff.append({
                "id": None,
                "clasificacion": "nullable_desalineado",
                "schema": schema,
                "tabla": tabla,
                "columna": col_name,
                "detalle": {
                    "db": {"nullable": db_col.get("nullable")},
                    "orm": {"nullable": orm_col.get("nullable")},
                },
            })

        # Comment
        if (db_col.get("comment") or "") != (orm_col.get("comment") or ""):
            diff.append({
                "id": None,
                "clasificacion": "comment_desalineado",
                "schema": schema,
                "tabla": tabla,
                "columna": col_name,
                "detalle": {
                    "db": {"comment": db_col.get("comment")},
                    "orm": {"comment": orm_col.get("comment")},
                },
            })

    return diff


# ============================================================
# Comparacion: constraints
# ============================================================

def diff_constraints(db_table, orm_table, schema, tabla):
    """Compara constraints de una tabla.

    Matching:
    - PK: por columnas. El nombre NO se compara: la DB tiene dos
      convenciones mezcladas (<tabla>_pkey autogenerados + pk_<tabla>
      explicitos). El ORM usa pk_<tabla>. Como el nombre de un PK no
      tiene semantica funcional, matchear por columnas es suficiente.
    - FK: por (columnas, schema_ref, tabla_ref). El nombre NO se compara
      por la misma razon: la DB tiene FKs con nombres cortos
      (fk_<tabla>_<col>) y largos (fk_<tabla>_<col>_<ref>) mezclados.
    - UNIQUE: por columnas. Si las columnas matchean, no se reporta.
    - CHECK: por nombre. Los CHECKs con nombres divergentes aparecen
      como constraint_falta + constraint_sobra (deuda D-027).
    """
    diff = []

    db_cons = db_table["constraints"]
    orm_cons = orm_table["constraints"]

    # PK
    db_pk = db_cons.get("primary_key")
    orm_pk = orm_cons.get("primary_key")
    if db_pk and not orm_pk:
        diff.append({
            "id": None, "clasificacion": "constraint_falta",
            "schema": schema, "tabla": tabla, "columna": None,
            "tipo_constraint": "pk",
            "detalle": {"db": db_pk, "orm": None},
        })
    elif not db_pk and orm_pk:
        diff.append({
            "id": None, "clasificacion": "constraint_sobra",
            "schema": schema, "tabla": tabla, "columna": None,
            "tipo_constraint": "pk",
            "detalle": {"db": None, "orm": orm_pk},
        })
    elif db_pk and orm_pk:
        if db_pk.get("columns") != orm_pk.get("columns"):
            diff.append({
                "id": None, "clasificacion": "constraint_desalineada",
                "schema": schema, "tabla": tabla, "columna": None,
                "tipo_constraint": "pk",
                "detalle": {"db": db_pk, "orm": orm_pk},
            })
        # NOTA: no se compara db_pk.name != orm_pk.name.
        # El nombre de un PK no tiene semantica funcional y la DB tiene
        # convenciones mezcladas. Matchear por columnas es suficiente.

    # FKs - match por columnas
    db_fks = {(tuple(f["columns"]), f["references"]["schema"], f["references"]["table"]): f
              for f in db_cons.get("foreign_keys", [])}
    orm_fks = {(tuple(f["columns"]), f["references"]["schema"], f["references"]["table"]): f
               for f in orm_cons.get("foreign_keys", [])}

    for key in db_fks.keys() - orm_fks.keys():
        diff.append({
            "id": None, "clasificacion": "constraint_falta",
            "schema": schema, "tabla": tabla, "columna": None,
            "tipo_constraint": "fk",
            "detalle": {"db": db_fks[key], "orm": None},
        })
    for key in orm_fks.keys() - db_fks.keys():
        diff.append({
            "id": None, "clasificacion": "constraint_sobra",
            "schema": schema, "tabla": tabla, "columna": None,
            "tipo_constraint": "fk",
            "detalle": {"db": None, "orm": orm_fks[key]},
        })
    # NOTA: no se compara nombre de FK. Misma razon que PK.
    # Las FKs que matchean por (columnas, ref) no se reportan aunque
    # el nombre difiera.

    # UNIQUEs - match por columnas    
    db_uqs = {tuple(u["columns"]): u for u in db_cons.get("unique", [])}
    orm_uqs = {tuple(u["columns"]): u for u in orm_cons.get("unique", [])}

    # Columnas de UNIQUEs del ORM declarados como Index(unique=True).
    # Postgres expone los CREATE UNIQUE INDEX como UniqueConstraint en
    # pg_constraint. SQLAlchemy los declara como Index(unique=True), no
    # como UniqueConstraint. Sin este set, un UNIQUE declarado en ORM
    # como Index aparece como constraint_falta falso.
    # Excluye partial (WHERE) porque un partial unique index no es
    # equivalente a un UNIQUE constraint.
    orm_idx_uq_cols = {
        tuple(i.get("columns") or [])
        for i in (orm_table.get("indexes") or [])
        if i.get("unique") and not i.get("primary") and not _is_partial_index(i)
    }

    for key in db_uqs.keys() - orm_uqs.keys():
        # Si el ORM declara el mismo UNIQUE via Index(unique=True),
        # no es constraint_falta.
        if key in orm_idx_uq_cols:
            continue
        diff.append({
            "id": None, "clasificacion": "constraint_falta",
            "schema": schema, "tabla": tabla, "columna": None,
            "tipo_constraint": "unique",
            "detalle": {"db": db_uqs[key], "orm": None},
        })
    for key in orm_uqs.keys() - db_uqs.keys():
        diff.append({
            "id": None, "clasificacion": "constraint_sobra",
            "schema": schema, "tabla": tabla, "columna": None,
            "tipo_constraint": "unique",
            "detalle": {"db": None, "orm": orm_uqs[key]},
        })

    # CHECKs - match por nombre (los CHECK no siempre tienen columnas).
    # Excluye *_not_null autogenerados por Alembic: no son deuda real,
    # son artefactos del ALTER TABLE ... SET NOT NULL.
    db_cks = {
        c.get("name"): c
        for c in db_cons.get("check", [])
        if not RE_NOT_NULL_AUTOGEN.match(c.get("name") or "")
    }
    orm_cks = {
        c.get("name"): c
        for c in orm_cons.get("check", [])
        if not RE_NOT_NULL_AUTOGEN.match(c.get("name") or "")
    }

    for name in db_cks.keys() - orm_cks.keys():
        diff.append({
            "id": None, "clasificacion": "constraint_falta",
            "schema": schema, "tabla": tabla, "columna": None,
            "tipo_constraint": "check",
            "detalle": {"db": db_cks[name], "orm": None},
        })
    for name in orm_cks.keys() - db_cks.keys():
        diff.append({
            "id": None, "clasificacion": "constraint_sobra",
            "schema": schema, "tabla": tabla, "columna": None,
            "tipo_constraint": "check",
            "detalle": {"db": None, "orm": orm_cks[name]},
        })

    return diff


# ============================================================
# Comparacion: indices
# ============================================================

def _is_pk_index(idx):
    """True si el indice es la PK (pk_<tabla> o <tabla>_pkey).

    SQLAlchemy declara la PK via primary_key=True, no como Index. El
    introspector de DB si la incluye en indexes. Reportarla como
    indice_falta es ruido (deuda orm.indice_falta_incluye_pks).
    """
    name = idx.get("name") or ""
    return RE_PK_INDEX.match(name) is not None


def _is_partial_index(idx):
    """True si el indice es partial (tiene clausula WHERE).

    Postgres expone el predicado dentro de `definition`, no como campo
    aparte. Formato:
        CREATE UNIQUE INDEX uq_x ON t USING btree (a, b) WHERE (activo = true)
    Un UniqueConstraint de SQLAlchemy no puede expresar WHERE, asi que
    un partial unique index de DB nunca es equivalente a un
    UniqueConstraint de ORM.
    """
    definition = (idx.get("definition") or "").lower()
    return " where " in definition


def _orm_unique_cols(orm_table):
    """Set de tuplas de columnas con UniqueConstraint en el ORM.

    Los UniqueConstraint viven en constraints.unique, no en indexes.
    El diff no los miraba, generando falsos positivos de indice_falta
    cuando la DB expone lo mismo como CREATE UNIQUE INDEX (patron
    autogenerado *_key, o explicito uq_*).
    """
    result = set()
    cons = orm_table.get("constraints") or {}
    for u in cons.get("unique") or []:
        cols = tuple(u.get("columns") or [])
        if cols:
            result.add(cols)
    return result


def _norm_idx_name(name):
    """Normaliza nombre de indice para matching tolerante.

    Baja a lowercase y quita espacios. No quita prefijos: los nombres
    en DB y ORM deben coincidir salvo sufijos cosmeticos.
    """
    if not name:
        return ""
    return str(name).strip().lower()


def _idx_key(idx):
    """Clave de matching para un indice.

    Usa (nombre_normalizado, columnas). El nombre es necesario porque el
    ORM puede declarar dos indices sobre la misma columna (ej. B-tree +
    GIST sobre Geography). Con solo `columns` se colapsan y uno queda
    invisible (deuda orm.diff_indexes_colapsa_por_columnas).
    """
    cols = tuple(idx.get("columns") or [])
    return (_norm_idx_name(idx.get("name")), cols)


def diff_indexes(db_table, orm_table, schema, tabla):
    """Compara indices de una tabla. Match por (nombre_normalizado, columnas).

    Excluye indices de PRIMARY KEY de ambos lados: no son declarables
    como Index en el ORM.

    Los indices del ORM que parecen auto-generados por GeoAlchemy2
    (GIST sobre Geography) y no existen en DB se clasifican como
    indice_falta_en_db, no como indice_sobra: el ORM esta correcto,
    falta la migracion que los cree en DB.

    Ademas, un CREATE UNIQUE INDEX en DB se considera equivalente a un
    UniqueConstraint en ORM si tienen las mismas columnas (mismo orden)
    y el indice de DB no es partial. Elimina falsos positivos por
    naming divergente (*_key vs uq_*) sin tocar la DB.
    """
    diff = []

    db_idx = {
        _idx_key(i): i
        for i in db_table.get("indexes", [])
        if not _is_pk_index(i)
    }
    orm_idx = {
        _idx_key(i): i
        for i in orm_table.get("indexes", [])
        if not _is_pk_index(i)
    }

    # UniqueConstraints del ORM indexados por columnas. Permite matchear
    # un CREATE UNIQUE INDEX (DB) contra un UniqueConstraint (ORM) sin
    # depender del nombre (que historicamente diverge: *_key vs uq_*).
    orm_unique_cols = _orm_unique_cols(orm_table)

    for key in db_idx.keys() - orm_idx.keys():
        idx = db_idx[key]

        # Equivalencia UNIQUE INDEX (DB) <-> UniqueConstraint (ORM).
        # Excluye partial: SQLAlchemy no puede expresar WHERE en un
        # UniqueConstraint, asi que un partial unique index de DB nunca
        # es equivalente a un UniqueConstraint de ORM.
        if (idx.get("unique") and not idx.get("primary")
                and not _is_partial_index(idx)
                and tuple(idx.get("columns") or []) in orm_unique_cols):
            continue

        diff.append({
            "id": None, "clasificacion": "indice_falta",
            "schema": schema, "tabla": tabla, "columna": None,
            "detalle": {"db": idx, "orm": None},
        })

    for key in orm_idx.keys() - db_idx.keys():
        idx = orm_idx[key]
        clasif = "indice_falta_en_db" if _is_geoalchemy2_gist(idx) else "indice_sobra"
        diff.append({
            "id": None, "clasificacion": clasif,
            "schema": schema, "tabla": tabla, "columna": None,
            "detalle": {"db": None, "orm": idx},
        })

    for key in db_idx.keys() & orm_idx.keys():
        if db_idx[key].get("name") != orm_idx[key].get("name"):
            diff.append({
                "id": None, "clasificacion": "indice_nombre_desalineado",
                "schema": schema, "tabla": tabla, "columna": None,
                "detalle": {"db": db_idx[key], "orm": orm_idx[key]},
            })

    return diff


# ============================================================
# Construccion del diff completo
# ============================================================

def build_diff(db, orm):
    """Construye el diff completo."""
    log("Comparando schemas...")
    diff = diff_schemas(db, orm)

    schemas_comunes = sorted(set(db["schemas"].keys()) & set(orm["schemas"].keys()))
    log(f"  Schemas comunes: {len(schemas_comunes)}")

    log("Comparando tablas...")
    diff.extend(diff_tables(db, orm, schemas_comunes))

    log("Comparando columnas, constraints e indices...")
    for schema in schemas_comunes:
        db_tables = db["schemas"][schema]["tables"]
        orm_tables = orm["schemas"][schema]["tables"]
        tablas_comunes = sorted(set(db_tables.keys()) & set(orm_tables.keys()))

        for tabla in tablas_comunes:
            if (schema, tabla) in SYSTEM_TABLES:
                continue

            db_t = db_tables[tabla]
            orm_t = orm_tables[tabla]

            diff.extend(diff_columns(db_t, orm_t, schema, tabla))
            diff.extend(diff_constraints(db_t, orm_t, schema, tabla))
            diff.extend(diff_indexes(db_t, orm_t, schema, tabla))

    # Asignar IDs, Tier y requiere_decision
    log("Clasificando items...")
    for i, item in enumerate(diff, start=1):
        item["id"] = f"D-{i:04d}"
        tier = assign_tier(item["schema"], item.get("tabla"), item["clasificacion"])
        item["tier"] = tier

        req_dec, razon = detect_requires_decision(
            item["schema"], item.get("tabla"), item.get("columna"),
            item["clasificacion"], item.get("detalle", {})
        )
        item["requiere_decision"] = req_dec
        item["razon_decision"] = razon

    # Filtrar system tables
    diff = [d for d in diff if d["tier"] is not None]

    return diff


# ============================================================
# Escritura de JSON
# ============================================================

def write_json(diff, output_path):
    """Escribe el JSON del diff."""
    por_clasif = Counter(d["clasificacion"] for d in diff)
    por_tier = Counter(d["tier"] for d in diff)
    n_req_dec = sum(1 for d in diff if d.get("requiere_decision"))

    data = {
        "meta": {
            "capturado_en": datetime.now(timezone.utc).isoformat(),
            "stats": {
                "total_diferencias": len(diff),
                "por_clasificacion": dict(por_clasif),
                "por_tier": {str(k): v for k, v in sorted(por_tier.items())},
                "requiere_decision": n_req_dec,
            },
        },
        "diferencias": diff,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    size_kb = Path(output_path).stat().st_size / 1024
    log(f"OK. {output_path} ({size_kb:.1f} KB)")


# ============================================================
# Reporte markdown
# ============================================================

def write_report(diff, output_path):
    """Escribe el reporte markdown."""
    por_clasif = Counter(d["clasificacion"] for d in diff)
    por_tier = Counter(d["tier"] for d in diff)
    req_dec = [d for d in diff if d.get("requiere_decision")]

    lines = []
    lines.append("# Reporte de Diff ORM vs DB")
    lines.append("")
    lines.append(f"**Fecha:** {datetime.now(timezone.utc).isoformat()}")
    lines.append("")
    lines.append("## Resumen ejecutivo")
    lines.append("")
    lines.append(f"- **{len(diff)} diferencias** en total.")
    for tier in sorted(por_tier.keys()):
        lines.append(f"- **Tier {tier}**: {por_tier[tier]} items.")
    lines.append(f"- **{len(req_dec)} items requieren decision manual.**")
    lines.append("")

    lines.append("### Por clasificacion")
    lines.append("")
    lines.append("| Clasificacion | Cantidad |")
    lines.append("|---|---|")
    for k, v in sorted(por_clasif.items(), key=lambda x: -x[1]):
        lines.append(f"| {k} | {v} |")
    lines.append("")

    # Por Tier
    for tier in sorted(por_tier.keys()):
        tier_items = [d for d in diff if d["tier"] == tier]
        lines.append(f"---")
        lines.append("")
        lines.append(f"## Tier {tier} — {len(tier_items)} items")
        lines.append("")

        # Agrupar por clasificacion
        por_clas_tier = defaultdict(list)
        for d in tier_items:
            por_clas_tier[d["clasificacion"]].append(d)

        for clasif in sorted(por_clas_tier.keys()):
            items = por_clas_tier[clasif]
            lines.append(f"### {clasif} ({len(items)})")
            lines.append("")

            # Si son muchos, agrupar por tabla
            if len(items) > 20 and clasif in ("indice_falta", "columna_falta", "constraint_falta"):
                por_tabla = defaultdict(int)
                for d in items:
                    por_tabla[f"{d['schema']}.{d['tabla']}"] += 1
                lines.append("| Tabla | Cantidad |")
                lines.append("|---|---|")
                for t, c in sorted(por_tabla.items(), key=lambda x: -x[1]):
                    lines.append(f"| {t} | {c} |")
                lines.append("")
            else:
                for d in items[:50]:
                    detail = ""
                    if d.get("columna"):
                        detail = d["columna"]
                    elif d.get("tabla"):
                        detail = f"{d['schema']}.{d['tabla']}"
                    else:
                        detail = d["schema"]
                    lines.append(f"- `{d['id']}` — {detail}")
                if len(items) > 50:
                    lines.append(f"- ... y {len(items) - 50} mas (ver JSON)")
                lines.append("")

    # Requiere decision
    if req_dec:
        lines.append("---")
        lines.append("")
        lines.append("## Items que requieren decision manual")
        lines.append("")
        lines.append("| ID | Item | Razon |")
        lines.append("|---|---|---|")
        for d in req_dec[:50]:
            item = f"{d['schema']}.{d.get('tabla') or ''}"
            if d.get("columna"):
                item += f".{d['columna']}"
            lines.append(f"| {d['id']} | {item} | {d['razon_decision']} |")
        if len(req_dec) > 50:
            lines.append(f"| ... | ... | {len(req_dec) - 50} mas |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Archivos generados")
    lines.append("")
    lines.append("- `orm_diff.json` — datos completos.")
    lines.append("- `orm_diff_reporte.md` — este informe.")
    lines.append("- `orm_diff_acciones.csv` — CSV de acciones sugeridas.")
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    size_kb = Path(output_path).stat().st_size / 1024
    log(f"OK. {output_path} ({size_kb:.1f} KB)")


# ============================================================
# CSV de acciones
# ============================================================

ACCION_MAP = {
    "columna_falta": "Agregar columna al modelo",
    "columna_sobra": "Eliminar columna del modelo",
    "tabla_falta": "Crear modelo",
    "tabla_sobra": "Eliminar modelo",
    "tipo_desalineado": "Alinear tipo",
    "nullable_desalineado": "Alinear nullable",
    "comment_desalineado": "Alinear comment",
    "server_default_desalineado": "Alinear default",
    "indice_falta": "Agregar indice al modelo",
    "indice_sobra": "Eliminar indice del modelo",
    "indice_nombre_desalineado": "Alinear nombre de indice",
    "constraint_falta": "Agregar constraint al modelo",
    "constraint_sobra": "Eliminar constraint del modelo",
    "constraint_desalineada": "Alinear constraint",
    "constraint_nombre_desalineado": "Alinear nombre de constraint",
    "schema_falta": "Crear modulo de modelos para schema",
    "schema_sobra": "Eliminar modulo de modelos",
}


PRIORIDAD_MAP = {1: "ALTA", 2: "MEDIA", 3: "BAJA", 4: "ELIMINAR"}


def write_csv(diff, output_path):
    """Escribe el CSV de acciones."""
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "clasificacion", "tier", "schema", "tabla", "columna",
                         "accion_sugerida", "prioridad", "requiere_decision", "razon_decision"])

        for d in diff:
            writer.writerow([
                d["id"],
                d["clasificacion"],
                d["tier"],
                d["schema"],
                d.get("tabla") or "",
                d.get("columna") or "",
                ACCION_MAP.get(d["clasificacion"], "Revisar"),
                PRIORIDAD_MAP.get(d["tier"], "MEDIA"),
                "SI" if d.get("requiere_decision") else "NO",
                d.get("razon_decision") or "",
            ])

    size_kb = Path(output_path).stat().st_size / 1024
    log(f"OK. {output_path} ({size_kb:.1f} KB)")


# ============================================================
# Resumen humano
# ============================================================

def print_summary(diff):
    por_tier = Counter(d["tier"] for d in diff)
    por_clasif = Counter(d["clasificacion"] for d in diff)
    n_req = sum(1 for d in diff if d.get("requiere_decision"))

    log("=" * 60)
    log("RESUMEN DEL DIFF")
    log("=" * 60)
    log(f"Total diferencias: {len(diff)}")
    log("")
    log("Por Tier:")
    for tier in sorted(por_tier.keys()):
        log(f"  Tier {tier}: {por_tier[tier]}")
    log("")
    log("Por clasificacion (top 10):")
    for k, v in por_clasif.most_common(10):
        log(f"  {k}: {v}")
    log("")
    log(f"Requieren decision: {n_req}")
    log("=" * 60)


# ============================================================
# Main
# ============================================================

def main():
    global VERBOSE

    parser = argparse.ArgumentParser(description="Diff ORM vs DB.")
    parser.add_argument("--db", default=str(DEFAULT_DB),
                        help=f"Path del DB snapshot (default: {DEFAULT_DB})")
    parser.add_argument("--orm", default=str(DEFAULT_ORM),
                        help=f"Path del ORM snapshot (default: {DEFAULT_ORM})")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR),
                        help=f"Directorio de salida (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()
    VERBOSE = args.verbose

    log("Iniciando...")

    db = load_json(args.db)
    orm = load_json(args.orm)

    log(f"DB: {db['meta']['stats']['total_schemas']} schemas, "
        f"{db['meta']['stats']['total_tables']} tablas, "
        f"{db['meta']['stats']['total_columns']} columnas, "
        f"{db['meta']['stats']['total_indexes']} indices, "
        f"{db['meta']['stats']['total_constraints']} constraints")
    log(f"ORM: {orm['meta']['stats']['total_schemas']} schemas, "
        f"{orm['meta']['stats']['total_tables']} tablas, "
        f"{orm['meta']['stats']['total_columns']} columnas, "
        f"{orm['meta']['stats']['total_indexes']} indices, "
        f"{orm['meta']['stats']['total_constraints']} constraints")

    diff = build_diff(db, orm)
    log(f"Total diferencias: {len(diff)}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    write_json(diff, output_dir / "orm_diff.json")
    write_report(diff, output_dir / "orm_diff_reporte.md")
    write_csv(diff, output_dir / "orm_diff_acciones.csv")

    print_summary(diff)
    log("Listo.")


if __name__ == "__main__":
    main()