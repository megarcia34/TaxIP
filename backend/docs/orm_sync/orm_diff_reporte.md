# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-05T13:06:31.843653+00:00

## Resumen ejecutivo

- **467 diferencias** en total.
- **Tier 1**: 80 items.
- **Tier 2**: 275 items.
- **Tier 3**: 111 items.
- **Tier 4**: 1 items.
- **2 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| indice_falta | 148 |
| constraint_nombre_desalineado | 124 |
| constraint_desalineada | 72 |
| constraint_falta | 61 |
| comment_desalineado | 20 |
| constraint_sobra | 17 |
| tabla_falta | 10 |
| nullable_desalineado | 4 |
| indice_nombre_desalineado | 4 |
| indice_sobra | 3 |
| schema_falta | 2 |
| tabla_sobra | 1 |
| columna_falta | 1 |

---

## Tier 1 — 80 items

### comment_desalineado (6)

- `D-0181` — declarado_por
- `D-0182` — transaccion_id
- `D-0317` — snapshot_dia_contractual
- `D-0428` — latitud
- `D-0429` — longitud
- `D-0450` — solicitado_en

### constraint_desalineada (10)

- `D-0062` — auth.usuario
- `D-0107` — fleet.chofer_vehiculo
- `D-0183` — fleet.ingreso_turno
- `D-0318` — fleet.turno_chofer
- `D-0327` — fleet.vehiculo
- `D-0379` — payment.transaccion
- `D-0403` — tenant.control_base
- `D-0417` — trip.calificacion
- `D-0430` — trip.historial_estado_viaje
- `D-0451` — trip.viaje_solicitado

### constraint_falta (10)

- `D-0066` — auth.usuario
- `D-0111` — fleet.chofer_vehiculo
- `D-0329` — fleet.vehiculo
- `D-0331` — fleet.vehiculo
- `D-0332` — fleet.vehiculo
- `D-0422` — trip.calificacion
- `D-0452` — trip.viaje_solicitado
- `D-0453` — trip.viaje_solicitado
- `D-0454` — trip.viaje_solicitado
- `D-0455` — trip.viaje_solicitado

### constraint_nombre_desalineado (27)

- `D-0063` — auth.usuario
- `D-0064` — auth.usuario
- `D-0065` — auth.usuario
- `D-0108` — fleet.chofer_vehiculo
- `D-0109` — fleet.chofer_vehiculo
- `D-0110` — fleet.chofer_vehiculo
- `D-0319` — fleet.turno_chofer
- `D-0320` — fleet.turno_chofer
- `D-0321` — fleet.turno_chofer
- `D-0328` — fleet.vehiculo
- `D-0380` — payment.transaccion
- `D-0381` — payment.transaccion
- `D-0382` — payment.transaccion
- `D-0404` — tenant.control_base
- `D-0405` — tenant.control_base
- `D-0418` — trip.calificacion
- `D-0419` — trip.calificacion
- `D-0420` — trip.calificacion
- `D-0431` — trip.historial_estado_viaje
- `D-0456` — trip.viaje_solicitado
- `D-0457` — trip.viaje_solicitado
- `D-0458` — trip.viaje_solicitado
- `D-0459` — trip.viaje_solicitado
- `D-0460` — trip.viaje_solicitado
- `D-0461` — trip.viaje_solicitado
- `D-0462` — trip.viaje_solicitado
- `D-0463` — trip.viaje_solicitado

### constraint_sobra (2)

- `D-0330` — fleet.vehiculo
- `D-0421` — trip.calificacion

### indice_falta (17)

- `D-0067` — auth.usuario
- `D-0112` — fleet.chofer_vehiculo
- `D-0184` — fleet.ingreso_turno
- `D-0322` — fleet.turno_chofer
- `D-0323` — fleet.turno_chofer
- `D-0324` — fleet.turno_chofer
- `D-0325` — fleet.turno_chofer
- `D-0326` — fleet.turno_chofer
- `D-0333` — fleet.vehiculo
- `D-0334` — fleet.vehiculo
- `D-0335` — fleet.vehiculo
- `D-0336` — fleet.vehiculo
- `D-0383` — payment.transaccion
- `D-0406` — tenant.control_base
- `D-0423` — trip.calificacion
- `D-0432` — trip.historial_estado_viaje
- `D-0464` — trip.viaje_solicitado

### indice_nombre_desalineado (4)

- `D-0068` — auth.usuario
- `D-0337` — fleet.vehiculo
- `D-0466` — trip.viaje_solicitado
- `D-0467` — trip.viaje_solicitado

### indice_sobra (2)

- `D-0113` — fleet.chofer_vehiculo
- `D-0465` — trip.viaje_solicitado

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

---

