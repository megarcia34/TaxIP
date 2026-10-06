CONTEXTO RONDA 9 a 10 — Handoff detallado
Documento de arranque. Pegar como primer mensaje del proximo chat.

1. Proyecto

TaxIP 2.0 — backend FastAPI + SQLAlchemy 2.0 async + PostgreSQL 17 + PostGIS 3.6.

Root backend: D:\aTaxip\backend

Git root: D:/aTaxip

Branch: main

Python: 3.12.10 (venv en .\venv\Scripts\Activate.ps1)

Alembic head: m3_010

Backend: python run.py (NO python -m uvicorn)

2. Estado al cierre de Ronda 9

Fecha de cierre: 2026-10-06

Tag de cierre: ronda9-fase9-completa

Commit: a887cc3

HEAD local = HEAD remoto: a887cc3 (tag pusheado)

Working tree: clean

Diff total: 332 items (bajo desde 404 al inicio de R9, −17.8%).

Tags existentes:

ronda5-baseline-pre, ronda5-fase0-completa, ronda5-fase1-completa, ronda5-completa

ronda6-fase2-sesion1-completa, ronda6-fase2-sesion2-completa, ronda6-fase3-completa, ronda6-completa

ronda7-fase4b-paso3-completo, ronda7-fase4b-paso7-completo, ronda7-fase4b-completa

ronda8-fase6-completa

ronda9-fase9-completa

Commits locales R9 (todos pusheados):

158e594 fix(fleet): eliminar B-tree redundante sobre Geography (Paso 9.2)

1ac1294 fix(orm_sync): excluir indices de PK de indice_falta en diff (Paso 9.1)

3. Diff actual (332 items) — desglose completo

Por clasificacion

Clasificacion	Cant.	Naturaleza	Accion

constraint_nombre_desalineado	124	Naming convention (ORM usa prefijos pk_/fk_/ck_/uq_).	NO TOCAR (cosmetico)

constraint_desalineada	72	PKs con nombre distinto (cosmetico).	Manual / ignorar

constraint_falta	61	CHECKs reales (~33) + other (~20) + UNIQUEs (~9) + FKs (~7).	Paso 4 residual (bloqueado)

comment_desalineado	20	Mojibake (13) + Tipo A (7).	Requiere UPDATE DB

constraint_sobra	17	UNIQUEs fantasma (patron D-017).	Decision funcional

indice_falta	14	UNIQUE INDEX cosmeticos.	Decision (D-026)

tabla_falta	10	Ampliado a ~16 por alembic.	Fase 4c

nullable_desalineado	4	Fantasma.	Ignorar

indice_nombre_desalineado	3	Cosmetico.	Ignorar

indice_sobra	3	GIST de GeoAlchemy2 sin aplicar en DB.	Migracion Alembic (R10)

schema_falta	2	comunicacion, rentabilidad.	Fase 4c

tabla_sobra	1	trip.reserva.	Fase 4d

columna_falta	1	usuario_rol.control_base_id.	Decision: no tocar

Por Tier

Tier	Cant.	Estado

Tier 1 (critico)	62	En progreso

Tier 2 (importante)	158	En progreso

Tier 3 (cosmetico)	111	Mayormente ignorable

Tier 4 (muerte)	1	trip.reserva

Deuda real vs ruido

Deuda real (~110 items):

61 constraint_falta (CHECKs + FKs + UNIQUEs faltantes).

20 comment_desalineado.

10 tabla_falta + 2 schema_falta (Fase 4c).

3 indice_sobra (GIST sin aplicar en DB).

3 deudas de tooling R9 (colapso, ambiguedad, GIST).

1 columna_falta (no tocar).

~13 otros.

Ruido/cosmetico (~200 items):

124 constraint_nombre_desalineado.

72 constraint_desalineada.

14 indice_falta (UNIQUE INDEX cosmeticos).

17 constraint_sobra.

3 indice_nombre_desalineado.

1 tabla_sobra.

4 nullable_desalineado.

4. Que se cerro en Ronda 9

Paso 9.1 — Excluir PKs de indice_falta (commit 1ac1294)

Problema: diff.py reportaba 72 PKs (pk_* / *_pkey) como indice_falta.

Causa: diff_indexes matcheaba por columnas, y el introspector de DB incluye
la PK en indexes. El ORM no la declara como Index (va via primary_key=True).

Fix: agregar RE_PK_INDEX = re.compile(r"^(pk_.+|.+_pkey)$") y filtrar en
diff_indexes antes de construir los dicts.

