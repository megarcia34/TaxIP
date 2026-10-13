CONTEXTO RONDA 14 a 15 - Handoff detallado
Documento de arranque. Pegar como primer mensaje del proximo chat.

1. Proyecto

TaxIP 2.0 - backend FastAPI + SQLAlchemy 2.0 async + PostgreSQL 17 + PostGIS 3.6.

Root backend: D:\aTaxip\backend
Git root: D:/aTaxip
Branch: main
Python: 3.12.10 (venv en .\venv\Scripts\Activate.ps1)
Alembic head: m3_015
Backend: python run.py (NO python -m uvicorn)

2. Estado al cierre de Ronda 14

Fecha de cierre: 2026-10-11
Tag de cierre: ronda14-fase14-completa (a crear)
Commit de cierre: (pendiente)

Working tree al cierre: solo snapshots regenerados + docs.

DIFF TOTAL: 0 items.

LA ALINEACION BD <-> ORM ESTA COMPLETA.

Tags existentes:
  ronda5-baseline-pre, ronda5-fase0-completa, ronda5-fase1-completa, ronda5-completa
  ronda6-fase2-sesion1-completa, ronda6-fase2-sesion2-completa, ronda6-fase3-completa, ronda6-completa
  ronda7-fase4b-paso3-completo, ronda7-fase4b-paso7-completo, ronda7-fase4b-completa
  ronda8-fase6-completa
  ronda9-fase9-completa
  ronda10-fase10-completa
  ronda11-fase11-completa
  ronda12-fase12-completa
  ronda13-fase13-completa
  ronda14-fase14-completa (pendiente de crear)

Commits de R14 (todos en main):
  17f4d6d feat(models): declarar 5 FKs en corporate.cuenta_corriente y trip.viaje_solicitado
  3db3e7b feat(migrations): m3_015 renombrar 16 CHECKs al naming canonico ck_<tabla>_<col>
  0f4434c feat(models): declarar CHECKs de auth (turno_empleado, codigo_verificacion)
  f7c7413 feat(models): declarar CHECKs de fleet.contrato_vehiculo
  60bd195 feat(models): declarar CHECKs de payment.pago_empresa
  80c030b feat(models): declarar CHECKs de public.escaneo_qr
  ed589a6 feat(models): declarar CHECK de trip.calificacion

3. Diff actual: 0 items

LA ALINEACION BD <-> ORM ESTA COMPLETA.

Metricas finales (post-R14):
- Schemas: 12 (DB) vs 12 (ORM).
- Tablas: 90 (DB) vs 88 (ORM).
  Nota: la diferencia (90 vs 88) es porque la DB tiene 2 tablas de
  sistema (alembic_version, spatial_ref_sys) que el ORM no declara.
- Columnas: 1064 (DB) vs 1058 (ORM).
  Nota: la diferencia son columnas de las 2 tablas de sistema.
- Indices: 287 (DB) vs 173 (ORM).
  Nota: la diferencia son indices internos de Postgres.
- Constraints: 788 (DB) vs 337 (ORM).
  Nota: la diferencia son *_not_null autogenerados (~450).

El diff real (excluyendo system tables y autogenerados) es 0.

4. Que se cerro en Ronda 14

Fase R14.3 - Declarar 5 FKs en ORM (commit 17f4d6d)

5 FKs que la DB tenia y el ORM no declaraba:
- corporate.cuenta_corriente.propietario_id -> auth.usuario.id
- trip.viaje_solicitado.empleado_id -> auth.usuario.id
- trip.viaje_solicitado.movimiento_cc_id -> corporate.movimiento_cuenta.id
- trip.viaje_solicitado.turno_empleado_id -> auth.turno_empleado.id
- trip.viaje_solicitado.cuenta_corriente_id -> corporate.cuenta_corriente.id

Ademas se corrigio turno_empleado_id que apuntaba a auth.usuario.id
en vez de auth.turno_empleado.id.

Impacto: -5 items.

Fase R14.1 - Migracion m3_015 (commit 3db3e7b, aplicada)

16 CHECKs renombrados al naming canonico ck_<tabla>_<col>:

