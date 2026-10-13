CONTEXTO RONDA 11 a 12 — Handoff detallado
Documento de arranque. Pegar como primer mensaje del proximo chat.

1. Proyecto

TaxIP 2.0 — backend FastAPI + SQLAlchemy 2.0 async + PostgreSQL 17 + PostGIS 3.6.

Root backend: D:\aTaxip\backend
Git root: D:/aTaxip
Branch: main
Python: 3.12.10 (venv en .\venv\Scripts\Activate.ps1)
Alembic head: m3_012
Backend: python run.py (NO python -m uvicorn)

2. Estado al cierre de Ronda 11

Fecha de cierre: 2026-10-08
Tag de cierre: ronda11-fase11-completa (a crear)
Commit de cierre funcional: 3cac4d2

Working tree al cierre: solo snapshots regenerados + docs.

Diff total: 71 items (bajo desde 114 al inicio de R11, -38%).

Tags existentes:
  ronda5-baseline-pre, ronda5-fase0-completa, ronda5-fase1-completa, ronda5-completa
  ronda6-fase2-sesion1-completa, ronda6-fase2-sesion2-completa, ronda6-fase3-completa, ronda6-completa
  ronda7-fase4b-paso3-completo, ronda7-fase4b-paso7-completo, ronda7-fase4b-completa
  ronda8-fase6-completa
  ronda9-fase9-completa
  ronda10-fase10-completa
  ronda11-fase11-completa (pendiente de crear)

Commits locales R11 (todos pusheados):

Fix de tooling:

  6918cb1 fix(orm_sync): matchear UNIQUE INDEX (DB) contra UniqueConstraint (ORM)

Paso 6 residual (indices B-tree + UNIQUEs compuestos):

  a8ce682 feat(models): declarar indices faltantes en auth (Paso 6 residual)
  b8478a2 feat(models): declarar idx_cuenta_corriente_empresa en ORM (Paso 6 residual)
  58a47f0 feat(models): declarar uniques compuestos faltantes en fleet
  97a75cc feat(models): declarar uq_config_tarifa_vehiculo en ORM (Paso 6 residual)

Fase 4c (tablas faltantes):

  207033e feat(models): declarar audit.alertas_vencimiento en ORM (Fase 4c)
  ef34688 feat(models): declarar configuracion_pasarela y qr_cobro en ORM (Fase 4c)
  9b9de07 feat(models): declarar historial_chofer_vehiculo y relacion_propietario_vehiculo en ORM (Fase 4c)
  fcb3218 feat(models): declarar codigo_metadatos y codigo_verificacion en ORM (Fase 4c)
  2354a1c feat(models): declarar plantilla_viaje y prestadora_telefonica en ORM (Fase 4c)
  3c28fb9 feat(models): crear comunicacion.py con conversacion, email_enviado, mensaje (Fase 4c)
  5c3db3f feat(models): crear rentabilidad.py con 3 tablas del schema rentabilidad (Fase 4c)
  92fa67e feat(models): declarar trip.broadcast_log en ORM (Fase 4c)

nullable_desalineado:

  b8591fa fix(models): alinear nullable de audit.alerta_desvio.viaje_id con DB
  ca0fc11 fix(models): alinear nullable de CategoriaGasto.updated_at con DB
  28dd808 fix(models): alinear nullable de GastoVehiculo.vehiculo_id con DB
  982b538 fix(models): alinear nullable de GastoVehiculo.vehiculo_id con DB
         (mensaje incorrecto: el cambio real es MantenimientoVehiculo.vehiculo_id)

comments Tipo A (comment -> doc):

  e1a086c fix(models): mover comments a doc en corporate (3 columnas)
  103e57f fix(models): mover comments a doc en fleet (2 columnas)
  3cac4d2 fix(models): mover comments a doc en public (2 columnas)

3. Diff actual (71 items) — desglose completo

Por clasificacion

Clasificacion            Cant.   Naturaleza                                Accion

constraint_falta         49      CHECKs D-027 (~26) + FKs (~10) +          R12 (DB)
                                 UNIQUEs (~10) + other (~3).
comment_desalineado      13      Mojibake (todos).                          R12 (UPDATE DB)
constraint_sobra         6       5 UNIQUEs Caso C + metodo_pago.            Decision / R12
tabla_sobra              1       trip.reserva.                              Decision funcional
columna_falta            1       usuario_rol.control_base_id.               Decision: no tocar
indice_falta             1       Redundante contrato_vehiculo.              Decision (aceptar)

