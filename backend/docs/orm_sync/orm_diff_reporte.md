# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-03T19:22:53.743060+00:00

## Resumen ejecutivo

- **1108 diferencias** en total.
- **Tier 1**: 175 items.
- **Tier 2**: 812 items.
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
| columna_falta | 37 |
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

- `D-0425` — declarado_por
- `D-0426` — medio_pago
- `D-0427` — transaccion_id
- `D-0714` — snapshot_dia_contractual
- `D-1037` — latitud
- `D-1038` — longitud
- `D-1074` — solicitado_en

### constraint_desalineada (10)

- `D-0147` — auth.usuario
- `D-0288` — fleet.chofer_vehiculo
- `D-0428` — fleet.ingreso_turno
- `D-0715` — fleet.turno_chofer
- `D-0740` — fleet.vehiculo
- `D-0888` — payment.transaccion
- `D-0967` — tenant.control_base
- `D-1016` — trip.calificacion
- `D-1039` — trip.historial_estado_viaje
- `D-1075` — trip.viaje_solicitado

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
- `D-0289` — fleet.chofer_vehiculo
- `D-0290` — fleet.chofer_vehiculo
- `D-0291` — fleet.chofer_vehiculo
- `D-0716` — fleet.turno_chofer
- `D-0717` — fleet.turno_chofer
- `D-0718` — fleet.turno_chofer
- `D-0741` — fleet.vehiculo
- `D-0889` — payment.transaccion
- `D-0890` — payment.transaccion
- `D-0891` — payment.transaccion
- `D-0968` — tenant.control_base
- `D-0969` — tenant.control_base
- `D-1017` — trip.calificacion
- `D-1018` — trip.calificacion
- `D-1019` — trip.calificacion
- `D-1040` — trip.historial_estado_viaje
- `D-1080` — trip.viaje_solicitado
- `D-1081` — trip.viaje_solicitado
- `D-1082` — trip.viaje_solicitado
- `D-1083` — trip.viaje_solicitado
- `D-1084` — trip.viaje_solicitado
- `D-1085` — trip.viaje_solicitado
- `D-1086` — trip.viaje_solicitado
- `D-1087` — trip.viaje_solicitado

### constraint_sobra (11)

- `D-0727` — fleet.turno_chofer
- `D-0743` — fleet.vehiculo
- `D-1020` — trip.calificacion
- `D-1098` — trip.viaje_solicitado
- `D-1099` — trip.viaje_solicitado
- `D-1100` — trip.viaje_solicitado
- `D-1101` — trip.viaje_solicitado
- `D-1102` — trip.viaje_solicitado
- `D-1103` — trip.viaje_solicitado
- `D-1104` — trip.viaje_solicitado
- `D-1105` — trip.viaje_solicitado

### indice_falta (18)

- `D-0155` — auth.usuario
- `D-0296` — fleet.chofer_vehiculo
- `D-0439` — fleet.ingreso_turno
- `D-0728` — fleet.turno_chofer
- `D-0729` — fleet.turno_chofer
- `D-0730` — fleet.turno_chofer
- `D-0731` — fleet.turno_chofer
- `D-0732` — fleet.turno_chofer
- `D-0751` — fleet.vehiculo
- `D-0752` — fleet.vehiculo
- `D-0753` — fleet.vehiculo
- `D-0754` — fleet.vehiculo
- `D-0893` — payment.transaccion
- `D-0972` — tenant.control_base
- `D-0973` — tenant.control_base
- `D-1027` — trip.calificacion
- `D-1042` — trip.historial_estado_viaje
- `D-1106` — trip.viaje_solicitado

### indice_nombre_desalineado (3)

- `D-0156` — auth.usuario
- `D-0755` — fleet.vehiculo
- `D-1108` — trip.viaje_solicitado

### indice_sobra (3)

- `D-0297` — fleet.chofer_vehiculo
- `D-0894` — payment.transaccion
- `D-1107` — trip.viaje_solicitado

### nullable_desalineado (25)

