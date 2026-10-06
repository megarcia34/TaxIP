CONTEXTO RONDA 8 a 9 — Handoff detallado
Documento de arranque. Pegar como primer mensaje del próximo chat.

1. Proyecto
TaxIP 2.0 — backend FastAPI + SQLAlchemy 2.0 async + PostgreSQL 17 + PostGIS 3.6.

Root backend: D:\aTaxip\backend

Git root: D:/aTaxip

Branch: main

Python: 3.12.10 (venv en .\venv\Scripts\Activate.ps1)

Alembic head: m3_010

Backend: python run.py (NO python -m uvicorn)

2. Estado al cierre de Ronda 8
Fecha de cierre: 2026-10-05

Tag de cierre: ronda8-fase6-completa

Commit: c5bd634

HEAD local = HEAD remoto: c5bd634 (tag pusheado)

Working tree: clean

Diff total: 404 items (bajó desde 877 al inicio de R8, −54%).

Tags existentes:

ronda5-baseline-pre, ronda5-fase0-completa, ronda5-fase1-completa, ronda5-completa

ronda6-fase2-sesion1-completa, ronda6-fase2-sesion2-completa, ronda6-fase3-completa, ronda6-completa

ronda7-fase4b-paso3-completo, ronda7-fase4b-paso7-completo, ronda7-fase4b-completa

ronda8-fase6-completa

Commits locales R8 (todos pusheados):

text
c5bd634 fix(turno, gasto_turno): agregar 6 indices (Paso 6.9 y 6.10)
44daf51 fix(fleet): agregar UNIQUE documentos_chofer + indices categoria_gasto y documento_propietario (Paso 6.8.C+6.8.D)
6fd1de4 chore(orm_sync): regenerar snapshot post UNIQUE fix (Paso 6.8.A)
d133472 fix(fleet): usar Index unique=True para uq_neumatico_codigo_interno (refleja DB)
ce55835 fix(fleet): agregar 41 indices (neumatico_* + contrato_vehiculo + notificacion + contrato_qr + propietario) (Paso 6.8.A+B)
824d770 fix(fleet): agregar 26 indices de neumatico_* (Paso 6.8.A)
a2010f2 fix(geo, foto_viaje): agregar 2 indices faltantes (Paso 6.6 y 6.7)
973dda9 fix(payment): agregar 4 indices faltantes en pago_empresa (Paso 6.5)
f6226f2 fix(public): agregar 6 indices faltantes (Paso 6.4)
e120b55 fix(tenant): agregar 5 indices faltantes (Paso 6.3)
f6c9fe1 fix(corporate): agregar 7 indices faltantes (Paso 6.2)
b04a2fb fix(audit): agregar 8 indices faltantes en schema audit (Paso 6.1)
b2edb4e fix(trip): corregir doble prefijo ck_ en 8 CHECKs de viaje_solicitado (Paso 4)
d3692f1 fix(orm_sync): excluir *_not_null autogenerados de constraint_falta (Fix 2)
6927f08 fix(orm_sync): normalizar Geography case-insensitive en diff (Fix 1)
270a1e7 chore(orm_sync): congelar baseline diff R7 para Ronda 8
39649ed docs: cierre documental Ronda 7 (handoff + alembic check)
d362823 Fase 4b 9.1: alinear km_registro (Numeric(10,2)) + cerrar Paso 2 residual [tag ronda7-fase4b-completa]
3. Diff actual (404 items) — desglose completo
Por clasificacion
Clasificacion	Cant.	Naturaleza	Accion
constraint_nombre_desalineado	124	Naming convention (ORM usa prefijos pk_/fk_/ck_/uq_).	NO TOCAR (cosmetico)
indice_falta	86	72 PKs + 14 UNIQUE INDEX	Fix de tooling (PKs) + decision (UNIQUEs)
constraint_desalineada	72	PKs con nombre distinto (cosmetico).	Manual / ignorar
constraint_falta	61	CHECKs reales (~33) + other (~20) + UNIQUEs (~9) + FKs (~7).	Paso 4 residual
comment_desalineado	20	Mojibake (13) + Tipo A (7).	Requiere UPDATE DB
constraint_sobra	17	UNIQUEs fantasma (patron D-017).	Decision funcional
tabla_falta	10	Ampliado a ~16 por alembic.	Fase 4c
nullable_desalineado	4	Fantasma.	Ignorar
indice_nombre_desalineado	3	Cosmetico.	Ignorar
indice_sobra	3	Real.	Paso 9
schema_falta	2	comunicacion, rentabilidad.	Fase 4c
tabla_sobra	1	trip.reserva.	Fase 4d
columna_falta	1	usuario_rol.control_base_id.	Decision: no tocar
Por Tier
Tier	Cant.	Estado
Tier 1 (critico)	72	En progreso
Tier 2 (importante)	220	En progreso
Tier 3 (cosmetico)	111	Mayormente ignorable
Tier 4 (muerte)	1	trip.reserva
Deuda real vs ruido
Deuda real (~110 items):

