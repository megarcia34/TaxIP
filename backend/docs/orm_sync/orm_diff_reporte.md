# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-03T19:17:44.785580+00:00

## Resumen ejecutivo

- **1119 diferencias** en total.
- **Tier 1**: 176 items.
- **Tier 2**: 822 items.
- **Tier 3**: 120 items.
- **Tier 4**: 1 items.
- **24 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| constraint_falta | 428 |
| indice_falta | 192 |
| constraint_nombre_desalineado | 124 |
| nullable_desalineado | 114 |
| constraint_desalineada | 72 |
| tipo_desalineado | 65 |
| columna_falta | 47 |
| comment_desalineado | 29 |
| constraint_sobra | 24 |
| tabla_falta | 10 |
| indice_sobra | 6 |
| indice_nombre_desalineado | 5 |
| schema_falta | 2 |
| tabla_sobra | 1 |

---

## Tier 1 — 176 items

### comment_desalineado (7)

- `D-0435` — declarado_por
- `D-0436` — medio_pago
- `D-0437` — transaccion_id
- `D-0724` — snapshot_dia_contractual
- `D-1047` — latitud
- `D-1048` — longitud
- `D-1084` — solicitado_en

### constraint_desalineada (10)

- `D-0147` — auth.usuario
- `D-0298` — fleet.chofer_vehiculo
- `D-0438` — fleet.ingreso_turno
- `D-0725` — fleet.turno_chofer
- `D-0750` — fleet.vehiculo
- `D-0898` — payment.transaccion
- `D-0977` — tenant.control_base
- `D-1026` — trip.calificacion
- `D-1049` — trip.historial_estado_viaje
- `D-1085` — trip.viaje_solicitado

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

- `D-0148` — auth.usuario
- `D-0149` — auth.usuario
- `D-0150` — auth.usuario
- `D-0299` — fleet.chofer_vehiculo
- `D-0300` — fleet.chofer_vehiculo
- `D-0301` — fleet.chofer_vehiculo
- `D-0726` — fleet.turno_chofer
- `D-0727` — fleet.turno_chofer
- `D-0728` — fleet.turno_chofer
- `D-0751` — fleet.vehiculo
- `D-0899` — payment.transaccion
- `D-0900` — payment.transaccion
- `D-0901` — payment.transaccion
- `D-0978` — tenant.control_base
- `D-0979` — tenant.control_base
- `D-1027` — trip.calificacion
- `D-1028` — trip.calificacion
- `D-1029` — trip.calificacion
- `D-1050` — trip.historial_estado_viaje
- `D-1090` — trip.viaje_solicitado
- `D-1091` — trip.viaje_solicitado
- `D-1092` — trip.viaje_solicitado
- `D-1093` — trip.viaje_solicitado
- `D-1094` — trip.viaje_solicitado
- `D-1095` — trip.viaje_solicitado
- `D-1096` — trip.viaje_solicitado
- `D-1097` — trip.viaje_solicitado

### constraint_sobra (11)

- `D-0737` — fleet.turno_chofer
- `D-0753` — fleet.vehiculo
- `D-1030` — trip.calificacion
- `D-1108` — trip.viaje_solicitado
- `D-1109` — trip.viaje_solicitado
- `D-1110` — trip.viaje_solicitado
- `D-1111` — trip.viaje_solicitado
- `D-1112` — trip.viaje_solicitado
- `D-1113` — trip.viaje_solicitado
- `D-1114` — trip.viaje_solicitado
- `D-1115` — trip.viaje_solicitado

### indice_falta (18)

- `D-0155` — auth.usuario
- `D-0306` — fleet.chofer_vehiculo
- `D-0449` — fleet.ingreso_turno
- `D-0738` — fleet.turno_chofer
- `D-0739` — fleet.turno_chofer
- `D-0740` — fleet.turno_chofer
- `D-0741` — fleet.turno_chofer
- `D-0742` — fleet.turno_chofer
- `D-0761` — fleet.vehiculo
- `D-0762` — fleet.vehiculo
- `D-0763` — fleet.vehiculo
- `D-0764` — fleet.vehiculo
- `D-0903` — payment.transaccion
- `D-0982` — tenant.control_base
- `D-0983` — tenant.control_base
- `D-1037` — trip.calificacion
- `D-1052` — trip.historial_estado_viaje
- `D-1116` — trip.viaje_solicitado

