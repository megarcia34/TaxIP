# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-08T19:01:28.966738+00:00

## Resumen ejecutivo

- **71 diferencias** en total.
- **Tier 1**: 17 items.
- **Tier 2**: 46 items.
- **Tier 3**: 7 items.
- **Tier 4**: 1 items.
- **1 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| constraint_falta | 49 |
| comment_desalineado | 13 |
| constraint_sobra | 6 |
| tabla_sobra | 1 |
| columna_falta | 1 |
| indice_falta | 1 |

---

## Tier 1 — 17 items

### comment_desalineado (6)

- `D-0028` — declarado_por
- `D-0029` — transaccion_id
- `D-0045` — snapshot_dia_contractual
- `D-0060` — latitud
- `D-0061` — longitud
- `D-0067` — solicitado_en

### constraint_falta (9)

- `D-0002` — auth.codigo_verificacion
- `D-0013` — fleet.chofer_vehiculo
- `D-0047` — fleet.vehiculo
- `D-0048` — fleet.vehiculo
- `D-0059` — trip.calificacion
- `D-0068` — trip.viaje_solicitado
- `D-0069` — trip.viaje_solicitado
- `D-0070` — trip.viaje_solicitado
- `D-0071` — trip.viaje_solicitado

### constraint_sobra (2)

- `D-0046` — fleet.vehiculo
- `D-0058` — trip.calificacion

---

## Tier 2 — 46 items

### columna_falta (1)

- `D-0007` — control_base_id

### constraint_falta (40)

| Tabla | Cantidad |
|---|---|
| fleet.contrato_vehiculo | 11 |
| fleet.neumatico_sugerencia | 3 |
| fleet.neumatico_vehiculo | 3 |
| fleet.notificacion_vencimiento | 3 |
| corporate.cuenta_corriente | 2 |
| corporate.movimiento_cuenta | 2 |
| payment.pago_empresa | 2 |
| public.escaneo_qr | 2 |
| auth.refresh_token | 1 |
| auth.turno_empleado | 1 |
| auth.usuario_rol | 1 |
| fleet.documento_propietario | 1 |
| fleet.documentos_chofer | 1 |
| fleet.modelo | 1 |
| fleet.neumatico_historial_posicion | 1 |
| fleet.neumatico_imagen | 1 |
| fleet.neumatico_medicion | 1 |
| fleet.neumatico_operacion | 1 |
| fleet.propietario_vehiculo | 1 |
| payment.configuracion_tarifa_vehiculo | 1 |

### constraint_sobra (4)

- `D-0003` — auth.perfil_general
- `D-0005` — auth.reset_token
- `D-0052` — payment.metodo_pago
- `D-0057` — tenant.configuracion_tenant

### indice_falta (1)

- `D-0025` — fleet.contrato_vehiculo

---

## Tier 3 — 7 items

### comment_desalineado (7)

- `D-0049` — descripcion
- `D-0050` — modo_calculo
- `D-0062` — resuelto_en
- `D-0063` — usuario_id
- `D-0064` — distancia_por_ficha
- `D-0065` — precio_por_ficha
- `D-0066` — precio_por_minuto_espera

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
