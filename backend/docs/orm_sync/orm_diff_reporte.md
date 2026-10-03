# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-03T19:51:29.517513+00:00

## Resumen ejecutivo

- **1086 diferencias** en total.
- **Tier 1**: 175 items.
- **Tier 2**: 790 items.
- **Tier 3**: 120 items.
- **Tier 4**: 1 items.
- **24 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| constraint_falta | 427 |
| indice_falta | 192 |
| constraint_nombre_desalineado | 124 |
| nullable_desalineado | 108 |
| constraint_desalineada | 72 |
| tipo_desalineado | 61 |
| comment_desalineado | 29 |
| columna_falta | 26 |
| constraint_sobra | 24 |
| tabla_falta | 10 |
| indice_sobra | 6 |
| indice_nombre_desalineado | 4 |
| schema_falta | 2 |
| tabla_sobra | 1 |

---

## Tier 1 — 175 items

### comment_desalineado (7)

- `D-0413` — declarado_por
- `D-0414` — medio_pago
- `D-0415` — transaccion_id
- `D-0702` — snapshot_dia_contractual
- `D-1015` — latitud
- `D-1016` — longitud
- `D-1052` — solicitado_en

### constraint_desalineada (10)

- `D-0147` — auth.usuario
- `D-0276` — fleet.chofer_vehiculo
- `D-0416` — fleet.ingreso_turno
- `D-0703` — fleet.turno_chofer
- `D-0728` — fleet.vehiculo
- `D-0876` — payment.transaccion
- `D-0955` — tenant.control_base
- `D-0994` — trip.calificacion
- `D-1017` — trip.historial_estado_viaje
- `D-1053` — trip.viaje_solicitado

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
- `D-0277` — fleet.chofer_vehiculo
- `D-0278` — fleet.chofer_vehiculo
- `D-0279` — fleet.chofer_vehiculo
- `D-0704` — fleet.turno_chofer
- `D-0705` — fleet.turno_chofer
- `D-0706` — fleet.turno_chofer
- `D-0729` — fleet.vehiculo
- `D-0877` — payment.transaccion
- `D-0878` — payment.transaccion
- `D-0879` — payment.transaccion
- `D-0956` — tenant.control_base
- `D-0957` — tenant.control_base
- `D-0995` — trip.calificacion
- `D-0996` — trip.calificacion
- `D-0997` — trip.calificacion
- `D-1018` — trip.historial_estado_viaje
- `D-1058` — trip.viaje_solicitado
- `D-1059` — trip.viaje_solicitado
- `D-1060` — trip.viaje_solicitado
- `D-1061` — trip.viaje_solicitado
- `D-1062` — trip.viaje_solicitado
- `D-1063` — trip.viaje_solicitado
- `D-1064` — trip.viaje_solicitado
- `D-1065` — trip.viaje_solicitado

### constraint_sobra (11)

- `D-0715` — fleet.turno_chofer
- `D-0731` — fleet.vehiculo
- `D-0998` — trip.calificacion
- `D-1076` — trip.viaje_solicitado
- `D-1077` — trip.viaje_solicitado
- `D-1078` — trip.viaje_solicitado
- `D-1079` — trip.viaje_solicitado
- `D-1080` — trip.viaje_solicitado
- `D-1081` — trip.viaje_solicitado
- `D-1082` — trip.viaje_solicitado
- `D-1083` — trip.viaje_solicitado

### indice_falta (18)

- `D-0155` — auth.usuario
- `D-0284` — fleet.chofer_vehiculo
- `D-0427` — fleet.ingreso_turno
- `D-0716` — fleet.turno_chofer
- `D-0717` — fleet.turno_chofer
- `D-0718` — fleet.turno_chofer
- `D-0719` — fleet.turno_chofer
- `D-0720` — fleet.turno_chofer
- `D-0739` — fleet.vehiculo
- `D-0740` — fleet.vehiculo
- `D-0741` — fleet.vehiculo
- `D-0742` — fleet.vehiculo
- `D-0881` — payment.transaccion
- `D-0960` — tenant.control_base
- `D-0961` — tenant.control_base
- `D-1005` — trip.calificacion
- `D-1020` — trip.historial_estado_viaje
- `D-1084` — trip.viaje_solicitado

### indice_nombre_desalineado (3)