Por Tier

Tier                    Cant.   Estado

Tier 1 (critico)        17      En progreso
Tier 2 (importante)     46      En progreso
Tier 3 (cosmetico)      7       Mayormente ignorable
Tier 4 (muerte)         1       trip.reserva

4. Que se cerro en Ronda 11

Fix de tooling — diff.py (commit 6918cb1)

Problema: diff_indexes no veia los UniqueConstraint del ORM, que viven en
constraints.unique y no en indexes. Generaba falsos positivos de indice_falta
cuando la DB exponia lo mismo como CREATE UNIQUE INDEX (patron *_key
autogenerado, o uq_* explicito).

Fix: nuevo helper _orm_unique_cols() + _is_partial_index(). Matching
UNIQUE INDEX (DB) vs UniqueConstraint (ORM) por columnas, excluyendo partial.

Impacto: 114 -> 102 (-12 items).

Paso 6 residual — indices B-tree (9 items)

B-tree y UNIQUEs que la DB ya tenia y el ORM no declaraba:

  auth.autorizacion_inicio           idx_autorizacion_inicio_token
  auth.refresh_token                 unique_usuario_token (UNIQUE compuesto)
  auth.usuario_rol                   uq_usuario_rol_activo (UNIQUE partial)
  corporate.cuenta_corriente         idx_cuenta_corriente_empresa
  fleet.contrato_qr                  idx_contrato_qr_token
  fleet.contrato_vehiculo            idx_contrato_estado (renombrado desde ix_...)
  fleet.documento_propietario        uq_documento_propietario_tipo (UNIQUE compuesto)
  fleet.modelo                       modelo_marca_id_nombre_key (UNIQUE compuesto)
  fleet.notificacion_vencimiento     uq_notificacion_documento_nivel (UNIQUE compuesto)
  payment.configuracion_tarifa_vehiculo  uq_config_tarifa_vehiculo (UNIQUE compuesto)

Impacto: 102 -> 93 (-9 items).

Fase 4c — tablas faltantes (11 items)

Tablas que la DB ya tenia y el ORM no declaraba:

  audit.alertas_vencimiento
  payment.configuracion_pasarela
  payment.qr_cobro
  fleet.historial_chofer_vehiculo
  fleet.relacion_propietario_vehiculo
  auth.codigo_metadatos
  auth.codigo_verificacion
  auth.plantilla_viaje
  auth.prestadora_telefonica
  trip.broadcast_log

Mas 2 schemas nuevos:

  comunicacion (3 tablas: conversacion, email_enviado, mensaje)
  rentabilidad (3 tablas: analisis_medios_pago, rentabilidad_diaria_vehiculo,
                 rentabilidad_mensual_vehiculo)

Impacto: 93 -> 82 (-11 items; 10 tabla_falta + 2 schema_falta -1 CHECK residual
                     de codigo_verificacion).

nullable_desalineado (4 items)

Las 4 columnas con nullable divergente entre ORM y DB. Todas pasaron de
nullable=True en ORM a nullable=False (la DB ya tenia NOT NULL):

  audit.alerta_desvio.viaje_id
  fleet.categoria_gasto.updated_at
  fleet.gasto_vehiculo.vehiculo_id
  fleet.mantenimiento_vehiculo.vehiculo_id

Impacto: 82 -> 78 (-4 items).

comments Tipo A (7 items)

Los 7 comments que el ORM tenia y la DB no. Se movieron a `doc=`
(documentacion interna de SQLAlchemy, NO persistida en pg_description):

  corporate.factura_corporativa.estado
  corporate.movimiento_cuenta.tipo_movimiento
  corporate.pago_corporativo.estado
  fleet.notificacion_vencimiento.entidad_tipo
  fleet.notificacion_vencimiento.nivel
  public.escaneo_qr.resultado
  public.escaneo_qr.tipo_qr

Impacto: 78 -> 71 (-7 items).

5. Deudas cerradas en R11

  orm.diff_indexes_unique_vs_constraint (nueva, cerrada): 12 items.
  orm.indice_falta (Paso 6 residual): 22 -> 1 (queda redundante
                                            contrato_vehiculo).
  orm.tabla_falta_ampliada: 10 -> 0 (Fase 4c completa).
  orm.schema_falta: 2 -> 0 (comunicacion + rentabilidad creados).
  orm.nullable_desalineado: 4 -> 0 (todos alineados).
  orm.comment_tipo_a: 7 -> 0 (movidos a doc).