- `D-0142` — activo
- `D-0143` — created_at
- `D-0145` — tipo_usuario_id
- `D-0146` — updated_at
- `D-0278` — activo
- `D-0279` — calificacion_promedio
- `D-0280` — created_at
- `D-0281` — estado_laboral
- `D-0282` — estado_panico
- `D-0283` — total_calificaciones
- `D-0285` — ultima_conexion
- `D-0286` — updated_at
- `D-0287` — vehiculo_id
- `D-0733` — activo
- `D-0734` — capacidad
- `D-0735` — control_base_id
- `D-0736` — created_at
- `D-0737` — qr_activo
- `D-0738` — qr_uuid
- `D-0739` — updated_at
- `D-0884` — billetera_id
- `D-0885` — created_at
- `D-0959` — activo
- `D-0960` — created_at
- `D-0966` — updated_at

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

### tipo_desalineado (11)

- `D-0144` — password_hash
- `D-0284` — ubicacion
- `D-0886` — monto
- `D-0887` — saldo_despues
- `D-0961` — email
- `D-0962` — latitud
- `D-0963` — longitud
- `D-0964` — motivo_suspension
- `D-0965` — nombre
- `D-1072` — destino
- `D-1073` — origen

---

## Tier 2 — 812 items

### columna_falta (37)

| Tabla | Cantidad |
|---|---|
| tenant.configuracion_tenant | 23 |
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
- `D-0184` — corporate.cuenta_corriente
- `D-0205` — corporate.factura_corporativa
- `D-0233` — corporate.movimiento_cuenta
- `D-0249` — corporate.pago_corporativo
- `D-0262` — fleet.categoria_gasto
- `D-0301` — fleet.contrato_qr
- `D-0314` — fleet.contrato_vehiculo
- `D-0352` — fleet.documento_propietario
- `D-0363` — fleet.documento_vehiculo
- `D-0375` — fleet.documentos_chofer
- `D-0391` — fleet.foto_vehiculo
- `D-0399` — fleet.gasto_turno
- `D-0414` — fleet.gasto_vehiculo
- `D-0451` — fleet.liquidacion
- `D-0488` — fleet.liquidacion_ajuste
- `D-0500` — fleet.liquidacion_detalle
- `D-0510` — fleet.liquidacion_estado_historial
- `D-0521` — fleet.mantenimiento_vehiculo
- `D-0529` — fleet.marca
- `D-0537` — fleet.modelo
- `D-0548` — fleet.neumatico_historial_posicion
- `D-0569` — fleet.neumatico_imagen
- `D-0587` — fleet.neumatico_medicion
- `D-0604` — fleet.neumatico_operacion
- `D-0621` — fleet.neumatico_operacion_detalle
- `D-0634` — fleet.neumatico_sugerencia
- `D-0657` — fleet.neumatico_vehiculo
- `D-0681` — fleet.notificacion_vencimiento
- `D-0702` — fleet.propietario_vehiculo
- `D-0756` — geo.ciudad
- `D-0762` — geo.pais
- `D-0766` — geo.provincia
- `D-0771` — notification.notificacion
- `D-0783` — payment.billetera
- `D-0821` — payment.configuracion_tarifa
- `D-0835` — payment.configuracion_tarifa_vehiculo
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
- `D-0207` — corporate.factura_corporativa
- `D-0265` — fleet.categoria_gasto
- `D-0303` — fleet.contrato_qr
- `D-0407` — fleet.gasto_turno
- `D-0531` — fleet.marca
- `D-0860` — payment.metodo_pago
- `D-0898` — public.comercio
- `D-0956` — tenant.configuracion_tenant
- `D-0999` — tenant.factura

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
- `D-0832` — payment.configuracion_tarifa
- `D-1061` — trip.panico

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
- `D-0298` — activo
- `D-0299` — created_at
- `D-0300` — usos
- `D-0311` — created_at
- `D-0312` — estado_contrato
- `D-0351` — created_at
- `D-0361` — created_at
- `D-0362` — updated_at
- `D-0374` — subido_en
- `D-0388` — created_at
- `D-0389` — es_principal
- `D-0390` — orden
- `D-0411` — created_at
- `D-0413` — moneda
- `D-0440` — calculada_en
- `D-0441` — canon
- `D-0442` — comision_chofer
- `D-0443` — created_at
- `D-0444` — estado
- `D-0445` — monto_bruto
- `D-0446` — total_chofer
- `D-0447` — total_gastos
- `D-0448` — total_propietario
- `D-0449` — updated_at
- `D-0450` — version
- `D-0487` — created_at
- `D-0499` — created_at
- `D-0509` — created_at
- `D-0520` — created_at
- `D-0528` — created_at
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
- `D-0412` — km_registro
- `D-0545` — created_at
- `D-0546` — fecha_desmontaje
- `D-0547` — fecha_montaje
- `D-0567` — created_at
- `D-0568` — fecha_subida
- `D-0585` — created_at
- `D-0586` — fecha_medicion
- `D-0601` — created_at
- `D-0602` — fecha_operacion
- `D-0603` — updated_at
- `D-0620` — created_at
- `D-0630` — created_at
- `D-0631` — fecha_atendida
- `D-0632` — fecha_generacion
- `D-0633` — updated_at
- `D-0653` — created_at
- `D-0654` — fecha_alta
- `D-0655` — fecha_baja
- `D-0656` — updated_at
- `D-0780` — saldo
- `D-0792` — distancia_por_ficha
- `D-0796` — metros_por_ficha
- `D-0799` — modo_cobro_tiempo
- `D-0802` — precio_por_ficha
- `D-0804` — precio_por_km
- `D-0805` — precio_por_minuto
- `D-0806` — precio_por_minuto_espera
- `D-0808` — recargo_domingo
- `D-0810` — recargo_feriado
- `D-0811` — recargo_nocturno
- `D-0813` — seg_por_ficha_espera
- `D-0815` — tarifa_base
- `D-0817` — velocidad_referencia_kmh
- `D-0819` — velocidad_umbral_kmh
- `D-0833` — factor_precio
- `D-0834` — tipo_vehiculo_id
- `D-0848` — descuento
- `D-0851` — total
- `D-0852` — total_final
- `D-0867` — monto
- `D-0977` — latitud
- `D-0978` — limite_credito
- `D-0980` — longitud
- `D-0981` — tarifa_preferencial
- ... y 4 mas (ver JSON)

