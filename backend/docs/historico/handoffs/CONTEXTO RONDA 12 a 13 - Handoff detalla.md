CONTEXTO RONDA 12 a 13 - Handoff detallado
Documento de arranque. Pegar como primer mensaje del proximo chat.

1. Proyecto

TaxIP 2.0 - backend FastAPI + SQLAlchemy 2.0 async + PostgreSQL 17 + PostGIS 3.6.

Root backend: D:\aTaxip\backend
Git root: D:/aTaxip
Branch: main
Python: 3.12.10 (venv en .\venv\Scripts\Activate.ps1)
Alembic head: m3_013
Backend: python run.py (NO python -m uvicorn)

2. Estado al cierre de Ronda 12

Fecha de cierre: 2026-10-10
Tag de cierre: ronda12-fase12-completa (a crear)
Commit de cierre funcional: 5856d32

Working tree al cierre: solo snapshots regenerados + docs.

Diff total: 27 items (bajo desde 71 al inicio de R12, -62%).

Tags existentes:
  ronda5-baseline-pre, ronda5-fase0-completa, ronda5-fase1-completa, ronda5-completa
  ronda6-fase2-sesion1-completa, ronda6-fase2-sesion2-completa, ronda6-fase3-completa, ronda6-completa
  ronda7-fase4b-paso3-completo, ronda7-fase4b-paso7-completo, ronda7-fase4b-completa
  ronda8-fase6-completa
  ronda9-fase9-completa
  ronda10-fase10-completa
  ronda11-fase11-completa
  ronda12-fase12-completa (pendiente de crear)

Commits locales R12 (todos pusheados):

Migracion:
  b95edd0 feat(migrations): m3_013 agrega 5 UNIQUEs Caso C del ORM a la DB

Fixes de tooling:
  11e5631 fix(orm_sync): matchear UniqueConstraint (DB) contra Index(unique=True) (ORM)

Fixes del ORM (unique):
  7d48ef3 fix(models): agregar unique=True a Index unique_propietario_vehiculo_activo

CHECKs Grupo 1 (doble prefijo, declarados en ORM):
  c3393a9 feat(models): declarar CheckConstraints de corporate (Paso 4 residual)
  7c50431 feat(models): declarar CheckConstraints en fleet (vehiculo, chofer_vehiculo, notificacion_vencimiento)
  81ebf1d feat(models): declarar CheckConstraints en fleet.contrato_vehiculo
  5049322 feat(models): declarar CheckConstraints en fleet (neumaticos)

FK:
  5856d32 feat(models): declarar FK corporate.movimiento_cuenta.created_by

Comments:
  49da7de fix(models): corregir encoding de comments en fleet.ingreso_turno
  419a464 fix(models): alinear comment de trip.viaje_solicitado.solicitado_en
  e81311e fix(models): agregar comment= en payment.configuracion_tarifa
  3fbf298 fix(models): agregar comment= en trip (historial_estado, panico, tipo_vehiculo)

3. Diff actual (27 items) - desglose completo

Por clasificacion

Clasificacion            Cant.   Naturaleza                                Accion

constraint_falta / check 16      CHECKs G2a (sin convention).              m3_014 (R13)
constraint_falta / fk    6       FKs huerfanas (columnas no en ORM).        P4 (R13)
tabla_sobra              1       trip.reserva.                              Decision funcional
columna_falta            1       usuario_rol.control_base_id.               Decision
indice_falta             1       Redundante contrato_vehiculo.              Decision
comment_desalineado      1       snapshot_dia_contractual.                  Decision
constraint_sobra         1       metodo_pago.                               Decision / R13

Por Tier

Tier                    Cant.   Estado

Tier 1 (critico)        7       En progreso
Tier 2 (importante)     19      En progreso
Tier 3 (cosmetico)      0       Cerrado
Tier 4 (muerte)         1       trip.reserva

4. Que se cerro en Ronda 12

Migracion m3_013 (commit b95edd0)

5 UNIQUEs Caso C agregados a DB:
  auth.perfil_general.usuario_id -> uq_perfil_general_usuario_id
  auth.reset_token.token -> uq_reset_token_token
  fleet.vehiculo.qr_uuid -> uq_vehiculo_qr_uuid
  tenant.configuracion_tenant.control_base_id -> uq_configuracion_tenant_control_base_id
  trip.calificacion.viaje_id -> uq_calificacion_viaje_id

Impacto: 71 -> 66 (-5).

