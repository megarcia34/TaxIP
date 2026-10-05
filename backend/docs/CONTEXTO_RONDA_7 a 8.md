Resumen de cierre Ronda 7 — Handoff para Ronda 8
Documento de arranque. Pegar como primer mensaje del próximo chat.

1. Proyecto
TaxIP 2.0 — backend FastAPI + SQLAlchemy 2.0 async + PostgreSQL 17 + PostGIS 3.6.

Root: D:\aTaxip\backend

Git root: D:/aTaxip

Branch: main

Python: 3.12.10 (venv en .\venv\Scripts\Activate.ps1)

Alembic head: m3_010

Backend: FastAPI, se corre con python run.py (NO python -m uvicorn).

2. Estado al cierre de Ronda 7
Fecha de cierre: 2026-10-05 07:15
Tag de cierre: ronda7-fase4b-completa en commit d362823
HEAD local = HEAD remoto: d362823 (con tag ronda7-fase4b-completa)
Working tree: clean

Diff total: 877 items (bajó desde 1205 al inicio de R7, −27.2%).

Tags existentes:

ronda5-baseline-pre

ronda5-fase0-completa

ronda5-fase1-completa

ronda5-completa

ronda6-fase2-sesion1-completa

ronda6-fase2-sesion2-completa

ronda6-fase3-completa

ronda6-completa

ronda7-fase4b-paso3-completo

ronda7-fase4b-paso7-completo

ronda7-fase4b-completa

Verificación final R7:

alembic check OK (ruidoso, esperado — guardado en docs/orm_sync/alembic_check_cierre_r7_2026-10-04.txt, sin commitear).

python -c "import app.models" → Models OK.

python run.py → startup completo, cero errores.

3. Diff actual (877 items) — desglose
Por clasificación
Clasificación	Cant.	Naturaleza
constraint_falta	427	~400 falsos positivos (*_not_null autogenerados) + ~27 CHECKs/UNIQUEs/FKs reales
indice_falta	180	Mayoría PKs/UNIQUEs (ruido). ~40-50 índices reales
constraint_nombre_desalineado	124	Cosmético (FKs con naming convention). No tocar
constraint_desalineada	72	Cosmético (PKs con nombre distinto). Manual
constraint_sobra	25	Mayoría falsos positivos
comment_desalineado	20	13 con mojibake + 7 Tipo A. Deuda
tabla_falta	10	Schemas comunicacion, rentabilidad + sueltas → Fase 4c
nullable_desalineado	4	Fantasma (ya aplicados)
indice_nombre_desalineado	4	Cosmético
tipo_desalineado	4	Todos Geography (case). Deuda
indice_sobra	3	Real (eliminar del ORM) → Paso 9
schema_falta	2	comunicacion, rentabilidad → Fase 4c
tabla_sobra	1	Cosmético
columna_falta	1	usuario_rol.control_base_id (decisión: no tocar)
Por Tier
Tier	Cant.
Tier 1	141
Tier 2	625
Tier 3	111
Tier 4	1
Por archivo (automatizables)
Archivo	Items	Estado
app/models/fleet.py	303	Trabajado 3.13, 7.1–7.7, 8.2, 9.1
app/models/auth.py	84	Trabajado 3.14
app/models/trip.py	79	Residuales
app/models/corporate.py	62	Trabajado 3.6
app/models/liquidacion.py	62	Trabajado 3.12
app/models/payment.py	58	Trabajado 3.8, 8.1
app/models/tenant.py	36	Trabajado 3.7
app/models/audit.py	27	Trabajado 3.1, 9.1
app/models/public.py	27	Trabajado 3.2
app/models/turno.py	17	Trabajado 3.10
app/models/geo.py	12	Trabajado 3.4
app/models/gasto_turno.py	11	Trabajado 3.11
app/models/foto_viaje.py	8	No tocado → Fase 4d
app/models/notification.py	6	Trabajado 3.3
4. Qué se cerró en Ronda 7 (Fase 4b)
Paso 3 — Nullable desalineado + columnas + tipos + índices (cerrado en 3.1–3.14)
Archivos: audit.py, public.py, notification.py, geo.py, foto_viaje.py, corporate.py, tenant.py, payment.py, trip.py, turno.py, gasto_turno.py, liquidacion.py, fleet.py, auth.py.