---

## Tier 3 — 120 items

### comment_desalineado (22)

- `D-0204` — estado
- `D-0232` — tipo_movimiento
- `D-0248` — estado
- `D-0313` — estado_contrato
- `D-0678` — entidad_tipo
- `D-0679` — nivel
- `D-0791` — descripcion
- `D-0793` — distancia_por_ficha
- `D-0794` — hora_fin_nocturno
- `D-0795` — hora_inicio_nocturno
- `D-0798` — modo_calculo
- `D-0801` — moneda
- `D-0803` — precio_por_ficha
- `D-0807` — precio_por_minuto_espera
- `D-0809` — recargo_domingo
- `D-0908` — resultado
- `D-0909` — tipo_qr
- `D-1053` — resuelto_en
- `D-1055` — usuario_id
- `D-1062` — distancia_por_ficha
- `D-1063` — precio_por_ficha
- `D-1064` — precio_por_minuto_espera

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
- `D-0263` — fleet.categoria_gasto
- `D-0315` — fleet.contrato_vehiculo
- `D-0316` — fleet.contrato_vehiculo
- `D-0317` — fleet.contrato_vehiculo
- `D-0318` — fleet.contrato_vehiculo
- `D-0364` — fleet.documento_vehiculo
- `D-0376` — fleet.documentos_chofer
- `D-0400` — fleet.gasto_turno
- `D-0401` — fleet.gasto_turno
- `D-0415` — fleet.gasto_vehiculo
- `D-0416` — fleet.gasto_vehiculo
- `D-0417` — fleet.gasto_vehiculo
- `D-0452` — fleet.liquidacion
- `D-0453` — fleet.liquidacion
- `D-0454` — fleet.liquidacion
- `D-0455` — fleet.liquidacion
- `D-0456` — fleet.liquidacion
- `D-0457` — fleet.liquidacion
- `D-0458` — fleet.liquidacion
- `D-0459` — fleet.liquidacion
- `D-0460` — fleet.liquidacion
- `D-0489` — fleet.liquidacion_ajuste
- `D-0490` — fleet.liquidacion_ajuste
- `D-0491` — fleet.liquidacion_ajuste
- `D-0501` — fleet.liquidacion_detalle
- `D-0511` — fleet.liquidacion_estado_historial
- `D-0512` — fleet.liquidacion_estado_historial
- `D-0513` — fleet.liquidacion_estado_historial
- `D-0522` — fleet.mantenimiento_vehiculo
- `D-0523` — fleet.mantenimiento_vehiculo
- `D-0538` — fleet.modelo
- `D-0549` — fleet.neumatico_historial_posicion
- `D-0550` — fleet.neumatico_historial_posicion
- `D-0551` — fleet.neumatico_historial_posicion
- `D-0552` — fleet.neumatico_historial_posicion
- `D-0570` — fleet.neumatico_imagen
- ... y 47 mas (ver JSON)