Impacto: −72 items (indice_falta: 86 → 14). Diff total: 404 → 332.

Paso 9.2 — Limpieza de indice_sobra (commit 158e594)

Hallazgo inicial: 3 items clasificados como indice_sobra.

Analisis:
- D-0091 fleet.chofer_vehiculo: B-tree redundante (index=True) sobre ubicacion.
- D-0312 trip.panico: GIST sobre ubicacion, ausente en DB.
- D-0331 trip.viaje_solicitado: GIST sobre destino, ausente en DB.

Descubrimiento clave: GeoAlchemy2 auto-genera Index GIST sobre columnas
Geography con spatial_index=True (default). Los 3 items son del tipo GIST,
no ruido real. Son utiles para queries espaciales.

Fix aplicado: quitar index=True de fleet.chofer_vehiculo.ubicacion. El B-tree
era redundante con el GIST auto-generado.

Impacto real: cleanup, aunque el diff NO bajo (sigue en 332) por el bug de
colapso de diff_indexes (dos indices sobre la misma columna → uno invisible).

Documentacion

- DEUDA_TECNICA_ACTUAL.md actualizado (R9 + 3 deudas nuevas).
- orm_decisiones.md actualizado (D-022 a D-025).
- Handoff R9→R10 (este documento).

5. Deudas nuevas identificadas en R9

orm.indice_sobra_ambiguo (Tier 3)

diff.py clasifica como indice_sobra dos casos distintos:
1. Ruido real: B-tree sobre Geography.
2. Indices GIST auto-generados por GeoAlchemy2, ausentes en DB.

Requiere analisis manual por item. Los 3 actuales son todos GIST.

orm.geoalchemy2_indices_no_aplicados (Tier 2)

3 indices GIST declarados por ORM (via GeoAlchemy2), ausentes en DB:
- fleet.chofer_vehiculo.idx_chofer_vehiculo_ubicacion
- trip.panico.idx_panico_ubicacion
- trip.viaje_solicitado.idx_viaje_solicitado_destino

Requieren migracion Alembic para crearlos en DB.

orm.diff_indexes_colapsa_por_columnas (Tier 2)

diff.py matchea indices por tuple(columns), no por nombre. Si el ORM declara
dos indices sobre la misma columna, solo uno aparece en el diff. Enmascara
fixes. Fix: matchear por (nombre, columnas).

6. Deudas cerradas en R9

orm.indice_falta_incluye_pks — CERRADA (Paso 9.1, commit 1ac1294).

7. Deudas pendientes (heredadas + nuevas)

Bloqueante produccion

B5 — ViajeSolicitado desactualizado. Tecnicamente desbloqueado (Fase 4a
completada en R6). Falta verificacion formal.

Critico

orm.db_desalineados — 332 items. En progreso.

Alta prioridad

orm.paso4_check_constraints_residual — ~61 items de constraint_falta.

G63 — Alerta si el motor de precios cae a fallback.

G67 — check_out_turno sin escapatoria si hay viajes huerfanos.

G80 — App apunta a Metro (no funciona fuera de WiFi dev).

Media prioridad

metodo_pago.catalogo_sucio, metodo_pago.fk_catalogo, metodo_pago.ingreso_turno,
metodo_pago.frontend_e2.

flujo_caja.ingreso_turno.

F5, F6, G68, G70, G72, G74, G76, G81, J15, G82 (heredadas).

Baja prioridad

orm.reserva_modulo_activo (Fase 4d).

orm.foto_viaje_out_of_scope (Fase 4d).

datos.turno_chofer_km_final_outlier (Tier 3).

orm.indices_duplicados.

orm.constraint_nombres_numericos.

Backend heredadas, Frontend, Endpoints, Proceso, Funcional (sin cambios).

Expo-router / EAS

G77, G78, G79 (workaround activo, no tocar).

8. Plan de Ronda 10 (recomendado)

Prioridad 1 — Fix de diff_indexes (colapso por columnas)

Deuda: orm.diff_indexes_colapsa_por_columnas.

Cambio: matchear indices por (nombre_normalizado, columnas) en vez de solo
columnas.

Impacto esperado: diff reflejara correctamente los 332 items. Probablemente
baje a 331 (el B-tree eliminado en D-023 ya no aparece).

Riesgo: bajo (solo cambia matching, no elimina items).

Prioridad 2 — Migracion Alembic para los 3 GIST

