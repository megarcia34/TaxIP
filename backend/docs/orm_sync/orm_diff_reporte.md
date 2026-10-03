# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-03T19:28:35.718917+00:00

## Resumen ejecutivo

- **1104 diferencias** en total.
- **Tier 1**: 175 items.
- **Tier 2**: 808 items.
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
| columna_falta | 33 |
| comment_desalineado | 29 |
| constraint_sobra | 24 |
| tabla_falta | 10 |
| indice_sobra | 6 |
| indice_nombre_desalineado | 4 |
| schema_falta | 2 |
| tabla_sobra | 1 |

---

## Tier 1 — 175 items

### comment_desalineado (7)

- `D-0421` — declarado_por
- `D-0422` — medio_pago
- `D-0423` — transaccion_id
- `D-0710` — snapshot_dia_contractual
- `D-1033` — latitud
- `D-1034` — longitud
- `D-1070` — solicitado_en

### constraint_desalineada (10)

- `D-0147` — auth.usuario
- `D-0284` — fleet.chofer_vehiculo
- `D-0424` — fleet.ingreso_turno
- `D-0711` — fleet.turno_chofer
- `D-0736` — fleet.vehiculo
- `D-0884` — payment.transaccion
- `D-0963` — tenant.control_base
- `D-1012` — trip.calificacion
- `D-1035` — trip.historial_estado_viaje
- `D-1071` — trip.viaje_solicitado

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
- `D-0285` — fleet.chofer_vehiculo
- `D-0286` — fleet.chofer_vehiculo
- `D-0287` — fleet.chofer_vehiculo
- `D-0712` — fleet.turno_chofer
- `D-0713` — fleet.turno_chofer
- `D-0714` — fleet.turno_chofer
- `D-0737` — fleet.vehiculo
- `D-0885` — payment.transaccion
- `D-0886` — payment.transaccion
- `D-0887` — payment.transaccion
- `D-0964` — tenant.control_base
- `D-0965` — tenant.control_base
- `D-1013` — trip.calificacion
- `D-1014` — trip.calificacion
- `D-1015` — trip.calificacion
- `D-1036` — trip.historial_estado_viaje
- `D-1076` — trip.viaje_solicitado
- `D-1077` — trip.viaje_solicitado
- `D-1078` — trip.viaje_solicitado
- `D-1079` — trip.viaje_solicitado
- `D-1080` — trip.viaje_solicitado
- `D-1081` — trip.viaje_solicitado
- `D-1082` — trip.viaje_solicitado
- `D-1083` — trip.viaje_solicitado

### constraint_sobra (11)

- `D-0723` — fleet.turno_chofer
- `D-0739` — fleet.vehiculo
- `D-1016` — trip.calificacion
- `D-1094` — trip.viaje_solicitado
- `D-1095` — trip.viaje_solicitado
- `D-1096` — trip.viaje_solicitado
- `D-1097` — trip.viaje_solicitado
- `D-1098` — trip.viaje_solicitado
- `D-1099` — trip.viaje_solicitado
- `D-1100` — trip.viaje_solicitado
- `D-1101` — trip.viaje_solicitado

### indice_falta (18)

- `D-0155` — auth.usuario
- `D-0292` — fleet.chofer_vehiculo
- `D-0435` — fleet.ingreso_turno
- `D-0724` — fleet.turno_chofer
- `D-0725` — fleet.turno_chofer
- `D-0726` — fleet.turno_chofer
- `D-0727` — fleet.turno_chofer
- `D-0728` — fleet.turno_chofer
- `D-0747` — fleet.vehiculo
- `D-0748` — fleet.vehiculo
- `D-0749` — fleet.vehiculo
- `D-0750` — fleet.vehiculo
- `D-0889` — payment.transaccion
- `D-0968` — tenant.control_base
- `D-0969` — tenant.control_base
- `D-1023` — trip.calificacion
- `D-1038` — trip.historial_estado_viaje
- `D-1102` — trip.viaje_solicitado

### indice_nombre_desalineado (3)

- `D-0156` — auth.usuario
- `D-0751` — fleet.vehiculo
- `D-1104` — trip.viaje_solicitado

