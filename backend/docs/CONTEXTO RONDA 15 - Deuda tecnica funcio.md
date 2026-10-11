CONTEXTO RONDA 15 - Deuda tecnica funcional
Documento de arranque para metodo_pago y deudas residuales.
Pegar como primer mensaje del proximo chat.

1. Proyecto

TaxIP 2.0 - backend FastAPI + SQLAlchemy 2.0 async + PostgreSQL 17 + PostGIS 3.6.

Root backend: D:\aTaxip\backend
Git root: D:/aTaxip
Branch: main
Python: 3.12.10 (venv en .\venv\Scripts\Activate.ps1)
Alembic head: m3_015
Backend: python run.py (NO python -m uvicorn)

2. Estado al arrancar Ronda 15

Fecha de arranque: 2026-10-11
Ronda anterior: R14 cerrada (tag ronda14-fase14-completa)
Commit de cierre R14: ba4bc19

DIFF BD <-> ORM: 0 items.

LA ALINEACION ESTRUCTURAL BD <-> ORM ESTA COMPLETA.

Working tree: limpio (post-cierre R14).
Backup DB: docs/backups/taxip_db_ronda14.dump

3. Objetivo de Ronda 15

Resolver deuda tecnica FUNCIONAL (no estructural).
La alineacion estructural BD <-> ORM esta completa; ahora hay que
resolver las deudas funcionales y de proceso que el diff no captura.

Orden propuesto:
  P1: metodo_pago (catalogo sucio) - requiere decision funcional.
  P2: Verificacion de alembic check (ver seccion 8).
  P3: Limpieza de tooling (diff.py, introspect_orm.py).
  P4: Documentacion de deudas residuales.

4. Deuda tecnica: metodo_pago.catalogo_sucio

Contexto

La tabla payment.metodo_pago actua como catalogo de metodos de pago.
Tiene 12 filas. El ORM la declara (clase MetodoPago en app/models/payment.py)
pero no tiene UNIQUE sobre nombre desde R13 (se quito unique=True).

Estado actual de las 12 filas (capturado en R13):

  id (primeros 8) | nombre
  ----------------+------------------
  07ea1d08        | billetera
  e089ac07        | credito
  d4e6243c        | debito
  cb41ddfa        | efectivo      <- duplicado literal
  fe092c54        | efectivo      <- duplicado literal
  3d0ed074        | mercadopago   <- duplicado literal + pasarela
  73c5600b        | mercadopago   <- duplicado literal + pasarela
  c70b8365        | qr
  485fde34        | tarjeta_credito
  4827a710        | tarjeta_debito
  5924dc90        | transferencia
  44b8881e        | wallet

Problemas identificados

1. 2 pares de duplicados literales: efectivo x2, mercadopago x2.
2. 1 par de sinonimos: billetera / wallet.
3. 2 duplicados semanticos: credito / tarjeta_credito, debito / tarjeta_debito.
4. 1 valor que es pasarela, no metodo: mercadopago.
5. La tabla no tiene UNIQUE constraint sobre nombre.
6. La tabla no tiene CHECK constraint sobre nombre.

Uso actual

- 0 transacciones referencian la tabla (transaccion.metodo_pago_id esta vacio).
- 1 FK activa: payment.transaccion.metodo_pago_id -> payment.metodo_pago.id.
- El codigo NO usa el catalogo para logica de negocio. Usa strings
  directamente en:
  - trip.viaje_solicitado.metodo_pago (CHECK: efectivo, tarjeta_debito,
    qr, transferencia).
  - fleet.ingreso_turno.medio_pago (comment: efectivo, debito, credito,
    qr, transferencia, billetera).
  - tenant.configuracion_tenant (mixes: mix_efectivo, mix_transferencia,
    mix_qr, mix_debito, mix_credito).

Vocabulario canonico actual (segun CHECK de viaje_solicitado)

efectivo | tarjeta_debito | qr | transferencia

