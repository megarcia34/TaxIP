# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-03T19:06:52.514049+00:00

## Resumen ejecutivo

- **1131 diferencias** en total.
- **Tier 1**: 176 items.
- **Tier 2**: 834 items.
- **Tier 3**: 120 items.
- **Tier 4**: 1 items.
- **24 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| constraint_falta | 428 |
| indice_falta | 192 |
| constraint_nombre_desalineado | 124 |
| nullable_desalineado | 115 |
| tipo_desalineado | 76 |
| constraint_desalineada | 72 |
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

- `D-0446` — declarado_por
- `D-0447` — medio_pago
- `D-0448` — transaccion_id
- `D-0735` — snapshot_dia_contractual
- `D-1059` — latitud
- `D-1060` — longitud
- `D-1096` — solicitado_en

### constraint_desalineada (10)

- `D-0147` — auth.usuario
- `D-0309` — fleet.chofer_vehiculo
- `D-0449` — fleet.ingreso_turno
- `D-0736` — fleet.turno_chofer
- `D-0761` — fleet.vehiculo
- `D-0909` — payment.transaccion
- `D-0988` — tenant.control_base
- `D-1037` — trip.calificacion
- `D-1061` — trip.historial_estado_viaje
- `D-1097` — trip.viaje_solicitado

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
- `D-0310` — fleet.chofer_vehiculo
- `D-0311` — fleet.chofer_vehiculo
- `D-0312` — fleet.chofer_vehiculo
- `D-0737` — fleet.turno_chofer
- `D-0738` — fleet.turno_chofer
- `D-0739` — fleet.turno_chofer
- `D-0762` — fleet.vehiculo
- `D-0910` — payment.transaccion
- `D-0911` — payment.transaccion
- `D-0912` — payment.transaccion
- `D-0989` — tenant.control_base
- `D-0990` — tenant.control_base
- `D-1038` — trip.calificacion
- `D-1039` — trip.calificacion
- `D-1040` — trip.calificacion
- `D-1062` — trip.historial_estado_viaje
- `D-1102` — trip.viaje_solicitado
- `D-1103` — trip.viaje_solicitado
- `D-1104` — trip.viaje_solicitado
- `D-1105` — trip.viaje_solicitado
- `D-1106` — trip.viaje_solicitado
- `D-1107` — trip.viaje_solicitado
- `D-1108` — trip.viaje_solicitado
- `D-1109` — trip.viaje_solicitado

### constraint_sobra (11)

- `D-0748` — fleet.turno_chofer
- `D-0764` — fleet.vehiculo
- `D-1041` — trip.calificacion
- `D-1120` — trip.viaje_solicitado
- `D-1121` — trip.viaje_solicitado
- `D-1122` — trip.viaje_solicitado
- `D-1123` — trip.viaje_solicitado
- `D-1124` — trip.viaje_solicitado
- `D-1125` — trip.viaje_solicitado
- `D-1126` — trip.viaje_solicitado
- `D-1127` — trip.viaje_solicitado

### indice_falta (18)

- `D-0155` — auth.usuario
- `D-0317` — fleet.chofer_vehiculo
- `D-0460` — fleet.ingreso_turno
- `D-0749` — fleet.turno_chofer
- `D-0750` — fleet.turno_chofer
- `D-0751` — fleet.turno_chofer
- `D-0752` — fleet.turno_chofer
- `D-0753` — fleet.turno_chofer
- `D-0772` — fleet.vehiculo
- `D-0773` — fleet.vehiculo
- `D-0774` — fleet.vehiculo
- `D-0775` — fleet.vehiculo
- `D-0914` — payment.transaccion
- `D-0993` — tenant.control_base
- `D-0994` — tenant.control_base
- `D-1048` — trip.calificacion
- `D-1064` — trip.historial_estado_viaje
- `D-1128` — trip.viaje_solicitado

### indice_nombre_desalineado (4)

- `D-0156` — auth.usuario
- `D-0776` — fleet.vehiculo
- `D-1130` — trip.viaje_solicitado
- `D-1131` — trip.viaje_solicitado

### indice_sobra (3)