### indice_sobra (3)

- `D-0293` — fleet.chofer_vehiculo
- `D-0890` — payment.transaccion
- `D-1103` — trip.viaje_solicitado

### nullable_desalineado (25)

- `D-0142` — activo
- `D-0143` — created_at
- `D-0145` — tipo_usuario_id
- `D-0146` — updated_at
- `D-0274` — activo
- `D-0275` — calificacion_promedio
- `D-0276` — created_at
- `D-0277` — estado_laboral
- `D-0278` — estado_panico
- `D-0279` — total_calificaciones
- `D-0281` — ultima_conexion
- `D-0282` — updated_at
- `D-0283` — vehiculo_id
- `D-0729` — activo
- `D-0730` — capacidad
- `D-0731` — control_base_id
- `D-0732` — created_at
- `D-0733` — qr_activo
- `D-0734` — qr_uuid
- `D-0735` — updated_at
- `D-0880` — billetera_id
- `D-0881` — created_at
- `D-0955` — activo
- `D-0956` — created_at
- `D-0962` — updated_at

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

### tipo_desalineado (11)

- `D-0144` — password_hash
- `D-0280` — ubicacion
- `D-0882` — monto
- `D-0883` — saldo_despues
- `D-0957` — email
- `D-0958` — latitud
- `D-0959` — longitud
- `D-0960` — motivo_suspension
- `D-0961` — nombre
- `D-1068` — destino
- `D-1069` — origen

---

## Tier 2 — 808 items

### columna_falta (33)