auth.codigo_verificacion:  chk_codigo_verificacion_tipo -> ck_codigo_verificacion_tipo
auth.turno_empleado:        check_estado_turno -> ck_turno_empleado_estado
fleet.contrato_vehiculo (9): ck_contrato_* -> ck_contrato_vehiculo_*
payment.pago_empresa (2):   pago_empresa_*_check -> ck_pago_empresa_*
public.escaneo_qr (2):      chk_escaneo_qr_* -> ck_escaneo_qr_*
trip.calificacion:          calificacion_puntaje_check -> ck_calificacion_puntaje

Impacto: -16 items.

Fase R14.2 - Declarar 16 CHECKs en ORM (commits 0f4434c, f7c7413,
60bd195, 80c030b, ed589a6)

Con la convention de database.py:
  ck_%(table_name)s_%(constraint_name)s

Cada CheckConstraint se declara con name=<sufijo>. La convention
genera el nombre final.

- auth.py:
  - turno_empleado: name="estado" -> ck_turno_empleado_estado
  - codigo_verificacion: name="tipo" -> ck_codigo_verificacion_tipo
- fleet.py (9):
  - contrato_vehiculo: name="compensacion_km", "estado",
    "extension_valida", "dia_inicio_semana", "porcentaje",
    "activo_estado", "horario_valido", "duracion_minima", "auto_gestion"
- payment.py (2):
  - pago_empresa: name="estado", "monto"
- public.py (2):
  - escaneo_qr: name="resultado", "tipo"
- trip.py (1):
  - calificacion: name="puntaje"

Impacto: cierra los 16 items que quedaban.

5. Deudas cerradas en R14

  orm.naming_convention_check_divergente (Grupo 2).
  orm.paso4_check_constraints_residual.

6. Deudas residuales (no-diff, funcionales)

La alineacion BD <-> ORM esta completa. Pero hay deudas funcionales
y de proceso que el diff no captura:

metodo_pago:
  - metodo_pago.catalogo_sucio (12 filas, 2 duplicados, 0 uso real).
  - metodo_pago.fk_catalogo.
  - metodo_pago.frontend_e2.
  - metodo_pago.flujo_propietario / flujo_empresa.
  - metodo_pago.ingreso_turno.
  - flujo_caja.ingreso_turno.

tooling / proceso:
  - orm.snapshot_orm_stale.
  - orm.ids_diff_no_estables.
  - orm.diff_clasifica_mal_columnas_ausentes.
  - orm.diff_falsos_positivos_tipo_cambio.
  - orm.alembic_check_ruidoso.

otras:
  - orm.modulo_duplicado_trip_service (documentar).
  - orm.ciclo_fk_usuario_control_base (documentar).

Alta prioridad (heredadas de R12):
  - G63 - Alerta si el motor de precios cae a fallback.
  - G67 - check_out_turno sin escapatoria si hay viajes huerfanos.
  - G80 - App apunta a Metro.

Media prioridad (heredadas de R12):
  - F5, F6, G68, G70, G72, G74, G76, G81, J15, G82.

Baja prioridad (heredadas de R12):
  - Backend heredadas (A1, A2, A5).
  - Frontend (D2, D6, E2).
  - Endpoints faltantes (F4, F8).
  - Proceso, encoding, metadata (G23, G28, G29, G32, G33, G37, G42,
    G54, G55, G73).
  - Funcional heredada (H1, H2, H3).
  - ORM y funcional futuro (J1-J5, J14, J19).
  - Nuevas Ronda 4 (metodo_pago.config_credito, etc.).

Expo-router / EAS:
  - G77, G78, G79 (workaround activo, no tocar).

Ver docs/DEUDA_TECNICA_ACTUAL.md para el detalle completo.

7. Plan de Ronda 15 (recomendado)

Prioridad 1 - Refactor funcional de metodo_pago

Deuda: metodo_pago.catalogo_sucio.

Accion: limpiar el catalogo de 12 filas:
  - Eliminar 1 de los 2 "efectivo" (elegir cual).
  - Eliminar los 2 "mercadopago" (es pasarela, no metodo).
  - Unificar "billetera" y "wallet" (elegir uno).
  - Unificar "credito"/"tarjeta_credito" y "debito"/"tarjeta_debito".
  - Decidir el vocabulario canonico (efectivo, tarjeta_debito, qr,
    transferencia, + otros).
  - Agregar UNIQUE constraint a nombre.
  - Agregar CHECK constraint con el vocabulario canonico.

