# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-05T22:29:39.035833+00:00

## Resumen ejecutivo

- **404 diferencias** en total.
- **Tier 1**: 72 items.
- **Tier 2**: 220 items.
- **Tier 3**: 111 items.
- **Tier 4**: 1 items.
- **2 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| constraint_nombre_desalineado | 124 |
| indice_falta | 86 |
| constraint_desalineada | 72 |
| constraint_falta | 61 |
| comment_desalineado | 20 |
| constraint_sobra | 17 |
| tabla_falta | 10 |
| nullable_desalineado | 4 |
| indice_nombre_desalineado | 3 |
| indice_sobra | 3 |
| schema_falta | 2 |
| tabla_sobra | 1 |
| columna_falta | 1 |

---

## Tier 1 — 72 items

### comment_desalineado (6)

- `D-0160` — declarado_por
- `D-0161` — transaccion_id
- `D-0262` — snapshot_dia_contractual
- `D-0366` — latitud
- `D-0367` — longitud
- `D-0388` — solicitado_en

### constraint_desalineada (10)

- `D-0062` — auth.usuario
- `D-0106` — fleet.chofer_vehiculo
- `D-0162` — fleet.ingreso_turno
- `D-0263` — fleet.turno_chofer
- `D-0268` — fleet.vehiculo
- `D-0317` — payment.transaccion
- `D-0341` — tenant.control_base
- `D-0355` — trip.calificacion
- `D-0368` — trip.historial_estado_viaje
- `D-0389` — trip.viaje_solicitado

### constraint_falta (10)

- `D-0066` — auth.usuario
- `D-0110` — fleet.chofer_vehiculo
- `D-0270` — fleet.vehiculo
- `D-0272` — fleet.vehiculo
- `D-0273` — fleet.vehiculo
- `D-0360` — trip.calificacion
- `D-0390` — trip.viaje_solicitado
- `D-0391` — trip.viaje_solicitado
- `D-0392` — trip.viaje_solicitado
- `D-0393` — trip.viaje_solicitado

### constraint_nombre_desalineado (27)

- `D-0063` — auth.usuario
- `D-0064` — auth.usuario
- `D-0065` — auth.usuario
- `D-0107` — fleet.chofer_vehiculo
- `D-0108` — fleet.chofer_vehiculo
- `D-0109` — fleet.chofer_vehiculo
- `D-0264` — fleet.turno_chofer
- `D-0265` — fleet.turno_chofer
- `D-0266` — fleet.turno_chofer
- `D-0269` — fleet.vehiculo
- `D-0318` — payment.transaccion
- `D-0319` — payment.transaccion
- `D-0320` — payment.transaccion
- `D-0342` — tenant.control_base
- `D-0343` — tenant.control_base
- `D-0356` — trip.calificacion
- `D-0357` — trip.calificacion
- `D-0358` — trip.calificacion
- `D-0369` — trip.historial_estado_viaje
- `D-0394` — trip.viaje_solicitado
- `D-0395` — trip.viaje_solicitado
- `D-0396` — trip.viaje_solicitado
- `D-0397` — trip.viaje_solicitado
- `D-0398` — trip.viaje_solicitado
- `D-0399` — trip.viaje_solicitado
- `D-0400` — trip.viaje_solicitado
- `D-0401` — trip.viaje_solicitado

### constraint_sobra (2)

- `D-0271` — fleet.vehiculo
- `D-0359` — trip.calificacion

### indice_falta (10)

- `D-0067` — auth.usuario
- `D-0111` — fleet.chofer_vehiculo
- `D-0163` — fleet.ingreso_turno
- `D-0267` — fleet.turno_chofer
- `D-0274` — fleet.vehiculo
- `D-0321` — payment.transaccion
- `D-0344` — tenant.control_base
- `D-0361` — trip.calificacion
- `D-0370` — trip.historial_estado_viaje
- `D-0402` — trip.viaje_solicitado

### indice_nombre_desalineado (3)

- `D-0068` — auth.usuario
- `D-0275` — fleet.vehiculo
- `D-0404` — trip.viaje_solicitado

### indice_sobra (2)

- `D-0112` — fleet.chofer_vehiculo
- `D-0403` — trip.viaje_solicitado

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

---

## Tier 2 — 220 items

### columna_falta (1)

- `D-0073` — control_base_id

### constraint_desalineada (62)

