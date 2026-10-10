# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-10T11:33:21.963181+00:00

## Resumen ejecutivo

- **27 diferencias** en total.
- **Tier 1**: 7 items.
- **Tier 2**: 19 items.
- **Tier 4**: 1 items.
- **1 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| constraint_falta | 22 |
| tabla_sobra | 1 |
| columna_falta | 1 |
| indice_falta | 1 |
| comment_desalineado | 1 |
| constraint_sobra | 1 |

---

## Tier 1 — 7 items

### comment_desalineado (1)

- `D-0017` — snapshot_dia_contractual

### constraint_falta (6)

- `D-0002` — auth.codigo_verificacion
- `D-0023` — trip.calificacion
- `D-0024` — trip.viaje_solicitado
- `D-0025` — trip.viaje_solicitado
- `D-0026` — trip.viaje_solicitado
- `D-0027` — trip.viaje_solicitado

---

## Tier 2 — 19 items

### columna_falta (1)

- `D-0004` — control_base_id

### constraint_falta (16)

- `D-0003` — auth.turno_empleado
- `D-0005` — auth.usuario_rol
- `D-0006` — corporate.cuenta_corriente
- `D-0007` — fleet.contrato_vehiculo
- `D-0008` — fleet.contrato_vehiculo
- `D-0009` — fleet.contrato_vehiculo
- `D-0010` — fleet.contrato_vehiculo
- `D-0011` — fleet.contrato_vehiculo
- `D-0012` — fleet.contrato_vehiculo
- `D-0013` — fleet.contrato_vehiculo
- `D-0014` — fleet.contrato_vehiculo
- `D-0015` — fleet.contrato_vehiculo
- `D-0019` — payment.pago_empresa
- `D-0020` — payment.pago_empresa
- `D-0021` — public.escaneo_qr
- `D-0022` — public.escaneo_qr

### constraint_sobra (1)

- `D-0018` — payment.metodo_pago

### indice_falta (1)

- `D-0016` — fleet.contrato_vehiculo

---

## Tier 4 — 1 items

### tabla_sobra (1)

- `D-0001` — trip.reserva

---

## Items que requieren decision manual

| ID | Item | Razon |
|---|---|---|
| D-0002 | auth.codigo_verificacion | j9_dos_fuentes_de_verdad |

---

## Archivos generados

- `orm_diff.json` — datos completos.
- `orm_diff_reporte.md` — este informe.
- `orm_diff_acciones.csv` — CSV de acciones sugeridas.