- `D-0156` — auth.usuario
- `D-0743` — fleet.vehiculo
- `D-1086` — trip.viaje_solicitado

### indice_sobra (3)

- `D-0285` — fleet.chofer_vehiculo
- `D-0882` — payment.transaccion
- `D-1085` — trip.viaje_solicitado

### nullable_desalineado (25)

- `D-0142` — activo
- `D-0143` — created_at
- `D-0145` — tipo_usuario_id
- `D-0146` — updated_at
- `D-0266` — activo
- `D-0267` — calificacion_promedio
- `D-0268` — created_at
- `D-0269` — estado_laboral
- `D-0270` — estado_panico
- `D-0271` — total_calificaciones
- `D-0273` — ultima_conexion
- `D-0274` — updated_at
- `D-0275` — vehiculo_id
- `D-0721` — activo
- `D-0722` — capacidad
- `D-0723` — control_base_id
- `D-0724` — created_at
- `D-0725` — qr_activo
- `D-0726` — qr_uuid
- `D-0727` — updated_at
- `D-0872` — billetera_id
- `D-0873` — created_at
- `D-0947` — activo
- `D-0948` — created_at
- `D-0954` — updated_at

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

### tipo_desalineado (11)

- `D-0144` — password_hash
- `D-0272` — ubicacion
- `D-0874` — monto
- `D-0875` — saldo_despues
- `D-0949` — email
- `D-0950` — latitud
- `D-0951` — longitud
- `D-0952` — motivo_suspension
- `D-0953` — nombre
- `D-1050` — destino
- `D-1051` — origen

---

## Tier 2 — 790 items

### columna_falta (26)

| Tabla | Cantidad |
|---|---|
| tenant.configuracion_tenant | 23 |
| auth.direccion_frecuente | 2 |
| auth.usuario_rol | 1 |

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
- `D-0184` — corporate.cuenta_corriente
- `D-0201` — corporate.factura_corporativa
- `D-0223` — corporate.movimiento_cuenta
- `D-0238` — corporate.pago_corporativo
- `D-0250` — fleet.categoria_gasto
- `D-0289` — fleet.contrato_qr
- `D-0302` — fleet.contrato_vehiculo
- `D-0340` — fleet.documento_propietario
- `D-0351` — fleet.documento_vehiculo
- `D-0363` — fleet.documentos_chofer
- `D-0379` — fleet.foto_vehiculo
- `D-0387` — fleet.gasto_turno
- `D-0402` — fleet.gasto_vehiculo
- `D-0439` — fleet.liquidacion
- `D-0476` — fleet.liquidacion_ajuste
- `D-0488` — fleet.liquidacion_detalle
- `D-0498` — fleet.liquidacion_estado_historial
- `D-0509` — fleet.mantenimiento_vehiculo
- `D-0517` — fleet.marca
- `D-0525` — fleet.modelo
- `D-0536` — fleet.neumatico_historial_posicion
- `D-0557` — fleet.neumatico_imagen
- `D-0575` — fleet.neumatico_medicion
- `D-0592` — fleet.neumatico_operacion
- `D-0609` — fleet.neumatico_operacion_detalle
- `D-0622` — fleet.neumatico_sugerencia
- `D-0645` — fleet.neumatico_vehiculo
- `D-0669` — fleet.notificacion_vencimiento
- `D-0690` — fleet.propietario_vehiculo
- `D-0744` — geo.ciudad
- `D-0750` — geo.pais
- `D-0754` — geo.provincia
- `D-0759` — notification.notificacion
- `D-0771` — payment.billetera
- `D-0809` — payment.configuracion_tarifa
- `D-0823` — payment.configuracion_tarifa_vehiculo
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

### constraint_sobra (13)

- `D-0056` — auth.autorizacion_inicio
- `D-0084` — auth.perfil_general
- `D-0118` — auth.tipo_usuario
- `D-0187` — corporate.cuenta_corriente
- `D-0203` — corporate.factura_corporativa
- `D-0253` — fleet.categoria_gasto
- `D-0291` — fleet.contrato_qr
- `D-0395` — fleet.gasto_turno
- `D-0519` — fleet.marca
- `D-0848` — payment.metodo_pago
- `D-0886` — public.comercio
- `D-0944` — tenant.configuracion_tenant
- `D-0977` — tenant.factura

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
- `D-0820` — payment.configuracion_tarifa
- `D-1039` — trip.panico

