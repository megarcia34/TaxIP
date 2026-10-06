# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-06T22:10:53.209753+00:00

## Resumen ejecutivo

- **114 diferencias** en total.
- **Tier 1**: 20 items.
- **Tier 2**: 79 items.
- **Tier 3**: 14 items.
- **Tier 4**: 1 items.
- **2 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| constraint_falta | 48 |
| indice_falta | 22 |
| comment_desalineado | 20 |
| tabla_falta | 10 |
| constraint_sobra | 6 |
| nullable_desalineado | 4 |
| schema_falta | 2 |
| tabla_sobra | 1 |
| columna_falta | 1 |

---

## Tier 1 — 20 items

### comment_desalineado (6)

- `D-0058` — declarado_por
- `D-0059` — transaccion_id
- `D-0081` — snapshot_dia_contractual
- `D-0103` — latitud
- `D-0104` — longitud
- `D-0110` — solicitado_en

### constraint_falta (8)

- `D-0039` — fleet.chofer_vehiculo
- `D-0083` — fleet.vehiculo
- `D-0084` — fleet.vehiculo
- `D-0102` — trip.calificacion
- `D-0111` — trip.viaje_solicitado
- `D-0112` — trip.viaje_solicitado
- `D-0113` — trip.viaje_solicitado
- `D-0114` — trip.viaje_solicitado

### constraint_sobra (2)

- `D-0082` — fleet.vehiculo
- `D-0101` — trip.calificacion

### indice_falta (2)

- `D-0023` — auth.usuario
- `D-0085` — fleet.vehiculo

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

---

## Tier 2 — 79 items

### columna_falta (1)

- `D-0024` — control_base_id

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

- `D-0017` — auth.perfil_general
- `D-0020` — auth.reset_token
- `D-0091` — payment.metodo_pago
- `D-0099` — tenant.configuracion_tenant

### indice_falta (20)

- `D-0015` — auth.autorizacion_inicio
- `D-0016` — auth.autorizacion_inicio
- `D-0019` — auth.refresh_token
- `D-0021` — auth.tipo_usuario
- `D-0026` — auth.usuario_rol
- `D-0029` — corporate.cuenta_corriente
- `D-0030` — corporate.cuenta_corriente
- `D-0032` — corporate.factura_corporativa
- `D-0038` — fleet.categoria_gasto
- `D-0040` — fleet.contrato_qr
- `D-0041` — fleet.contrato_qr
- `D-0053` — fleet.contrato_vehiculo
- `D-0055` — fleet.documento_propietario
- `D-0061` — fleet.marca
- `D-0063` — fleet.modelo
- `D-0079` — fleet.notificacion_vencimiento
- `D-0086` — payment.billetera
- `D-0090` — payment.configuracion_tarifa_vehiculo
- `D-0094` — public.comercio
- `D-0100` — tenant.factura

### nullable_desalineado (4)

- `D-0014` — viaje_id
- `D-0037` — updated_at
- `D-0057` — vehiculo_id
- `D-0060` — vehiculo_id

### schema_falta (2)

- `D-0001` — comunicacion
- `D-0002` — rentabilidad

### tabla_falta (8)

- `D-0003` — audit.alertas_vencimiento
- `D-0006` — auth.plantilla_viaje
- `D-0007` — auth.prestadora_telefonica
- `D-0008` — fleet.historial_chofer_vehiculo
- `D-0009` — fleet.relacion_propietario_vehiculo
- `D-0010` — payment.configuracion_pasarela
- `D-0011` — payment.qr_cobro
- `D-0012` — trip.broadcast_log

---

## Tier 3 — 14 items

### comment_desalineado (14)

- `D-0031` — estado
- `D-0033` — tipo_movimiento
- `D-0036` — estado
- `D-0074` — entidad_tipo
- `D-0075` — nivel
- `D-0087` — descripcion
- `D-0088` — modo_calculo
- `D-0095` — resultado
- `D-0096` — tipo_qr
- `D-0105` — resuelto_en
- `D-0106` — usuario_id
- `D-0107` — distancia_por_ficha
- `D-0108` — precio_por_ficha
- `D-0109` — precio_por_minuto_espera

---

## Tier 4 — 1 items

### tabla_sobra (1)

- `D-0013` — trip.reserva

---

## Items que requieren decision manual

| ID | Item | Razon |
|---|---|---|
| D-0004 | auth.codigo_metadatos | j9_dos_fuentes_de_verdad |
| D-0005 | auth.codigo_verificacion | j9_dos_fuentes_de_verdad |

---

## Archivos generados

- `orm_diff.json` — datos completos.
- `orm_diff_reporte.md` — este informe.
- `orm_diff_acciones.csv` — CSV de acciones sugeridas.
