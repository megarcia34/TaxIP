# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-04T22:40:09.758107+00:00

## Resumen ejecutivo

- **877 diferencias** en total.
- **Tier 1**: 139 items.
- **Tier 2**: 626 items.
- **Tier 3**: 111 items.
- **Tier 4**: 1 items.
- **2 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| constraint_falta | 427 |
| indice_falta | 180 |
| constraint_nombre_desalineado | 124 |
| constraint_desalineada | 72 |
| constraint_sobra | 25 |
| comment_desalineado | 20 |
| tabla_falta | 10 |
| tipo_desalineado | 5 |
| nullable_desalineado | 4 |
| indice_nombre_desalineado | 3 |
| indice_sobra | 3 |
| schema_falta | 2 |
| tabla_sobra | 1 |
| columna_falta | 1 |

---

## Tier 1 — 139 items

### comment_desalineado (6)

- `D-0347` — declarado_por
- `D-0348` — transaccion_id
- `D-0595` — snapshot_dia_contractual
- `D-0806` — latitud
- `D-0807` — longitud
- `D-0843` — solicitado_en

### constraint_desalineada (10)

- `D-0111` — auth.usuario
- `D-0224` — fleet.chofer_vehiculo
- `D-0349` — fleet.ingreso_turno
- `D-0596` — fleet.turno_chofer
- `D-0613` — fleet.vehiculo
- `D-0710` — payment.transaccion
- `D-0750` — tenant.control_base
- `D-0785` — trip.calificacion
- `D-0808` — trip.historial_estado_viaje
- `D-0844` — trip.viaje_solicitado

### constraint_falta (58)

| Tabla | Cantidad |
|---|---|
| trip.viaje_solicitado | 14 |
| fleet.ingreso_turno | 10 |
| fleet.turno_chofer | 8 |
| fleet.vehiculo | 8 |
| trip.calificacion | 6 |
| auth.usuario | 4 |
| fleet.chofer_vehiculo | 4 |
| tenant.control_base | 2 |
| payment.transaccion | 1 |
| trip.historial_estado_viaje | 1 |

### constraint_nombre_desalineado (27)

- `D-0112` — auth.usuario
- `D-0113` — auth.usuario
- `D-0114` — auth.usuario
- `D-0225` — fleet.chofer_vehiculo
- `D-0226` — fleet.chofer_vehiculo
- `D-0227` — fleet.chofer_vehiculo
- `D-0597` — fleet.turno_chofer
- `D-0598` — fleet.turno_chofer
- `D-0599` — fleet.turno_chofer
- `D-0614` — fleet.vehiculo
- `D-0711` — payment.transaccion
- `D-0712` — payment.transaccion
- `D-0713` — payment.transaccion
- `D-0751` — tenant.control_base
- `D-0752` — tenant.control_base
- `D-0786` — trip.calificacion
- `D-0787` — trip.calificacion
- `D-0788` — trip.calificacion
- `D-0809` — trip.historial_estado_viaje
- `D-0849` — trip.viaje_solicitado
- `D-0850` — trip.viaje_solicitado
- `D-0851` — trip.viaje_solicitado
- `D-0852` — trip.viaje_solicitado
- `D-0853` — trip.viaje_solicitado
- `D-0854` — trip.viaje_solicitado
- `D-0855` — trip.viaje_solicitado
- `D-0856` — trip.viaje_solicitado

### constraint_sobra (10)

- `D-0616` — fleet.vehiculo
- `D-0789` — trip.calificacion
- `D-0867` — trip.viaje_solicitado
- `D-0868` — trip.viaje_solicitado
- `D-0869` — trip.viaje_solicitado
- `D-0870` — trip.viaje_solicitado
- `D-0871` — trip.viaje_solicitado
- `D-0872` — trip.viaje_solicitado
- `D-0873` — trip.viaje_solicitado
- `D-0874` — trip.viaje_solicitado

### indice_falta (18)