### nullable_desalineado (83)

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
- `D-0286` — activo
- `D-0287` — created_at
- `D-0288` — usos
- `D-0299` — created_at
- `D-0300` — estado_contrato
- `D-0339` — created_at
- `D-0349` — created_at
- `D-0350` — updated_at
- `D-0362` — subido_en
- `D-0376` — created_at
- `D-0377` — es_principal
- `D-0378` — orden
- `D-0399` — created_at
- `D-0401` — moneda
- `D-0428` — calculada_en
- `D-0429` — canon
- `D-0430` — comision_chofer
- `D-0431` — created_at
- `D-0432` — estado
- `D-0433` — monto_bruto
- `D-0434` — total_chofer
- `D-0435` — total_gastos
- `D-0436` — total_propietario
- `D-0437` — updated_at
- `D-0438` — version
- `D-0475` — created_at
- `D-0487` — created_at
- `D-0497` — created_at
- `D-0508` — created_at
- `D-0516` — created_at
- ... y 33 mas (ver JSON)

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

### tipo_desalineado (50)

- `D-0071` — latitud
- `D-0072` — longitud
- `D-0124` — facturado_total
- `D-0168` — fecha_fin
- `D-0169` — fecha_inicio
- `D-0400` — km_registro
- `D-0533` — created_at
- `D-0534` — fecha_desmontaje
- `D-0535` — fecha_montaje
- `D-0555` — created_at
- `D-0556` — fecha_subida
- `D-0573` — created_at
- `D-0574` — fecha_medicion
- `D-0589` — created_at
- `D-0590` — fecha_operacion
- `D-0591` — updated_at
- `D-0608` — created_at
- `D-0618` — created_at
- `D-0619` — fecha_atendida
- `D-0620` — fecha_generacion
- `D-0621` — updated_at
- `D-0641` — created_at
- `D-0642` — fecha_alta
- `D-0643` — fecha_baja
- `D-0644` — updated_at
- `D-0768` — saldo
- `D-0780` — distancia_por_ficha
- `D-0784` — metros_por_ficha
- `D-0787` — modo_cobro_tiempo
- `D-0790` — precio_por_ficha
- `D-0792` — precio_por_km
- `D-0793` — precio_por_minuto
- `D-0794` — precio_por_minuto_espera
- `D-0796` — recargo_domingo
- `D-0798` — recargo_feriado
- `D-0799` — recargo_nocturno
- `D-0801` — seg_por_ficha_espera
- `D-0803` — tarifa_base
- `D-0805` — velocidad_referencia_kmh
- `D-0807` — velocidad_umbral_kmh
- `D-0821` — factor_precio
- `D-0822` — tipo_vehiculo_id
- `D-0836` — descuento
- `D-0839` — total
- `D-0840` — total_final
- `D-0855` — monto
- `D-0970` — canon_total
- `D-0971` — porcentaje_plataforma
- `D-0972` — total_a_pagar
- `D-1032` — ubicacion

---

## Tier 3 — 120 items

### comment_desalineado (22)

