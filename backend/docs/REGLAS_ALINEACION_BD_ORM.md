# REGLAS DE ALINEACION BD <-> ORM <-> POSTGRES

**Documento vivo. Pegar como primer mensaje al inicio de cada chat.**
**Ultima actualizacion:** 2026-10-13 (post R18)

---

## PRINCIPIO FUNDAMENTAL

**LA DB ES LA FUENTE DE VERDAD.**
**El ORM se adapta a la DB. NO al reves.**

Si hay conflicto entre lo que dice la DB y lo que dice el ORM:

1. **La DB manda.**
2. **Se ajusta el ORM.**
3. **NO se toca la DB** (salvo migracion explicita con backup previo).

---

## REGLAS OPERATIVAS

### 1. Comentarios: leer de Postgres, replicar en ORM

**NO inventar semantica.**

- **SIEMPRE** leer el `COMMENT ON COLUMN` real de Postgres.
- **Replicarlo textual** en el docstring del ORM.
- Si el comment tiene tildes, respetarlas (UTF-8).
- Si el comment tiene mojibake, corregirlo (pero documentar el cambio).

**Ejemplo:**

DB:
```sql
COMMENT ON COLUMN fleet.turno_chofer.snapshot_dia_contractual
IS 'Dia contractual al inicio del turno (ej. LUNES, MARTES). Snapshot inmutable.';
ORM:
python

snapshot_dia_contractual = Column(
    String(20),
    nullable=True,
    comment="Dia contractual al inicio del turno (ej. LUNES, MARTES). Snapshot inmutable."
)

Regla: el texto es el mismo. Solo se documenta del lado Python.
2. NO tocar la DB para agregar comentarios

El comment ya esta en la DB.

    Si el ORM no lo tiene, se agrega en el ORM.

    NO se corre COMMENT ON COLUMN (a menos que falte en la DB).

Excepcion: si el comment falta en ambos lados y querés documentarlo:

    Usar doc= en el ORM (no persiste en DB).

    NO usar comment= (persiste y desalinea).

Regla general:

    comment= → solo cuando el texto tambien esta en la DB (sincronizado).

    doc= → documentacion interna de Python que NO va a la DB.

3. Naming de constraints: seguir la convention

La convention esta en app/database.py:
python

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

Aplicacion:

    UniqueConstraint("nombre") → SQLAlchemy genera uq_<tabla>_nombre automaticamente.

    CheckConstraint("...", name="nombre") → SQLAlchemy genera ck_<tabla>_nombre.

    NO repetir el prefijo ck_<tabla>_ en el name= (SQLAlchemy lo agrega).

Ejemplo:

✅ Correcto:
python

CheckConstraint(
    "nombre IN ('efectivo', 'tarjeta_debito', 'qr', 'transferencia')",
    name="nombre",   # genera: ck_metodo_pago_nombre
)

❌ Incorrecto:
python

CheckConstraint(
    "...",
    name="ck_metodo_pago_nombre",   # genera: ck_metodo_pago_ck_metodo_pago_nombre
)

4. Alinear nullable/tipo desde la DB, no al reves

Si la DB tiene NOT NULL y el ORM no:

    Alinear el ORM a nullable=False.

    NO tocar la DB.

Si la DB tiene NUMERIC(10,8) y el ORM tiene String(50):

    Alinear el ORM a Numeric(10, 8).

    NO tocar la DB.

La DB es la fuente de verdad.
5. Migraciones: SOLO op.execute manual

NO usar alembic revision --autogenerate. Es destructivo.

Razon: el ORM tiene representaciones cosmeticas distintas a la DB (nombres de FK, ondelete, UNIQUEs como index vs constraint, etc.). Autogenerate generaria operaciones falsas y romperia la DB.

Regla:

    Toda migracion se escribe a mano.

    Se usa op.execute("...") con SQL raw.

    Antes de aplicar: backup DB + revisar diff = 0.

6. Antes de tocar el ORM: regenerar snapshots

El diff.py compara snapshots. Si el ORM cambio y el snapshot no:

    El diff da falsos positivos.

Antes de cualquier verificacion:
powershell

Get-ChildItem -Recurse scripts\orm_sync\__pycache__ -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force
python -B scripts\orm_sync\introspect_db.py
python -B scripts\orm_sync\introspect_orm.py
python -B scripts\orm_sync\diff.py
python -B scripts\orm_sync\apply.py --stats

Esperado: Total items: 0.
7. alembic check es ruidoso. Usar diff.py.

alembic check reporta ~200 operaciones que son falsos positivos:

    Naming de FK distinto (DB legacy vs ORM convention).

    UNIQUE constraint vs UNIQUE index.

    FKs con ondelete declarado en ORM pero no aplicado en DB.

El diff.py es la fuente de verdad. Reporta 0 items cuando todo esta alineado.

NUNCA correr alembic revision --autogenerate.
8. CODIGO: ASCII puro en comentarios y logs (N10)

En codigo Python:

    Comentarios → ASCII puro.

    Docstrings → ASCII puro.

    Logs → ASCII puro (o emojis si el logger esta en UTF-8 configurado).

    Strings al usuario final → tildes OK.

Razon: el proyecto tuvo problemas de mojibake con logs en Windows (cp1252 vs UTF-8). N10 existe para evitar eso.
9. Encoding: UTF-8 SIN BOM

Todos los archivos .py deben guardarse con UTF-8 SIN BOM.

Si VS Code agrega BOM:

    Python tira SyntaxError: invalid non-printable character U+FEFF.

    Hay que removerlo con script.

Configurar VS Code:

    Ctrl+, → buscar files.encoding → poner utf8 (sin BOM).

    files.autoGuessEncoding: false.

Verificar BOM tras cada save:
powershell

$file = "ruta\al\archivo.py"
$bytes = [System.IO.File]::ReadAllBytes((Resolve-Path $file))
if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    Write-Host "BOM detectado - removiendo..."
    $newBytes = $bytes[3..($bytes.Length - 1)]
    [System.IO.File]::WriteAllBytes((Resolve-Path $file), $newBytes)
} else {
    Write-Host "Sin BOM OK"
}

10. Una migracion = una responsabilidad

Cada migracion hace UNA cosa:

    Agregar un CHECK.

    Renombrar un constraint.

    Eliminar un indice.

    Agregar una columna.

NO mezclar:

    Cambios estructurales.

    Cambios de datos.

    Cambios cosmeticos.

Razon: facilita rollback selectivo y auditoria.
FLUJO DE TRABAJO
Al agregar una constraint/comentario al ORM:

    Leer la DB primero:
    sql

    SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname = '...';
    SELECT obj_description('schema.tabla'::regclass, 'pg_class');

    Replicar en el ORM (con la convention correcta).

    Verificar diff = 0:
    powershell

    python -B scripts\orm_sync\diff.py
    python -B scripts\orm_sync\apply.py --stats

    Si diff > 0: ver el reporte, corregir el ORM (NO la DB).

    Commitear con mensaje claro.

Al agregar una constraint/comentario NUEVOS:

    Primero la migracion (con op.execute).

    Aplicar (alembic upgrade head).

    Verificar en DB (que la constraint/comment este).

    Replicar en el ORM.

    Verificar diff = 0.

    Commitear.

Antes de commitear:

    ✅ Diff BD ↔ ORM = 0.

    ✅ Todos los archivos sin BOM.

    ✅ Sintaxis OK (python -c "import ast; ...").

    ✅ App importa (python -c "from app.main import app").

    ✅ Backup DB (si tocaste schema).

ERRORES COMUNES (que ya nos pasaron)
Error	Causa	Fix
SyntaxError: invalid non-printable character U+FEFF	BOM en el archivo	Remover BOM
Diff > 0 tras cambiar el ORM	Snapshot desactualizado	Regenerar snapshots
Diff > 0 tras agregar CHECK	name= con prefijo ck_<tabla>_ duplicado	Usar solo name="nombre"
ImportError: partially initialized module	Import circular	Revisar imports
Mojibake en logs	cp1252 vs UTF-8	N10 + reconfigure(encoding='utf-8')
alembic check reporta 200+ items	Falsos positivos	Ignorar. Usar diff.py.
Snapshot regenerado cambia sin tocar DB	Timestamp de captura	Regenerar y verificar diff real
COMANDOS CLAVE
Verificar alineacion completa
powershell

Get-ChildItem -Recurse scripts\orm_sync\__pycache__ -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force
python -B scripts\orm_sync\introspect_db.py
python -B scripts\orm_sync\introspect_orm.py
python -B scripts\orm_sync\diff.py
python -B scripts\orm_sync\apply.py --stats

Esperado: Total items: 0.
Backup DB
powershell

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_rondaN.dump"

Aplicar migracion
powershell

alembic upgrade head
alembic current

Ver constraints de una tabla
powershell

$env:PGPASSWORD = "postgres123"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'schema.tabla'::regclass;"

Ver comments de una columna
powershell

& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U postgres -d taxip_db -c "SELECT col_description('schema.tabla'::regclass, ordinal_position) FROM information_schema.columns WHERE table_schema = 'schema' AND table_name = 'tabla' AND column_name = 'columna';"

REFERENCIAS

    Deuda pendiente: docs/DEUDA_TECNICA_ACTUAL.md

    Historico de rondas: docs/HISTORICO_CERRADAS.md

    Decisiones ORM: docs/orm_sync/orm_decisiones.md

    Snapshots: docs/orm_sync/

    Backups: docs/backups/

PRINCIPIO FINAL

    No hay que inventar semantica.
    Hay que leer el comment de Postgres y replicarlo en el docstring del ORM.
    No hay que tocar la DB. El comment ya esta. Solo se documenta del lado Python.
    Los comentarios inline propuestos quedan sujetos a lo que diga el comment real.
    La DB es la fuente de verdad.

FIN DEL DOCUMENTO