Ese es el vocabulario que el codigo respeta hoy en el flujo de viajes.

Investigacion pendiente (a hacer al arrancar R15)

Antes de decidir, ejecutar estos comandos:

1. Ver todas las filas actuales:
   $env:PGPASSWORD = "postgres123"
   & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT id, nombre FROM payment.metodo_pago ORDER BY nombre, id;"

2. Ver uso real (transacciones):
   $env:PGPASSWORD = "postgres123"
   & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT COUNT(*) FROM payment.transaccion WHERE metodo_pago_id IS NOT NULL;"

3. Ver CHECK de viaje_solicitado:
   $env:PGPASSWORD = "postgres123"
   & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname = 'ck_viaje_solicitado_metodo_pago';"

4. Ver CHECKs que usan metodo_pago como string:
   git grep -n "metodo_pago" -- "app/models/*.py" | Select-String "CheckConstraint"

5. Ver todos los usos de strings relacionados:
   git grep -n "efectivo\|tarjeta_debito\|mercadopago\|billetera" -- "app/*.py"

6. Ver si el frontend muestra los valores del catalogo:
   Buscar en el proyecto frontend (si esta en el repo).
   Buscar en docs/api si hay contrato con el catalogo.

7. Ver endpoints que usan metodo_pago:
   git grep -n "metodo_pago" -- "app/routers/*.py"

8. Ver schemas que exponen metodo_pago:
   git grep -n "metodo_pago" -- "app/schemas/*.py"

Decision funcional pendiente

Una vez completada la investigacion, decidir:

A. Vocabulario canonico.

Opcion 1 (minimalista, 4 valores):
  efectivo, tarjeta_debito, qr, transferencia
  (alineado con el CHECK de viaje_solicitado)

Opcion 2 (extendida, 6 valores):
  efectivo, tarjeta_debito, tarjeta_credito, qr, transferencia, billetera
  (agrega tarjeta_credito y billetera, deprecando credito/debito/wallet)

Opcion 3 (completa, 8 valores):
  efectivo, tarjeta_debito, tarjeta_credito, qr, transferencia,
  billetera, mercadopago, otro
  (mantiene mercadopago como metodo propio)

B. Filas a eliminar del catalogo.

- efectivo x2 -> conservar 1 (elegir id).
- mercadopago x2 -> eliminar ambos (es pasarela, no metodo) o
  conservar 1 si se decide incluirlo como metodo.
- billetera / wallet -> elegir uno.
- credito / tarjeta_credito -> elegir uno.
- debito / tarjeta_debito -> elegir uno.

C. Constraint a agregar.

- UNIQUE sobre nombre (o UNIQUE parcial).
- CHECK con el vocabulario canonico (o dejar sin CHECK).

D. Relacion con trip.viaje_solicitado.metodo_pago.

Hoy usa strings (CHECK: efectivo, tarjeta_debito, qr, transferencia).
Decidir si:
  - Se mantiene como esta (strings).
  - Se refactoriza a FK por metodo_pago_id.

E. Relacion con fleet.ingreso_turno.medio_pago.

Hoy tiene comment pero no CHECK. Decidir si:
  - Se agrega CHECK.
  - Se alinea con el vocabulario canonico.

Plan de migracion (a ejecutar despues de decidir)

Migracion m3_016:
  1. Eliminar filas duplicadas del catalogo (con backup previo).
  2. Agregar UNIQUE constraint a nombre.
  3. Agregar CHECK constraint con el vocabulario canonico.
  4. Actualizar comment de la tabla si aplica.

Verificar post-migracion:
  $env:PGPASSWORD = "postgres123"
  & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT id, nombre FROM payment.metodo_pago ORDER BY nombre;"

  # Verificar diff = 0
  python -B scripts\orm_sync\apply.py --stats

Commit:
  feat(migrations): m3_016 limpiar catalogo metodo_pago + UNIQUE + CHECK

