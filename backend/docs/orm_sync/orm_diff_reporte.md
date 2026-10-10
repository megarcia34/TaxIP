# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-10T15:22:06.134256+00:00

## Resumen ejecutivo

- **21 diferencias** en total.
- **Tier 1**: 6 items.
- **Tier 2**: 15 items.
- **1 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| constraint_falta | 21 |

---

## Tier 1 — 6 items

### constraint_falta (6)

- `D-0001` — auth.codigo_verificacion
- `D-0017` — trip.calificacion
- `D-0018` — trip.viaje_solicitado
- `D-0019` — trip.viaje_solicitado
- `D-0020` — trip.viaje_solicitado
- `D-0021` — trip.viaje_solicitado

---

## Tier 2 — 15 items

### constraint_falta (15)

- `D-0002` — auth.turno_empleado
- `D-0003` — corporate.cuenta_corriente
- `D-0004` — fleet.contrato_vehiculo
- `D-0005` — fleet.contrato_vehiculo
- `D-0006` — fleet.contrato_vehiculo
- `D-0007` — fleet.contrato_vehiculo
- `D-0008` — fleet.contrato_vehiculo
- `D-0009` — fleet.contrato_vehiculo
- `D-0010` — fleet.contrato_vehiculo
- `D-0011` — fleet.contrato_vehiculo
- `D-0012` — fleet.contrato_vehiculo
- `D-0013` — payment.pago_empresa
- `D-0014` — payment.pago_empresa
- `D-0015` — public.escaneo_qr
- `D-0016` — public.escaneo_qr

---

## Items que requieren decision manual

| ID | Item | Razon |
|---|---|---|
| D-0001 | auth.codigo_verificacion | j9_dos_fuentes_de_verdad |

---

## Archivos generados

- `orm_diff.json` — datos completos.
- `orm_diff_reporte.md` — este informe.
- `orm_diff_acciones.csv` — CSV de acciones sugeridas.