Deuda: orm.geoalchemy2_indices_no_aplicados.

Accion: crear migracion m3_011 que cree los 3 indices GIST en DB:
- fleet.chofer_vehiculo.idx_chofer_vehiculo_ubicacion
- trip.panico.idx_panico_ubicacion
- trip.viaje_solicitado.idx_viaje_solicitado_destino

Requiere: backup DB previo, verificacion post-migracion con pg_indexes.

Impacto esperado: −3 indice_sobra.

Riesgo: medio (DDL en DB, requiere backup).

Prioridad 3 — Fase 4c (tablas faltantes)

Crear:
- app/models/comunicacion.py (3 tablas: conversacion, email_enviado, mensaje).
- app/models/rentabilidad.py (3 tablas: analisis_medios_pago,
  rentabilidad_diaria_vehiculo, rentabilidad_mensual_vehiculo).
- Ampliar app/models/auth.py (4 tablas: codigo_metadatos, codigo_verificacion,
  plantilla_viaje, prestadora_telefonica).
- Ampliar app/models/payment.py (2 tablas: qr_cobro, configuracion_pasarela).
- Ampliar app/models/audit.py (alertas_vencimiento).
- Ampliar app/models/trip.py (broadcast_log — decisional).
- Ampliar app/models/fleet.py (historial_chofer_vehiculo,
  relacion_propietario_vehiculo).
- Registrar en app/models/__init__.py.

Impacto esperado: −10 tabla_falta −2 schema_falta = −12 items.

Prioridad 4 — Decisiones D-026, D-027, D-028

- D-026: UniqueConstraint vs Unique Index (14 items). Aplicar Index(unique=True)
  en masa (patron D-017).
- D-027: naming_convention_check_divergente (~13 CHECKs). Cambiar convention
  o matchear por definicion en diff.py.
- D-028: indice_sobra_ambiguo. Heuristica o lista blanca en diff.py.

Prioridad 5 — Comments (mojibake)

Deuda: 13 items con mojibake + 7 Tipo A = 20 total.

Accion: requiere UPDATE en DB con backup previo.

Impacto: −20 items.

Prioridad 6 — Actualizar deuda y docs

docs/DEUDA_TECNICA_ACTUAL.md (ya actualizado en R9).

docs/CONTEXTO_RONDA_10 a 11.md (nuevo handoff).

docs/orm_sync/orm_decisiones.md (D-029 a D-031 si aplica).

9. Mensaje de arranque sugerido para Ronda 10

Continuamos Ronda 10. Ronda 9 cerrada (tag ronda9-fase9-completa en <hash>,
origin/main sincronizado). 332 items en el diff.

Estado verificado:
- Python 3.12.10, PostgreSQL 17, PostGIS 3.6, Alembic head m3_010.
- Backend arranca limpio (python run.py OK).
- Imports de modelos OK.
- fleet schema 100% reconciliado.

Prioridad R10:
A) Fix de diff_indexes (colapso por columnas) (−1 item, bajo riesgo).
B) Migracion Alembic para los 3 GIST (−3 items, requiere backup).
C) Fase 4c (tablas faltantes) (−12 items).
D) Decisiones D-026, D-027, D-028.
E) Comments mojibake (20 items).

Recomendacion: A primero (rapido, bajo riesgo), despues B (requiere cuidado),
despues C (grande), D y E si queda tiempo.

Reglas: no tocar DB sin backup, no correr alembic autogenerate,
no usar python -m uvicorn. Ciclo: editar → verificar import →
regenerar snapshots → apply.py --stats → commit.

10. Comandos utiles

Verificar entorno

cd D:\aTaxip\backend
.\venv\Scripts\Activate.ps1
alembic current
alembic heads
git log --oneline -5
git status

Regenerar snapshots

python scripts\orm_sync\introspect_orm.py    # solo si cambio el ORM
python scripts\orm_sync\diff.py
python scripts\orm_sync\apply.py --stats

Analizar diff

# Ver items por clasificacion
python scripts\orm_sync\apply.py --report --filter-clasif <clasificacion>

# Filtrar por schema
python scripts\orm_sync\apply.py --report --filter-schema fleet

# Ver CHECKs residuales
python scripts\orm_sync\filtrar_check.py --stats
python scripts\orm_sync\filtrar_check.py --report --subtipo check

# Ver items de un archivo
python scripts\orm_sync\apply.py --report --filter-schema <schema> --filter-clasif <clasif>