Fix de tooling diff.py (commit 11e5631)

Problema: diff_constraints solo matcheaba constraints.unique de DB
contra constraints.unique de ORM. Los UNIQUEs declarados como
Index(unique=True) en ORM (patron D-017) aparecian como
constraint_falta falsos (8 items).

Fix: extender el matching con un set `orm_idx_uq_cols` que captura las
columnas de Index(unique=True) del ORM (excluyendo partial). Si un
UNIQUE de DB matchea por columnas, no se reporta.

Impacto: 36 -> 29 (-7).

Fix del ORM: unique=True faltante (commit 7d48ef3)

fleet.propietario_vehiculo.unique_propietario_vehiculo_activo tenia el
nombre "unique_" pero faltaba unique=True. El diff lo reportaba como
constraint_falta / unique. Se agrego el flag.

Impacto: 29 -> 28 (-1).

CHECKs Grupo 1 (commits c3393a9, 7c50431, 81ebf1d, 5049322)

18 CHECKs con doble prefijo en DB declarados en ORM:
- corporate.py (2): ck_cuenta_corriente_ck_cc_estado,
  ck_movimiento_cuenta_ck_mc_estado.
- fleet.py (16): vehiculo (2), chofer_vehiculo (1), contrato_vehiculo (2),
  neumatico_vehiculo (2), neumatico_historial_posicion (1),
  neumatico_medicion (1), neumatico_operacion (1), neumatico_sugerencia (3),
  neumatico_imagen (1), notificacion_vencimiento (2).

Impacto: 52 -> 36 (-16).

Comments residuales (commits 49da7de, 419a464, e81311e, 3fbf298)

- Mojibake en fleet.ingreso_turno: declarado_por, transaccion_id.
- Tilde en trip.viaje_solicitado.solicitado_en.
- comment= agregado en 9 columnas (payment.configuracion_tarifa x2,
  trip x7).

Impacto: 66 -> 54 (-12 en dos pasos: -2 -1 -9).

FK declarada (commit 5856d32)

corporate.movimiento_cuenta.created_by -> auth.usuario.id.

Impacto: 28 -> 27 (-1).

5. Deudas cerradas en R12

  orm.unique_constraints_caso_c (parcial: 5 de 6 cerrados; metodo_pago
                                  queda).
  orm.unique_constraint_vs_unique_index (parcial: el caso
                                          Index(unique=True) esta
                                          cerrado).
  orm.naming_convention_check_divergente (parcial: Grupo 1 cerrado,
                                           Grupo 2 va a m3_014).
  orm.comment_mojibake (parcial: 12 de 13 cerrados; queda
                        snapshot_dia_contractual).
  orm.paso4_check_constraints_residual (parcial).
  orm.indices_duplicados (parcial).

6. Deudas pendientes (heredadas + nuevas)

Bloqueante produccion

B5 - ViajeSolicitado desactualizado. Tecnicamente desbloqueado.
Falta verificacion formal.

Critico

orm.db_desalineados - 27 items. En progreso. Todo lo que queda
requiere DB o decision funcional.

Alta prioridad

orm.paso4_check_constraints_residual - 16 CHECKs G2a con naming
divergente. Requieren m3_014 (RENAME CONSTRAINT).

orm.columnas_snapshot_turno_faltantes (NUEVA R12) - 6 columnas
snapshot_* de fleet.turno_chofer existen en DB y no en ORM.

orm.diff_clasifica_mal_columnas_ausentes (NUEVA R12) - el diff
clasifica como comment_desalineado una columna que en realidad no
existe en ORM.

orm.ids_diff_no_estables (NUEVA R12) - IDs D-XXXX se regeneran en
cada corrida.

orm.snapshot_orm_stale (NUEVA R12) - regenerar siempre antes de
comparar.

G63 - Alerta si el motor de precios cae a fallback.
G67 - check_out_turno sin escapatoria si hay viajes huerfanos.
G80 - App apunta a Metro.

Media prioridad

metodo_pago.catalogo_sucio, metodo_pago.fk_catalogo, etc.
flujo_caja.ingreso_turno.
F5, F6, G68, G70, G72, G74, G76, G81, J15, G82 (heredadas).

Baja prioridad

orm.reserva_modulo_activo (Fase 4d).
orm.foto_viaje_out_of_scope (Fase 4d).
datos.turno_chofer_km_final_outlier (Tier 3).
orm.indices_duplicados.
orm.constraint_nombres_numericos.
orm.ciclo_fk_usuario_control_base (R11+).

