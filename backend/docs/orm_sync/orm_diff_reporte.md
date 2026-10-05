# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-05T21:42:02.273464+00:00

## Resumen ejecutivo

- **425 diferencias** en total.
- **Tier 1**: 79 items.
- **Tier 2**: 234 items.
- **Tier 3**: 111 items.
- **Tier 4**: 1 items.
- **2 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| constraint_nombre_desalineado | 124 |
| indice_falta | 107 |
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

## Tier 1 — 79 items

### comment_desalineado (6)

- `D-0173` — declarado_por
- `D-0174` — transaccion_id
- `D-0276` — snapshot_dia_contractual
- `D-0387` — latitud
- `D-0388` — longitud
- `D-0409` — solicitado_en

### constraint_desalineada (10)

- `D-0062` — auth.usuario
- `D-0107` — fleet.chofer_vehiculo
- `D-0175` — fleet.ingreso_turno
- `D-0277` — fleet.turno_chofer
- `D-0286` — fleet.vehiculo
- `D-0338` — payment.transaccion
- `D-0362` — tenant.control_base
- `D-0376` — trip.calificacion
- `D-0389` — trip.historial_estado_viaje
- `D-0410` — trip.viaje_solicitado

### constraint_falta (10)

- `D-0066` — auth.usuario
- `D-0111` — fleet.chofer_vehiculo
- `D-0288` — fleet.vehiculo
- `D-0290` — fleet.vehiculo
- `D-0291` — fleet.vehiculo
- `D-0381` — trip.calificacion
- `D-0411` — trip.viaje_solicitado
- `D-0412` — trip.viaje_solicitado
- `D-0413` — trip.viaje_solicitado
- `D-0414` — trip.viaje_solicitado

### constraint_nombre_desalineado (27)

- `D-0063` — auth.usuario
- `D-0064` — auth.usuario
- `D-0065` — auth.usuario
- `D-0108` — fleet.chofer_vehiculo
- `D-0109` — fleet.chofer_vehiculo
- `D-0110` — fleet.chofer_vehiculo
- `D-0278` — fleet.turno_chofer
- `D-0279` — fleet.turno_chofer
- `D-0280` — fleet.turno_chofer
- `D-0287` — fleet.vehiculo
- `D-0339` — payment.transaccion
- `D-0340` — payment.transaccion
- `D-0341` — payment.transaccion
- `D-0363` — tenant.control_base
- `D-0364` — tenant.control_base
- `D-0377` — trip.calificacion
- `D-0378` — trip.calificacion
- `D-0379` — trip.calificacion
- `D-0390` — trip.historial_estado_viaje
- `D-0415` — trip.viaje_solicitado
- `D-0416` — trip.viaje_solicitado
- `D-0417` — trip.viaje_solicitado
- `D-0418` — trip.viaje_solicitado
- `D-0419` — trip.viaje_solicitado
- `D-0420` — trip.viaje_solicitado
- `D-0421` — trip.viaje_solicitado
- `D-0422` — trip.viaje_solicitado

### constraint_sobra (2)

- `D-0289` — fleet.vehiculo
- `D-0380` — trip.calificacion

### indice_falta (17)

- `D-0067` — auth.usuario
- `D-0112` — fleet.chofer_vehiculo
- `D-0176` — fleet.ingreso_turno
- `D-0281` — fleet.turno_chofer
- `D-0282` — fleet.turno_chofer
- `D-0283` — fleet.turno_chofer
- `D-0284` — fleet.turno_chofer
- `D-0285` — fleet.turno_chofer
- `D-0292` — fleet.vehiculo
- `D-0293` — fleet.vehiculo
- `D-0294` — fleet.vehiculo
- `D-0295` — fleet.vehiculo
- `D-0342` — payment.transaccion
- `D-0365` — tenant.control_base
- `D-0382` — trip.calificacion
- `D-0391` — trip.historial_estado_viaje
- `D-0423` — trip.viaje_solicitado

### indice_nombre_desalineado (3)

- `D-0068` — auth.usuario
- `D-0296` — fleet.vehiculo
- `D-0425` — trip.viaje_solicitado

### indice_sobra (2)

- `D-0113` — fleet.chofer_vehiculo
- `D-0424` — trip.viaje_solicitado

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

---