### indice_nombre_desalineado (4)

- `D-0156` — auth.usuario
- `D-0765` — fleet.vehiculo
- `D-1118` — trip.viaje_solicitado
- `D-1119` — trip.viaje_solicitado

### indice_sobra (3)

- `D-0307` — fleet.chofer_vehiculo
- `D-0904` — payment.transaccion
- `D-1117` — trip.viaje_solicitado

### nullable_desalineado (25)

- `D-0142` — activo
- `D-0143` — created_at
- `D-0145` — tipo_usuario_id
- `D-0146` — updated_at
- `D-0288` — activo
- `D-0289` — calificacion_promedio
- `D-0290` — created_at
- `D-0291` — estado_laboral
- `D-0292` — estado_panico
- `D-0293` — total_calificaciones
- `D-0295` — ultima_conexion
- `D-0296` — updated_at
- `D-0297` — vehiculo_id
- `D-0743` — activo
- `D-0744` — capacidad
- `D-0745` — control_base_id
- `D-0746` — created_at
- `D-0747` — qr_activo
- `D-0748` — qr_uuid
- `D-0749` — updated_at
- `D-0894` — billetera_id
- `D-0895` — created_at
- `D-0969` — activo
- `D-0970` — created_at
- `D-0976` — updated_at

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

### tipo_desalineado (11)

- `D-0144` — password_hash
- `D-0294` — ubicacion
- `D-0896` — monto
- `D-0897` — saldo_despues
- `D-0971` — email
- `D-0972` — latitud
- `D-0973` — longitud
- `D-0974` — motivo_suspension
- `D-0975` — nombre
- `D-1082` — destino
- `D-1083` — origen

---

## Tier 2 — 822 items

### columna_falta (47)

| Tabla | Cantidad |
|---|---|
| tenant.configuracion_tenant | 23 |
| corporate.cuenta_corriente | 10 |
| corporate.movimiento_cuenta | 6 |
| corporate.factura_corporativa | 4 |
| auth.direccion_frecuente | 2 |
| auth.usuario_rol | 1 |
| corporate.pago_corporativo | 1 |

### constraint_desalineada (62)

- `D-0015` — audit.alerta_desvio
- `D-0025` — audit.log_acciones
- `D-0034` — audit.log_gps
- `D-0046` — auth.auditoria_email
- `D-0054` — auth.autorizacion_inicio
- `D-0073` — auth.direccion_frecuente
- `D-0081` — auth.perfil_general
- `D-0089` — auth.refresh_token
- `D-0100` — auth.reset_token
- `D-0109` — auth.taxista_favorito
- `D-0116` — auth.tipo_usuario
- `D-0128` — auth.turno_empleado
- `D-0160` — auth.usuario_empresa
- `D-0170` — auth.usuario_rol
- `D-0194` — corporate.cuenta_corriente
- `D-0215` — corporate.factura_corporativa
- `D-0243` — corporate.movimiento_cuenta
- `D-0259` — corporate.pago_corporativo
- `D-0272` — fleet.categoria_gasto
- `D-0311` — fleet.contrato_qr
- `D-0324` — fleet.contrato_vehiculo
- `D-0362` — fleet.documento_propietario
- `D-0373` — fleet.documento_vehiculo
- `D-0385` — fleet.documentos_chofer
- `D-0401` — fleet.foto_vehiculo
- `D-0409` — fleet.gasto_turno
- `D-0424` — fleet.gasto_vehiculo
- `D-0461` — fleet.liquidacion
- `D-0498` — fleet.liquidacion_ajuste
- `D-0510` — fleet.liquidacion_detalle
- `D-0520` — fleet.liquidacion_estado_historial
- `D-0531` — fleet.mantenimiento_vehiculo
- `D-0539` — fleet.marca
- `D-0547` — fleet.modelo
- `D-0558` — fleet.neumatico_historial_posicion
- `D-0579` — fleet.neumatico_imagen
- `D-0597` — fleet.neumatico_medicion
- `D-0614` — fleet.neumatico_operacion
- `D-0631` — fleet.neumatico_operacion_detalle
- `D-0644` — fleet.neumatico_sugerencia
- `D-0667` — fleet.neumatico_vehiculo
- `D-0691` — fleet.notificacion_vencimiento
- `D-0712` — fleet.propietario_vehiculo
- `D-0766` — geo.ciudad
- `D-0772` — geo.pais
- `D-0776` — geo.provincia
- `D-0781` — notification.notificacion
- `D-0793` — payment.billetera
- `D-0831` — payment.configuracion_tarifa
- `D-0845` — payment.configuracion_tarifa_vehiculo
- ... y 12 mas (ver JSON)