Paso 7 — D-012 timestamps naive (cerrado en 7.1–7.7)
19 timestamps migrados en 7 clases Neumatico* de fleet.py:

NeumaticoOperacionDetalle.created_at

NeumaticoImagen.fecha_subida, .created_at

NeumaticoMedicion.fecha_medicion, .created_at

NeumaticoHistorialPosicion.fecha_montaje, .fecha_desmontaje, .created_at

NeumaticoOperacion.fecha_operacion, .created_at, .updated_at

NeumaticoSugerencia.fecha_generacion, .fecha_atendida, .created_at, .updated_at

NeumaticoVehiculo.fecha_alta, .fecha_baja, .created_at, .updated_at

Cambios:

DateTime(timezone=True) → DateTime(timezone=False)

default=now → server_default=func.now()

onupdate=now → onupdate=func.now()

Bug resuelto: now = datetime.now (Python-side, naive) en columnas tz-aware. PostgreSQL interpretaba el naive con el timezone del server.

Commits: d00dec7, b1d8703, 632bf70, 88c6326, af6abfe, 8a7909e, 56570fa.

Paso 8 (parcial) — Comments (cerrado en 8.1, 8.2)
9 comments alineados:

payment.py (7): ConfiguracionTarifa.{distancia_por_ficha, hora_fin_nocturno, hora_inicio_nocturno, moneda, precio_por_ficha, precio_por_minuto_espera, recargo_domingo}

fleet.py (2): IngresoTurno.medio_pago (→ 6 valores, D-005), ContratoVehiculo.estado_contrato

Commits: 5dd6db6, c80f352.

Paso 2 residual — Tipos (cerrado en 9.1)
fleet.gasto_vehiculo.km_registro: Numeric → Numeric(10, 2).

Commit: d362823.

Fixes administrativos
5b9e689 (7.9): fix encabezado deuda.

022d1fc (7.10): fix fecha encabezado.

6ea9706: .gitignore (temporales de debug).

5. Bloques / deudas identificados en Ronda 7
Paso 4 (CHECKs) — BLOQUEADO
Deuda: orm.naming_convention_check_divergente
Causa: la convention ck_%(table_name)s_%(constraint_name)s en app/database.py agrega prefijo ck_<tabla>_ a todos los CHECKs del ORM. La DB tiene CHECKs con nombres que NO siguen esa convention.
Intento de fix: quoted_name(..., quote=True) — NO funciona en SQLAlchemy 2.0.
Estado: salteado. Deuda orm.paso4_check_constraints_bloqueado.

Paso 8 residual — Comments
Deuda: orm.comments_db_con_mojibake (13 items) + orm.comments_orm_sin_db (7 items).

Items con mojibake (13):

fleet.turno_chofer.snapshot_dia_contractual

fleet.ingreso_turno.declarado_por (doble mojibake)

fleet.ingreso_turno.transaccion_id (doble mojibake)

payment.configuracion_tarifa.descripcion

payment.configuracion_tarifa.modo_calculo

trip.historial_estado_viaje.latitud

trip.historial_estado_viaje.longitud

trip.panico.resuelto_en

trip.panico.usuario_id

trip.tipo_vehiculo.distancia_por_ficha

trip.tipo_vehiculo.precio_por_ficha

trip.tipo_vehiculo.precio_por_minuto_espera

trip.viaje_solicitado.solicitado_en

Items Tipo A (ORM tiene, DB no) (7):

corporate.factura_corporativa.estado

corporate.movimiento_cuenta.tipo_movimiento

corporate.pago_corporativo.estado

fleet.notificacion_vencimiento.entidad_tipo

fleet.notificacion_vencimiento.nivel

public.escaneo_qr.resultado

public.escaneo_qr.tipo_qr

Geography — Deuda
Deuda: orm.geography_case_divergente
Items (4):

fleet.chofer_vehiculo.ubicacion

trip.panico.ubicacion

trip.viaje_solicitado.destino

