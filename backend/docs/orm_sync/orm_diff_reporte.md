# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-03T18:41:17.394240+00:00

## Resumen ejecutivo

- **1149 diferencias** en total.
- **Tier 1**: 175 items.
- **Tier 2**: 853 items.
- **Tier 3**: 120 items.
- **Tier 4**: 1 items.
- **24 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| constraint_falta | 428 |
| indice_falta | 192 |
| nullable_desalineado | 127 |
| constraint_nombre_desalineado | 124 |
| tipo_desalineado | 78 |
| constraint_desalineada | 72 |
| columna_falta | 47 |
| comment_desalineado | 29 |
| constraint_sobra | 24 |
| tabla_falta | 10 |
| indice_sobra | 9 |
| indice_nombre_desalineado | 4 |
| schema_falta | 2 |
| columna_sobra | 2 |
| tabla_sobra | 1 |

---

## Tier 1 — 175 items

### comment_desalineado (7)

- `D-0449` — declarado_por
- `D-0450` — medio_pago
- `D-0451` — transaccion_id
- `D-0738` — snapshot_dia_contractual
- `D-1078` — latitud
- `D-1079` — longitud
- `D-1115` — solicitado_en

### constraint_desalineada (10)

- `D-0150` — auth.usuario
- `D-0312` — fleet.chofer_vehiculo
- `D-0452` — fleet.ingreso_turno
- `D-0739` — fleet.turno_chofer
- `D-0764` — fleet.vehiculo
- `D-0921` — payment.transaccion
- `D-1007` — tenant.control_base
- `D-1056` — trip.calificacion
- `D-1080` — trip.historial_estado_viaje
- `D-1116` — trip.viaje_solicitado

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

- `D-0151` — auth.usuario
- `D-0152` — auth.usuario
- `D-0153` — auth.usuario
- `D-0313` — fleet.chofer_vehiculo
- `D-0314` — fleet.chofer_vehiculo
- `D-0315` — fleet.chofer_vehiculo
- `D-0740` — fleet.turno_chofer
- `D-0741` — fleet.turno_chofer
- `D-0742` — fleet.turno_chofer
- `D-0765` — fleet.vehiculo
- `D-0922` — payment.transaccion
- `D-0923` — payment.transaccion
- `D-0924` — payment.transaccion
- `D-1008` — tenant.control_base
- `D-1009` — tenant.control_base
- `D-1057` — trip.calificacion
- `D-1058` — trip.calificacion
- `D-1059` — trip.calificacion
- `D-1081` — trip.historial_estado_viaje
- `D-1121` — trip.viaje_solicitado
- `D-1122` — trip.viaje_solicitado
- `D-1123` — trip.viaje_solicitado
- `D-1124` — trip.viaje_solicitado
- `D-1125` — trip.viaje_solicitado
- `D-1126` — trip.viaje_solicitado
- `D-1127` — trip.viaje_solicitado
- `D-1128` — trip.viaje_solicitado

### constraint_sobra (11)

- `D-0751` — fleet.turno_chofer
- `D-0767` — fleet.vehiculo
- `D-1060` — trip.calificacion
- `D-1139` — trip.viaje_solicitado
- `D-1140` — trip.viaje_solicitado
- `D-1141` — trip.viaje_solicitado
- `D-1142` — trip.viaje_solicitado
- `D-1143` — trip.viaje_solicitado
- `D-1144` — trip.viaje_solicitado
- `D-1145` — trip.viaje_solicitado
- `D-1146` — trip.viaje_solicitado

### indice_falta (18)

- `D-0158` — auth.usuario
- `D-0320` — fleet.chofer_vehiculo
- `D-0463` — fleet.ingreso_turno
- `D-0752` — fleet.turno_chofer
- `D-0753` — fleet.turno_chofer
- `D-0754` — fleet.turno_chofer
- `D-0755` — fleet.turno_chofer
- `D-0756` — fleet.turno_chofer
- `D-0775` — fleet.vehiculo
- `D-0776` — fleet.vehiculo
- `D-0777` — fleet.vehiculo
- `D-0778` — fleet.vehiculo
- `D-0926` — payment.transaccion
- `D-1012` — tenant.control_base
- `D-1013` — tenant.control_base
- `D-1067` — trip.calificacion
- `D-1083` — trip.historial_estado_viaje
- `D-1147` — trip.viaje_solicitado

### indice_nombre_desalineado (3)

- `D-0159` — auth.usuario
- `D-0779` — fleet.vehiculo
- `D-1149` — trip.viaje_solicitado

### indice_sobra (3)

- `D-0321` — fleet.chofer_vehiculo
- `D-0927` — payment.transaccion
- `D-1148` — trip.viaje_solicitado

### nullable_desalineado (25)