6. Deudas pendientes (heredadas + nuevas)

Bloqueante produccion

B5 — ViajeSolicitado desactualizado. Tecnicamente desbloqueado (Fase 4a
completada en R6). Falta verificacion formal.

Critico

orm.db_desalineados — 71 items. En progreso. Todo lo que queda requiere
DB o decision funcional (ver seccion 3).

Alta prioridad

orm.paso4_check_constraints_residual — ~26 CHECKs con naming convention
divergente (patron D-027). Requieren ALTER TABLE RENAME CONSTRAINT en DB.

orm.comment_mojibake — 13 comentarios con encoding roto en DB. Requieren
UPDATE en pg_description.

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
orm.ciclo_fk_usuario_control_base (R11+).

Backend heredadas, Frontend, Endpoints, Proceso, Funcional (sin cambios).

Expo-router / EAS

G77, G78, G79 (workaround activo, no tocar).

7. Plan de Ronda 12 (recomendado)

Prioridad 1 — Migracion m3_013 (5 UNIQUEs Caso C)

Deuda: orm.unique_constraints_caso_c.

Accion: agregar los 5 UNIQUEs a la DB con los nombres que el ORM ya
declara:
  uq_perfil_general_usuario_id
  uq_reset_token_token
  uq_vehiculo_qr_uuid
  uq_configuracion_tenant_control_base_id
  uq_calificacion_viaje_id

Requiere: backup DB previo, verificacion post-migracion con pg_constraint.

Impacto esperado: -10 items (5 constraint_sobra + 5 indice_falta simetricos).

Riesgo: bajo (ya verificado 0 duplicados en R10).

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

Prioridad 3 — Migracion m3_015 (comments mojibake)

Deuda: orm.comment_mojibake.

Accion: UPDATE pg_description para corregir el encoding de 13 comments.

Requiere: backup DB previo.

Impacto esperado: -13 items.

Riesgo: bajo (solo comentarios, no cambia datos).

Prioridad 4 — Decisiones funcionales

- trip.reserva (tabla_sobra): decidir si crear en DB o deprecar el modulo.
- usuario_rol.control_base_id (columna_falta): decidir si agregar en ORM
  o eliminar de DB.
- contrato_vehiculo redundancia: decidir si declarar el indice redundante
  en ORM (cerrar el item) o eliminar el indice de la DB en una migracion.
- metodo_pago (constraint_sobra): limpiar catalogo sucio antes de agregar
  el UNIQUE.

Prioridad 5 — Actualizar deuda y docs

docs/DEUDA_TECNICA_ACTUAL.md (ya actualizado en R11).
docs/CONTEXTO_RONDA_11 a 12.md (nuevo handoff).
docs/orm_sync/orm_decisiones.md (D-030 a D-034 si aplica).

8. Mensaje de arranque sugerido para Ronda 12

Continuamos Ronda 12. Ronda 11 cerrada (tag ronda11-fase11-completa
pendiente, commit 3cac4d2, origin/main sincronizado). 71 items en el
diff.

Estado verificado:
- Python 3.12.10, PostgreSQL 17, PostGIS 3.6, Alembic head m3_012.
- Backend arranca limpio (python run.py OK).
- Imports de modelos OK.
- Los fixes de tooling de R11 estan aplicados (diff.py).
- Fase 4c completa (12 tablas + 2 schemas).

Prioridad R12:
A) Migracion m3_013 (5 UNIQUEs Caso C) (-10 items, requiere backup).
B) Migracion m3_014 (CHECKs D-027) (-26 items, requiere auditoria).
C) Migracion m3_015 (comments mojibake) (-13 items, requiere backup).
D) Decisiones funcionales (trip.reserva, usuario_rol, metodo_pago).

Recomendacion: A primero (bajo riesgo, alto impacto), despues C (bajo riesgo),
despues B (auditoria), D al final si queda tiempo.

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

python scripts\orm_sync\introspect_orm.py    # solo si cambio el ORM
python scripts\orm_sync\diff.py
python scripts\orm_sync\apply.py --stats

Limpiar cache (importante tras editar scripts en scripts/orm_sync/)

Get-ChildItem -Recurse scripts\orm_sync\__pycache__ -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force

Backup DB

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda12.dump"

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
NO usar `<archivo>` / `<Clase>` literal en comandos PowerShell (los
  placeholders se reemplazan por valores reales antes de ejecutar).