| Tabla | Cantidad |
|---|---|
| tenant.configuracion_tenant | 23 |
| corporate.movimiento_cuenta | 6 |
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
- `D-0184` — corporate.cuenta_corriente
- `D-0201` — corporate.factura_corporativa
- `D-0229` — corporate.movimiento_cuenta
- `D-0245` — corporate.pago_corporativo
- `D-0258` — fleet.categoria_gasto
- `D-0297` — fleet.contrato_qr
- `D-0310` — fleet.contrato_vehiculo
- `D-0348` — fleet.documento_propietario
- `D-0359` — fleet.documento_vehiculo
- `D-0371` — fleet.documentos_chofer
- `D-0387` — fleet.foto_vehiculo
- `D-0395` — fleet.gasto_turno
- `D-0410` — fleet.gasto_vehiculo
- `D-0447` — fleet.liquidacion
- `D-0484` — fleet.liquidacion_ajuste
- `D-0496` — fleet.liquidacion_detalle
- `D-0506` — fleet.liquidacion_estado_historial
- `D-0517` — fleet.mantenimiento_vehiculo
- `D-0525` — fleet.marca
- `D-0533` — fleet.modelo
- `D-0544` — fleet.neumatico_historial_posicion
- `D-0565` — fleet.neumatico_imagen
- `D-0583` — fleet.neumatico_medicion
- `D-0600` — fleet.neumatico_operacion
- `D-0617` — fleet.neumatico_operacion_detalle
- `D-0630` — fleet.neumatico_sugerencia
- `D-0653` — fleet.neumatico_vehiculo
- `D-0677` — fleet.notificacion_vencimiento
- `D-0698` — fleet.propietario_vehiculo
- `D-0752` — geo.ciudad
- `D-0758` — geo.pais
- `D-0762` — geo.provincia
- `D-0767` — notification.notificacion
- `D-0779` — payment.billetera
- `D-0817` — payment.configuracion_tarifa
- `D-0831` — payment.configuracion_tarifa_vehiculo
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
- `D-0187` — corporate.cuenta_corriente
- `D-0203` — corporate.factura_corporativa
- `D-0261` — fleet.categoria_gasto
- `D-0299` — fleet.contrato_qr
- `D-0403` — fleet.gasto_turno
- `D-0527` — fleet.marca
- `D-0856` — payment.metodo_pago
- `D-0894` — public.comercio
- `D-0952` — tenant.configuracion_tenant
- `D-0995` — tenant.factura

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
- `D-0828` — payment.configuracion_tarifa
- `D-1057` — trip.panico

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
- `D-0294` — activo
- `D-0295` — created_at
- `D-0296` — usos
- `D-0307` — created_at
- `D-0308` — estado_contrato
- `D-0347` — created_at
- `D-0357` — created_at
- `D-0358` — updated_at
- `D-0370` — subido_en
- `D-0384` — created_at
- `D-0385` — es_principal
- `D-0386` — orden
- `D-0407` — created_at
- `D-0409` — moneda
- `D-0436` — calculada_en
- `D-0437` — canon
- `D-0438` — comision_chofer
- `D-0439` — created_at
- `D-0440` — estado
- `D-0441` — monto_bruto
- `D-0442` — total_chofer
- `D-0443` — total_gastos
- `D-0444` — total_propietario
- `D-0445` — updated_at
- `D-0446` — version
- `D-0483` — created_at
- `D-0495` — created_at
- `D-0505` — created_at
- `D-0516` — created_at
- `D-0524` — created_at
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
- `D-0408` — km_registro
- `D-0541` — created_at
- `D-0542` — fecha_desmontaje
- `D-0543` — fecha_montaje
- `D-0563` — created_at
- `D-0564` — fecha_subida
- `D-0581` — created_at
- `D-0582` — fecha_medicion
- `D-0597` — created_at
- `D-0598` — fecha_operacion
- `D-0599` — updated_at
- `D-0616` — created_at
- `D-0626` — created_at
- `D-0627` — fecha_atendida
- `D-0628` — fecha_generacion
- `D-0629` — updated_at
- `D-0649` — created_at
- `D-0650` — fecha_alta
- `D-0651` — fecha_baja
- `D-0652` — updated_at
- `D-0776` — saldo
- `D-0788` — distancia_por_ficha
- `D-0792` — metros_por_ficha
- `D-0795` — modo_cobro_tiempo
- `D-0798` — precio_por_ficha
- `D-0800` — precio_por_km
- `D-0801` — precio_por_minuto
- `D-0802` — precio_por_minuto_espera
- `D-0804` — recargo_domingo
- `D-0806` — recargo_feriado
- `D-0807` — recargo_nocturno
- `D-0809` — seg_por_ficha_espera
- `D-0811` — tarifa_base
- `D-0813` — velocidad_referencia_kmh
- `D-0815` — velocidad_umbral_kmh
- `D-0829` — factor_precio
- `D-0830` — tipo_vehiculo_id
- `D-0844` — descuento
- `D-0847` — total
- `D-0848` — total_final
- `D-0863` — monto
- `D-0973` — latitud
- `D-0974` — limite_credito
- `D-0976` — longitud
- `D-0977` — tarifa_preferencial
- ... y 4 mas (ver JSON)

---

## Tier 3 — 120 items

### comment_desalineado (22)