- `D-0145` — activo
- `D-0146` — created_at
- `D-0148` — tipo_usuario_id
- `D-0149` — updated_at
- `D-0302` — activo
- `D-0303` — calificacion_promedio
- `D-0304` — created_at
- `D-0305` — estado_laboral
- `D-0306` — estado_panico
- `D-0307` — total_calificaciones
- `D-0309` — ultima_conexion
- `D-0310` — updated_at
- `D-0311` — vehiculo_id
- `D-0757` — activo
- `D-0758` — capacidad
- `D-0759` — control_base_id
- `D-0760` — created_at
- `D-0761` — qr_activo
- `D-0762` — qr_uuid
- `D-0763` — updated_at
- `D-0917` — billetera_id
- `D-0918` — created_at
- `D-0999` — activo
- `D-1000` — created_at
- `D-1006` — updated_at

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

### tipo_desalineado (11)

- `D-0147` — password_hash
- `D-0308` — ubicacion
- `D-0919` — monto
- `D-0920` — saldo_despues
- `D-1001` — email
- `D-1002` — latitud
- `D-1003` — longitud
- `D-1004` — motivo_suspension
- `D-1005` — nombre
- `D-1113` — destino
- `D-1114` — origen

---

## Tier 2 — 853 items

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

### columna_sobra (2)

- `D-0034` — ubicacion
- `D-0035` — velocidad_kmh

### constraint_desalineada (62)

- `D-0015` — audit.alerta_desvio
- `D-0025` — audit.log_acciones
- `D-0036` — audit.log_gps
- `D-0049` — auth.auditoria_email
- `D-0057` — auth.autorizacion_inicio
- `D-0076` — auth.direccion_frecuente
- `D-0084` — auth.perfil_general
- `D-0092` — auth.refresh_token
- `D-0103` — auth.reset_token
- `D-0112` — auth.taxista_favorito
- `D-0119` — auth.tipo_usuario
- `D-0131` — auth.turno_empleado
- `D-0163` — auth.usuario_empresa
- `D-0173` — auth.usuario_rol
- `D-0200` — corporate.cuenta_corriente
- `D-0225` — corporate.factura_corporativa
- `D-0256` — corporate.movimiento_cuenta
- `D-0273` — corporate.pago_corporativo
- `D-0286` — fleet.categoria_gasto
- `D-0325` — fleet.contrato_qr
- `D-0338` — fleet.contrato_vehiculo
- `D-0376` — fleet.documento_propietario
- `D-0387` — fleet.documento_vehiculo
- `D-0399` — fleet.documentos_chofer
- `D-0415` — fleet.foto_vehiculo
- `D-0423` — fleet.gasto_turno
- `D-0438` — fleet.gasto_vehiculo
- `D-0475` — fleet.liquidacion
- `D-0512` — fleet.liquidacion_ajuste
- `D-0524` — fleet.liquidacion_detalle
- `D-0534` — fleet.liquidacion_estado_historial
- `D-0545` — fleet.mantenimiento_vehiculo
- `D-0553` — fleet.marca
- `D-0561` — fleet.modelo
- `D-0572` — fleet.neumatico_historial_posicion
- `D-0593` — fleet.neumatico_imagen
- `D-0611` — fleet.neumatico_medicion
- `D-0628` — fleet.neumatico_operacion
- `D-0645` — fleet.neumatico_operacion_detalle
- `D-0658` — fleet.neumatico_sugerencia
- `D-0681` — fleet.neumatico_vehiculo
- `D-0705` — fleet.notificacion_vencimiento
- `D-0726` — fleet.propietario_vehiculo
- `D-0782` — geo.ciudad
- `D-0789` — geo.pais
- `D-0795` — geo.provincia
- `D-0802` — notification.notificacion
- `D-0816` — payment.billetera
- `D-0854` — payment.configuracion_tarifa
- `D-0868` — payment.configuracion_tarifa_vehiculo
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

- `D-0059` — auth.autorizacion_inicio
- `D-0087` — auth.perfil_general
- `D-0121` — auth.tipo_usuario
- `D-0203` — corporate.cuenta_corriente
- `D-0227` — corporate.factura_corporativa
- `D-0289` — fleet.categoria_gasto
- `D-0327` — fleet.contrato_qr
- `D-0431` — fleet.gasto_turno
- `D-0555` — fleet.marca
- `D-0893` — payment.metodo_pago
- `D-0936` — public.comercio
- `D-0996` — tenant.configuracion_tenant
- `D-1039` — tenant.factura

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

### indice_sobra (6)

- `D-0046` — audit.log_gps
- `D-0110` — auth.reset_token
- `D-0809` — notification.notificacion
- `D-0810` — notification.notificacion
- `D-0865` — payment.configuracion_tarifa
- `D-1102` — trip.panico

### nullable_desalineado (102)