61 constraint_falta (CHECKs + FKs + UNIQUEs faltantes).

20 comment_desalineado.

10 tabla_falta + 2 schema_falta (Fase 4c).

3 indice_sobra.

1 columna_falta (no tocar).

~13 otros.

Ruido/cosmetico (~294 items):

124 constraint_nombre_desalineado.

72 constraint_desalineada.

86 indice_falta (72 PKs + 14 UNIQUE INDEX).

17 constraint_sobra.

3 indice_nombre_desalineado.

1 tabla_sobra.

4. Que se cerro en Ronda 8
Fixes de tooling (diff.py)
Fix 1 (6927f08): funcion _types_equivalent() que normaliza Geography/Geometry a lowercase antes de comparar. Elimina los 4 falsos positivos de tipo_desalineado. Impacto: −4 items.

Fix 2 (d3692f1): regex RE_NOT_NULL_AUTOGEN = r"^\d+_\d+_\d+_not_null$" para excluir CHECKs autogenerados por Alembic. Impacto: −358 items (constraint_falta: 427 → 69).

Fix del ORM
Fix 3 (b2edb4e): los 8 CheckConstraint de trip.viaje_solicitado tenian name="ck_viaje_solicitado_ck_viaje_X" (con prefijo ck_viaje_solicitado_ interno). La convention ck_%(table_name)s_%(constraint_name)s de app/database.py agregaba el prefijo otra vez, generando nombres triple-prefijados. Fix: quitar el prefijo interno. Impacto: −16 items.

Fase 6 — Indices reales (~98 aplicados)
Archivo	Indices	Commit
audit.py	8	b04a2fb
corporate.py	7	f6c9fe1
tenant.py	5	e120b55
public.py	6	f6226f2
payment.py	4	973dda9
geo.py	1	a2010f2
foto_viaje.py	1	a2010f2
fleet.py (neumatico_*)	26	824d770
fleet.py (resto)	41	ce55835
fleet.py (UNIQUE fix)	1	d133472
fleet.py (6.8.C+D)	4	44daf51
turno.py + gasto_turno.py	6	c5bd634
Total	~98	
Impacto acumulado: indice_falta: 180 → 86 (−94). fleet schema 100% reconciliado.

Documentacion
270a1e7: baseline diff R7 congelado.

39649ed: handoff R7→R8 + alembic check cierre R7.

6fd1de4: snapshot regenerado post UNIQUE fix.

5. Deudas nuevas identificadas en R8
orm.unique_constraint_vs_unique_index (Tier 3)
14 items donde el ORM declara UniqueConstraint y la DB tiene CREATE UNIQUE INDEX. Funcionalmente equivalentes. Afecta: auth.autorizacion_inicio, auth.refresh_token, auth.tipo_usuario, auth.usuario_rol, corporate.cuenta_corriente, corporate.factura_corporativa, fleet.categoria_gasto, fleet.contrato_qr, fleet.marca, fleet.vehiculo, payment.billetera, payment.metodo_pago, public.comercio, tenant.configuracion_tenant, tenant.factura, trip.calificacion. Fix posible: cambiar UniqueConstraint por Index(unique=True) en masa (patron D-017).

orm.indice_falta_incluye_pks (Tier 2)
diff.py reporta 72 PKs (pk_* / *_pkey) como indice_falta. Son ruido. Fix de tooling: filtrar en diff_indexes por nombre. Bajaría el diff de 404 a ~332.

orm.comercio_indice_redundante (Tier 3)
public.comercio.idx_comercio_codigo_qr es redundante con el UNIQUE constraint comercio_codigo_qr_key (misma columna). Aplicado por fidelidad a la DB.

orm.tabla_falta_ampliada (Tier 2)
El alembic check revelo ~16 tablas faltantes (no 10):

comunicacion (3): conversacion (7 cols), email_enviado (9), mensaje (8).

rentabilidad (3): analisis_medios_pago (10), rentabilidad_diaria_vehiculo (13), rentabilidad_mensual_vehiculo (13).

auth (4): codigo_metadatos (6), codigo_verificacion (9), plantilla_viaje (19), prestadora_telefonica (6).

payment (2): qr_cobro (10), configuracion_pasarela (7).

audit (1): alertas_vencimiento (8).

trip (1): broadcast_log (11).

fleet (2): historial_chofer_vehiculo (6), relacion_propietario_vehiculo (7).