- `D-0318` — fleet.chofer_vehiculo
- `D-0915` — payment.transaccion
- `D-1129` — trip.viaje_solicitado

### nullable_desalineado (25)

- `D-0142` — activo
- `D-0143` — created_at
- `D-0145` — tipo_usuario_id
- `D-0146` — updated_at
- `D-0299` — activo
- `D-0300` — calificacion_promedio
- `D-0301` — created_at
- `D-0302` — estado_laboral
- `D-0303` — estado_panico
- `D-0304` — total_calificaciones
- `D-0306` — ultima_conexion
- `D-0307` — updated_at
- `D-0308` — vehiculo_id
- `D-0754` — activo
- `D-0755` — capacidad
- `D-0756` — control_base_id
- `D-0757` — created_at
- `D-0758` — qr_activo
- `D-0759` — qr_uuid
- `D-0760` — updated_at
- `D-0905` — billetera_id
- `D-0906` — created_at
- `D-0980` — activo
- `D-0981` — created_at
- `D-0987` — updated_at

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

### tipo_desalineado (11)

- `D-0144` — password_hash
- `D-0305` — ubicacion
- `D-0907` — monto
- `D-0908` — saldo_despues
- `D-0982` — email
- `D-0983` — latitud
- `D-0984` — longitud
- `D-0985` — motivo_suspension
- `D-0986` — nombre
- `D-1094` — destino
- `D-1095` — origen

---

## Tier 2 — 834 items

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
- `D-0197` — corporate.cuenta_corriente
- `D-0222` — corporate.factura_corporativa
- `D-0253` — corporate.movimiento_cuenta
- `D-0270` — corporate.pago_corporativo
- `D-0283` — fleet.categoria_gasto
- `D-0322` — fleet.contrato_qr
- `D-0335` — fleet.contrato_vehiculo
- `D-0373` — fleet.documento_propietario
- `D-0384` — fleet.documento_vehiculo
- `D-0396` — fleet.documentos_chofer
- `D-0412` — fleet.foto_vehiculo
- `D-0420` — fleet.gasto_turno
- `D-0435` — fleet.gasto_vehiculo
- `D-0472` — fleet.liquidacion
- `D-0509` — fleet.liquidacion_ajuste
- `D-0521` — fleet.liquidacion_detalle
- `D-0531` — fleet.liquidacion_estado_historial
- `D-0542` — fleet.mantenimiento_vehiculo
- `D-0550` — fleet.marca
- `D-0558` — fleet.modelo
- `D-0569` — fleet.neumatico_historial_posicion
- `D-0590` — fleet.neumatico_imagen
- `D-0608` — fleet.neumatico_medicion
- `D-0625` — fleet.neumatico_operacion
- `D-0642` — fleet.neumatico_operacion_detalle
- `D-0655` — fleet.neumatico_sugerencia
- `D-0678` — fleet.neumatico_vehiculo
- `D-0702` — fleet.notificacion_vencimiento
- `D-0723` — fleet.propietario_vehiculo
- `D-0777` — geo.ciudad
- `D-0783` — geo.pais
- `D-0787` — geo.provincia
- `D-0792` — notification.notificacion
- `D-0804` — payment.billetera
- `D-0842` — payment.configuracion_tarifa
- `D-0856` — payment.configuracion_tarifa_vehiculo
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
- `D-0200` — corporate.cuenta_corriente
- `D-0224` — corporate.factura_corporativa
- `D-0286` — fleet.categoria_gasto
- `D-0324` — fleet.contrato_qr
- `D-0428` — fleet.gasto_turno
- `D-0552` — fleet.marca
- `D-0881` — payment.metodo_pago
- `D-0919` — public.comercio
- `D-0977` — tenant.configuracion_tenant
- `D-1020` — tenant.factura

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
- `D-0853` — payment.configuracion_tarifa
- `D-1083` — trip.panico