- `D-0014` — viaje_id
- `D-0047` — created_at
- `D-0048` — valid
- `D-0056` — created_at
- `D-0073` — created_at
- `D-0081` — created_at
- `D-0082` — updated_at
- `D-0083` — usuario_id
- `D-0090` — created_at
- `D-0091` — usado
- `D-0101` — created_at
- `D-0102` — usado
- `D-0111` — created_at
- `D-0126` — created_at
- `D-0128` — facturado_total
- `D-0129` — updated_at
- `D-0130` — viajes_gestionados
- `D-0160` — activo
- `D-0161` — created_at
- `D-0162` — rol
- `D-0322` — activo
- `D-0323` — created_at
- `D-0324` — usos
- `D-0335` — created_at
- `D-0336` — estado_contrato
- `D-0375` — created_at
- `D-0385` — created_at
- `D-0386` — updated_at
- `D-0398` — subido_en
- `D-0412` — created_at
- `D-0413` — es_principal
- `D-0414` — orden
- `D-0435` — created_at
- `D-0437` — moneda
- `D-0464` — calculada_en
- `D-0465` — canon
- `D-0466` — comision_chofer
- `D-0467` — created_at
- `D-0468` — estado
- `D-0469` — monto_bruto
- `D-0470` — total_chofer
- `D-0471` — total_gastos
- `D-0472` — total_propietario
- `D-0473` — updated_at
- `D-0474` — version
- `D-0511` — created_at
- `D-0523` — created_at
- `D-0533` — created_at
- `D-0544` — created_at
- `D-0552` — created_at
- ... y 52 mas (ver JSON)

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

### tipo_desalineado (67)

- `D-0074` — latitud
- `D-0075` — longitud
- `D-0127` — facturado_total
- `D-0171` — fecha_fin
- `D-0172` — fecha_inicio
- `D-0197` — limite_credito
- `D-0198` — saldo_actual
- `D-0199` — saldo_disponible
- `D-0220` — descuento
- `D-0222` — iva
- `D-0223` — subtotal
- `D-0224` — total
- `D-0252` — monto
- `D-0253` — saldo_anterior
- `D-0254` — saldo_nuevo
- `D-0272` — monto
- `D-0436` — km_registro
- `D-0569` — created_at
- `D-0570` — fecha_desmontaje
- `D-0571` — fecha_montaje
- `D-0591` — created_at
- `D-0592` — fecha_subida
- `D-0609` — created_at
- `D-0610` — fecha_medicion
- `D-0625` — created_at
- `D-0626` — fecha_operacion
- `D-0627` — updated_at
- `D-0644` — created_at
- `D-0654` — created_at
- `D-0655` — fecha_atendida
- `D-0656` — fecha_generacion
- `D-0657` — updated_at
- `D-0677` — created_at
- `D-0678` — fecha_alta
- `D-0679` — fecha_baja
- `D-0680` — updated_at
- `D-0813` — saldo
- `D-0825` — distancia_por_ficha
- `D-0829` — metros_por_ficha
- `D-0832` — modo_cobro_tiempo
- `D-0835` — precio_por_ficha
- `D-0837` — precio_por_km
- `D-0838` — precio_por_minuto
- `D-0839` — precio_por_minuto_espera
- `D-0841` — recargo_domingo
- `D-0843` — recargo_feriado
- `D-0844` — recargo_nocturno
- `D-0846` — seg_por_ficha_espera
- `D-0848` — tarifa_base
- `D-0850` — velocidad_referencia_kmh
- ... y 17 mas (ver JSON)

---

## Tier 3 — 120 items

### comment_desalineado (22)

- `D-0221` — estado
- `D-0255` — tipo_movimiento
- `D-0271` — estado
- `D-0337` — estado_contrato
- `D-0702` — entidad_tipo
- `D-0703` — nivel
- `D-0824` — descripcion
- `D-0826` — distancia_por_ficha
- `D-0827` — hora_fin_nocturno
- `D-0828` — hora_inicio_nocturno
- `D-0831` — modo_calculo
- `D-0834` — moneda
- `D-0836` — precio_por_ficha
- `D-0840` — precio_por_minuto_espera
- `D-0842` — recargo_domingo
- `D-0947` — resultado
- `D-0949` — tipo_qr
- `D-1094` — resuelto_en
- `D-1096` — usuario_id
- `D-1103` — distancia_por_ficha
- `D-1104` — precio_por_ficha
- `D-1105` — precio_por_minuto_espera

### constraint_nombre_desalineado (97)