Expo-router / EAS

G77, G78, G79 (workaround activo, no tocar).

7. Plan de Ronda 13 (recomendado)

Prioridad 1 - Migracion m3_014 (CHECKs G2a, ~16 items)

Deuda: orm.naming_convention_check_divergente (Grupo 2) +
orm.paso4_check_constraints_residual.

Accion: renombrar los CHECKs en DB a nombres canonicos
`ck_<tabla>_<col>` via ALTER TABLE ... RENAME CONSTRAINT. Despues
declarar los CheckConstraint en ORM con el `name=` correcto.

CHECKs G2a (~16):
  auth.codigo_verificacion.chk_codigo_verificacion_tipo
  auth.turno_empleado.check_estado_turno
  fleet.contrato_vehiculo.check_auto_gestion
  fleet.contrato_vehiculo.check_porcentaje
  fleet.contrato_vehiculo.ck_contrato_compensacion_km
  fleet.contrato_vehiculo.ck_contrato_duracion_minima
  fleet.contrato_vehiculo.ck_contrato_activo_estado
  fleet.contrato_vehiculo.ck_contrato_extension_valida
  fleet.contrato_vehiculo.ck_contrato_dia_inicio_semana
  fleet.contrato_vehiculo.ck_contrato_horario_valido
  fleet.contrato_vehiculo.ck_contrato_estado
  payment.pago_empresa.pago_empresa_estado_check
  payment.pago_empresa.pago_empresa_monto_check
  public.escaneo_qr.chk_escaneo_qr_resultado
  public.escaneo_qr.chk_escaneo_qr_tipo
  trip.calificacion.calificacion_puntaje_check

Requiere: backup DB previo.

Impacto esperado: -16 items.

Riesgo: medio (auditoria individual por CHECK).

Prioridad 2 - Decisiones funcionales (P4)

- trip.reserva (tabla_sobra): decidir crear en DB o deprecar el
  modulo. Endpoints /api/reservas estan rotos actualmente.
- usuario_rol.control_base_id (columna_falta): decidir agregar en ORM
  o eliminar de DB. La FK existe en DB.
- contrato_vehiculo redundancia: decidir declarar el indice en ORM
  (cerrar item) o eliminar el indice de la DB.
- metodo_pago (constraint_sobra): limpiar catalogo sucio (2 duplicados
  efectivo, mercadopago) antes de agregar UNIQUE.
- snapshot_dia_contractual + 5 columnas snapshot_* de
  fleet.turno_chofer: decidir declarar en ORM (columna + comment) o
  deprecar.

Prioridad 3 - FKs huerfanas (~6 items)

Las FKs de trip.viaje_solicitado (turno_empleado_id, empleado_id,
movimiento_cc_id, cuenta_corriente_id) y auth.usuario_rol
(control_base_id) apuntan a columnas que NO existen en ORM. Requieren
declarar las columnas primero. Depende de P2.

Impacto esperado: -6 items.

Prioridad 4 - Cierre de R12 residual

Una vez cerradas las 3 prioridades anteriores, el diff deberia quedar
en ~5 items (solo decisiones funcionales no resueltas).

8. Mensaje de arranque sugerido para Ronda 13

Continuamos Ronda 13. Ronda 12 cerrada (tag ronda12-fase12-completa
pendiente, commit 5856d32, origin/main sincronizado). 27 items en el
diff.

Estado verificado:
- Python 3.12.10, PostgreSQL 17, PostGIS 3.6, Alembic head m3_013.
- Backend arranca limpio (python run.py OK).
- Imports de modelos OK.
- Fixes de tooling de R12 aplicados (diff.py).
- CHECKs Grupo 1 declarados en ORM (18).

Prioridad R13:
A) Migracion m3_014 (CHECKs G2a, ~16 items). Requiere backup +
   auditoria.
B) Decisiones funcionales (P4, ~6 items).
C) FKs huerfanas (~6 items, depende de B).

Recomendacion: A primero (requiere backup, alto impacto), despues B
si hay input del usuario, despues C.

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
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda13.dump"

Consultar pg_constraint de una tabla

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT conname, contype, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = '<schema>.<tabla>'::regclass ORDER BY conname;"

Consultar pg_indexes de una tabla

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT indexname, indexdef FROM pg_indexes WHERE schemaname='<schema>' AND tablename='<tabla>' ORDER BY indexname;"

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
NO cambiar solo el tipo Python (Mapped[Optional[...]] -> Mapped[...]) cuando
  el objetivo es cambiar nullable. Cambiar SOLO la palabra True/False.