## Tier 2 — 234 items

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
- `D-0114` — fleet.contrato_qr
- `D-0119` — fleet.contrato_vehiculo
- `D-0136` — fleet.documento_propietario
- `D-0141` — fleet.documento_vehiculo
- `D-0146` — fleet.documentos_chofer
- `D-0153` — fleet.foto_vehiculo
- `D-0157` — fleet.gasto_turno
- `D-0166` — fleet.gasto_vehiculo
- `D-0177` — fleet.liquidacion
- `D-0188` — fleet.liquidacion_ajuste
- `D-0193` — fleet.liquidacion_detalle
- `D-0196` — fleet.liquidacion_estado_historial
- `D-0202` — fleet.mantenimiento_vehiculo
- `D-0206` — fleet.marca
- `D-0211` — fleet.modelo
- `D-0216` — fleet.neumatico_historial_posicion
- `D-0223` — fleet.neumatico_imagen
- `D-0230` — fleet.neumatico_medicion
- `D-0236` — fleet.neumatico_operacion
- `D-0242` — fleet.neumatico_operacion_detalle
- `D-0246` — fleet.neumatico_sugerencia
- `D-0255` — fleet.neumatico_vehiculo
- `D-0265` — fleet.notificacion_vencimiento
- `D-0271` — fleet.propietario_vehiculo
- `D-0297` — geo.ciudad
- `D-0300` — geo.pais
- `D-0302` — geo.provincia
- `D-0305` — notification.notificacion
- `D-0308` — payment.billetera
- `D-0316` — payment.configuracion_tarifa
- `D-0319` — payment.configuracion_tarifa_vehiculo
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
- `D-0116` — fleet.contrato_qr
- `D-0161` — fleet.gasto_turno
- `D-0208` — fleet.marca
- `D-0311` — payment.billetera
- `D-0329` — payment.metodo_pago
- `D-0346` — public.comercio
- `D-0360` — tenant.configuracion_tenant
- `D-0374` — tenant.factura

### indice_falta (90)

| Tabla | Cantidad |
|---|---|
| fleet.documentos_chofer | 4 |
| fleet.categoria_gasto | 3 |
| fleet.documento_propietario | 3 |
| fleet.documento_vehiculo | 3 |
| fleet.foto_vehiculo | 3 |
| fleet.gasto_turno | 3 |
| fleet.gasto_vehiculo | 3 |
| auth.autorizacion_inicio | 2 |
| auth.refresh_token | 2 |
| auth.tipo_usuario | 2 |
| auth.usuario_rol | 2 |
| corporate.cuenta_corriente | 2 |
| corporate.factura_corporativa | 2 |
| fleet.contrato_qr | 2 |
| fleet.marca | 2 |
| fleet.modelo | 2 |
| fleet.neumatico_vehiculo | 2 |
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

- `D-0403` — trip.panico

### nullable_desalineado (4)

- `D-0014` — viaje_id
- `D-0099` — updated_at
- `D-0165` — vehiculo_id
- `D-0201` — vehiculo_id

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
- `D-0263` — entidad_tipo
- `D-0264` — nivel
- `D-0314` — descripcion
- `D-0315` — modo_calculo
- `D-0348` — resultado
- `D-0349` — tipo_qr
- `D-0397` — resuelto_en
- `D-0398` — usuario_id
- `D-0404` — distancia_por_ficha
- `D-0405` — precio_por_ficha
- `D-0406` — precio_por_minuto_espera

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
- `D-0120` — fleet.contrato_vehiculo
- `D-0121` — fleet.contrato_vehiculo
- `D-0122` — fleet.contrato_vehiculo
- `D-0123` — fleet.contrato_vehiculo
- `D-0142` — fleet.documento_vehiculo
- `D-0147` — fleet.documentos_chofer
- `D-0158` — fleet.gasto_turno
- `D-0159` — fleet.gasto_turno
- `D-0167` — fleet.gasto_vehiculo
- `D-0168` — fleet.gasto_vehiculo
- `D-0169` — fleet.gasto_vehiculo
- `D-0178` — fleet.liquidacion
- `D-0179` — fleet.liquidacion
- `D-0180` — fleet.liquidacion
- `D-0181` — fleet.liquidacion
- `D-0182` — fleet.liquidacion
- `D-0183` — fleet.liquidacion
- `D-0184` — fleet.liquidacion
- `D-0185` — fleet.liquidacion
- `D-0186` — fleet.liquidacion
- `D-0189` — fleet.liquidacion_ajuste
- `D-0190` — fleet.liquidacion_ajuste
- `D-0191` — fleet.liquidacion_ajuste
- `D-0194` — fleet.liquidacion_detalle
- `D-0197` — fleet.liquidacion_estado_historial
- `D-0198` — fleet.liquidacion_estado_historial
- `D-0199` — fleet.liquidacion_estado_historial
- `D-0203` — fleet.mantenimiento_vehiculo
- `D-0204` — fleet.mantenimiento_vehiculo
- `D-0212` — fleet.modelo
- `D-0217` — fleet.neumatico_historial_posicion
- `D-0218` — fleet.neumatico_historial_posicion
- `D-0219` — fleet.neumatico_historial_posicion
- `D-0220` — fleet.neumatico_historial_posicion
- `D-0224` — fleet.neumatico_imagen
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