### constraint_falta (370)

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
| corporate.pago_corporativo | 9 |
| fleet.neumatico_sugerencia | 9 |
| auth.usuario_rol | 8 |
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

### constraint_sobra (13)

- `D-0056` — auth.autorizacion_inicio
- `D-0084` — auth.perfil_general
- `D-0118` — auth.tipo_usuario
- `D-0197` — corporate.cuenta_corriente
- `D-0217` — corporate.factura_corporativa
- `D-0275` — fleet.categoria_gasto
- `D-0313` — fleet.contrato_qr
- `D-0417` — fleet.gasto_turno
- `D-0541` — fleet.marca
- `D-0870` — payment.metodo_pago
- `D-0908` — public.comercio
- `D-0966` — tenant.configuracion_tenant
- `D-1009` — tenant.factura

### indice_falta (174)

| Tabla | Cantidad |
|---|---|
| fleet.contrato_vehiculo | 7 |
| fleet.notificacion_vencimiento | 7 |
| fleet.neumatico_historial_posicion | 6 |
| fleet.neumatico_vehiculo | 6 |
| public.escaneo_qr | 6 |
| audit.log_acciones | 5 |
| auth.autorizacion_inicio | 5 |
| auth.turno_empleado | 5 |
| auth.usuario_rol | 5 |
| corporate.factura_corporativa | 5 |
| fleet.neumatico_imagen | 5 |
| fleet.neumatico_operacion | 5 |
| fleet.neumatico_sugerencia | 5 |
| payment.pago_empresa | 5 |
| tenant.factura | 5 |
| auth.auditoria_email | 4 |
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
| auth.refresh_token | 2 |
| auth.tipo_usuario | 2 |
| corporate.cuenta_corriente | 2 |
| fleet.marca | 2 |
| fleet.modelo | 2 |
| geo.ciudad | 2 |
| payment.configuracion_tarifa_vehiculo | 2 |
| public.comercio | 2 |
| trip.foto_viaje | 2 |
| auth.direccion_frecuente | 1 |
| auth.perfil_general | 1 |
| auth.reset_token | 1 |
| auth.taxista_favorito | 1 |
| auth.usuario_empresa | 1 |
| fleet.liquidacion | 1 |
| fleet.liquidacion_ajuste | 1 |
| fleet.liquidacion_detalle | 1 |
| fleet.liquidacion_estado_historial | 1 |
| fleet.mantenimiento_vehiculo | 1 |
| geo.pais | 1 |
| geo.provincia | 1 |
| notification.notificacion | 1 |
| payment.billetera | 1 |
| payment.configuracion_tarifa | 1 |
| payment.factura_empresa | 1 |
| payment.metodo_pago | 1 |
| tenant.configuracion_tenant | 1 |
| tenant.empresa | 1 |
| trip.objeto_olvidado | 1 |
| trip.panico | 1 |
| trip.tipo_vehiculo | 1 |

### indice_sobra (3)

- `D-0107` — auth.reset_token
- `D-0842` — payment.configuracion_tarifa
- `D-1071` — trip.panico

### nullable_desalineado (89)

- `D-0014` — viaje_id
- `D-0044` — created_at
- `D-0045` — valid
- `D-0053` — created_at
- `D-0070` — created_at
- `D-0078` — created_at
- `D-0079` — updated_at
- `D-0080` — usuario_id
- `D-0087` — created_at
- `D-0088` — usado
- `D-0098` — created_at
- `D-0099` — usado
- `D-0108` — created_at
- `D-0123` — created_at
- `D-0125` — facturado_total
- `D-0126` — updated_at
- `D-0127` — viajes_gestionados
- `D-0157` — activo
- `D-0158` — created_at
- `D-0159` — rol
- `D-0308` — activo
- `D-0309` — created_at
- `D-0310` — usos
- `D-0321` — created_at
- `D-0322` — estado_contrato
- `D-0361` — created_at
- `D-0371` — created_at
- `D-0372` — updated_at
- `D-0384` — subido_en
- `D-0398` — created_at
- `D-0399` — es_principal
- `D-0400` — orden
- `D-0421` — created_at
- `D-0423` — moneda
- `D-0450` — calculada_en
- `D-0451` — canon
- `D-0452` — comision_chofer
- `D-0453` — created_at
- `D-0454` — estado
- `D-0455` — monto_bruto
- `D-0456` — total_chofer
- `D-0457` — total_gastos
- `D-0458` — total_propietario
- `D-0459` — updated_at
- `D-0460` — version
- `D-0497` — created_at
- `D-0509` — created_at
- `D-0519` — created_at
- `D-0530` — created_at
- `D-0538` — created_at
- ... y 39 mas (ver JSON)

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