Requiere decision funcional.

Prioridad 2 - Verificacion de alembic check

Deuda: orm.alembic_check_ruidoso.

Accion: correr alembic check y ver si ahora reporta 0 operaciones
pendientes (con el diff en 0, deberia ser limpio).

Prioridad 3 - Limpieza de tooling

Deudas: orm.ids_diff_no_estables, orm.snapshot_orm_stale.

Accion:
  - Fijar IDs D-XXXX estables en diff.py (basados en tupla).
  - Verificar que introspect_orm.py regenera orm_snapshot.json siempre
    antes de diff.py.

Prioridad 4 - Documentacion de deudas residuales

Accion: documentar las deudas funcionales en el DEUDA_TECNICA_ACTUAL.md
con planes concretos.

8. Mensaje de arranque sugerido para Ronda 15

Continuamos Ronda 15. Ronda 14 cerrada (tag ronda14-fase14-completa
pendiente, commits en main). Diff BD <-> ORM: 0 items.

Estado verificado:
- Python 3.12.10, PostgreSQL 17, PostGIS 3.6, Alembic head m3_015.
- Backend arranca limpio (python run.py OK).
- Imports de modelos OK.
- Diff en 0.

Prioridad R15:
A) Refactor funcional de metodo_pago (catalogo sucio). Requiere
   decision funcional.
B) Verificacion de alembic check.
C) Limpieza de tooling (diff.py, introspect_orm.py).
D) Documentacion de deudas residuales.

Recomendacion: A primero si hay input del usuario, despues B
(rapido), despues C y D.

Reglas: no tocar DB sin backup, no correr alembic autogenerate,
no usar python -m uvicorn. Ciclo: editar -> verificar import ->
regenerar snapshots -> apply.py --stats -> commit.

9. Comandos utiles

Verificar entorno

cd D:\aTaxip\backend
.\venv\Scripts\Activate.ps1
alembic current
alembic heads
git log --oneline -5
git status

Regenerar snapshots

python -B scripts\orm_sync\introspect_db.py    # solo si cambio la DB
python -B scripts\orm_sync\introspect_orm.py    # solo si cambio el ORM
python -B scripts\orm_sync\diff.py
python -B scripts\orm_sync\apply.py --stats

Limpiar cache (importante tras editar scripts/orm_sync/)

Get-ChildItem -Recurse scripts\orm_sync\__pycache__ -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force

Backup DB

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda15.dump"

Consultar pg_constraint de una tabla

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT conname, contype, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = '<schema>.<tabla>'::regclass ORDER BY conname;"

10. Reglas operativas (CRITICAS)

NO committear snapshots en commits intermedios.

- Commits intermedios: solo archivos de codigo (.py) o migraciones.
- Cierre de ronda: UN unico commit "chore: snapshots de cierre RN" con
  los snapshots regenerados + docs.
- Docs: commits separados, agrupados por tema, solo al cierre de ronda.

NO hacer

NO tocar la DB sin backup previo.
NO correr alembic revision --autogenerate (destructivo).
NO usar python -m uvicorn. Usar python run.py.
NO commitear cambios de tipo masivo sin verificar import.
NO pegar bloques grandes sin verificar pestana activa.
NO restaurar snapshots con git restore (se regeneran con los scripts).
NO cambiar solo el tipo Python (Mapped[Optional[...]] -> Mapped[...])
  cuando el objetivo es cambiar nullable. Cambiar SOLO la palabra
  True/False.
NO reemplazar bloques enteros cuando se busca cambiar una sola palabra.
NO usar <archivo> / <Clase> literal en comandos PowerShell.
NO usar IDs D-XXXX de orm_diff.json como referencia persistente.

SI hacer

1 commit por paso.
Snapshots (introspect_orm.py + diff.py) al inicio de cada sub-paso.
Comentarios de codigo: ASCII puro (N10).
Comments de columnas en ORM: usar doc= (NO comment=) para
  documentacion interna que no se persiste en DB.
PowerShell + here-string: usar @"..."@ o @'...'@ para evitar
  problemas con \".
Errores de encoding: VS Code debe guardar UTF-8 SIN BOM.
  Al usar Set-Content -Encoding UTF8 en PS 5.1, remover el BOM
  con un script Python.