- `D-0200` — estado
- `D-0228` — tipo_movimiento
- `D-0244` — estado
- `D-0309` — estado_contrato
- `D-0674` — entidad_tipo
- `D-0675` — nivel
- `D-0787` — descripcion
- `D-0789` — distancia_por_ficha
- `D-0790` — hora_fin_nocturno
- `D-0791` — hora_inicio_nocturno
- `D-0794` — modo_calculo
- `D-0797` — moneda
- `D-0799` — precio_por_ficha
- `D-0803` — precio_por_minuto_espera
- `D-0805` — recargo_domingo
- `D-0904` — resultado
- `D-0905` — tipo_qr
- `D-1049` — resuelto_en
- `D-1051` — usuario_id
- `D-1058` — distancia_por_ficha
- `D-1059` — precio_por_ficha
- `D-1060` — precio_por_minuto_espera

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
- `D-0259` — fleet.categoria_gasto
- `D-0311` — fleet.contrato_vehiculo
- `D-0312` — fleet.contrato_vehiculo
- `D-0313` — fleet.contrato_vehiculo
- `D-0314` — fleet.contrato_vehiculo
- `D-0360` — fleet.documento_vehiculo
- `D-0372` — fleet.documentos_chofer
- `D-0396` — fleet.gasto_turno
- `D-0397` — fleet.gasto_turno
- `D-0411` — fleet.gasto_vehiculo
- `D-0412` — fleet.gasto_vehiculo
- `D-0413` — fleet.gasto_vehiculo
- `D-0448` — fleet.liquidacion
- `D-0449` — fleet.liquidacion
- `D-0450` — fleet.liquidacion
- `D-0451` — fleet.liquidacion
- `D-0452` — fleet.liquidacion
- `D-0453` — fleet.liquidacion
- `D-0454` — fleet.liquidacion
- `D-0455` — fleet.liquidacion
- `D-0456` — fleet.liquidacion
- `D-0485` — fleet.liquidacion_ajuste
- `D-0486` — fleet.liquidacion_ajuste
- `D-0487` — fleet.liquidacion_ajuste
- `D-0497` — fleet.liquidacion_detalle
- `D-0507` — fleet.liquidacion_estado_historial
- `D-0508` — fleet.liquidacion_estado_historial
- `D-0509` — fleet.liquidacion_estado_historial
- `D-0518` — fleet.mantenimiento_vehiculo
- `D-0519` — fleet.mantenimiento_vehiculo
- `D-0534` — fleet.modelo
- `D-0545` — fleet.neumatico_historial_posicion
- `D-0546` — fleet.neumatico_historial_posicion
- `D-0547` — fleet.neumatico_historial_posicion
- `D-0548` — fleet.neumatico_historial_posicion
- `D-0566` — fleet.neumatico_imagen
- ... y 47 mas (ver JSON)

### indice_nombre_desalineado (1)

- `D-0785` — payment.billetera

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
| D-0422 | fleet.ingreso_turno.medio_pago | vocabulario_metodo_pago |
| D-0541 | fleet.neumatico_historial_posicion.created_at | timestamp_naive_vs_tz |
| D-0542 | fleet.neumatico_historial_posicion.fecha_desmontaje | timestamp_naive_vs_tz |
| D-0543 | fleet.neumatico_historial_posicion.fecha_montaje | timestamp_naive_vs_tz |
| D-0563 | fleet.neumatico_imagen.created_at | timestamp_naive_vs_tz |
| D-0564 | fleet.neumatico_imagen.fecha_subida | timestamp_naive_vs_tz |
| D-0581 | fleet.neumatico_medicion.created_at | timestamp_naive_vs_tz |
| D-0582 | fleet.neumatico_medicion.fecha_medicion | timestamp_naive_vs_tz |
| D-0597 | fleet.neumatico_operacion.created_at | timestamp_naive_vs_tz |
| D-0598 | fleet.neumatico_operacion.fecha_operacion | timestamp_naive_vs_tz |
| D-0599 | fleet.neumatico_operacion.updated_at | timestamp_naive_vs_tz |
| D-0616 | fleet.neumatico_operacion_detalle.created_at | timestamp_naive_vs_tz |
| D-0626 | fleet.neumatico_sugerencia.created_at | timestamp_naive_vs_tz |
| D-0627 | fleet.neumatico_sugerencia.fecha_atendida | timestamp_naive_vs_tz |
| D-0628 | fleet.neumatico_sugerencia.fecha_generacion | timestamp_naive_vs_tz |
| D-0629 | fleet.neumatico_sugerencia.updated_at | timestamp_naive_vs_tz |
| D-0649 | fleet.neumatico_vehiculo.created_at | timestamp_naive_vs_tz |
| D-0650 | fleet.neumatico_vehiculo.fecha_alta | timestamp_naive_vs_tz |
| D-0651 | fleet.neumatico_vehiculo.fecha_baja | timestamp_naive_vs_tz |
| D-0652 | fleet.neumatico_vehiculo.updated_at | timestamp_naive_vs_tz |
| D-0958 | tenant.control_base.latitud | orm_mal_db_bien |
| D-0959 | tenant.control_base.longitud | orm_mal_db_bien |

---

## Archivos generados

- `orm_diff.json` — datos completos.
- `orm_diff_reporte.md` — este informe.
- `orm_diff_acciones.csv` — CSV de acciones sugeridas.
