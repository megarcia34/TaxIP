CONTEXTO RONDA 10 a 11 — Handoff detallado
Documento de arranque. Pegar como primer mensaje del proximo chat.

1. Proyecto

TaxIP 2.0 — backend FastAPI + SQLAlchemy 2.0 async + PostgreSQL 17 + PostGIS 3.6.

Root backend: D:\aTaxip\backend

Git root: D:/aTaxip

Branch: main

Python: 3.12.10 (venv en .\venv\Scripts\Activate.ps1)

Alembic head: m3_012

Backend: python run.py (NO python -m uvicorn)

2. Estado al cierre de Ronda 10

Fecha de cierre: 2026-10-06

Tag de cierre: ronda10-fase10-completa (pendiente)

Commit: b8ffd5a

HEAD local = HEAD remoto: b8ffd5a (pusheado)

Working tree: clean (solo snapshots pendientes de commit de cierre)

Diff total: 114 items (bajo desde 332 al inicio de R10, −66%).

Tags existentes:

ronda5-baseline-pre, ronda5-fase0-completa, ronda5-fase1-completa, ronda5-completa

ronda6-fase2-sesion1-completa, ronda6-fase2-sesion2-completa, ronda6-fase3-completa, ronda6-completa

ronda7-fase4b-paso3-completo, ronda7-fase4b-paso7-completo, ronda7-fase4b-completa

ronda8-fase6-completa

ronda9-fase9-completa

ronda10-fase10-completa (pendiente de crear)

Commits locales R10 (todos pusheados):

b8ffd5a feat(migrations): m3_012 renombra CHECK gasto_turno al nombre canonico

783363b fix(orm_sync): forzar cast ::text[] en arrays de information_schema

9520129 fix(orm_sync): matchear PK y FK por columnas, no por nombre

1af08de fix(gasto_turno): alinear nombre de CHECK a la convention del ORM

ccead93 fix(models): eliminar index=True redundante en columnas UNIQUE

1d4debd fix(trip): restaurar idx_viaje_origen_gist + desactivar GIST auto en origen

113f324 fix(orm_sync): matchear indices por (nombre, columnas) + clasificar GIST GeoAlchemy2

3. Diff actual (114 items) — desglose completo

Por clasificacion

Clasificacion	Cant.	Naturaleza	Accion

constraint_falta	48	CHECKs reales (~26) + FKs (~10) + UNIQUEs (~10) + other (~2).	Paso 4 residual / m3_014

indice_falta	22	B-tree reales.	Paso 6 residual

comment_desalineado	20	Mojibake (13) + Tipo A (7).	Requiere UPDATE DB

tabla_falta	10	Ampliado a ~16 por alembic.	Fase 4c

constraint_sobra	6	5 UNIQUEs Caso C + metodo_pago.	m3_013 + D-005

nullable_desalineado	4	Fantasma.	Ignorar

schema_falta	2	comunicacion, rentabilidad.	Fase 4c

tabla_sobra	1	trip.reserva.	Fase 4d

columna_falta	1	usuario_rol.control_base_id.	Decision: no tocar

Por Tier

Tier	Cant.	Estado

Tier 1 (critico)	20	En progreso

Tier 2 (importante)	79	En progreso

Tier 3 (cosmetico)	14	Mayormente ignorable

Tier 4 (muerte)	1	trip.reserva

Deuda real vs ruido

Deuda real (~114 items):

48 constraint_falta (CHECKs + FKs + UNIQUEs).

22 indice_falta (B-tree reales).

20 comment_desalineado.

10 tabla_falta + 2 schema_falta (Fase 4c).

6 constraint_sobra (5 UNIQUEs Caso C + metodo_pago).

4 nullable_desalineado (fantasmas).

1 tabla_sobra + 1 columna_falta.

Ruido: minimo. El fix de tooling de R10 elimino los 176 items
cosmeticos y los ~100 falsos positivos por columnas corruptas.

4. Que se cerro en Ronda 10

Fix 1 — diff_indexes matching (commit 113f324)

Problema: diff_indexes matcheaba por tuple(columns). Si el ORM declaraba
dos indices sobre la misma columna, solo uno aparecia. Enmascaraba fixes.

Fix: matching por (nombre_normalizado, columnas) + clasificacion
indice_falta_en_db para GIST auto-generados por GeoAlchemy2.

Impacto: 332 → 341 (sube porque expone 9 indice_falta antes colapsados
y +4 indice_falta_en_db).

Fix 2 — trip.py (commit 1d4debd)