trip.viaje_solicitado.origen

Causa: GeoAlchemy2 normaliza geometry_type a minúscula internamente. DB tiene Point mayúscula. No se puede alinear desde el ORM.

Deudas anteriores (siguen vigentes)
orm.alembic_check_ruidoso (Tier 2)

orm.snapshot_desactualizado (Tier 2)

orm.diff_falsos_positivos_tipo_cambio (Tier 2)

orm.diff_check_constraints_duplicados (Tier 2)

orm.diff_check_nombres_no_matchean (Tier 2)

orm.reserva_modulo_activo (Tier 2)

orm.foto_viaje_out_of_scope (Tier 2)

orm.db_desalineados (Crítico)

B5 — Modelo ViajeSolicitado desactualizado (Bloqueante)

6. Archivos clave (rutas completas)
Scripts
scripts/orm_sync/introspect_db.py → genera docs/orm_sync/db_snapshot.json

scripts/orm_sync/introspect_orm.py → genera docs/orm_sync/orm_snapshot.json

scripts/orm_sync/diff.py → genera docs/orm_sync/orm_diff.json + orm_diff_reporte.md + orm_diff_acciones.csv

scripts/orm_sync/apply.py → borradores + --stats + --report + --generate

scripts/orm_sync/filtrar_check.py → lista constraint_falta (excluye *_not_null), con subtipos

Snapshots
docs/orm_sync/db_snapshot.json

docs/orm_sync/orm_snapshot.json

docs/orm_sync/orm_diff.json

docs/orm_sync/orm_diff_reporte.md

docs/orm_sync/orm_diff_acciones.csv

docs/orm_sync/orm_diff_acciones.csv

docs/orm_sync/alembic_check_cierre_r7_2026-10-04.txt (sin commitear)

docs/orm_sync/borradores/ (en .gitignore)

Documentación
docs/DEUDA_TECNICA_ACTUAL.md — pendiente de actualizar con 3 deudas nuevas + recuento

docs/orm_sync/orm_decisiones.md — pendiente D-014 + D-015

docs/orm_reconciliacion_plan.md

docs/orm_sync/orm_plan_aplicacion.md

docs/orm_sync/baseline_info.md

Backups
docs/backups/taxip_db_ronda7.dump (559 KB)

docs/backups/taxip_db_2026-09-30.dump

ORM (modelos)
app/models/fleet.py (24 clases)

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

app/models/__init__.py (registra modelos)

Bitácoras (fuera del repo)
E:\Taxip\app chofer\BITACORA_M1.md

E:\Taxip\app chofer\BITACORA_M2.md

E:\Taxip\app chofer\BITACORA_M3.md

7. Reglas operativas (críticas)
NO tocar la DB sin backup previo.

NO correr alembic revision --autogenerate (destructivo en este estado).

NO usar python -m uvicorn. Usar python run.py.

1 commit por paso. N15: verificar pestaña activa antes de pegar bloques grandes. N16: cambios en archivos con varias clases, uno por clase, verificar import.

Snapshots al inicio de cada sub-paso (deuda orm.snapshot_desactualizado).

Comentarios de código: ASCII puro (N10). Comments de columnas (strings al usuario): UTF-8 permitido.

alembic check NO es gate útil por paso.

PowerShell + here-string: usar @"..."@ para evitar problemas con \".

Errores de encoding: VS Code debe guardar UTF-8 (abajo a la derecha).

Si un paste falla: verificar pestaña activa.

Si el import falla: revertir con git checkout -- <archivo>.

Comandos con -c en PowerShell pueden fallar por escaping. Usar script temporal en archivo si es complejo.

Select-String no tiene -Recurse: usar Get-ChildItem -Recurse -Filter *.py | Select-String.

Ciclo por sub-paso
powershell
cd D:\aTaxip\backend
.\venv\Scripts\Activate.ps1

# 1. Aplicar cambios al archivo
# 2. Verificar import
python -c "from app.models.<archivo> import <Clase>; print('Import OK')"

# 3. Regenerar snapshots
python scripts\orm_sync\introspect_orm.py
python scripts\orm_sync\diff.py