### nullable_desalineado (90)

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
- `D-0319` — activo
- `D-0320` — created_at
- `D-0321` — usos
- `D-0332` — created_at
- `D-0333` — estado_contrato
- `D-0372` — created_at
- `D-0382` — created_at
- `D-0383` — updated_at
- `D-0395` — subido_en
- `D-0409` — created_at
- `D-0410` — es_principal
- `D-0411` — orden
- `D-0432` — created_at
- `D-0434` — moneda
- `D-0461` — calculada_en
- `D-0462` — canon
- `D-0463` — comision_chofer
- `D-0464` — created_at
- `D-0465` — estado
- `D-0466` — monto_bruto
- `D-0467` — total_chofer
- `D-0468` — total_gastos
- `D-0469` — total_propietario
- `D-0470` — updated_at
- `D-0471` — version
- `D-0508` — created_at
- `D-0520` — created_at
- `D-0530` — created_at
- `D-0541` — created_at
- `D-0549` — created_at
- ... y 40 mas (ver JSON)

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

### tipo_desalineado (65)

- `D-0071` — latitud
- `D-0072` — longitud
- `D-0124` — facturado_total
- `D-0168` — fecha_fin
- `D-0169` — fecha_inicio
- `D-0194` — limite_credito
- `D-0195` — saldo_actual
- `D-0196` — saldo_disponible
- `D-0217` — descuento
- `D-0219` — iva
- `D-0220` — subtotal
- `D-0221` — total
- `D-0249` — monto
- `D-0250` — saldo_anterior
- `D-0251` — saldo_nuevo
- `D-0269` — monto
- `D-0433` — km_registro
- `D-0566` — created_at
- `D-0567` — fecha_desmontaje
- `D-0568` — fecha_montaje
- `D-0588` — created_at
- `D-0589` — fecha_subida
- `D-0606` — created_at
- `D-0607` — fecha_medicion
- `D-0622` — created_at
- `D-0623` — fecha_operacion
- `D-0624` — updated_at
- `D-0641` — created_at
- `D-0651` — created_at
- `D-0652` — fecha_atendida
- `D-0653` — fecha_generacion
- `D-0654` — updated_at
- `D-0674` — created_at
- `D-0675` — fecha_alta
- `D-0676` — fecha_baja
- `D-0677` — updated_at
- `D-0801` — saldo
- `D-0813` — distancia_por_ficha
- `D-0817` — metros_por_ficha
- `D-0820` — modo_cobro_tiempo
- `D-0823` — precio_por_ficha
- `D-0825` — precio_por_km
- `D-0826` — precio_por_minuto
- `D-0827` — precio_por_minuto_espera
- `D-0829` — recargo_domingo
- `D-0831` — recargo_feriado
- `D-0832` — recargo_nocturno
- `D-0834` — seg_por_ficha_espera
- `D-0836` — tarifa_base
- `D-0838` — velocidad_referencia_kmh
- ... y 15 mas (ver JSON)

---

## Tier 3 — 120 items

### comment_desalineado (22)