El commit 113f324 elimino idx_viaje_origen_gist asumiendo redundancia.
Verificacion contra DB: la DB tiene idx_viaje_origen_gist y NO tiene el
auto-generado. Restaurado el Index manual + spatial_index=False en
origen.

Impacto: 341 → 339 (-2).

Fix 3 — auth.py + fleet.py (commit ccead93)

auth.usuario.email y fleet.vehiculo.patente tienen UNIQUE en DB. El
index=True del ORM generaba indices B-tree duplicados. Eliminado.

Impacto: indice_sobra 1 → 0.

Fix 4 — gasto_turno.py (commit 1af08de)

CHECK con name='check_monto_positivo' expandido por convention a
ck_gasto_turno_check_monto_positivo. Cambiado a name='monto_check' →
ck_gasto_turno_monto_check (canonico).

Fix 5 — introspect_db.py cast ::text[] (commit 783363b)

Bug grave: psycopg2 no adaptaba los arrays de information_schema a
list. El db_snapshot.json tenia PKs y UNIQUEs con columnas corruptas.

Fix: cast ::text[] en array_agg. Impacto: ~100 falsos positivos
eliminados.

Fix 6 — diff_constraints PK/FK por columnas (commit 9520129)

La DB tiene dos convenciones de nombres mezcladas. El ORM usa pk_<tabla>
y fk_<tabla>_<col>_<ref>. 176 items cosmeticos.

Fix: PK/FK matchean por columnas (y ref), no por nombre.

Impacto: 295 → 119 (-60%).

Migracion m3_011 (commit 783363b)

Crea 3 GIST sobre Geography:
- fleet.chofer_vehiculo.idx_chofer_vehiculo_ubicacion
- trip.panico.idx_panico_ubicacion
- trip.viaje_solicitado.idx_viaje_solicitado_destino

Impacto: 119 → 116 (-3 indice_falta_en_db, -3 indice_falta simetricos).

Migracion m3_012 (commit b8ffd5a)

Rename CHECK gasto_turno_monto_check → ck_gasto_turno_monto_check.

Impacto: 116 → 114 (-2 items).

5. Deudas nuevas identificadas en R10

orm.unique_constraints_caso_c (Tier 2)

5 UNIQUEs que el ORM declara y la DB no tiene:
- auth.perfil_general.usuario_id
- auth.reset_token.token
- fleet.vehiculo.qr_uuid
- tenant.configuracion_tenant.control_base_id
- trip.calificacion.viaje_id

Verificacion: 0 duplicados en las 5 tablas.

Accion: migracion m3_013.

6. Deudas cerradas en R10

- orm.introspect_db_arrays_corruptos.
- orm.diff_nombres_pk_fk.
- orm.indice_falta_en_db.
- orm.gasto_turno_check_nombre.
- orm.diff_indexes_colapsa_por_columnas.
- orm.geoalchemy2_indices_no_aplicados.
- orm.indice_sobra_ambiguo.

7. Deudas pendientes (heredadas + nuevas)

Bloqueante produccion

B5 — ViajeSolicitado desactualizado. Tecnicamente desbloqueado (Fase 4a
completada en R6). Falta verificacion formal.

Critico

orm.db_desalineados — 114 items. En progreso.

Alta prioridad

orm.paso4_check_constraints_residual — ~26 CHECKs con naming convention
divergente.

G63 — Alerta si el motor de precios cae a fallback.

G67 — check_out_turno sin escapatoria si hay viajes huerfanos.

G80 — App apunta a Metro.

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

8. Plan de Ronda 11 (recomendado)

Prioridad 1 — Migracion m3_013 (5 UNIQUEs Caso C)

Deuda: orm.unique_constraints_caso_c.

Accion: agregar los 5 UNIQUEs a la DB con los nombres que el ORM ya
declara:
- uq_perfil_general_usuario_id
- uq_reset_token_token
- uq_vehiculo_qr_uuid
- uq_configuracion_tenant_control_base_id
- uq_calificacion_viaje_id

Requiere: backup DB previo, verificacion post-migracion con pg_constraint.

Impacto esperado: -10 items (5 constraint_sobra + 5 indice_falta simetricos).

Riesgo: bajo (ya verificado 0 duplicados).

Prioridad 2 — Migracion m3_014 (CHECKs D-027)

Deuda: orm.naming_convention_check_divergente + orm.paso4_check_constraints_residual.

Accion: auditar los ~26 CHECKs restantes con naming divergente. Para
cada uno:
1. Verificar el nombre real en DB (psql pg_constraint).
2. Decidir si renombrar en DB (m3_014) o cambiar el ORM.

Grupos:
- Doble prefijo en DB: ck_<tabla>_ck_<tabla>_<nombre> (~10).
- Sin convention: check_X, X_check, chk_X (~16).