NO reemplazar bloques enteros cuando se busca cambiar una sola palabra
  (los reemplazos de bloque arrastran indentacion y contenido).
NO usar <archivo> / <Clase> literal en comandos PowerShell (los
  placeholders se reemplazan por valores reales antes de ejecutar).
NO usar IDs D-XXXX de orm_diff.json como referencia persistente
  (se regeneran en cada corrida, D-035).

SI hacer

1 commit por paso.
Snapshots (introspect_orm.py + diff.py) al inicio de cada sub-paso.
Comentarios de codigo: ASCII puro (N10).
Comments de columnas en ORM: usar `doc=` (NO `comment=`) para
  documentacion interna que no se persiste en DB.
PowerShell + here-string: usar @"..."@ para evitar problemas con \".
Errores de encoding: VS Code debe guardar UTF-8 SIN BOM.
Usar Ctrl+Shift+O (symbol navigation) en VS Code para saltar a clases,
  NO Ctrl+F por texto (hay columnas con nombres repetidos).

Ciclo por sub-paso

cd D:\aTaxip\backend
.\venv\Scripts\Activate.ps1

# 1. Editar archivo
# 2. Verificar sintaxis
python -c "import ast; ast.parse(open('app/models/<archivo>.py', encoding='utf-8').read()); print('Sintaxis OK')"

# 3. Verificar import
python -c "from app.models.<archivo> import <Clase>; print('Import OK')"

# 4. Verificar diff de un cambio especifico (debe ser 1 linea)
git diff app/models/<archivo>.py

# 5. Regenerar snapshots
Get-ChildItem -Recurse scripts\orm_sync\__pycache__ -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force
python -B scripts\orm_sync\introspect_orm.py
python -B scripts\orm_sync\diff.py

# 6. Ver stats
python -B scripts\orm_sync\apply.py --stats

# 7. Commit
git add app\models\<archivo>.py
git commit -m "..."

Regla del BOM

VS Code puede agregar un BOM (EF BB BF) al inicio del archivo. Esto rompe
import ast y todos los scripts de orm_sync. Si pasa:

python -c "content = open('app/models/<archivo>.py', encoding='utf-8-sig').read(); open('app/models/<archivo>.py', 'w', encoding='utf-8').write(content); print('BOM removed')"

Regla de trailing whitespace

git diff puede detectar trailing whitespace como lineas modificadas
(invisible). Si pasa, limpiar las lineas con:

python -c "
content = open('app/models/<archivo>.py', encoding='utf-8').read()
lines = content.split('\n')
for i in range(len(lines)):
    if lines[i].endswith(' ') or lines[i].endswith('\t'):
        lines[i] = lines[i].rstrip()
open('app/models/<archivo>.py', 'w', encoding='utf-8').write('\n'.join(lines))
"

11. Archivos clave

Scripts

scripts/orm_sync/introspect_db.py  -> docs/orm_sync/db_snapshot.json
scripts/orm_sync/introspect_orm.py -> docs/orm_sync/orm_snapshot.json
scripts/orm_sync/diff.py           -> docs/orm_sync/orm_diff.json + reporte + CSV
scripts/orm_sync/apply.py          -> stats/report/generate
scripts/orm_sync/filtrar_check.py  -> lista constraint_falta

Snapshots

docs/orm_sync/db_snapshot.json
docs/orm_sync/orm_snapshot.json
docs/orm_sync/orm_diff.json
docs/orm_sync/orm_diff_reporte.md
docs/orm_sync/orm_diff_acciones.csv

Documentacion

docs/DEUDA_TECNICA_ACTUAL.md (actualizado post-R12)
docs/HISTORICO_CERRADAS.md (R4-R7)
docs/orm_sync/orm_decisiones.md
docs/orm_sync/orm_decisiones_historico.md
docs/orm_reconciliacion_plan.md
docs/orm_sync/orm_plan_aplicacion.md
docs/orm_sync/baseline_info.md
docs/CONTEXTO_RONDA_12 a 13.md (este documento)

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
app/models/comunicacion.py   (nuevo R11)
app/models/rentabilidad.py   (nuevo R11)
app/database.py (naming convention de constraints)

Migraciones

migrations/versions/m3_010_metodo_pago_canonico.py
migrations/versions/m3_011.py
migrations/versions/m3_012.py
migrations/versions/m3_013.py