# 4. Ver stats
python scripts\orm_sync\apply.py --stats

# 5. Commit
git add app/models/<archivo>.py docs/orm_sync/
git commit -m "..."
8. Plan de Ronda 8 (recomendado)
Prioridad 1 — Documentación pendiente de R7
Actualizar docs/DEUDA_TECNICA_ACTUAL.md:

3 deudas nuevas (orm.comments_db_con_mojibake, orm.comments_orm_sin_db, orm.geography_case_divergente).

Recuento total + encabezado.

Actualizar docs/orm_sync/orm_decisiones.md:

D-014 (cierre Paso 8 parcial).

D-015 (cierre Paso 2 residual).

Limpiar secciones históricas "CERRADAS EN RONDA 4/5/6" → mover a docs/HISTORICO_CERRADAS.md.

Commit del alembic_check_cierre_r7_2026-10-04.txt.

Prioridad 2 — Fix de diff.py (la palanca más grande)
Problemas identificados:

Reporta ~400 *_not_null autogenerados como constraint_falta.

Matchea CHECKs por nombre exacto (falla con naming convention).

Matchea Geography case-sensitive (point vs Point).

Reporta constraint_sobra para FKs que no matchean por nombre.

Impacto esperado: eliminar ~400 falsos positivos. Diff queda en ~450.

Cambios sugeridos:

Normalizar tipos Geography (lowercase).

Matchear CHECKs por definición normalizada, no por nombre.

Excluir *_not_null autogenerados.

Matchear FKs por columnas, no por nombre.

Prioridad 3 — Paso 6 (índices reales)
Filtrar los ~40-50 reales (excluir PKs y UNIQUEs).

Aplicar en ORM.

Prioridad 4 — Paso 9 (limpieza)
3 indice_sobra (eliminar del ORM).

1 tabla_sobra (cosmético).

Prioridad 5 — Fase 4c
Crear app/models/comunicacion.py (3 tablas).

Crear app/models/rentabilidad.py (3 tablas).

Registrar en app/models/__init__.py.

Prioridad 6 — Fase 4d
app/models/foto_viaje.py (1 item).

trip.reserva (Reserva) — decisión funcional pendiente.

Otras tablas sueltas.

9. Mensaje de arranque sugerido para Ronda 8
text
Continuamos Ronda 8. Ronda 7 cerrada (tag ronda7-fase4b-completa en d362823,
origin/main sincronizado). 877 items en el diff.

Estado verificado:
- Python 3.12.10, PostgreSQL 17, PostGIS 3.6, Alembic head m3_010.
- Backend arranca limpio (python run.py OK).
- Imports de modelos OK.

Pendiente R7:
- Docs: 3 deudas nuevas + D-014/D-015 + limpieza histórica +
  commit del alembic_check de cierre.

Prioridad R8:
A) Fix de diff.py (eliminar ~400 falsos positivos de un saque).
B) Paso 6 (índices reales ~40-50).
C) Paso 9 (limpieza, 4 items).
D) Fase 4c (comunicacion.py + rentabilidad.py).

Recomendación: A primero (mayor impacto), después C (rápido),
después B, después D. Documentación de R7 en paralelo o al final.

Reglas: no tocar DB sin backup, no correr alembic autogenerate,
no usar python -m uvicorn. Ciclo: editar → verificar import →
regenerar snapshots → apply.py --stats → commit.
10. Comandos útiles
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
python scripts\orm_sync\introspect_db.py    # solo si la DB cambió
python scripts\orm_sync\introspect_orm.py
python scripts\orm_sync\diff.py
Ver stats del diff
powershell
python scripts\orm_sync\apply.py --stats
Report filtrado
powershell
python scripts\orm_sync\apply.py --report --filter-schema fleet --filter-clasif tipo_desalineado
python scripts\orm_sync\apply.py --report --filter-clasif comment_desalineado
python scripts\orm_sync\filtrar_check.py --stats
python scripts\orm_sync\filtrar_check.py --report --subtipo check
Generar borrador
powershell
python scripts\orm_sync\apply.py --generate app/models/fleet.py
Backup DB
powershell
$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda8.dump"
FIN DEL DOCUMENTO