Impacto esperado: -26 items (13 constraint_sobra + 13 constraint_falta).

Riesgo: medio (auditoria individual por CHECK).

Prioridad 3 — Fase 4c (tablas faltantes)

Deuda: orm.tabla_falta_ampliada.

Crear:
- app/models/comunicacion.py (3 tablas).
- app/models/rentabilidad.py (3 tablas).
- Ampliar auth.py (4 tablas).
- Ampliar payment.py (2 tablas).
- Ampliar audit.py (1 tabla).
- Ampliar trip.py (1 tabla: broadcast_log — decisional).
- Ampliar fleet.py (2 tablas).

Impacto esperado: -10 tabla_falta - 2 schema_falta = -12 items.

Prioridad 4 — Paso 6 residual (indices B-tree)

Deuda: 22 indice_falta.

Accion: aplicar los B-tree reales al ORM (~15-20).

Impacto: -15 a -20 items.

Prioridad 5 — Comments (backup previo)

Deuda: 20 comment_desalineado.

- 7 Tipo A (ORM tiene, DB no): COMMENT ON COLUMN en DB.
- 13 mojibake: COMMENT ON COLUMN corregido en DB.

Requiere: backup DB.

Impacto: -20 items.

Prioridad 6 — Actualizar deuda y docs

docs/DEUDA_TECNICA_ACTUAL.md (ya actualizado en R10).

docs/CONTEXTO_RONDA_11 a 12.md (nuevo handoff).

docs/orm_sync/orm_decisiones.md (D-029 a D-031 si aplica).

9. Mensaje de arranque sugerido para Ronda 11

Continuamos Ronda 11. Ronda 10 cerrada (tag ronda10-fase10-completa
pendiente, commit b8ffd5a, origin/main sincronizado). 114 items en el
diff.

Estado verificado:
- Python 3.12.10, PostgreSQL 17, PostGIS 3.6, Alembic head m3_012.
- Backend arranca limpio (python run.py OK).
- Imports de modelos OK.
- Los fixes de tooling de R10 estan aplicados (diff.py, introspect_db.py).

Prioridad R11:
A) Migracion m3_013 (5 UNIQUEs Caso C) (-10 items, requiere backup).
B) Migracion m3_014 (CHECKs D-027) (-26 items, requiere auditoria).
C) Fase 4c (tablas faltantes) (-12 items).
D) Paso 6 residual (indices B-tree) (-15 a -20 items).
E) Comments mojibake (-20 items).

Recomendacion: A primero (bajo riesgo, alto impacto), despues C (ORM puro,
sin DB), despues B (auditoria), D y E si queda tiempo.

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

python scripts\orm_sync\introspect_db.py    # solo si cambio la DB
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

Backup DB

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda11.dump"

Consultar pg_constraint de una tabla

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT conname, contype, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = '<schema>.<tabla>'::regclass ORDER BY conname;"

Consultar pg_indexes de una tabla

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT indexname, indexdef FROM pg_indexes WHERE schemaname='<schema>' AND tablename='<tabla>' ORDER BY indexname;"

11. Reglas operativas (CRITICAS)

NO committear snapshots en commits intermedios.

- Commits intermedios: solo archivos de codigo (.py) o migraciones.
- Cierre de ronda: UN unico commit "chore: snapshots de cierre RN" con
  los 5 snapshots regenerados + docs.
- Docs: commits separados, agrupados por tema, solo al cierre de ronda.

NO hacer

NO tocar la DB sin backup previo.

NO correr alembic revision --autogenerate (destructivo).

NO usar python -m uvicorn. Usar python run.py.

NO commitear cambios de tipo masivo sin verificar import.

NO pegar bloques grandes sin verificar pestana activa.

NO pegar fragmentos de codigo Python en PowerShell (van en el editor).

SI hacer

1 commit por paso.

Snapshots (introspect_db.py + introspect_orm.py + diff.py) al inicio de
cada sub-paso.

Comentarios de codigo: ASCII puro (N10).

Comments de columnas (strings al usuario): UTF-8 permitido.

PowerShell + here-string: usar @"..."@ para evitar problemas con \".

Errores de encoding: VS Code debe guardar UTF-8 SIN BOM.

Ciclo por sub-paso

cd D:\aTaxip\backend
.\venv\Scripts\Activate.ps1

# 1. Editar archivo
# 2. Verificar sintaxis
python -c "import ast; ast.parse(open('app/models/<archivo>.py', encoding='utf-8').read()); print('Sintaxis OK')"

# 3. Verificar import
python -c "from app.models.<archivo> import <Clase>; print('Import OK')"