metodo_pago.pasarela (actualizada)
Hallazgo R8: payment.qr_cobro y payment.configuracion_pasarela ya existen en la DB pero no estan declaradas en el ORM. La infra para /cobro-qr esta hecha.

6. Deudas cerradas en R8
orm.geography_case_divergente — CERRADA (Fix 1).

orm.naming_convention_doble_prefijo — CERRADA (Fix 3).

orm.diff_check_nombres_no_matchean — CERRADA (Fix 2).

7. Deudas pendientes (heredadas + nuevas)
Bloqueante produccion
B5 — ViajeSolicitado desactualizado. Tecnicamente desbloqueado (Fase 4a completada en R6). Falta verificacion formal.

Critico
orm.db_desalineados — 404 items. En progreso.

Alta prioridad
orm.paso4_check_constraints_residual — ~61 items de constraint_falta.

G63 — Alerta si el motor de precios cae a fallback.

G67 — check_out_turno sin escapatoria si hay viajes huerfanos.

G80 — App apunta a Metro (no funciona fuera de WiFi dev).

Media prioridad
metodo_pago.catalogo_sucio, metodo_pago.fk_catalogo, metodo_pago.ingreso_turno, metodo_pago.frontend_e2.

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

8. Plan de Ronda 9 (recomendado)
Prioridad 1 — Fix de diff.py (PKs ruidosas)
Deuda: orm.indice_falta_incluye_pks.

Cambio: filtrar en diff_indexes los nombres pk_* y *_pkey. Tambien constraint_desalineada (PKs con nombre distinto).

Impacto esperado: 404 → ~332 items (−72). La palanca mas grande.

Riesgo: bajo (solo excluye PKs, no indices reales).

Prioridad 2 — Fase 4c (tablas faltantes)
Crear:

app/models/comunicacion.py (3 tablas: conversacion, email_enviado, mensaje).

app/models/rentabilidad.py (3 tablas: analisis_medios_pago, rentabilidad_diaria_vehiculo, rentabilidad_mensual_vehiculo).

Ampliar app/models/auth.py (4 tablas: codigo_metadatos, codigo_verificacion, plantilla_viaje, prestadora_telefonica).

Ampliar app/models/payment.py (2 tablas: qr_cobro, configuracion_pasarela).

Ampliar app/models/audit.py (alertas_vencimiento).

Ampliar app/models/trip.py (broadcast_log — decisional).

Ampliar app/models/fleet.py (historial_chofer_vehiculo, relacion_propietario_vehiculo).

Registrar en app/models/__init__.py.

Impacto esperado: −10 tabla_falta −2 schema_falta = −12 items.

Prioridad 3 — Paso 9 (limpieza)
Items: 3 indice_sobra + 1 tabla_sobra.

Impacto: −4 items.

Prioridad 4 — Comments (mojibake)
Deuda: 13 items con mojibake + 7 Tipo A = 20 total.

Accion: requiere UPDATE en DB con backup previo. Backup obligatorio.

Impacto: −20 items.

Prioridad 5 — Paso 4 residual (CHECKs)
Bloqueado por orm.naming_convention_check_divergente.

Fix propuesto: matchear CHECKs por definicion normalizada en diff.py, no por nombre.

Impacto potencial: ~61 items de constraint_falta.

Prioridad 6 — Actualizar deuda y docs
docs/DEUDA_TECNICA_ACTUAL.md (ya actualizado).

docs/CONTEXTO_RONDA_8 a 9.md (este documento).

docs/orm_sync/orm_decisiones.md (D-014 a D-019).

9. Mensaje de arranque sugerido para Ronda 9
text
Continuamos Ronda 9. Ronda 8 cerrada (tag ronda8-fase6-completa en c5bd634,
origin/main sincronizado). 404 items en el diff.

Estado verificado:
- Python 3.12.10, PostgreSQL 17, PostGIS 3.6, Alembic head m3_010.
- Backend arranca limpio (python run.py OK).
- Imports de modelos OK.
- fleet schema 100% reconciliado.

Prioridad R9:
A) Fix de diff.py para excluir PKs de indice_falta (−72 items).
B) Fase 4c (comunicacion.py, rentabilidad.py, ampliar auth.py, payment.py,
   audit.py, trip.py, fleet.py) (−12 items).
C) Paso 9 (limpieza, 4 items).
D) Comments mojibake (20 items).
E) Paso 4 residual (CHECKs, ~61 items) si se desbloquea.

Recomendacion: A primero (mayor impacto, bajo riesgo), despues B,
despues C, despues D. E si queda tiempo.