- `D-0119` — auth.usuario
- `D-0232` — fleet.chofer_vehiculo
- `D-0360` — fleet.ingreso_turno
- `D-0608` — fleet.turno_chofer
- `D-0609` — fleet.turno_chofer
- `D-0610` — fleet.turno_chofer
- `D-0611` — fleet.turno_chofer
- `D-0612` — fleet.turno_chofer
- `D-0624` — fleet.vehiculo
- `D-0625` — fleet.vehiculo
- `D-0626` — fleet.vehiculo
- `D-0627` — fleet.vehiculo
- `D-0715` — payment.transaccion
- `D-0755` — tenant.control_base
- `D-0756` — tenant.control_base
- `D-0796` — trip.calificacion
- `D-0811` — trip.historial_estado_viaje
- `D-0875` — trip.viaje_solicitado

### indice_nombre_desalineado (3)

- `D-0120` — auth.usuario
- `D-0628` — fleet.vehiculo
- `D-0877` — trip.viaje_solicitado

### indice_sobra (2)

- `D-0233` — fleet.chofer_vehiculo
- `D-0876` — trip.viaje_solicitado

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

### tipo_desalineado (3)

- `D-0223` — ubicacion
- `D-0841` — destino
- `D-0842` — origen

---

## Tier 2 — 626 items

### columna_falta (1)

- `D-0128` — control_base_id

### constraint_desalineada (62)

- `D-0015` — audit.alerta_desvio
- `D-0025` — audit.log_acciones
- `D-0034` — audit.log_gps
- `D-0044` — auth.auditoria_email
- `D-0048` — auth.autorizacion_inicio
- `D-0059` — auth.direccion_frecuente
- `D-0064` — auth.perfil_general
- `D-0070` — auth.refresh_token
- `D-0079` — auth.reset_token
- `D-0087` — auth.taxista_favorito
- `D-0094` — auth.tipo_usuario
- `D-0101` — auth.turno_empleado
- `D-0121` — auth.usuario_empresa
- `D-0129` — auth.usuario_rol
- `D-0140` — corporate.cuenta_corriente
- `D-0157` — corporate.factura_corporativa
- `D-0179` — corporate.movimiento_cuenta
- `D-0194` — corporate.pago_corporativo
- `D-0207` — fleet.categoria_gasto
- `D-0234` — fleet.contrato_qr
- `D-0244` — fleet.contrato_vehiculo
- `D-0281` — fleet.documento_propietario
- `D-0290` — fleet.documento_vehiculo
- `D-0301` — fleet.documentos_chofer
- `D-0314` — fleet.foto_vehiculo
- `D-0322` — fleet.gasto_turno
- `D-0336` — fleet.gasto_vehiculo
- `D-0361` — fleet.liquidacion
- `D-0397` — fleet.liquidacion_ajuste
- `D-0408` — fleet.liquidacion_detalle
- `D-0417` — fleet.liquidacion_estado_historial
- `D-0428` — fleet.mantenimiento_vehiculo
- `D-0435` — fleet.marca
- `D-0442` — fleet.modelo
- `D-0450` — fleet.neumatico_historial_posicion
- `D-0469` — fleet.neumatico_imagen
- `D-0485` — fleet.neumatico_medicion
- `D-0499` — fleet.neumatico_operacion
- `D-0515` — fleet.neumatico_operacion_detalle
- `D-0524` — fleet.neumatico_sugerencia
- `D-0543` — fleet.neumatico_vehiculo
- `D-0564` — fleet.notificacion_vencimiento
- `D-0583` — fleet.propietario_vehiculo
- `D-0629` — geo.ciudad
- `D-0635` — geo.pais
- `D-0639` — geo.provincia
- `D-0644` — notification.notificacion
- `D-0651` — payment.billetera
- `D-0661` — payment.configuracion_tarifa
- `D-0672` — payment.configuracion_tarifa_vehiculo
- ... y 12 mas (ver JSON)

### constraint_falta (369)