- `D-0016` — audit.alerta_desvio
- `D-0037` — audit.log_gps
- `D-0038` — audit.log_gps
- `D-0077` — auth.direccion_frecuente
- `D-0085` — auth.perfil_general
- `D-0086` — auth.perfil_general
- `D-0093` — auth.refresh_token
- `D-0104` — auth.reset_token
- `D-0113` — auth.taxista_favorito
- `D-0114` — auth.taxista_favorito
- `D-0132` — auth.turno_empleado
- `D-0133` — auth.turno_empleado
- `D-0164` — auth.usuario_empresa
- `D-0165` — auth.usuario_empresa
- `D-0287` — fleet.categoria_gasto
- `D-0339` — fleet.contrato_vehiculo
- `D-0340` — fleet.contrato_vehiculo
- `D-0341` — fleet.contrato_vehiculo
- `D-0342` — fleet.contrato_vehiculo
- `D-0388` — fleet.documento_vehiculo
- `D-0400` — fleet.documentos_chofer
- `D-0424` — fleet.gasto_turno
- `D-0425` — fleet.gasto_turno
- `D-0439` — fleet.gasto_vehiculo
- `D-0440` — fleet.gasto_vehiculo
- `D-0441` — fleet.gasto_vehiculo
- `D-0476` — fleet.liquidacion
- `D-0477` — fleet.liquidacion
- `D-0478` — fleet.liquidacion
- `D-0479` — fleet.liquidacion
- `D-0480` — fleet.liquidacion
- `D-0481` — fleet.liquidacion
- `D-0482` — fleet.liquidacion
- `D-0483` — fleet.liquidacion
- `D-0484` — fleet.liquidacion
- `D-0513` — fleet.liquidacion_ajuste
- `D-0514` — fleet.liquidacion_ajuste
- `D-0515` — fleet.liquidacion_ajuste
- `D-0525` — fleet.liquidacion_detalle
- `D-0535` — fleet.liquidacion_estado_historial
- `D-0536` — fleet.liquidacion_estado_historial
- `D-0537` — fleet.liquidacion_estado_historial
- `D-0546` — fleet.mantenimiento_vehiculo
- `D-0547` — fleet.mantenimiento_vehiculo
- `D-0562` — fleet.modelo
- `D-0573` — fleet.neumatico_historial_posicion
- `D-0574` — fleet.neumatico_historial_posicion
- `D-0575` — fleet.neumatico_historial_posicion
- `D-0576` — fleet.neumatico_historial_posicion
- `D-0594` — fleet.neumatico_imagen
- ... y 47 mas (ver JSON)

### indice_nombre_desalineado (1)

- `D-0822` — payment.billetera

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
| D-0450 | fleet.ingreso_turno.medio_pago | vocabulario_metodo_pago |
| D-0569 | fleet.neumatico_historial_posicion.created_at | timestamp_naive_vs_tz |
| D-0570 | fleet.neumatico_historial_posicion.fecha_desmontaje | timestamp_naive_vs_tz |
| D-0571 | fleet.neumatico_historial_posicion.fecha_montaje | timestamp_naive_vs_tz |
| D-0591 | fleet.neumatico_imagen.created_at | timestamp_naive_vs_tz |
| D-0592 | fleet.neumatico_imagen.fecha_subida | timestamp_naive_vs_tz |
| D-0609 | fleet.neumatico_medicion.created_at | timestamp_naive_vs_tz |
| D-0610 | fleet.neumatico_medicion.fecha_medicion | timestamp_naive_vs_tz |
| D-0625 | fleet.neumatico_operacion.created_at | timestamp_naive_vs_tz |
| D-0626 | fleet.neumatico_operacion.fecha_operacion | timestamp_naive_vs_tz |
| D-0627 | fleet.neumatico_operacion.updated_at | timestamp_naive_vs_tz |
| D-0644 | fleet.neumatico_operacion_detalle.created_at | timestamp_naive_vs_tz |
| D-0654 | fleet.neumatico_sugerencia.created_at | timestamp_naive_vs_tz |
| D-0655 | fleet.neumatico_sugerencia.fecha_atendida | timestamp_naive_vs_tz |
| D-0656 | fleet.neumatico_sugerencia.fecha_generacion | timestamp_naive_vs_tz |
| D-0657 | fleet.neumatico_sugerencia.updated_at | timestamp_naive_vs_tz |
| D-0677 | fleet.neumatico_vehiculo.created_at | timestamp_naive_vs_tz |
| D-0678 | fleet.neumatico_vehiculo.fecha_alta | timestamp_naive_vs_tz |
| D-0679 | fleet.neumatico_vehiculo.fecha_baja | timestamp_naive_vs_tz |
| D-0680 | fleet.neumatico_vehiculo.updated_at | timestamp_naive_vs_tz |
| D-1002 | tenant.control_base.latitud | orm_mal_db_bien |
| D-1003 | tenant.control_base.longitud | orm_mal_db_bien |

---

## Archivos generados

- `orm_diff.json` — datos completos.
- `orm_diff_reporte.md` — este informe.
- `orm_diff_acciones.csv` — CSV de acciones sugeridas.