Reglas: no tocar DB sin backup, no correr alembic autogenerate,
no usar python -m uvicorn. Ciclo: editar → verificar import →
regenerar snapshots → apply.py --stats → commit.
10. Comandos utiles
Verificar entorno
powershell
cd D:\aTaxip\backend
.\venv\Scripts\Activate.ps1
alembic current
alembic heads
git status
git log --oneline -5
Regenerar snapshots
powershell
python scripts\orm_sync\introspect_orm.py    # solo si cambio el ORM
python scripts\orm_sync\diff.py
python scripts\orm_sync\apply.py --stats
Analizar diff
powershell
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
powershell
$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda9.dump"
Consultar pg_indexes de una tabla
powershell
$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT indexname, indexdef FROM pg_indexes WHERE schemaname='<schema>' AND tablename='<tabla>' ORDER BY indexname;"
Consultar pg_constraint de una tabla
powershell
$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT conname, contype, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = '<schema>.<tabla>'::regclass ORDER BY conname;"
Ver tamano del archivo (util para .gitignore)
powershell
Get-Item docs\orm_sync\alembic_check_cierre_r8_2026-10-05.txt | Select-Object Length
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
powershell
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
VS Code puede agregar un BOM (EF BB BF) al inicio del archivo. Esto rompe import ast y todos los scripts de orm_sync. Si pasa:

powershell
python -c "content = open('app/models/<archivo>.py', encoding='utf-8-sig').read(); open('app/models/<archivo>.py', 'w', encoding='utf-8').write(content); print('BOM removed')"
Verificar sin BOM:

powershell
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

docs/orm_sync/baseline_diff_r7_final.json (baseline R7 congelado)

docs/orm_sync/alembic_check_cierre_r8_2026-10-05.txt (snapshot post-R8)

Documentacion
docs/DEUDA_TECNICA_ACTUAL.md (actualizado post-R8)

docs/HISTORICO_CERRADAS.md (R4-R7)

docs/orm_sync/orm_decisiones.md (D-014 a D-019)

docs/orm_sync/orm_decisiones_historico.md (D-001 a D-013)

docs/orm_reconciliacion_plan.md

docs/orm_sync/orm_plan_aplicacion.md

docs/orm_sync/baseline_info.md

docs/CONTEXTO_RONDA_8 a 9.md (este documento)

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
Cuidado con BOM al editar.

app/models/auth.py — Pendiente Fase 4c
4 tablas faltantes: codigo_metadatos, codigo_verificacion, plantilla_viaje, prestadora_telefonica.
14 constraint_nombre_desalineado + 12 constraint_desalineada (cosmetico).
12 PKs + 4 UNIQUEs fantasma (ruido).

app/models/payment.py — Nuevo hallazgo R8
Tablas qr_cobro y configuracion_pasarela existen en DB pero no en ORM. Fase 4c.

app/database.py — Naming convention
python
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)
CUIDADO: la convention agrega prefijos automaticamente. Si declaras name="ck_X" en un CheckConstraint, el nombre final es ck_<tabla>_ck_X. No duplicar prefijos.

14. Numeros consolidados del diff
Metrica	R5 (inicio)	R6	R7 (inicio)	R8 (inicio)	R8 (fin)
Total	1280	1205	877	877	404
Tier 1	247	—	141	141	72
Tier 2	912	—	625	625	220
Tier 3	120	—	111	111	111
Tier 4	1	—	1	1	1
indice_falta	251	—	180	180	86
constraint_falta	541	—	427	427	61
constraint_nombre_desalineado	—	—	124	124	124
constraint_desalineada	—	—	72	72	72
comment_desalineado	—	—	20	20	20
tabla_falta	17	—	10	10	10
Bajada total: −876 items (−68.4%) desde R5. −473 items (−54%) en R8.

15. Como empezar R9 — Checklist
Verificar entorno:

powershell
cd D:\aTaxip\backend
.\venv\Scripts\Activate.ps1
alembic current      # → m3_010
git log --oneline -1 # → c5bd634
git status           # → clean
Verificar diff actual:

powershell
python scripts\orm_sync\apply.py --stats
# → Total 404 items
Backup DB preventivo:

powershell
$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda9.dump"
Empezar con Prioridad 1 (Fix diff.py PKs):

Ver la funcion diff_indexes en scripts/orm_sync/diff.py.

Agregar filtro pk_* / *_pkey.

Regenerar diff.

Verificar 404 → ~332.

Commit.

Seguir con Fase 4c.

16. Referencias cruzadas
Deuda completa: docs/DEUDA_TECNICA_ACTUAL.md.

Decisiones tomadas: docs/orm_sync/orm_decisiones.md (D-014 a D-019) + docs/orm_sync/orm_decisiones_historico.md.

Hallazgos historicos (H-001 a H-026): docs/orm_sync/orm_decisiones_historico.md.

Plan original: docs/orm_reconciliacion_plan.md.

Handoff R7→R8: docs/CONTEXTO_RONDA_7 a 8.md.

FIN DEL DOCUMENTO