| Tabla | Cantidad |
|---|---|
| fleet.contrato_vehiculo | 25 |
| fleet.liquidacion | 25 |
| corporate.factura_corporativa | 14 |
| corporate.cuenta_corriente | 12 |
| tenant.factura | 12 |
| fleet.notificacion_vencimiento | 11 |
| corporate.movimiento_cuenta | 10 |
| fleet.categoria_gasto | 10 |
| fleet.neumatico_vehiculo | 10 |
| fleet.neumatico_sugerencia | 9 |
| auth.usuario_rol | 8 |
| corporate.pago_corporativo | 8 |
| fleet.neumatico_historial_posicion | 8 |
| payment.configuracion_tarifa | 8 |
| public.comercio | 8 |
| auth.autorizacion_inicio | 7 |
| fleet.documentos_chofer | 7 |
| fleet.neumatico_operacion | 7 |
| payment.configuracion_tarifa_vehiculo | 7 |
| auth.turno_empleado | 6 |
| fleet.documento_vehiculo | 6 |
| fleet.liquidacion_ajuste | 6 |
| fleet.liquidacion_detalle | 6 |
| fleet.neumatico_imagen | 6 |
| fleet.neumatico_medicion | 6 |
| fleet.propietario_vehiculo | 6 |
| payment.pago_empresa | 6 |
| audit.alerta_desvio | 5 |
| auth.refresh_token | 5 |
| fleet.documento_propietario | 5 |
| fleet.gasto_turno | 5 |
| fleet.liquidacion_estado_historial | 5 |
| trip.objeto_olvidado | 5 |
| trip.tipo_vehiculo | 5 |
| audit.log_gps | 4 |
| auth.reset_token | 4 |
| fleet.contrato_qr | 4 |
| fleet.foto_vehiculo | 4 |
| fleet.gasto_vehiculo | 4 |
| fleet.modelo | 4 |
| notification.notificacion | 4 |
| trip.foto_viaje | 4 |
| audit.log_acciones | 3 |
| auth.taxista_favorito | 3 |
| auth.tipo_usuario | 3 |
| auth.usuario_empresa | 3 |
| fleet.mantenimiento_vehiculo | 3 |
| fleet.marca | 3 |
| fleet.neumatico_operacion_detalle | 3 |
| payment.billetera | 3 |
| payment.factura_empresa | 3 |
| public.escaneo_qr | 3 |
| tenant.empresa | 3 |
| auth.auditoria_email | 2 |
| auth.direccion_frecuente | 2 |
| geo.ciudad | 2 |
| geo.pais | 2 |
| geo.provincia | 2 |
| payment.metodo_pago | 2 |
| auth.perfil_general | 1 |
| tenant.configuracion_tenant | 1 |
| trip.panico | 1 |

### constraint_sobra (15)

- `D-0050` — auth.autorizacion_inicio
- `D-0067` — auth.perfil_general
- `D-0081` — auth.reset_token
- `D-0096` — auth.tipo_usuario
- `D-0143` — corporate.cuenta_corriente
- `D-0159` — corporate.factura_corporativa
- `D-0210` — fleet.categoria_gasto
- `D-0236` — fleet.contrato_qr
- `D-0330` — fleet.gasto_turno
- `D-0437` — fleet.marca
- `D-0654` — payment.billetera
- `D-0691` — payment.metodo_pago
- `D-0719` — public.comercio
- `D-0747` — tenant.configuracion_tenant
- `D-0768` — tenant.factura

### indice_falta (162)

| Tabla | Cantidad |
|---|---|
| fleet.contrato_vehiculo | 7 |
| fleet.notificacion_vencimiento | 7 |
| fleet.neumatico_historial_posicion | 6 |
| fleet.neumatico_vehiculo | 6 |
| public.escaneo_qr | 6 |
| audit.log_acciones | 5 |
| corporate.factura_corporativa | 5 |
| fleet.neumatico_imagen | 5 |
| fleet.neumatico_operacion | 5 |
| fleet.neumatico_sugerencia | 5 |
| payment.pago_empresa | 5 |
| tenant.factura | 5 |
| fleet.contrato_qr | 4 |
| fleet.documentos_chofer | 4 |
| fleet.neumatico_medicion | 4 |
| audit.alerta_desvio | 3 |
| audit.log_gps | 3 |
| corporate.movimiento_cuenta | 3 |
| corporate.pago_corporativo | 3 |
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
| fleet.marca | 2 |
| fleet.modelo | 2 |
| geo.ciudad | 2 |
| payment.billetera | 2 |
| payment.configuracion_tarifa_vehiculo | 2 |
| public.comercio | 2 |
| trip.foto_viaje | 2 |
| auth.auditoria_email | 1 |
| auth.direccion_frecuente | 1 |
| auth.perfil_general | 1 |
| auth.reset_token | 1 |
| auth.taxista_favorito | 1 |
| auth.turno_empleado | 1 |
| auth.usuario_empresa | 1 |
| fleet.liquidacion | 1 |
| fleet.liquidacion_ajuste | 1 |
| fleet.liquidacion_detalle | 1 |
| fleet.liquidacion_estado_historial | 1 |
| fleet.mantenimiento_vehiculo | 1 |
| geo.pais | 1 |
| geo.provincia | 1 |
| notification.notificacion | 1 |
| payment.configuracion_tarifa | 1 |
| payment.factura_empresa | 1 |
| payment.metodo_pago | 1 |
| tenant.configuracion_tenant | 1 |
| tenant.empresa | 1 |
| trip.objeto_olvidado | 1 |
| trip.panico | 1 |
| trip.tipo_vehiculo | 1 |