5. Deudas residuales adicionales (post-R14)

Ademas de metodo_pago, hay deudas residuales que el diff no captura:

A. Deudas funcionales

  metodo_pago.fk_catalogo
    Refactor estructural: evaluar FK por metodo_pago_id en
    trip.viaje_solicitado y fleet.ingreso_turno (en vez de string).

  metodo_pago.frontend_e2
    MetodoPago del frontend limitado a 4 valores.

  metodo_pago.flujo_propietario / flujo_empresa
    Vocabulario propio por definir.
    Referencias: liquidacion.py:329, fleet.py:875/880, empresa_dashboard.py:790.

  metodo_pago.ingreso_turno
    Comment de fleet.ingreso_turno.medio_pago divergente con DB.

  flujo_caja.ingreso_turno
    Comments de tipo_ingreso, medio_pago, origen mezclan vocabularios.

B. Deudas de tooling

  orm.ids_diff_no_estables
    Los IDs D-XXXX de orm_diff.json se regeneran en cada corrida.
    Usar (schema, tabla, columna, clasificacion, tipo_constraint, nombre).

  orm.snapshot_orm_stale
    El orm_snapshot.json puede quedar desactualizado.
    Regenerar siempre antes de comparar.

  orm.diff_clasifica_mal_columnas_ausentes
    El diff clasifica como comment_desalineado una columna que en
    realidad no existe en ORM.

  orm.diff_falsos_positivos_tipo_cambio
    Cuando se cambia tipo o nullable, el diff puede reportarlo como
    columna_falta.

C. Deudas de proceso

  orm.alembic_check_ruidoso
    Ver seccion 8 (hallazgos de R14).

  orm.modulo_duplicado_trip_service (documentar)
    app/models/trip_service.py era duplicado de app/services/trip_service.py.
    Eliminado en R13. Documentar para evitar reaparicion.

  orm.ciclo_fk_usuario_control_base (documentar)
    Ciclo de FKs auth.usuario <-> tenant.control_base. Requiere
    use_alter=True o deferrable. Postergado.

D. Deudas heredadas (no relacionadas con la alineacion)

Alta prioridad:
  - G63 - Alerta si el motor de precios cae a fallback.
  - G67 - check_out_turno sin escapatoria si hay viajes huerfanos.
  - G80 - App apunta a Metro.

Media prioridad:
  - F5, F6, G68, G70, G72, G74, G76, G81, J15, G82.

Baja prioridad (~21 items):
  - Backend heredadas (A1, A2, A5).
  - Frontend (D2, D6, E2).
  - Endpoints faltantes (F4, F8).
  - Proceso, encoding, metadata (G23, G28, G29, G32, G33, G37, G42,
    G54, G55, G73).
  - Funcional heredada (H1, H2, H3).
  - ORM y funcional futuro (J1-J5, J14, J19).

Expo-router / EAS:
  - G77, G78, G79 (workaround activo, no tocar).

Ver docs/DEUDA_TECNICA_ACTUAL.md para detalle completo.

6. Hallazgos del alembic check (2026-10-11)

Al arrancar R15, se corrio alembic check y revelo 3 categorias de
deuda que el diff NO captura.

Categoria A - Naming divergente (~15 items, falsos positivos)

Alembic compara por nombre + tipo (constraint vs index). El diff
compara por columnas. Alembic reporta "remove + add" para:

  comercio.codigo_qr       : comercio_codigo_qr_key vs uq_comercio_codigo_qr
  usuario.email            : usuario_email_key vs uq_usuario_email
  vehiculo.patente         : vehiculo_patente_key vs uq_vehiculo_patente
  marca.nombre             : marca_nombre_key vs uq_marca_nombre
  tipo_usuario.nombre      : tipo_usuario_nombre_key vs uq_tipo_usuario_nombre
  factura.numero_factura   : factura_numero_factura_key vs uq_factura_numero_factura
  billetera.usuario_id     : unique_usuario_billetera vs uq_billetera_usuario_id
  refresh_token            : constraint vs index
  documento_propietario    : constraint vs index
  neumatico_vehiculo       : constraint vs index
  configuracion_tarifa_vehiculo : constraint vs index
  notificacion_vencimiento : constraint vs index
  propietario_vehiculo     : constraint vs index
  documentos_chofer        : constraint vs index
  modelo                   : constraint vs index