- `D-0200` — estado
- `D-0222` — tipo_movimiento
- `D-0237` — estado
- `D-0301` — estado_contrato
- `D-0666` — entidad_tipo
- `D-0667` — nivel
- `D-0779` — descripcion
- `D-0781` — distancia_por_ficha
- `D-0782` — hora_fin_nocturno
- `D-0783` — hora_inicio_nocturno
- `D-0786` — modo_calculo
- `D-0789` — moneda
- `D-0791` — precio_por_ficha
- `D-0795` — precio_por_minuto_espera
- `D-0797` — recargo_domingo
- `D-0896` — resultado
- `D-0897` — tipo_qr
- `D-1031` — resuelto_en
- `D-1033` — usuario_id
- `D-1040` — distancia_por_ficha
- `D-1041` — precio_por_ficha
- `D-1042` — precio_por_minuto_espera

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
- `D-0251` — fleet.categoria_gasto
- `D-0303` — fleet.contrato_vehiculo
- `D-0304` — fleet.contrato_vehiculo
- `D-0305` — fleet.contrato_vehiculo
- `D-0306` — fleet.contrato_vehiculo
- `D-0352` — fleet.documento_vehiculo
- `D-0364` — fleet.documentos_chofer
- `D-0388` — fleet.gasto_turno
- `D-0389` — fleet.gasto_turno
- `D-0403` — fleet.gasto_vehiculo
- `D-0404` — fleet.gasto_vehiculo
- `D-0405` — fleet.gasto_vehiculo
- `D-0440` — fleet.liquidacion
- `D-0441` — fleet.liquidacion
- `D-0442` — fleet.liquidacion
- `D-0443` — fleet.liquidacion
- `D-0444` — fleet.liquidacion
- `D-0445` — fleet.liquidacion
- `D-0446` — fleet.liquidacion
- `D-0447` — fleet.liquidacion
- `D-0448` — fleet.liquidacion
- `D-0477` — fleet.liquidacion_ajuste
- `D-0478` — fleet.liquidacion_ajuste
- `D-0479` — fleet.liquidacion_ajuste
- `D-0489` — fleet.liquidacion_detalle
- `D-0499` — fleet.liquidacion_estado_historial
- `D-0500` — fleet.liquidacion_estado_historial
- `D-0501` — fleet.liquidacion_estado_historial
- `D-0510` — fleet.mantenimiento_vehiculo
- `D-0511` — fleet.mantenimiento_vehiculo
- `D-0526` — fleet.modelo
- `D-0537` — fleet.neumatico_historial_posicion
- `D-0538` — fleet.neumatico_historial_posicion
- `D-0539` — fleet.neumatico_historial_posicion
- `D-0540` — fleet.neumatico_historial_posicion
- `D-0558` — fleet.neumatico_imagen
- ... y 47 mas (ver JSON)

### indice_nombre_desalineado (1)

- `D-0777` — payment.billetera

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
| D-0414 | fleet.ingreso_turno.medio_pago | vocabulario_metodo_pago |
| D-0533 | fleet.neumatico_historial_posicion.created_at | timestamp_naive_vs_tz |
| D-0534 | fleet.neumatico_historial_posicion.fecha_desmontaje | timestamp_naive_vs_tz |
| D-0535 | fleet.neumatico_historial_posicion.fecha_montaje | timestamp_naive_vs_tz |
| D-0555 | fleet.neumatico_imagen.created_at | timestamp_naive_vs_tz |
| D-0556 | fleet.neumatico_imagen.fecha_subida | timestamp_naive_vs_tz |
| D-0573 | fleet.neumatico_medicion.created_at | timestamp_naive_vs_tz |
| D-0574 | fleet.neumatico_medicion.fecha_medicion | timestamp_naive_vs_tz |
| D-0589 | fleet.neumatico_operacion.created_at | timestamp_naive_vs_tz |
| D-0590 | fleet.neumatico_operacion.fecha_operacion | timestamp_naive_vs_tz |
| D-0591 | fleet.neumatico_operacion.updated_at | timestamp_naive_vs_tz |
| D-0608 | fleet.neumatico_operacion_detalle.created_at | timestamp_naive_vs_tz |
| D-0618 | fleet.neumatico_sugerencia.created_at | timestamp_naive_vs_tz |
| D-0619 | fleet.neumatico_sugerencia.fecha_atendida | timestamp_naive_vs_tz |
| D-0620 | fleet.neumatico_sugerencia.fecha_generacion | timestamp_naive_vs_tz |
| D-0621 | fleet.neumatico_sugerencia.updated_at | timestamp_naive_vs_tz |
| D-0641 | fleet.neumatico_vehiculo.created_at | timestamp_naive_vs_tz |
| D-0642 | fleet.neumatico_vehiculo.fecha_alta | timestamp_naive_vs_tz |
| D-0643 | fleet.neumatico_vehiculo.fecha_baja | timestamp_naive_vs_tz |
| D-0644 | fleet.neumatico_vehiculo.updated_at | timestamp_naive_vs_tz |
| D-0950 | tenant.control_base.latitud | orm_mal_db_bien |
| D-0951 | tenant.control_base.longitud | orm_mal_db_bien |

---

## Archivos generados

- `orm_diff.json` — datos completos.
- `orm_diff_reporte.md` — este informe.
- `orm_diff_acciones.csv` — CSV de acciones sugeridas.