- `D-0015` — audit.alerta_desvio
- `D-0018` — audit.log_acciones
- `D-0020` — audit.log_gps
- `D-0024` — auth.auditoria_email
- `D-0026` — auth.autorizacion_inicio
- `D-0031` — auth.direccion_frecuente
- `D-0034` — auth.perfil_general
- `D-0039` — auth.refresh_token
- `D-0044` — auth.reset_token
- `D-0048` — auth.taxista_favorito
- `D-0052` — auth.tipo_usuario
- `D-0057` — auth.turno_empleado
- `D-0069` — auth.usuario_empresa
- `D-0074` — auth.usuario_rol
- `D-0078` — corporate.cuenta_corriente
- `D-0086` — corporate.factura_corporativa
- `D-0092` — corporate.movimiento_cuenta
- `D-0097` — corporate.pago_corporativo
- `D-0100` — fleet.categoria_gasto
- `D-0113` — fleet.contrato_qr
- `D-0118` — fleet.contrato_vehiculo
- `D-0135` — fleet.documento_propietario
- `D-0139` — fleet.documento_vehiculo
- `D-0142` — fleet.documentos_chofer
- `D-0146` — fleet.foto_vehiculo
- `D-0148` — fleet.gasto_turno
- `D-0155` — fleet.gasto_vehiculo
- `D-0164` — fleet.liquidacion
- `D-0175` — fleet.liquidacion_ajuste
- `D-0180` — fleet.liquidacion_detalle
- `D-0183` — fleet.liquidacion_estado_historial
- `D-0189` — fleet.mantenimiento_vehiculo
- `D-0193` — fleet.marca
- `D-0198` — fleet.modelo
- `D-0203` — fleet.neumatico_historial_posicion
- `D-0210` — fleet.neumatico_imagen
- `D-0217` — fleet.neumatico_medicion
- `D-0223` — fleet.neumatico_operacion
- `D-0229` — fleet.neumatico_operacion_detalle
- `D-0233` — fleet.neumatico_sugerencia
- `D-0242` — fleet.neumatico_vehiculo
- `D-0251` — fleet.notificacion_vencimiento
- `D-0257` — fleet.propietario_vehiculo
- `D-0276` — geo.ciudad
- `D-0279` — geo.pais
- `D-0281` — geo.provincia
- `D-0284` — notification.notificacion
- `D-0287` — payment.billetera
- `D-0295` — payment.configuracion_tarifa
- `D-0298` — payment.configuracion_tarifa_vehiculo
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

- `D-0028` — auth.autorizacion_inicio
- `D-0037` — auth.perfil_general
- `D-0046` — auth.reset_token
- `D-0054` — auth.tipo_usuario
- `D-0081` — corporate.cuenta_corriente
- `D-0088` — corporate.factura_corporativa
- `D-0103` — fleet.categoria_gasto
- `D-0115` — fleet.contrato_qr
- `D-0152` — fleet.gasto_turno
- `D-0195` — fleet.marca
- `D-0290` — payment.billetera
- `D-0308` — payment.metodo_pago
- `D-0325` — public.comercio
- `D-0339` — tenant.configuracion_tenant
- `D-0353` — tenant.factura

### indice_falta (76)

| Tabla | Cantidad |
|---|---|
| auth.autorizacion_inicio | 2 |
| auth.refresh_token | 2 |
| auth.tipo_usuario | 2 |
| auth.usuario_rol | 2 |
| corporate.cuenta_corriente | 2 |
| corporate.factura_corporativa | 2 |
| fleet.categoria_gasto | 2 |
| fleet.contrato_qr | 2 |
| fleet.documento_propietario | 2 |
| fleet.marca | 2 |
| fleet.modelo | 2 |
| fleet.notificacion_vencimiento | 2 |
| payment.billetera | 2 |
| payment.configuracion_tarifa_vehiculo | 2 |
| audit.alerta_desvio | 1 |
| audit.log_acciones | 1 |
| audit.log_gps | 1 |
| auth.auditoria_email | 1 |
| auth.direccion_frecuente | 1 |
| auth.perfil_general | 1 |
| auth.reset_token | 1 |
| auth.taxista_favorito | 1 |
| auth.turno_empleado | 1 |
| auth.usuario_empresa | 1 |
| corporate.movimiento_cuenta | 1 |
| corporate.pago_corporativo | 1 |
| fleet.contrato_vehiculo | 1 |
| fleet.documento_vehiculo | 1 |
| fleet.documentos_chofer | 1 |
| fleet.foto_vehiculo | 1 |
| fleet.gasto_turno | 1 |
| fleet.gasto_vehiculo | 1 |
| fleet.liquidacion | 1 |
| fleet.liquidacion_ajuste | 1 |
| fleet.liquidacion_detalle | 1 |
| fleet.liquidacion_estado_historial | 1 |
| fleet.mantenimiento_vehiculo | 1 |
| fleet.neumatico_historial_posicion | 1 |
| fleet.neumatico_imagen | 1 |
| fleet.neumatico_medicion | 1 |
| fleet.neumatico_operacion | 1 |
| fleet.neumatico_operacion_detalle | 1 |
| fleet.neumatico_sugerencia | 1 |
| fleet.neumatico_vehiculo | 1 |
| fleet.propietario_vehiculo | 1 |
| geo.ciudad | 1 |
| geo.pais | 1 |
| geo.provincia | 1 |
| notification.notificacion | 1 |
| payment.configuracion_tarifa | 1 |
| payment.factura_empresa | 1 |
| payment.metodo_pago | 1 |
| payment.pago_empresa | 1 |
| public.comercio | 1 |
| public.escaneo_qr | 1 |
| tenant.configuracion_tenant | 1 |
| tenant.empresa | 1 |
| tenant.factura | 1 |
| trip.foto_viaje | 1 |
| trip.objeto_olvidado | 1 |
| trip.panico | 1 |
| trip.tipo_vehiculo | 1 |

