# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-06T10:46:04.486495+00:00

## Resumen ejecutivo

- **332 diferencias** en total.
- **Tier 1**: 62 items.
- **Tier 2**: 158 items.
- **Tier 3**: 111 items.
- **Tier 4**: 1 items.
- **2 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| constraint_nombre_desalineado | 124 |
| constraint_desalineada | 72 |
| constraint_falta | 61 |
| comment_desalineado | 20 |
| constraint_sobra | 17 |
| indice_falta | 14 |
| tabla_falta | 10 |
| nullable_desalineado | 4 |
| indice_nombre_desalineado | 3 |
| indice_sobra | 3 |
| schema_falta | 2 |
| tabla_sobra | 1 |
| columna_falta | 1 |

---

## Tier 1 — 62 items

### comment_desalineado (6)

- `D-0131` — declarado_por
- `D-0132` — transaccion_id
- `D-0216` — snapshot_dia_contractual
- `D-0299` — latitud
- `D-0300` — longitud
- `D-0317` — solicitado_en

### constraint_desalineada (10)

- `D-0050` — auth.usuario
- `D-0086` — fleet.chofer_vehiculo
- `D-0133` — fleet.ingreso_turno
- `D-0217` — fleet.turno_chofer
- `D-0221` — fleet.vehiculo
- `D-0259` — payment.transaccion
- `D-0279` — tenant.control_base
- `D-0290` — trip.calificacion
- `D-0301` — trip.historial_estado_viaje
- `D-0318` — trip.viaje_solicitado

### constraint_falta (10)

- `D-0054` — auth.usuario
- `D-0090` — fleet.chofer_vehiculo
- `D-0223` — fleet.vehiculo
- `D-0225` — fleet.vehiculo
- `D-0226` — fleet.vehiculo
- `D-0295` — trip.calificacion
- `D-0319` — trip.viaje_solicitado
- `D-0320` — trip.viaje_solicitado
- `D-0321` — trip.viaje_solicitado
- `D-0322` — trip.viaje_solicitado

### constraint_nombre_desalineado (27)

- `D-0051` — auth.usuario
- `D-0052` — auth.usuario
- `D-0053` — auth.usuario
- `D-0087` — fleet.chofer_vehiculo
- `D-0088` — fleet.chofer_vehiculo
- `D-0089` — fleet.chofer_vehiculo
- `D-0218` — fleet.turno_chofer
- `D-0219` — fleet.turno_chofer
- `D-0220` — fleet.turno_chofer
- `D-0222` — fleet.vehiculo
- `D-0260` — payment.transaccion
- `D-0261` — payment.transaccion
- `D-0262` — payment.transaccion
- `D-0280` — tenant.control_base
- `D-0281` — tenant.control_base
- `D-0291` — trip.calificacion
- `D-0292` — trip.calificacion
- `D-0293` — trip.calificacion
- `D-0302` — trip.historial_estado_viaje
- `D-0323` — trip.viaje_solicitado
- `D-0324` — trip.viaje_solicitado
- `D-0325` — trip.viaje_solicitado
- `D-0326` — trip.viaje_solicitado
- `D-0327` — trip.viaje_solicitado
- `D-0328` — trip.viaje_solicitado
- `D-0329` — trip.viaje_solicitado
- `D-0330` — trip.viaje_solicitado

### constraint_sobra (2)

- `D-0224` — fleet.vehiculo
- `D-0294` — trip.calificacion

### indice_nombre_desalineado (3)

- `D-0055` — auth.usuario
- `D-0227` — fleet.vehiculo
- `D-0332` — trip.viaje_solicitado

### indice_sobra (2)

- `D-0091` — fleet.chofer_vehiculo
- `D-0331` — trip.viaje_solicitado

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

---

## Tier 2 — 158 items

### columna_falta (1)

- `D-0059` — control_base_id

### constraint_desalineada (62)