Bitacoras (fuera del repo)

E:\Taxip\app chofer\BITACORA_M1.md
E:\Taxip\app chofer\BITACORA_M2.md
E:\Taxip\app chofer\BITACORA_M3.md

12. Archivos criticos con estado especial

app/models/trip.py - Residual del Paso 4

8 CHECKs de trip.viaje_solicitado corregidos en R8. Restaurado
idx_viaje_origen_gist en R10. trip.broadcast_log declarado en R11.
Comments agregados en R12 (solicitado_en, historial_estado, panico,
tipo_vehiculo).

Siguen pendientes:
- 4 FKs huerfanas (turno_empleado_id, empleado_id, movimiento_cc_id,
  cuenta_corriente_id).
- 1 tabla_sobra: trip.reserva (Fase 4d).

app/models/fleet.py

~26 clases. 60+ indices + varios UNIQUEs + 16 CHECKs nuevos.
Muchos fixes en R11-R12. Cuidado con BOM y trailing whitespace al
editar. Cuidado al buscar "updated_at" o "vehiculo_id": hay multiples
ocurrencias. Usar Ctrl+Shift+O (symbol navigation).

app/models/auth.py

Ampliado en R11 con codigo_metadatos, codigo_verificacion,
plantilla_viaje, prestadora_telefonica.

Tiene 1 CHECK pendiente (chk_codigo_verificacion_tipo) que va a
m3_014.

app/models/comunicacion.py (NUEVO R11)

3 tablas. Schema nuevo.

app/models/rentabilidad.py (NUEVO R11)

3 tablas. Schema nuevo.

app/database.py - Naming convention

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

CUIDADO: la convention agrega prefijos automaticamente. Si declaras
name="ck_X" en un CheckConstraint, el nombre final es ck_<tabla>_ck_X.
No duplicar prefijos. Si la DB tiene un nombre como chk_<tabla>_<algo>
(sin prefijo ck_), declarar name="<algo>" para que la convention lo
expanda al nombre exacto.

13. Numeros consolidados del diff

Metrica           R5     R6     R7     R8     R9     R10    R11    R12

Total             1280   1205   877    404    332    114    71     27
Tier 1            247    -      141    72     62     20     17     7
Tier 2            912    -      625    220    158    79     46     19
Tier 3            120    -      111    111    111    14     7      0
Tier 4            1      -      1      1      1      1      1      1
indice_falta      251    -      180    86     14     22     1      1
constraint_falta  541    -      427    61     61     48     49     22
comment_desal.    -      -      20     20     20     20     13     1
tabla_falta       17     -      10     10     10     10     0      0
schema_falta      -      -      -      -      -      2      0      0

Bajada total: -1253 items (-97.9%) desde R5.
-44 items (-62%) en R12.

14. Como empezar R13 - Checklist

Verificar entorno:

cd D:\aTaxip\backend
.\venv\Scripts\Activate.ps1
alembic current      # -> m3_013
git log --oneline -1 # -> 5856d32 o el commit de cierre
git status           # -> clean

Verificar diff actual:

python scripts\orm_sync\apply.py --stats
# -> Total 27 items

Backup DB preventivo:

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda13.dump"

Empezar con Prioridad 1 (m3_014):

Auditar los 16 CHECKs G2a con psql.
Decidir naming canonico (ck_<tabla>_<col>).
Crear migrations/versions/m3_014.py con los 16 ALTER TABLE RENAME
CONSTRAINT.
Aplicar alembic upgrade head.
Verificar 27 -> 11.
Declarar los CheckConstraint en ORM con name= correcto.
Verificar 11 -> 11 (o menos si el ORM ya no reporta).
Commit.

Seguir con Prioridad 2 (P4) si hay input del usuario.

15. Referencias cruzadas

Deuda completa: docs/DEUDA_TECNICA_ACTUAL.md.
Decisiones tomadas: docs/orm_sync/orm_decisiones.md +
docs/orm_sync/orm_decisiones_historico.md.
Hallazgos historicos (H-001 a H-026): docs/orm_sync/orm_decisiones_historico.md.
Plan original: docs/orm_reconciliacion_plan.md.
Handoff R11->R12: docs/CONTEXTO_RONDA_11 a 12.md.
Handoff R12->R13: docs/CONTEXTO_RONDA_12 a 13.md (este documento).

FIN DEL DOCUMENTO