Estos son falsos positivos del alembic check. El diff.py (que compara
por columnas) los considera equivalentes. El diff.py es la fuente
de verdad.

Accion: documentar. NO tocar. Opcional: si en algun momento se quiere
que alembic check sea limpio, se puede alinear el naming.

Categoria B - FKs con ondelete distinto (~30 items)

El ORM declara ondelete en el ForeignKey(...). La DB no tiene ese
ondelete aplicado (o tiene otro). Alembic detecta la diferencia.

Tablas afectadas (parcial):
  log_acciones, log_gps, autorizacion_inicio, perfil_general,
  usuario, usuario_rol, chofer_vehiculo, gasto_turno, gasto_vehiculo,
  mantenimiento_vehiculo, neumatico_*, turno_chofer, vehiculo,
  ciudad, provincia, configuracion_tarifa, transaccion,
  configuracion_tenant, control_base, calificacion,
  historial_estado_viaje, objeto_olvidado, panico, viaje_solicitado.

Accion pendiente: decidir por cada FK si:
  (a) aplicar ondelete en DB, o
  (b) quitar ondelete del ORM, o
  (c) dejar como deuda aceptada.

Categoria C - Indice faltante en ORM (1 item)

Alembic detecta que ix_qr_cobro_token existe en DB pero no en ORM.
El diff no lo detecto.

Accion pendiente: declarar en ORM o eliminar de DB.

Categoria D - Comentarios de tabla (5 items)

La DB tiene COMMENT ON TABLE para 5 tablas, el ORM no declara
comment= en __table_args__:
  auth.autorizacion_inicio
  auth.turno_empleado
  auth.usuario_rol
  fleet.contrato_qr
  fleet.documentos_chofer

Accion pendiente: declarar en ORM o eliminar de DB.

Comando para ver los hallazgos:
  alembic check 2>&1 | Out-File -FilePath docs\orm_sync\alembic_check_cierre_r14_2026-10-11.txt -Encoding UTF8

7. Orden de trabajo recomendado para R15

1. Investigar metodo_pago (comandos de la seccion 4).
2. Decision funcional (vocabulario + filas + constraints).
3. Migracion m3_016 (limpieza + UNIQUE + CHECK).
4. Verificar diff = 0.
5. Documentar hallazgos del alembic check.
6. Decidir prioridad: ondelete FKs vs tooling vs deudas funcionales.

8. Reglas operativas (CRITICAS)

NO committear snapshots en commits intermedios.
  - Commits intermedios: solo archivos de codigo (.py) o migraciones.
  - Cierre de ronda: UN unico commit "chore: snapshots de cierre RN".
  - Docs: commits separados, solo al cierre de ronda.

NO hacer:
  NO tocar la DB sin backup previo.
  NO correr alembic revision --autogenerate (destructivo).
  NO usar python -m uvicorn. Usar python run.py.
  NO commitear cambios de tipo masivo sin verificar import.
  NO pegar bloques grandes sin verificar pestana activa.
  NO restaurar snapshots con git restore (se regeneran con los scripts).
  NO cambiar solo el tipo Python cuando el objetivo es cambiar nullable.
  NO usar <archivo> / <Clase> literal en comandos PowerShell.
  NO usar IDs D-XXXX de orm_diff.json como referencia persistente.