SI hacer

1 commit por paso.
Snapshots (introspect_orm.py + diff.py) al inicio de cada sub-paso.
Comentarios de codigo: ASCII puro (N10).
Comments de columnas en ORM: usar `doc=` (NO `comment=`) para documentacion
  interna que no se persiste en DB.
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
docs/orm_sync/alembic_check_cierre_r8_2026-10-05.txt

Documentacion

docs/DEUDA_TECNICA_ACTUAL.md (actualizado post-R11)
docs/HISTORICO_CERRADAS.md (R4-R7)
docs/orm_sync/orm_decisiones.md
docs/orm_sync/orm_decisiones_historico.md
docs/orm_reconciliacion_plan.md
docs/orm_sync/orm_plan_aplicacion.md
docs/orm_sync/baseline_info.md
docs/CONTEXTO_RONDA_11 a 12.md (este documento)

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

Bitacoras (fuera del repo)

E:\Taxip\app chofer\BITACORA_M1.md
E:\Taxip\app chofer\BITACORA_M2.md
E:\Taxip\app chofer\BITACORA_M3.md

12. Archivos criticos con estado especial

app/models/trip.py — Residual del Paso 4

8 CHECKs de trip.viaje_solicitado corregidos en R8. Restaurado
idx_viaje_origen_gist en R10. trip.broadcast_log declarado en R11.
Siguen pendientes:
- constraint_falta residual (~26 CHECKs + FKs + UNIQUEs).
- 1 tabla_sobra: trip.reserva (Fase 4d).

app/models/fleet.py

~26 clases. 60+ indices + varios UNIQUEs. Muchos fixes en R11.
Cuidado con BOM al editar.
Cuidado al buscar "updated_at: Mapped" o "vehiculo_id" — hay multiples
ocurrencias. Usar Ctrl+Shift+O (symbol navigation) para saltar a la clase
correcta, no buscar por texto.

app/models/auth.py

Ampliado en R11 con codigo_metadatos, codigo_verificacion, plantilla_viaje,
prestadora_telefonica.

app/models/comunicacion.py (NUEVO R11)

3 tablas. Schema nuevo. Creado sin errores.

app/models/rentabilidad.py (NUEVO R11)

3 tablas. Schema nuevo. Creado sin errores.

app/database.py — Naming convention

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

Metrica           R5     R6     R7     R8     R9     R10    R11

Total             1280   1205   877    404    332    114    71
Tier 1            247    —      141    72     62     20     17
Tier 2            912    —      625    220    158    79     46
Tier 3            120    —      111    111    111    14     7
Tier 4            1      —      1      1      1      1      1
indice_falta      251    —      180    86     14     22     1
constraint_falta  541    —      427    61     61     48     49
comment_desal.    —      —      20     20     20     20     13
tabla_falta       17     —      10     10     10     10     0
schema_falta      —      —      —      —      —      2      0

Bajada total: -1209 items (-94.5%) desde R5.
-43 items (-37.7%) en R11.

14. Como empezar R12 — Checklist

Verificar entorno:

cd D:\aTaxip\backend
.\venv\Scripts\Activate.ps1
alembic current      # -> m3_012
git log --oneline -1 # -> 3cac4d2 o el commit de cierre
git status           # -> clean

Verificar diff actual:

python scripts\orm_sync\apply.py --stats
# -> Total 71 items

Backup DB preventivo:

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda12.dump"

Empezar con Prioridad 1 (m3_013):

Verificar los 5 UNIQUEs en DB.
Crear migrations/versions/m3_013.py con los 5 ALTER TABLE ADD CONSTRAINT.
Aplicar alembic upgrade head.
Verificar 71 -> 61.
Commit.

Seguir con Prioridad 3 (comments) o Prioridad 2 (CHECKs D-027).

15. Referencias cruzadas

Deuda completa: docs/DEUDA_TECNICA_ACTUAL.md.
Decisiones tomadas: docs/orm_sync/orm_decisiones.md +
docs/orm_sync/orm_decisiones_historico.md.
Hallazgos historicos (H-001 a H-026): docs/orm_sync/orm_decisiones_historico.md.
Plan original: docs/orm_reconciliacion_plan.md.
Handoff R10→R11: docs/CONTEXTO_RONDA_10 a 11.md.
Handoff R11→R12: docs/CONTEXTO_RONDA_11 a 12.md (este documento).

FIN DEL DOCUMENTO