### indice_sobra (1)

- `D-0382` — trip.panico

### nullable_desalineado (4)

- `D-0014` — viaje_id
- `D-0099` — updated_at
- `D-0154` — vehiculo_id
- `D-0188` — vehiculo_id

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

- `D-0085` — estado
- `D-0091` — tipo_movimiento
- `D-0096` — estado
- `D-0249` — entidad_tipo
- `D-0250` — nivel
- `D-0293` — descripcion
- `D-0294` — modo_calculo
- `D-0327` — resultado
- `D-0328` — tipo_qr
- `D-0376` — resuelto_en
- `D-0377` — usuario_id
- `D-0383` — distancia_por_ficha
- `D-0384` — precio_por_ficha
- `D-0385` — precio_por_minuto_espera

### constraint_nombre_desalineado (97)

- `D-0016` — audit.alerta_desvio
- `D-0021` — audit.log_gps
- `D-0022` — audit.log_gps
- `D-0032` — auth.direccion_frecuente
- `D-0035` — auth.perfil_general
- `D-0036` — auth.perfil_general
- `D-0040` — auth.refresh_token
- `D-0045` — auth.reset_token
- `D-0049` — auth.taxista_favorito
- `D-0050` — auth.taxista_favorito
- `D-0058` — auth.turno_empleado
- `D-0059` — auth.turno_empleado
- `D-0070` — auth.usuario_empresa
- `D-0071` — auth.usuario_empresa
- `D-0101` — fleet.categoria_gasto
- `D-0119` — fleet.contrato_vehiculo
- `D-0120` — fleet.contrato_vehiculo
- `D-0121` — fleet.contrato_vehiculo
- `D-0122` — fleet.contrato_vehiculo
- `D-0140` — fleet.documento_vehiculo
- `D-0143` — fleet.documentos_chofer
- `D-0149` — fleet.gasto_turno
- `D-0150` — fleet.gasto_turno
- `D-0156` — fleet.gasto_vehiculo
- `D-0157` — fleet.gasto_vehiculo
- `D-0158` — fleet.gasto_vehiculo
- `D-0165` — fleet.liquidacion
- `D-0166` — fleet.liquidacion
- `D-0167` — fleet.liquidacion
- `D-0168` — fleet.liquidacion
- `D-0169` — fleet.liquidacion
- `D-0170` — fleet.liquidacion
- `D-0171` — fleet.liquidacion
- `D-0172` — fleet.liquidacion
- `D-0173` — fleet.liquidacion
- `D-0176` — fleet.liquidacion_ajuste
- `D-0177` — fleet.liquidacion_ajuste
- `D-0178` — fleet.liquidacion_ajuste
- `D-0181` — fleet.liquidacion_detalle
- `D-0184` — fleet.liquidacion_estado_historial
- `D-0185` — fleet.liquidacion_estado_historial
- `D-0186` — fleet.liquidacion_estado_historial
- `D-0190` — fleet.mantenimiento_vehiculo
- `D-0191` — fleet.mantenimiento_vehiculo
- `D-0199` — fleet.modelo
- `D-0204` — fleet.neumatico_historial_posicion
- `D-0205` — fleet.neumatico_historial_posicion
- `D-0206` — fleet.neumatico_historial_posicion
- `D-0207` — fleet.neumatico_historial_posicion
- `D-0211` — fleet.neumatico_imagen
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