### indice_nombre_desalineado (1)

- `D-0789` — payment.billetera

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
| D-0426 | fleet.ingreso_turno.medio_pago | vocabulario_metodo_pago |
| D-0545 | fleet.neumatico_historial_posicion.created_at | timestamp_naive_vs_tz |
| D-0546 | fleet.neumatico_historial_posicion.fecha_desmontaje | timestamp_naive_vs_tz |
| D-0547 | fleet.neumatico_historial_posicion.fecha_montaje | timestamp_naive_vs_tz |
| D-0567 | fleet.neumatico_imagen.created_at | timestamp_naive_vs_tz |
| D-0568 | fleet.neumatico_imagen.fecha_subida | timestamp_naive_vs_tz |
| D-0585 | fleet.neumatico_medicion.created_at | timestamp_naive_vs_tz |
| D-0586 | fleet.neumatico_medicion.fecha_medicion | timestamp_naive_vs_tz |
| D-0601 | fleet.neumatico_operacion.created_at | timestamp_naive_vs_tz |
| D-0602 | fleet.neumatico_operacion.fecha_operacion | timestamp_naive_vs_tz |
| D-0603 | fleet.neumatico_operacion.updated_at | timestamp_naive_vs_tz |
| D-0620 | fleet.neumatico_operacion_detalle.created_at | timestamp_naive_vs_tz |
| D-0630 | fleet.neumatico_sugerencia.created_at | timestamp_naive_vs_tz |
| D-0631 | fleet.neumatico_sugerencia.fecha_atendida | timestamp_naive_vs_tz |
| D-0632 | fleet.neumatico_sugerencia.fecha_generacion | timestamp_naive_vs_tz |
| D-0633 | fleet.neumatico_sugerencia.updated_at | timestamp_naive_vs_tz |
| D-0653 | fleet.neumatico_vehiculo.created_at | timestamp_naive_vs_tz |
| D-0654 | fleet.neumatico_vehiculo.fecha_alta | timestamp_naive_vs_tz |
| D-0655 | fleet.neumatico_vehiculo.fecha_baja | timestamp_naive_vs_tz |
| D-0656 | fleet.neumatico_vehiculo.updated_at | timestamp_naive_vs_tz |
| D-0962 | tenant.control_base.latitud | orm_mal_db_bien |
| D-0963 | tenant.control_base.longitud | orm_mal_db_bien |

---

## Archivos generados

- `orm_diff.json` — datos completos.
- `orm_diff_reporte.md` — este informe.
- `orm_diff_acciones.csv` — CSV de acciones sugeridas.