## Tier 2 — 275 items

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
- `D-0121` — fleet.contrato_vehiculo
- `D-0144` — fleet.documento_propietario
- `D-0149` — fleet.documento_vehiculo
- `D-0154` — fleet.documentos_chofer
- `D-0161` — fleet.foto_vehiculo
- `D-0165` — fleet.gasto_turno
- `D-0174` — fleet.gasto_vehiculo
- `D-0185` — fleet.liquidacion
- `D-0196` — fleet.liquidacion_ajuste
- `D-0201` — fleet.liquidacion_detalle
- `D-0204` — fleet.liquidacion_estado_historial
- `D-0210` — fleet.mantenimiento_vehiculo
- `D-0214` — fleet.marca
- `D-0219` — fleet.modelo
- `D-0224` — fleet.neumatico_historial_posicion
- `D-0236` — fleet.neumatico_imagen
- `D-0247` — fleet.neumatico_medicion
- `D-0256` — fleet.neumatico_operacion
- `D-0266` — fleet.neumatico_operacion_detalle
- `D-0272` — fleet.neumatico_sugerencia
- `D-0285` — fleet.neumatico_vehiculo
- `D-0299` — fleet.notificacion_vencimiento
- `D-0310` — fleet.propietario_vehiculo
- `D-0338` — geo.ciudad
- `D-0341` — geo.pais
- `D-0343` — geo.provincia
- `D-0346` — notification.notificacion
- `D-0349` — payment.billetera
- `D-0357` — payment.configuracion_tarifa
- `D-0360` — payment.configuracion_tarifa_vehiculo
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
- `D-0169` — fleet.gasto_turno
- `D-0216` — fleet.marca
- `D-0352` — payment.billetera
- `D-0370` — payment.metodo_pago
- `D-0387` — public.comercio
- `D-0401` — tenant.configuracion_tenant
- `D-0415` — tenant.factura

### indice_falta (131)

| Tabla | Cantidad |
|---|---|
| fleet.contrato_vehiculo | 7 |
| fleet.notificacion_vencimiento | 7 |
| fleet.neumatico_historial_posicion | 6 |
| fleet.neumatico_vehiculo | 6 |
| fleet.neumatico_imagen | 5 |
| fleet.neumatico_operacion | 5 |
| fleet.neumatico_sugerencia | 5 |
| fleet.contrato_qr | 4 |
| fleet.documentos_chofer | 4 |
| fleet.neumatico_medicion | 4 |
| fleet.categoria_gasto | 3 |
| fleet.documento_propietario | 3 |
| fleet.documento_vehiculo | 3 |
| fleet.foto_vehiculo | 3 |
| fleet.gasto_turno | 3 |
| fleet.gasto_vehiculo | 3 |
| fleet.neumatico_operacion_detalle | 3 |
| fleet.propietario_vehiculo | 3 |
| auth.autorizacion_inicio | 2 |
| auth.refresh_token | 2 |
| auth.tipo_usuario | 2 |
| auth.usuario_rol | 2 |
| corporate.cuenta_corriente | 2 |
| corporate.factura_corporativa | 2 |
| fleet.marca | 2 |
| fleet.modelo | 2 |
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
| fleet.liquidacion | 1 |
| fleet.liquidacion_ajuste | 1 |
| fleet.liquidacion_detalle | 1 |
| fleet.liquidacion_estado_historial | 1 |
| fleet.mantenimiento_vehiculo | 1 |
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

- `D-0444` — trip.panico

### nullable_desalineado (4)

- `D-0014` — viaje_id
- `D-0099` — updated_at
- `D-0173` — vehiculo_id
- `D-0209` — vehiculo_id

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
- `D-0297` — entidad_tipo
- `D-0298` — nivel
- `D-0355` — descripcion
- `D-0356` — modo_calculo
- `D-0389` — resultado
- `D-0390` — tipo_qr
- `D-0438` — resuelto_en
- `D-0439` — usuario_id
- `D-0445` — distancia_por_ficha
- `D-0446` — precio_por_ficha
- `D-0447` — precio_por_minuto_espera

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
- `D-0122` — fleet.contrato_vehiculo
- `D-0123` — fleet.contrato_vehiculo
- `D-0124` — fleet.contrato_vehiculo
- `D-0125` — fleet.contrato_vehiculo
- `D-0150` — fleet.documento_vehiculo
- `D-0155` — fleet.documentos_chofer
- `D-0166` — fleet.gasto_turno
- `D-0167` — fleet.gasto_turno
- `D-0175` — fleet.gasto_vehiculo
- `D-0176` — fleet.gasto_vehiculo
- `D-0177` — fleet.gasto_vehiculo
- `D-0186` — fleet.liquidacion
- `D-0187` — fleet.liquidacion
- `D-0188` — fleet.liquidacion
- `D-0189` — fleet.liquidacion
- `D-0190` — fleet.liquidacion
- `D-0191` — fleet.liquidacion
- `D-0192` — fleet.liquidacion
- `D-0193` — fleet.liquidacion
- `D-0194` — fleet.liquidacion
- `D-0197` — fleet.liquidacion_ajuste
- `D-0198` — fleet.liquidacion_ajuste
- `D-0199` — fleet.liquidacion_ajuste
- `D-0202` — fleet.liquidacion_detalle
- `D-0205` — fleet.liquidacion_estado_historial
- `D-0206` — fleet.liquidacion_estado_historial
- `D-0207` — fleet.liquidacion_estado_historial
- `D-0211` — fleet.mantenimiento_vehiculo
- `D-0212` — fleet.mantenimiento_vehiculo
- `D-0220` — fleet.modelo
- `D-0225` — fleet.neumatico_historial_posicion
- `D-0226` — fleet.neumatico_historial_posicion
- `D-0227` — fleet.neumatico_historial_posicion
- `D-0228` — fleet.neumatico_historial_posicion
- `D-0237` — fleet.neumatico_imagen
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
