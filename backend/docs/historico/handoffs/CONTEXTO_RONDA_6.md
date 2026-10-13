# CONTEXTO RONDA 6 - TaxIP 2.0

**Fecha:** 2026-10-01
**Ronda previa:** Ronda 5 (cerrada)
**Proxima ronda:** Ronda 6 (Fase 2 del plan de reconciliacion)

---

## Estado actual

### Entorno verificado

- **Python:** 3.12.10
- **PostgreSQL:** 17.0 on x86_64-windows
- **PostGIS:** 3.6
- **Alembic head:** m3_010
- **Git root:** D:/aTaxip
- **Branch:** main
- **Commit HEAD:** a1e0859 (Ronda 5 Fase 1 Sesion 3)

### Tags de git

- ronda5-baseline-pre
- ronda5-fase0-completa
- ronda5-fase1-completa

### Archivos clave

- Plan de reconciliacion: docs/orm_reconciliacion_plan.md
- Deuda tecnica: docs/DEUDA_TECNICA_ACTUAL.md
- Decisiones: docs/orm_sync/orm_decisiones.md
- Reporte diff: docs/orm_sync/orm_diff_reporte.md
- Snapshots: docs/orm_sync/*.json
- Backups: docs/backups/*.dump

---

## Resumen de Ronda 5

### Fase 0 - Preparacion (completada)

- Backup DB pre-Fase 1: taxip_db_2026-09-30.dump (546 KB).
- Snapshot alembic check: alembic_check_baseline_2026-09-30.txt (432 KB).
- .gitattributes configurado para forzar *.txt, *.md, *.json como texto.
- baseline_info.md con el entorno verificado.

### Fase 1 - Diagnostico estructurado (completada)

**3 scripts creados:**

1. scripts/orm_sync/introspect_db.py - Snapshot de la DB.
2. scripts/orm_sync/introspect_orm.py - Snapshot del ORM.
3. scripts/orm_sync/diff.py - Comparacion y clasificacion.

**3 snapshots generados:**

1. docs/orm_sync/db_snapshot.json (788 KB)
   - 12 schemas, 90 tablas, 1065 columnas, 280 indices, 784 constraints.
2. docs/orm_sync/orm_snapshot.json (503 KB)
   - 10 schemas, 73 tablas, 838 columnas, 29 indices, 243 constraints.
3. docs/orm_sync/orm_diff.json (823 KB)
   - 1280 diferencias clasificadas.

**2 reportes generados:**

1. docs/orm_sync/orm_diff_reporte.md (21 KB) - Informe humano.
2. docs/orm_sync/orm_diff_acciones.csv (115 KB) - CSV para Fase 2.

**22 hallazgos documentados (H-001 a H-022)** en orm_decisiones.md.

---

## Resultado del diagnostico

### Magnitud real del problema

| Metrica | DB | ORM | Delta |
|---|---|---|---|
| Schemas | 12 | 10 | -2 |
| Tablas | 90 | 73 | -17 |
| Columnas | 1065 | 838 | -227 |
| Indices | 280 | 29 | -251 |
| Constraints | 784 | 243 | -541 |

**Diferencias totales clasificadas:** 1280.

### Por Tier

- Tier 1 (critico): 247
- Tier 2 (importante): 912
- Tier 3 (cosmetico): 120
- Tier 4 (muerte): 1

### Por clasificacion (top 5)

1. constraint_falta: 428
2. indice_falta: 207
3. nullable_desalineado: 158
4. constraint_nombre_desalineado: 124
5. tipo_desalineado: 114

### Items que requieren decision manual

**24 items:**

- 19 timestamps naive (7 tablas neumatico_*).
- 2 J9 (auth.codigo_metadatos, auth.codigo_verificacion).
- 2 orm_mal_db_bien (tenant.control_base.latitud/longitud).
- 1 vocabulario metodo_pago (fleet.ingreso_turno.medio_pago).

---

## Lo que NO se hizo en Ronda 5

- No se toco el ORM.
- No se toco la DB (solo lectura).
- No se corrio alembic revision.
- No se resolvieron los 24 items de decision.
- No se escribio apply.py.

---

## Proxima ronda - Fase 2

### Objetivo

Clasificacion y decisiones.

### Tareas

1. **Resolver los 24 items que requieren decision manual.**
   - Timestamps naive: decidir (a) ORM a naive, (b) DB a timestamptz, (c) ignorar.
   - J9: decidir unificacion o documentar dos fuentes.
   - control_base lat/lng: confirmar que ORM se adapta a DB (Numeric).
   - metodo_pago.medio_pago: canonizar vocabulario.

2. **Revisar los 247 items de Tier 1.**
   - Confirmar que todos son realmente criticos.
   - Ajustar Tier si hace falta.

3. **Revisar los 912 items de Tier 2.**
   - Priorizar por impacto.

4. **Escribir orm_plan_aplicacion.md.**
   - Lista de cambios a aplicar, agrupados por Tier y por archivo del ORM.
   - Orden de aplicacion.

5. **Actualizar orm_decisiones.md.**
   - Resolver los 24 items.
   - Documentar cada decision.

6. **Preparar Fase 3 (apply.py).**
   - Definir que cambios son automatizables.
   - Definir que cambios requieren intervencion manual.

### Entregables esperados

- docs/orm_sync/orm_decisiones.md (actualizado con 24 decisiones).
- docs/orm_sync/orm_plan_aplicacion.md (nuevo).
- Posible: docs/orm_sync/apply_dryrun_plan.md.

### Duracion estimada

1-2 sesiones.

### Riesgos

- Decisiones de negocio bloqueantes (vocabulario metodo_pago) pueden requerir input externo.
- El diseno de apply.py puede requerir mas analisis del esperado.

---

## Comandos utiles

### Verificar entorno

    cd D:\aTaxip\backend
    .\venv\Scripts\Activate.ps1
    alembic current
    alembic heads

### Regenerar snapshots

    python scripts\orm_sync\introspect_db.py
    python scripts\orm_sync\introspect_orm.py
    python scripts\orm_sync\diff.py

### Ver resumen del diff

    Get-Content "docs\orm_sync\orm_diff_reporte.md" -Head 50

### Ver items que requieren decision

    python -c "import json; d=json.load(open('docs/orm_sync/orm_diff.json')); [print(f\"{x['id']} - {x['schema']}.{x.get('tabla','')}.{x.get('columna','')} - {x['razon_decision']}\") for x in d['diferencias'] if x.get('requiere_decision')]"

### Backup DB

    $env:PGPASSWORD = "postgres123"
    & "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda6.dump"

---

## Reglas criticas (recordatorio)

- NO tocar la DB sin backup previo.
- NO correr alembic revision --autogenerate (destructivo).
- NO usar python -m uvicorn. Usar python run.py.
- SI documentar deuda tecnica nueva.
- SI actualizar DEUDA_TECNICA_ACTUAL.md al cerrar cada ronda.
- SI un bloque por mensaje.
- SI comentarios en ASCII puro (N10).

---

## Referencias

- Plan de reconciliacion: docs/orm_reconciliacion_plan.md
- Deuda tecnica: docs/DEUDA_TECNICA_ACTUAL.md
- Decisiones: docs/orm_sync/orm_decisiones.md
- Reporte diff: docs/orm_sync/orm_diff_reporte.md
- Acciones CSV: docs/orm_sync/orm_diff_acciones.csv
- Baseline: docs/orm_sync/baseline_info.md

---

**FIN DEL DOCUMENTO**