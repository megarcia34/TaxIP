# Baseline Info - Fase 0

**Capturado:** 2026-09-30 20:15:35
**Proposito:** Snapshot del entorno al inicio de Fase 1 (reconciliacion ORM-DB)

---

## Entorno

### Python

- **Version:** 3.12.10
- **Nota:** el traspaso decia 3.11, discrepancia documental

### Git

- **Root:** D:/aTaxip
- **Branch:** main
- **Commit:** 4c77f3adb44b087c5f1bff1eaafe082803903b68
- **Tag baseline:** ronda5-baseline-pre

### Alembic

- **Current:** m3_010 (head)
- **Heads:** m3_010 (head)

### PostgreSQL

- **pg_dump:** 17.0
- **psql:** 17.0
- **Server:** PostgreSQL 17.0 on x86_64-windows, compiled by msvc-19.41.34120, 64-bit
- **PostGIS:** 3.6 USE_GEOS=1 USE_PROJ=1 USE_STATS=1

---

## Inventario de schemas y tablas

| Schema | Tablas |
|---|---|
| audit | 4 |
| auth | 16 |
| comunicacion | 3 |
| corporate | 4 |
| fleet | 31 |
| geo | 3 |
| notification | 1 |
| payment | 9 |
| public | 4 |
| rentabilidad | 3 |
| tenant | 4 |
| trip | 8 |
| **TOTAL** | **90** |

---

## Archivos de referencia

- **Backup DB:** docs/backups/taxip_db_2026-09-30.dump (546 KB)
- **Snapshot alembic check:** docs/orm_sync/alembic_check_baseline_2026-09-30.txt (849 KB, 2.611 lineas)
- **Decisiones:** docs/orm_sync/orm_decisiones.md

---

**FIN DEL DOCUMENTO**