- `D-0015` — audit.alerta_desvio
- `D-0017` — audit.log_acciones
- `D-0018` — audit.log_gps
- `D-0021` — auth.auditoria_email
- `D-0022` — auth.autorizacion_inicio
- `D-0026` — auth.direccion_frecuente
- `D-0028` — auth.perfil_general
- `D-0032` — auth.refresh_token
- `D-0036` — auth.reset_token
- `D-0039` — auth.taxista_favorito
- `D-0042` — auth.tipo_usuario
- `D-0046` — auth.turno_empleado
- `D-0056` — auth.usuario_empresa
- `D-0060` — auth.usuario_rol
- `D-0063` — corporate.cuenta_corriente
- `D-0070` — corporate.factura_corporativa
- `D-0075` — corporate.movimiento_cuenta
- `D-0079` — corporate.pago_corporativo
- `D-0081` — fleet.categoria_gasto
- `D-0092` — fleet.contrato_qr
- `D-0096` — fleet.contrato_vehiculo
- `D-0112` — fleet.documento_propietario
- `D-0115` — fleet.documento_vehiculo
- `D-0117` — fleet.documentos_chofer
- `D-0120` — fleet.foto_vehiculo
- `D-0121` — fleet.gasto_turno
- `D-0127` — fleet.gasto_vehiculo
- `D-0134` — fleet.liquidacion
- `D-0144` — fleet.liquidacion_ajuste
- `D-0148` — fleet.liquidacion_detalle
- `D-0150` — fleet.liquidacion_estado_historial
- `D-0155` — fleet.mantenimiento_vehiculo
- `D-0158` — fleet.marca
- `D-0162` — fleet.modelo
- `D-0166` — fleet.neumatico_historial_posicion
- `D-0172` — fleet.neumatico_imagen
- `D-0178` — fleet.neumatico_medicion
- `D-0183` — fleet.neumatico_operacion
- `D-0188` — fleet.neumatico_operacion_detalle
- `D-0191` — fleet.neumatico_sugerencia
- `D-0199` — fleet.neumatico_vehiculo
- `D-0207` — fleet.notificacion_vencimiento
- `D-0212` — fleet.propietario_vehiculo
- `D-0228` — geo.ciudad
- `D-0230` — geo.pais
- `D-0231` — geo.provincia
- `D-0233` — notification.notificacion
- `D-0235` — payment.billetera
- `D-0242` — payment.configuracion_tarifa
- `D-0244` — payment.configuracion_tarifa_vehiculo
- ... y 12 mas (ver JSON)

### constraint_falta (51)

| Tabla | Cantidad |
|---|---|
| fleet.contrato_vehiculo | 11 |
| corporate.cuenta_corriente | 3 |
| fleet.neumatico_sugerencia | 3 |
| fleet.neumatico_vehiculo | 3 |
| fleet.notificacion_vencimiento | 3 |
| corporate.movimiento_cuenta | 2 |
| payment.pago_empresa | 2 |
| public.escaneo_qr | 2 |
| auth.autorizacion_inicio | 1 |
| auth.refresh_token | 1 |
| auth.tipo_usuario | 1 |
| auth.turno_empleado | 1 |
| auth.usuario_rol | 1 |
| corporate.factura_corporativa | 1 |
| fleet.categoria_gasto | 1 |
| fleet.contrato_qr | 1 |
| fleet.documento_propietario | 1 |
| fleet.documentos_chofer | 1 |
| fleet.gasto_turno | 1 |
| fleet.marca | 1 |
| fleet.modelo | 1 |
| fleet.neumatico_historial_posicion | 1 |
| fleet.neumatico_imagen | 1 |
| fleet.neumatico_medicion | 1 |
| fleet.neumatico_operacion | 1 |
| fleet.propietario_vehiculo | 1 |
| payment.billetera | 1 |
| payment.configuracion_tarifa_vehiculo | 1 |
| public.comercio | 1 |
| tenant.factura | 1 |

### constraint_sobra (15)

- `D-0024` — auth.autorizacion_inicio
- `D-0031` — auth.perfil_general
- `D-0038` — auth.reset_token
- `D-0044` — auth.tipo_usuario
- `D-0066` — corporate.cuenta_corriente
- `D-0072` — corporate.factura_corporativa
- `D-0084` — fleet.categoria_gasto
- `D-0094` — fleet.contrato_qr
- `D-0125` — fleet.gasto_turno
- `D-0160` — fleet.marca
- `D-0238` — payment.billetera
- `D-0252` — payment.metodo_pago
- `D-0266` — public.comercio
- `D-0278` — tenant.configuracion_tenant
- `D-0289` — tenant.factura