# 4. Regenerar snapshots
python scripts\orm_sync\introspect_orm.py
python scripts\orm_sync\diff.py

# 5. Ver stats
python scripts\orm_sync\apply.py --stats

# 6. Commit
git add app\models\<archivo>.py
git commit -m "..."

Regla del BOM

VS Code puede agregar un BOM (EF BB BF) al inicio del archivo. Esto rompe
import ast y todos los scripts de orm_sync. Si pasa:

python -c "content = open('app/models/<archivo>.py', encoding='utf-8-sig').read(); open('app/models/<archivo>.py', 'w', encoding='utf-8').write(content); print('BOM removed')"

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

docs/orm_sync/alembic_check_cierre_r8_2026-10-05.txt

Documentacion

docs/DEUDA_TECNICA_ACTUAL.md (actualizado post-R10)

docs/HISTORICO_CERRADAS.md (R4-R7)

docs/orm_sync/orm_decisiones.md

docs/orm_sync/orm_decisiones_historico.md

docs/orm_reconciliacion_plan.md

docs/orm_sync/orm_plan_aplicacion.md

docs/orm_sync/baseline_info.md

docs/CONTEXTO_RONDA_10 a 11.md (este documento)

ORM (modelos)

app/models/__init__.py

app/models/fleet.py

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

Migraciones

migrations/versions/m3_010_metodo_pago_canonico.py

migrations/versions/m3_011.py

migrations/versions/m3_012.py

Bitacoras (fuera del repo)

E:\Taxip\app chofer\BITACORA_M1.md

E:\Taxip\app chofer\BITACORA_M2.md

E:\Taxip\app chofer\BITACORA_M3.md

13. Archivos criticos con estado especial

app/models/trip.py — Residual del Paso 4

8 CHECKs de trip.viaje_solicitado corregidos en R8. Restaurado
idx_viaje_origen_gist en R10. Siguen pendientes:
- constraint_falta residual (~48 items en otros schemas).
- 1 tabla_sobra: trip.reserva (Fase 4d).
- 1 tabla_falta: trip.broadcast_log (11 cols).

app/models/fleet.py

23+ clases, ~1500 lineas. 60 indices + 2 UNIQUEs aplicados en R8.
B-tree redundante eliminado en R9. index=True redundante en patente
eliminado en R10. Cuidado con BOM al editar.

app/models/auth.py

4 tablas faltantes para Fase 4c: codigo_metadatos, codigo_verificacion,
plantilla_viaje, prestadora_telefonica.

index=True en email eliminado en R10.

app/models/payment.py

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

Metrica	R5 (inicio)	R6	R7	R8	R9	R10
Total	1280	1205	877	404	332	114
Tier 1	247	—	141	72	62	20
Tier 2	912	—	625	220	158	79
Tier 3	120	—	111	111	111	14
Tier 4	1	—	1	1	1	1
indice_falta	251	—	180	86	14	22
constraint_falta	541	—	427	61	61	48
comment_desalineado	—	—	20	20	20	20
tabla_falta	17	—	10	10	10	10

Bajada total: −1166 items (−91%) desde R5.
−218 items (−66%) en R10.

15. Como empezar R11 — Checklist

Verificar entorno:

cd D:\aTaxip\backend
.\venv\Scripts\Activate.ps1
alembic current      # → m3_012
git log --oneline -1 # → b8ffd5a
git status           # → clean

Verificar diff actual:

python scripts\orm_sync\apply.py --stats
# → Total 114 items

Backup DB preventivo:

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda11.dump"

Empezar con Prioridad 1 (m3_013):

Verificar los 5 UNIQUEs en DB (ya verificado 0 duplicados en R10).
Crear migrations/versions/m3_013.py con los 5 ALTER TABLE ADD CONSTRAINT.
Aplicar alembic upgrade head.
Verificar 114 → 104.
Commit.

Seguir con Prioridad 2 (m3_014) o Prioridad 3 (Fase 4c).

16. Referencias cruzadas

Deuda completa: docs/DEUDA_TECNICA_ACTUAL.md.

Decisiones tomadas: docs/orm_sync/orm_decisiones.md + docs/orm_sync/orm_decisiones_historico.md.

Hallazgos historicos (H-001 a H-026): docs/orm_sync/orm_decisiones_historico.md.

Plan original: docs/orm_reconciliacion_plan.md.

Handoff R9→R10: docs/CONTEXTO_RONDA_9 a 10.md.

Handoff R10→R11: docs/CONTEXTO_RONDA_10 a 11.md (este documento).

FIN DEL DOCUMENTO