Backup DB

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda10.dump"

Consultar pg_indexes de una tabla

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT indexname, indexdef FROM pg_indexes WHERE schemaname='<schema>' AND tablename='<tabla>' ORDER BY indexname;"

Consultar pg_constraint de una tabla

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT conname, contype, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = '<schema>.<tabla>'::regclass ORDER BY conname;"

11. Reglas operativas (CRITICAS)

NO hacer

NO tocar la DB sin backup previo.

NO correr alembic revision --autogenerate (destructivo).

NO usar python -m uvicorn. Usar python run.py.

NO commitear cambios de tipo masivo sin verificar import.

NO pegar bloques grandes sin verificar pestana activa.

SI hacer

1 commit por paso.

Snapshots (introspect_orm.py + diff.py) al inicio de cada sub-paso.

Comentarios de codigo: ASCII puro (N10).

Comments de columnas (strings al usuario): UTF-8 permitido.

PowerShell + here-string: usar @"..."@ para evitar problemas con \".

Errores de encoding: VS Code debe guardar UTF-8 SIN BOM.
Verificar abajo a la derecha antes de guardar. Si aparece "UTF-8 with BOM",
cambiar a "UTF-8". Esto rompe import ast.

Ciclo por sub-paso

cd D:\aTaxip\backend
.\venv\Scripts\Activate.ps1

# 1. Editar archivo
# 2. Verificar sintaxis
python -c "import ast; ast.parse(open('app/models/<archivo>.py', encoding='utf-8').read()); print('Sintaxis OK')"

# 3. Verificar import
python -c "from app.models.<archivo> import <Clase>; print('Import OK')"

# 4. Runtime check (ver indices/constraints)
@'
import sys
sys.path.insert(0, '.')
from app.models.<archivo> import <Clase>
for idx in <Clase>.__table__.indexes:
    print(f"  {idx.name} | {[c.name for c in idx.columns]}")
'@ | Out-File -Encoding utf8 scripts\orm_sync\_tmp_check.py
python scripts\orm_sync\_tmp_check.py
Remove-Item scripts\orm_sync\_tmp_check.py

# 5. Regenerar snapshots
python scripts\orm_sync\introspect_orm.py
python scripts\orm_sync\diff.py

# 6. Ver stats
python scripts\orm_sync\apply.py --stats

# 7. Commit
git add app\models\<archivo>.py docs\orm_sync\
git commit -m "..."

Regla del BOM

VS Code puede agregar un BOM (EF BB BF) al inicio del archivo. Esto rompe
import ast y todos los scripts de orm_sync. Si pasa:

python -c "content = open('app/models/<archivo>.py', encoding='utf-8-sig').read(); open('app/models/<archivo>.py', 'w', encoding='utf-8').write(content); print('BOM removed')"

Verificar sin BOM:

$bytes = [System.IO.File]::ReadAllBytes("D:\aTaxip\backend\app\models\<archivo>.py")
$bytes[0..2] | ForEach-Object { "{0:X2}" -f $_ }
# Si sale 22 22 22 (""") → OK. Si sale EF BB BF → BOM presente.

12. Archivos clave

Scripts

scripts/orm_sync/introspect_db.py → genera docs/orm_sync/db_snapshot.json.

scripts/orm_sync/introspect_orm.py → genera docs/orm_sync/orm_snapshot.json.

scripts/orm_sync/diff.py → genera docs/orm_sync/orm_diff.json + reporte + CSV.

scripts/orm_sync/apply.py → stats/report/generate.

scripts/orm_sync/filtrar_check.py → lista constraint_falta.

Snapshots

docs/orm_sync/db_snapshot.json

docs/orm_sync/orm_snapshot.json

docs/orm_sync/orm_diff.json

docs/orm_sync/orm_diff_reporte.md

docs/orm_sync/orm_diff_acciones.csv

docs/orm_sync/baseline_diff_r7_final.json (baseline R7)

docs/orm_sync/alembic_check_cierre_r8_2026-10-05.txt

Documentacion

docs/DEUDA_TECNICA_ACTUAL.md (actualizado post-R9)

docs/HISTORICO_CERRADAS.md (R4-R7)

docs/orm_sync/orm_decisiones.md (D-014 a D-028)

docs/orm_sync/orm_decisiones_historico.md (D-001 a D-013)

docs/orm_reconciliacion_plan.md

docs/orm_sync/orm_plan_aplicacion.md

docs/orm_sync/baseline_info.md