### indice_sobra (1)

- `D-0830` — trip.panico

### nullable_desalineado (4)

- `D-0014` — viaje_id
- `D-0206` — updated_at
- `D-0335` — vehiculo_id
- `D-0427` — vehiculo_id

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

### tipo_desalineado (2)

- `D-0334` — km_registro
- `D-0823` — ubicacion

---

## Tier 3 — 111 items

### comment_desalineado (14)

- `D-0156` — estado
- `D-0178` — tipo_movimiento
- `D-0193` — estado
- `D-0562` — entidad_tipo
- `D-0563` — nivel
- `D-0659` — descripcion
- `D-0660` — modo_calculo
- `D-0729` — resultado
- `D-0730` — tipo_qr
- `D-0822` — resuelto_en
- `D-0824` — usuario_id
- `D-0831` — distancia_por_ficha
- `D-0832` — precio_por_ficha
- `D-0833` — precio_por_minuto_espera

### constraint_nombre_desalineado (97)

- `D-0016` — audit.alerta_desvio
- `D-0035` — audit.log_gps
- `D-0036` — audit.log_gps
- `D-0060` — auth.direccion_frecuente
- `D-0065` — auth.perfil_general
- `D-0066` — auth.perfil_general
- `D-0071` — auth.refresh_token
- `D-0080` — auth.reset_token
- `D-0088` — auth.taxista_favorito
- `D-0089` — auth.taxista_favorito
- `D-0102` — auth.turno_empleado
- `D-0103` — auth.turno_empleado
- `D-0122` — auth.usuario_empresa
- `D-0123` — auth.usuario_empresa
- `D-0208` — fleet.categoria_gasto
- `D-0245` — fleet.contrato_vehiculo
- `D-0246` — fleet.contrato_vehiculo
- `D-0247` — fleet.contrato_vehiculo
- `D-0248` — fleet.contrato_vehiculo
- `D-0291` — fleet.documento_vehiculo
- `D-0302` — fleet.documentos_chofer
- `D-0323` — fleet.gasto_turno
- `D-0324` — fleet.gasto_turno
- `D-0337` — fleet.gasto_vehiculo
- `D-0338` — fleet.gasto_vehiculo
- `D-0339` — fleet.gasto_vehiculo
- `D-0362` — fleet.liquidacion
- `D-0363` — fleet.liquidacion
- `D-0364` — fleet.liquidacion
- `D-0365` — fleet.liquidacion
- `D-0366` — fleet.liquidacion
- `D-0367` — fleet.liquidacion
- `D-0368` — fleet.liquidacion
- `D-0369` — fleet.liquidacion
- `D-0370` — fleet.liquidacion
- `D-0398` — fleet.liquidacion_ajuste
- `D-0399` — fleet.liquidacion_ajuste
- `D-0400` — fleet.liquidacion_ajuste
- `D-0409` — fleet.liquidacion_detalle
- `D-0418` — fleet.liquidacion_estado_historial
- `D-0419` — fleet.liquidacion_estado_historial
- `D-0420` — fleet.liquidacion_estado_historial
- `D-0429` — fleet.mantenimiento_vehiculo
- `D-0430` — fleet.mantenimiento_vehiculo
- `D-0443` — fleet.modelo
- `D-0451` — fleet.neumatico_historial_posicion
- `D-0452` — fleet.neumatico_historial_posicion
- `D-0453` — fleet.neumatico_historial_posicion
- `D-0454` — fleet.neumatico_historial_posicion
- `D-0470` — fleet.neumatico_imagen
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