### indice_falta (14)

- `D-0025` — auth.autorizacion_inicio
- `D-0035` — auth.refresh_token
- `D-0045` — auth.tipo_usuario
- `D-0062` — auth.usuario_rol
- `D-0068` — corporate.cuenta_corriente
- `D-0073` — corporate.factura_corporativa
- `D-0085` — fleet.categoria_gasto
- `D-0095` — fleet.contrato_qr
- `D-0114` — fleet.documento_propietario
- `D-0161` — fleet.marca
- `D-0165` — fleet.modelo
- `D-0211` — fleet.notificacion_vencimiento
- `D-0239` — payment.billetera
- `D-0248` — payment.configuracion_tarifa_vehiculo

### indice_sobra (1)

- `D-0312` — trip.panico

### nullable_desalineado (4)

- `D-0014` — viaje_id
- `D-0080` — updated_at
- `D-0126` — vehiculo_id
- `D-0154` — vehiculo_id

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

## Tier 3 — 111 items

### comment_desalineado (14)

- `D-0069` — estado
- `D-0074` — tipo_movimiento
- `D-0078` — estado
- `D-0205` — entidad_tipo
- `D-0206` — nivel
- `D-0240` — descripcion
- `D-0241` — modo_calculo
- `D-0267` — resultado
- `D-0268` — tipo_qr
- `D-0307` — resuelto_en
- `D-0308` — usuario_id
- `D-0313` — distancia_por_ficha
- `D-0314` — precio_por_ficha
- `D-0315` — precio_por_minuto_espera

### constraint_nombre_desalineado (97)

- `D-0016` — audit.alerta_desvio
- `D-0019` — audit.log_gps
- `D-0020` — audit.log_gps
- `D-0027` — auth.direccion_frecuente
- `D-0029` — auth.perfil_general
- `D-0030` — auth.perfil_general
- `D-0033` — auth.refresh_token
- `D-0037` — auth.reset_token
- `D-0040` — auth.taxista_favorito
- `D-0041` — auth.taxista_favorito
- `D-0047` — auth.turno_empleado
- `D-0048` — auth.turno_empleado
- `D-0057` — auth.usuario_empresa
- `D-0058` — auth.usuario_empresa
- `D-0082` — fleet.categoria_gasto
- `D-0097` — fleet.contrato_vehiculo
- `D-0098` — fleet.contrato_vehiculo
- `D-0099` — fleet.contrato_vehiculo
- `D-0100` — fleet.contrato_vehiculo
- `D-0116` — fleet.documento_vehiculo
- `D-0118` — fleet.documentos_chofer
- `D-0122` — fleet.gasto_turno
- `D-0123` — fleet.gasto_turno
- `D-0128` — fleet.gasto_vehiculo
- `D-0129` — fleet.gasto_vehiculo
- `D-0130` — fleet.gasto_vehiculo
- `D-0135` — fleet.liquidacion
- `D-0136` — fleet.liquidacion
- `D-0137` — fleet.liquidacion
- `D-0138` — fleet.liquidacion
- `D-0139` — fleet.liquidacion
- `D-0140` — fleet.liquidacion
- `D-0141` — fleet.liquidacion
- `D-0142` — fleet.liquidacion
- `D-0143` — fleet.liquidacion
- `D-0145` — fleet.liquidacion_ajuste
- `D-0146` — fleet.liquidacion_ajuste
- `D-0147` — fleet.liquidacion_ajuste
- `D-0149` — fleet.liquidacion_detalle
- `D-0151` — fleet.liquidacion_estado_historial
- `D-0152` — fleet.liquidacion_estado_historial
- `D-0153` — fleet.liquidacion_estado_historial
- `D-0156` — fleet.mantenimiento_vehiculo
- `D-0157` — fleet.mantenimiento_vehiculo
- `D-0163` — fleet.modelo
- `D-0167` — fleet.neumatico_historial_posicion
- `D-0168` — fleet.neumatico_historial_posicion
- `D-0169` — fleet.neumatico_historial_posicion
- `D-0170` — fleet.neumatico_historial_posicion
- `D-0173` — fleet.neumatico_imagen
- ... y 47 mas (ver JSON)

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