### tipo_desalineado (54)

- `D-0071` — latitud
- `D-0072` — longitud
- `D-0124` — facturado_total
- `D-0168` — fecha_fin
- `D-0169` — fecha_inicio
- `D-0422` — km_registro
- `D-0555` — created_at
- `D-0556` — fecha_desmontaje
- `D-0557` — fecha_montaje
- `D-0577` — created_at
- `D-0578` — fecha_subida
- `D-0595` — created_at
- `D-0596` — fecha_medicion
- `D-0611` — created_at
- `D-0612` — fecha_operacion
- `D-0613` — updated_at
- `D-0630` — created_at
- `D-0640` — created_at
- `D-0641` — fecha_atendida
- `D-0642` — fecha_generacion
- `D-0643` — updated_at
- `D-0663` — created_at
- `D-0664` — fecha_alta
- `D-0665` — fecha_baja
- `D-0666` — updated_at
- `D-0790` — saldo
- `D-0802` — distancia_por_ficha
- `D-0806` — metros_por_ficha
- `D-0809` — modo_cobro_tiempo
- `D-0812` — precio_por_ficha
- `D-0814` — precio_por_km
- `D-0815` — precio_por_minuto
- `D-0816` — precio_por_minuto_espera
- `D-0818` — recargo_domingo
- `D-0820` — recargo_feriado
- `D-0821` — recargo_nocturno
- `D-0823` — seg_por_ficha_espera
- `D-0825` — tarifa_base
- `D-0827` — velocidad_referencia_kmh
- `D-0829` — velocidad_umbral_kmh
- `D-0843` — factor_precio
- `D-0844` — tipo_vehiculo_id
- `D-0858` — descuento
- `D-0861` — total
- `D-0862` — total_final
- `D-0877` — monto
- `D-0987` — latitud
- `D-0988` — limite_credito
- `D-0990` — longitud
- `D-0991` — tarifa_preferencial
- ... y 4 mas (ver JSON)

---

## Tier 3 — 120 items

### comment_desalineado (22)

- `D-0214` — estado
- `D-0242` — tipo_movimiento
- `D-0258` — estado
- `D-0323` — estado_contrato
- `D-0688` — entidad_tipo
- `D-0689` — nivel
- `D-0801` — descripcion
- `D-0803` — distancia_por_ficha
- `D-0804` — hora_fin_nocturno
- `D-0805` — hora_inicio_nocturno
- `D-0808` — modo_calculo
- `D-0811` — moneda
- `D-0813` — precio_por_ficha
- `D-0817` — precio_por_minuto_espera
- `D-0819` — recargo_domingo
- `D-0918` — resultado
- `D-0919` — tipo_qr
- `D-1063` — resuelto_en
- `D-1065` — usuario_id
- `D-1072` — distancia_por_ficha
- `D-1073` — precio_por_ficha
- `D-1074` — precio_por_minuto_espera

### constraint_nombre_desalineado (97)