- `D-0218` — estado
- `D-0252` — tipo_movimiento
- `D-0268` — estado
- `D-0334` — estado_contrato
- `D-0699` — entidad_tipo
- `D-0700` — nivel
- `D-0812` — descripcion
- `D-0814` — distancia_por_ficha
- `D-0815` — hora_fin_nocturno
- `D-0816` — hora_inicio_nocturno
- `D-0819` — modo_calculo
- `D-0822` — moneda
- `D-0824` — precio_por_ficha
- `D-0828` — precio_por_minuto_espera
- `D-0830` — recargo_domingo
- `D-0929` — resultado
- `D-0930` — tipo_qr
- `D-1075` — resuelto_en
- `D-1077` — usuario_id
- `D-1084` — distancia_por_ficha
- `D-1085` — precio_por_ficha
- `D-1086` — precio_por_minuto_espera

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
- `D-0284` — fleet.categoria_gasto
- `D-0336` — fleet.contrato_vehiculo
- `D-0337` — fleet.contrato_vehiculo
- `D-0338` — fleet.contrato_vehiculo
- `D-0339` — fleet.contrato_vehiculo
- `D-0385` — fleet.documento_vehiculo
- `D-0397` — fleet.documentos_chofer
- `D-0421` — fleet.gasto_turno
- `D-0422` — fleet.gasto_turno
- `D-0436` — fleet.gasto_vehiculo
- `D-0437` — fleet.gasto_vehiculo
- `D-0438` — fleet.gasto_vehiculo
- `D-0473` — fleet.liquidacion
- `D-0474` — fleet.liquidacion
- `D-0475` — fleet.liquidacion
- `D-0476` — fleet.liquidacion
- `D-0477` — fleet.liquidacion
- `D-0478` — fleet.liquidacion
- `D-0479` — fleet.liquidacion
- `D-0480` — fleet.liquidacion
- `D-0481` — fleet.liquidacion
- `D-0510` — fleet.liquidacion_ajuste
- `D-0511` — fleet.liquidacion_ajuste
- `D-0512` — fleet.liquidacion_ajuste
- `D-0522` — fleet.liquidacion_detalle
- `D-0532` — fleet.liquidacion_estado_historial
- `D-0533` — fleet.liquidacion_estado_historial
- `D-0534` — fleet.liquidacion_estado_historial
- `D-0543` — fleet.mantenimiento_vehiculo
- `D-0544` — fleet.mantenimiento_vehiculo
- `D-0559` — fleet.modelo
- `D-0570` — fleet.neumatico_historial_posicion
- `D-0571` — fleet.neumatico_historial_posicion
- `D-0572` — fleet.neumatico_historial_posicion
- `D-0573` — fleet.neumatico_historial_posicion
- `D-0591` — fleet.neumatico_imagen
- ... y 47 mas (ver JSON)

### indice_nombre_desalineado (1)

- `D-0810` — payment.billetera

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
| D-0447 | fleet.ingreso_turno.medio_pago | vocabulario_metodo_pago |
| D-0566 | fleet.neumatico_historial_posicion.created_at | timestamp_naive_vs_tz |
| D-0567 | fleet.neumatico_historial_posicion.fecha_desmontaje | timestamp_naive_vs_tz |
| D-0568 | fleet.neumatico_historial_posicion.fecha_montaje | timestamp_naive_vs_tz |
| D-0588 | fleet.neumatico_imagen.created_at | timestamp_naive_vs_tz |
| D-0589 | fleet.neumatico_imagen.fecha_subida | timestamp_naive_vs_tz |
| D-0606 | fleet.neumatico_medicion.created_at | timestamp_naive_vs_tz |
| D-0607 | fleet.neumatico_medicion.fecha_medicion | timestamp_naive_vs_tz |
| D-0622 | fleet.neumatico_operacion.created_at | timestamp_naive_vs_tz |
| D-0623 | fleet.neumatico_operacion.fecha_operacion | timestamp_naive_vs_tz |
| D-0624 | fleet.neumatico_operacion.updated_at | timestamp_naive_vs_tz |
| D-0641 | fleet.neumatico_operacion_detalle.created_at | timestamp_naive_vs_tz |
| D-0651 | fleet.neumatico_sugerencia.created_at | timestamp_naive_vs_tz |
| D-0652 | fleet.neumatico_sugerencia.fecha_atendida | timestamp_naive_vs_tz |
| D-0653 | fleet.neumatico_sugerencia.fecha_generacion | timestamp_naive_vs_tz |
| D-0654 | fleet.neumatico_sugerencia.updated_at | timestamp_naive_vs_tz |
| D-0674 | fleet.neumatico_vehiculo.created_at | timestamp_naive_vs_tz |
| D-0675 | fleet.neumatico_vehiculo.fecha_alta | timestamp_naive_vs_tz |
| D-0676 | fleet.neumatico_vehiculo.fecha_baja | timestamp_naive_vs_tz |
| D-0677 | fleet.neumatico_vehiculo.updated_at | timestamp_naive_vs_tz |
| D-0983 | tenant.control_base.latitud | orm_mal_db_bien |
| D-0984 | tenant.control_base.longitud | orm_mal_db_bien |

---

## Archivos generados

- `orm_diff.json` — datos completos.
- `orm_diff_reporte.md` — este informe.
- `orm_diff_acciones.csv` — CSV de acciones sugeridas.
