# CONTEXTO RONDA 7 - TaxIP 2.0

**Fecha:** 2026-10-02
**Ronda previa:** Ronda 6 (cerrada)
**Proxima ronda:** Ronda 7 (Fase 4b del plan de reconciliacion)

---

## Estado actual

### Entorno verificado

- **Python:** 3.12.10
- **PostgreSQL:** 17.0 on x86_64-windows
- **PostGIS:** 3.6
- **Alembic head:** m3_010
- **Git root:** D:/aTaxip
- **Branch:** main
- **Commit HEAD:** (lo llena el commit final de Ronda 6)

### Tags de git

- ronda5-baseline-pre
- ronda5-fase0-completa
- ronda5-fase1-completa
- ronda5-completa
- ronda6-fase2-sesion1-completa
- ronda6-fase2-sesion2-completa
- ronda6-fase3-completa
- ronda6-completa

### Archivos clave

- Plan de reconciliacion: docs/orm_reconciliacion_plan.md
- Deuda tecnica: docs/DEUDA_TECNICA_ACTUAL.md
- Decisiones: docs/orm_sync/orm_decisiones.md
- Plan de aplicacion: docs/orm_sync/orm_plan_aplicacion.md
- Reporte diff: docs/orm_sync/orm_diff_reporte.md
- Snapshots: docs/orm_sync/*.json
- Backups: docs/backups/*.dump

---

## Resumen de Ronda 5 (diagnostico)

- Fase 0 completa: backup + baseline + .gitattributes.
- Fase 1 completa: 3 scripts (introspect_db, introspect_orm, diff) +
  1.280 diferencias clasificadas en 4 tiers.
- 22 hallazgos (H-001 a H-022).
- Tag: ronda5-completa.

## Resumen de Ronda 6

### Fase 2 - Decisiones (completa)

- 24 items con decision manual resueltos.
- D-005 (metodo_pago): vocabulario canonico acotado.
- D-006 (J9 auth): falso positivo documental.
- D-007 (control_base): String(50) -> Numeric.
- D-012 (timestamps neumatico_*): ORM a naive.
- Entregables:
  - docs/orm_sync/orm_decisiones.md (actualizado).
  - docs/orm_sync/orm_plan_aplicacion.md (nuevo).
  - docs/DEUDA_TECNICA_ACTUAL.md (actualizado, 53 items).
- Tags: ronda6-fase2-sesion1-completa, ronda6-fase2-sesion2-completa.

### Fase 3 - apply.py (completa)

- scripts/orm_sync/apply.py (v3).
- 3 modos: --stats, --report, --generate.
- 1.193 items automatizables, 87 manuales.
- Entregables:
  - scripts/orm_sync/apply.py.
  - .gitignore (ignora borradores y logs).
- Tag: ronda6-fase3-completa.

### Fase 4a - trip.py (completa)

- 8 pasos aplicados a app/models/trip.py.
- ~103 items resueltos.
- B5 (ViajeSolicitado desactualizado) tecnicamente cerrado.

**Detalle de pasos:**

| Paso | Items | Commit |
|---|---|---|
| 1. imports + 5 cols | — | 8b6b6c0 |
| 2. 24 cols restantes | 24 | f43f3a8 |
| 3. 8 CHECK | 8 | a9b9767 |
| 4. 18 indices | 18 | 0589194 |
| 5.1. String 20 -> 30 | 2 | 40f023f |
| 5.2. DECIMAL -> Numeric | 18 | d294912 |
| 5.3. Numeric sin params | 3 | a0be2e6 |
| 5.5. nullable=False -> True | 25 | afd4a01 |
| 6. Borrar Reserva | POSTERGADO | (deuda) |

**Tag:** ronda6-completa.

---

## Estado del diff (post Fase 4a)

### Items por archivo

| Archivo | Total | Hecho | Falta | % |
|---|---|---|---|---|
| app/models/trip.py | 171 | ~103 | ~68 | 60% |
| app/models/fleet.py | 408 | 0 | 408 | 0% |
| app/models/auth.py | 144 | 0 | 144 | 0% |
| app/models/payment.py | 119 | 0 | 119 | 0% |
| app/models/corporate.py | 99 | 0 | 99 | 0% |
| app/models/tenant.py | 92 | 0 | 92 | 0% |
| app/models/audit.py | 44 | 0 | 44 | 0% |
| app/models/public.py | 36 | 0 | 36 | 0% |
| app/models/geo.py | 20 | 0 | 20 | 0% |
| app/models/notification.py | 11 | 0 | 11 | 0% |
| app/models/comunicacion.py | 1 | 0 | 1 | 0% (crear) |
| app/models/rentabilidad.py | 1 | 0 | 1 | 0% (crear) |
| **TOTAL** | **1.280** | **~103** | **~1.177** | **~8%** |

### Por Tier

| Tier | Total | Hecho | Falta |
|---|---|---|---|
| Tier 1 (critico) | 247 | ~80 | ~167 |
| Tier 2 (importante) | 912 | ~23 | ~889 |
| Tier 3 (cosmetico) | 120 | 0 | 120 |
| Tier 4 (muerte) | 1 | 0 | 1 |

---

## Proxima ronda - Fase 4b (fleet.py)

### Objetivo

Aplicar los cambios necesarios en app/models/fleet.py para alinearlo
con la DB.

### Items a resolver

- **511 automatizables:**
  - constraint_falta: mayoritario.
  - indice_falta: mayoritario.
  - nullable_desalineado: probablemente.
  - tipo_desalineado: probablemente.
  - columna_falta: minoritario.
- **93 Tier 1** (criticos).

### Archivos afectados

- app/models/fleet.py (511 items).
- Posible: app/models/fleet.py refactor del modulo neumatico_* (para D-012).

### Estrategia recomendada

1. **Regenerar snapshots** al inicio de la ronda (post-Fase 4a).
2. **Correr `apply.py --generate app/models/fleet.py`** para obtener el
   borrador actualizado.
3. **Revisar el borrador** y agrupar items por patron.
4. **Aplicar en pasos** (como en Fase 4a):
   - Paso 1: columnas faltantes.
   - Paso 2: CHECK constraints.
   - Paso 3: indices.
   - Paso 4: tipo desalineado.
   - Paso 5: nullable desalineado.
   - Paso 6: D-012 (timestamps neumatico_*).
5. **1 commit por paso.**
6. **`alembic check` despues de cada paso.**
7. **Tag al final: ronda7-completa.**

### Decisiones aplicables en Fase 4b

- **D-005** (metodo_pago): alinear comment de fleet.ingreso_turno.medio_pago.
- **D-012** (timestamps neumatico_*): cambiar DateTime(timezone=True) a
  DateTime(timezone=False) + server_default=func.now() en las 19 columnas.

### Duracion estimada

2-4 sesiones (fleet.py es el archivo mas grande).

### Riesgos

- fleet.py tiene 31 tablas y 22 clases. Es el archivo mas grande del ORM.
- Los timestamps naive de D-012 afectan 7 tablas neumatico_*.
- Puede haber nuevos patrones no vistos en trip.py.

---

## Lo que NO se hizo en Ronda 6

- No se aplico Fase 4b (fleet.py).
- No se aplico Fase 4c (auth + tenant + payment).
- No se aplico Fase 4d (resto).
- No se aplico Fase 4e (Reserva).
- No se corrio Fase 5 (verificacion final).

---

## Deudas independientes (no del plan original)

Surgieron durante Fase 4a y quedan pendientes de decision o ronda aparte:

1. **orm.reserva_modulo_activo:** el modulo /api/reservas esta activo
   pero la tabla trip.reserva no existe. Requiere decision funcional.
2. **orm.foto_viaje_out_of_scope:** el item D-1125 (foto_viaje.created_at
   nullable) esta en app/models/foto_viaje.py, no en trip.py. Fase 4d.
3. **metodo_pago.catalogo_sucio:** limpieza de payment.metodo_pago.
4. **metodo_pago.fk_catalogo:** refactor a FK por metodo_pago_id.
5. **metodo_pago.pasarela:** integracion con pasarela (decision comercial).
6. **infra.postgres_en_c:** PostgreSQL en C: (disco lleno, mover data dir).

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

### Generar borrador de fleet.py

    python scripts\orm_sync\apply.py --generate app/models/fleet.py

### Ver stats del diff

    python scripts\orm_sync\apply.py --stats

### Backup DB

    $env:PGPASSWORD = "postgres123"
    & "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -p 5432 -U postgres -d taxip_db -F c -b -f "D:\aTaxip\backend\docs\backups\taxip_db_ronda7.dump"

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
- Plan de aplicacion: docs/orm_sync/orm_plan_aplicacion.md
- Reporte diff: docs/orm_sync/orm_diff_reporte.md
- Baseline: docs/orm_sync/baseline_info.md

---

**FIN DEL DOCUMENTO**