- `D-0016` — audit.alerta_desvio
- `D-0035` — audit.log_gps
- `D-0036` — audit.log_gps
- `D-0074` — auth.direccion_frecuente
- `D-0082` — auth.perfil_general
- `D-0083` — auth.perfil_general
- `D-0090` — auth.refresh_token
- `D-0101` — auth.reset_token
- `D-0110` — auth.taxista_favorito
- `D-0111` — auth.taxista_favorito
- `D-0129` — auth.turno_empleado
- `D-0130` — auth.turno_empleado
- `D-0161` — auth.usuario_empresa
- `D-0162` — auth.usuario_empresa
- `D-0273` — fleet.categoria_gasto
- `D-0325` — fleet.contrato_vehiculo
- `D-0326` — fleet.contrato_vehiculo
- `D-0327` — fleet.contrato_vehiculo
- `D-0328` — fleet.contrato_vehiculo
- `D-0374` — fleet.documento_vehiculo
- `D-0386` — fleet.documentos_chofer
- `D-0410` — fleet.gasto_turno
- `D-0411` — fleet.gasto_turno
- `D-0425` — fleet.gasto_vehiculo
- `D-0426` — fleet.gasto_vehiculo
- `D-0427` — fleet.gasto_vehiculo
- `D-0462` — fleet.liquidacion
- `D-0463` — fleet.liquidacion
- `D-0464` — fleet.liquidacion
- `D-0465` — fleet.liquidacion
- `D-0466` — fleet.liquidacion
- `D-0467` — fleet.liquidacion
- `D-0468` — fleet.liquidacion
- `D-0469` — fleet.liquidacion
- `D-0470` — fleet.liquidacion
- `D-0499` — fleet.liquidacion_ajuste
- `D-0500` — fleet.liquidacion_ajuste
- `D-0501` — fleet.liquidacion_ajuste
- `D-0511` — fleet.liquidacion_detalle
- `D-0521` — fleet.liquidacion_estado_historial
- `D-0522` — fleet.liquidacion_estado_historial
- `D-0523` — fleet.liquidacion_estado_historial
- `D-0532` — fleet.mantenimiento_vehiculo
- `D-0533` — fleet.mantenimiento_vehiculo
- `D-0548` — fleet.modelo
- `D-0559` — fleet.neumatico_historial_posicion
- `D-0560` — fleet.neumatico_historial_posicion
- `D-0561` — fleet.neumatico_historial_posicion
- `D-0562` — fleet.neumatico_historial_posicion
- `D-0580` — fleet.neumatico_imagen
- ... y 47 mas (ver JSON)

### indice_nombre_desalineado (1)

- `D-0799` — payment.billetera

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
| D-0436 | fleet.ingreso_turno.medio_pago | vocabulario_metodo_pago |
| D-0555 | fleet.neumatico_historial_posicion.created_at | timestamp_naive_vs_tz |
| D-0556 | fleet.neumatico_historial_posicion.fecha_desmontaje | timestamp_naive_vs_tz |
| D-0557 | fleet.neumatico_historial_posicion.fecha_montaje | timestamp_naive_vs_tz |
| D-0577 | fleet.neumatico_imagen.created_at | timestamp_naive_vs_tz |
| D-0578 | fleet.neumatico_imagen.fecha_subida | timestamp_naive_vs_tz |
| D-0595 | fleet.neumatico_medicion.created_at | timestamp_naive_vs_tz |
| D-0596 | fleet.neumatico_medicion.fecha_medicion | timestamp_naive_vs_tz |
| D-0611 | fleet.neumatico_operacion.created_at | timestamp_naive_vs_tz |
| D-0612 | fleet.neumatico_operacion.fecha_operacion | timestamp_naive_vs_tz |
| D-0613 | fleet.neumatico_operacion.updated_at | timestamp_naive_vs_tz |
| D-0630 | fleet.neumatico_operacion_detalle.created_at | timestamp_naive_vs_tz |
| D-0640 | fleet.neumatico_sugerencia.created_at | timestamp_naive_vs_tz |
| D-0641 | fleet.neumatico_sugerencia.fecha_atendida | timestamp_naive_vs_tz |
| D-0642 | fleet.neumatico_sugerencia.fecha_generacion | timestamp_naive_vs_tz |
| D-0643 | fleet.neumatico_sugerencia.updated_at | timestamp_naive_vs_tz |
| D-0663 | fleet.neumatico_vehiculo.created_at | timestamp_naive_vs_tz |
| D-0664 | fleet.neumatico_vehiculo.fecha_alta | timestamp_naive_vs_tz |
| D-0665 | fleet.neumatico_vehiculo.fecha_baja | timestamp_naive_vs_tz |
| D-0666 | fleet.neumatico_vehiculo.updated_at | timestamp_naive_vs_tz |
| D-0972 | tenant.control_base.latitud | orm_mal_db_bien |
| D-0973 | tenant.control_base.longitud | orm_mal_db_bien |

---

## Archivos generados

- `orm_diff.json` — datos completos.
- `orm_diff_reporte.md` — este informe.
- `orm_diff_acciones.csv` — CSV de acciones sugeridas.