SI hacer:
  1 commit por paso.
  Snapshots al inicio de cada sub-paso.
  Comentarios de codigo: ASCII puro (N10).
  Comments de columnas en ORM: usar doc= (NO comment=) para
    documentacion interna que no se persiste en DB.
  PowerShell + here-string: usar @"..."@ o @'...'@.
  Errores de encoding: VS Code debe guardar UTF-8 SIN BOM.
    Al usar Set-Content -Encoding UTF8 en PS 5.1, remover el BOM
    con un script Python.
  Usar Ctrl+Shift+O (symbol navigation) en VS Code.

9. Comandos utiles

Verificar entorno:
  cd D:\aTaxip\backend
  .\venv\Scripts\Activate.ps1
  alembic current
  alembic heads
  git log --oneline -5
  git status

Regenerar snapshots:
  Get-ChildItem -Recurse scripts\orm_sync\__pycache__ -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force
  python -B scripts\orm_sync\introspect_db.py
  python -B scripts\orm_sync\introspect_orm.py
  python -B scripts\orm_sync\diff.py
  python -B scripts\orm_sync\apply.py --stats

Backup DB:
  $env:PGPASSWORD = "postgres123"
  & "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda15.dump"

Consultar metodo_pago:
  $env:PGPASSWORD = "postgres123"
  & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT id, nombre FROM payment.metodo_pago ORDER BY nombre, id;"

Ver constraints de metodo_pago:
  $env:PGPASSWORD = "postgres123"
  & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT conname, contype, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'payment.metodo_pago'::regclass ORDER BY conname;"

10. Archivos clave

Documentacion:
  docs/DEUDA_TECNICA_ACTUAL.md (actualizado post-R14)
  docs/CONTEXTO_RONDA_14 a 15.md (handoff R14->R15)
  docs/CONTEXTO_RONDA_15.md (este documento)
  docs/orm_sync/orm_decisiones.md
  docs/orm_reconciliacion_plan.md

Snapshots:
  docs/orm_sync/db_snapshot.json
  docs/orm_sync/orm_snapshot.json
  docs/orm_sync/orm_diff.json
  docs/orm_sync/orm_diff_reporte.md

ORM (modelos de interes):
  app/models/payment.py (MetodoPago, PagoEmpresa, Transaccion)
  app/models/trip.py (ViajeSolicitado.metodo_pago)
  app/models/fleet.py (IngresoTurno.medio_pago)
  app/models/tenant.py (ConfiguracionTenant: mixes)

Migraciones (head):
  migrations/versions/m3_015_rename_checks_canonico.py

11. Numeros consolidados del diff

Metrica           R10    R11    R12    R13    R14

Total             114    71     27     21     0
Tier 1            20     17     7      6      0
Tier 2            79     46     19     15     0
Tier 3            14     7      0      0      0
Tier 4            1      1      1      0      0

Bajada total: 114 -> 0 (-100%) desde R10.
Bajada total: 1280 -> 0 (-100%) desde R5.

LA ALINEACION ESTRUCTURAL BD <-> ORM ESTA COMPLETA.

12. Checklist de arranque R15

Verificar entorno:
  cd D:\aTaxip\backend
  .\venv\Scripts\Activate.ps1
  alembic current      # -> m3_015
  git log --oneline -1 # -> ba4bc19
  git status           # -> clean

Verificar diff:
  python -B scripts\orm_sync\apply.py --stats
  # -> Total 0 items

Backup DB:
  $env:PGPASSWORD = "postgres123"
  & "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda15.dump"

Investigar metodo_pago:
  Correr los comandos de la seccion 4.

Decidir vocabulario canonico:
  Discutir opciones 1/2/3 de la seccion 4.

Planificar migracion m3_016.

13. Referencias cruzadas

Deuda completa: docs/DEUDA_TECNICA_ACTUAL.md.
Handoff R14->R15: docs/CONTEXTO_RONDA_14 a 15.md.
Decisiones tomadas: docs/orm_sync/orm_decisiones.md.
Plan original: docs/orm_reconciliacion_plan.md.

FIN DEL DOCUMENTO