docs/CONTEXTO_RONDA_9 a 10.md (este documento)

ORM (modelos)

app/models/__init__.py (registra modelos)

app/models/fleet.py (23 clases, ~1500 lineas)

app/models/auth.py

app/models/trip.py

app/models/turno.py

app/models/gasto_turno.py

app/models/liquidacion.py

app/models/audit.py

app/models/public.py

app/models/notification.py

app/models/geo.py

app/models/foto_viaje.py

app/models/corporate.py

app/models/tenant.py

app/models/payment.py

app/database.py (naming convention de constraints)

Bitacoras (fuera del repo)

E:\Taxip\app chofer\BITACORA_M1.md

E:\Taxip\app chofer\BITACORA_M2.md

E:\Taxip\app chofer\BITACORA_M3.md

13. Archivos criticos con estado especial

app/models/trip.py — Residual del Paso 4

8 CHECKs de trip.viaje_solicitado corregidos en R8 (Fix 3). Siguen pendientes:

constraint_falta residual (~61 items en otros schemas).

1 tabla_sobra: trip.reserva (Fase 4d).

1 tabla_falta: trip.broadcast_log (11 cols).

app/models/fleet.py — 100% reconciliado

23 clases, ~1500 lineas. 60 indices + 2 UNIQUEs aplicados en R8.
B-tree redundante eliminado en R9 (Paso 9.2). Cuidado con BOM al editar.

app/models/auth.py — Pendiente Fase 4c

4 tablas faltantes: codigo_metadatos, codigo_verificacion, plantilla_viaje,
prestadora_telefonica.

14 constraint_nombre_desalineado + 12 constraint_desalineada (cosmetico).

12 PKs + 4 UNIQUEs fantasma (ruido).

app/models/payment.py — Nuevo hallazgo R8

Tablas qr_cobro y configuracion_pasarela existen en DB pero no en ORM.
Fase 4c.

app/database.py — Naming convention

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

CUIDADO: la convention agrega prefijos automaticamente. Si declaras
name="ck_X" en un CheckConstraint, el nombre final es ck_<tabla>_ck_X.
No duplicar prefijos.

14. Numeros consolidados del diff

Metrica	R5 (inicio)	R6	R7 (inicio)	R8 (inicio)	R8 (fin)	R9 (fin)
Total	1280	1205	877	877	404	332
Tier 1	247	—	141	141	72	62
Tier 2	912	—	625	625	220	158
Tier 3	120	—	111	111	111	111
Tier 4	1	—	1	1	1	1
indice_falta	251	—	180	180	86	14
constraint_falta	541	—	427	427	61	61
constraint_nombre_desalineado	—	—	124	124	124	124
constraint_desalineada	—	—	72	72	72	72
comment_desalineado	—	—	20	20	20	20
tabla_falta	17	—	10	10	10	10

Bajada total: −948 items (−74.1%) desde R5.
−72 items (−17.8%) en R9.
−473 items (−54%) en R8.

15. Como empezar R10 — Checklist

Verificar entorno:

cd D:\aTaxip\backend
.\venv\Scripts\Activate.ps1
alembic current      # → m3_010
git log --oneline -1 # → a887cc3
git status           # → clean

Verificar diff actual:

python scripts\orm_sync\apply.py --stats
# → Total 332 items

Backup DB preventivo:

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda10.dump"

Empezar con Prioridad 1 (fix diff_indexes):

Ver la funcion diff_indexes en scripts/orm_sync/diff.py.
Cambiar el matching de indices a (nombre_normalizado, columnas).
Regenerar diff.
Verificar 332 → ~331.
Commit.

Seguir con Prioridad 2 (migracion GIST).

16. Referencias cruzadas

Deuda completa: docs/DEUDA_TECNICA_ACTUAL.md.

Decisiones tomadas: docs/orm_sync/orm_decisiones.md (D-014 a D-028) +
docs/orm_sync/orm_decisiones_historico.md.

Hallazgos historicos (H-001 a H-026): docs/orm_sync/orm_decisiones_historico.md.

Plan original: docs/orm_reconciliacion_plan.md.

Handoff R7→R8: docs/CONTEXTO_RONDA_7 a 8.md.

Handoff R8→R9: docs/CONTEXTO_RONDA_8 a 9 — Handoff detallado.md.

Handoff R9→R10: docs/CONTEXTO_RONDA_9 a 10.md (este documento).

FIN DEL DOCUMENTO