Usar Ctrl+Shift+O (symbol navigation) en VS Code para saltar a clases.

Ciclo por sub-paso

cd D:\aTaxip\backend
.\venv\Scripts\Activate.ps1

# 1. Editar archivo
# 2. Verificar sintaxis
python -c "import ast; ast.parse(open('app/models/<archivo>.py', encoding='utf-8').read()); print('Sintaxis OK')"

# 3. Verificar import
python -c "from app.models.<archivo> import <Clase>; print('Import OK')"

# 4. Verificar app
python -c "from app.main import app; print('App OK')"

# 5. Ver diff
git diff app/models/<archivo>.py

# 6. Commit
git add app/models/<archivo>.py
git commit -m "..."

11. Archivos clave

Scripts
  scripts/orm_sync/introspect_db.py  -> docs/orm_sync/db_snapshot.json
  scripts/orm_sync/introspect_orm.py -> docs/orm_sync/orm_snapshot.json
  scripts/orm_sync/diff.py           -> docs/orm_sync/orm_diff.json + reporte + CSV
  scripts/orm_sync/apply.py          -> stats/report/generate

Snapshots
  docs/orm_sync/db_snapshot.json
  docs/orm_sync/orm_snapshot.json
  docs/orm_sync/orm_diff.json
  docs/orm_sync/orm_diff_reporte.md
  docs/orm_sync/orm_diff_acciones.csv

Documentacion
  docs/DEUDA_TECNICA_ACTUAL.md (actualizado post-R14)
  docs/HISTORICO_CERRADAS.md
  docs/orm_sync/orm_decisiones.md
  docs/orm_sync/orm_decisiones_historico.md
  docs/orm_reconciliacion_plan.md
  docs/orm_sync/baseline_info.md
  docs/CONTEXTO_RONDA_14 a 15.md (este documento)

ORM (modelos)
  app/models/__init__.py
  app/models/fleet.py
  app/models/auth.py
  app/models/trip.py
  app/models/turno.py
  app/models/corporate.py
  app/models/payment.py
  app/models/public.py
  app/models/tenant.py
  app/models/audit.py
  app/models/comunicacion.py
  app/models/rentabilidad.py
  app/database.py (naming convention)

Migraciones
  migrations/versions/m3_010_metodo_pago_canonico.py
  migrations/versions/m3_011.py
  migrations/versions/m3_012.py
  migrations/versions/m3_013.py
  migrations/versions/m3_014_cleanup_usuario_rol_contrato_index.py
  migrations/versions/m3_015_rename_checks_canonico.py

12. Numeros consolidados del diff

Metrica           R5     R6     R7     R8     R9     R10    R11    R12    R13    R14

Total             1280   1205   877    404    332    114    71     27     21     0
Tier 1            247    -      141    72     62     20     17     7      6      0
Tier 2            912    -      625    220    158    79     46     19     15     0
Tier 3            120    -      111    111    111    14     7      0      0      0
Tier 4            1      -      1      1      1      1      1      1      0      0

Bajada total: -1280 items (-100%) desde R5.

LA ALINEACION BD <-> ORM ESTA COMPLETA.

13. Como empezar R15 - Checklist

Verificar entorno:

cd D:\aTaxip\backend
.\venv\Scripts\Activate.ps1
alembic current      # -> m3_015
git log --oneline -1 # -> commit de cierre R14
git status           # -> clean

Verificar diff:

python -B scripts\orm_sync\apply.py --stats
# -> Total 0 items

Backup DB preventivo:

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda15.dump"

Empezar con Prioridad 1 (metodo_pago):

Decidir el vocabulario canonico.
Limpiar el catalogo (12 filas -> N filas).
Agregar UNIQUE + CHECK.
Migracion m3_016.
Verificar diff = 0.

14. Referencias cruzadas

Deuda completa: docs/DEUDA_TECNICA_ACTUAL.md.
Decisiones tomadas: docs/orm_sync/orm_decisiones.md.
Plan original: docs/orm_reconciliacion_plan.md.
Handoff R13->R14: docs/CONTEXTO_RONDA_13 a 14.md (no creado en R13).
Handoff R14->R15: docs/CONTEXTO_RONDA_14 a 15.md (este documento).

FIN DEL DOCUMENTO
