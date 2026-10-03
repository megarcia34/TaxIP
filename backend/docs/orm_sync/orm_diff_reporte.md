# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-03T15:51:38.812118+00:00

## Resumen ejecutivo

- **1160 diferencias** en total.
- **Tier 1**: 176 items.
- **Tier 2**: 863 items.
- **Tier 3**: 120 items.
- **Tier 4**: 1 items.
- **24 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| constraint_falta | 428 |
| indice_falta | 192 |
| nullable_desalineado | 132 |
| constraint_nombre_desalineado | 124 |
| tipo_desalineado | 83 |
| constraint_desalineada | 72 |
| columna_falta | 47 |
| comment_desalineado | 29 |
| constraint_sobra | 24 |
| tabla_falta | 10 |
| indice_sobra | 9 |
| indice_nombre_desalineado | 5 |
| schema_falta | 2 |
| columna_sobra | 2 |
| tabla_sobra | 1 |

---

## Tier 1 — 176 items

### comment_desalineado (7)

- `D-0459` — declarado_por
- `D-0460` — medio_pago
- `D-0461` — transaccion_id
- `D-0748` — snapshot_dia_contractual
- `D-1088` — latitud
- `D-1089` — longitud
- `D-1125` — solicitado_en

### constraint_desalineada (10)

- `D-0160` — auth.usuario
- `D-0322` — fleet.chofer_vehiculo
- `D-0462` — fleet.ingreso_turno
- `D-0749` — fleet.turno_chofer
- `D-0774` — fleet.vehiculo
- `D-0931` — payment.transaccion
- `D-1017` — tenant.control_base
- `D-1066` — trip.calificacion
- `D-1090` — trip.historial_estado_viaje
- `D-1126` — trip.viaje_solicitado

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

- `D-0161` — auth.usuario
- `D-0162` — auth.usuario
- `D-0163` — auth.usuario
- `D-0323` — fleet.chofer_vehiculo
- `D-0324` — fleet.chofer_vehiculo
- `D-0325` — fleet.chofer_vehiculo
- `D-0750` — fleet.turno_chofer
- `D-0751` — fleet.turno_chofer
- `D-0752` — fleet.turno_chofer
- `D-0775` — fleet.vehiculo
- `D-0932` — payment.transaccion
- `D-0933` — payment.transaccion
- `D-0934` — payment.transaccion
- `D-1018` — tenant.control_base
- `D-1019` — tenant.control_base
- `D-1067` — trip.calificacion
- `D-1068` — trip.calificacion
- `D-1069` — trip.calificacion
- `D-1091` — trip.historial_estado_viaje
- `D-1131` — trip.viaje_solicitado
- `D-1132` — trip.viaje_solicitado
- `D-1133` — trip.viaje_solicitado
- `D-1134` — trip.viaje_solicitado
- `D-1135` — trip.viaje_solicitado
- `D-1136` — trip.viaje_solicitado
- `D-1137` — trip.viaje_solicitado
- `D-1138` — trip.viaje_solicitado

### constraint_sobra (11)

- `D-0761` — fleet.turno_chofer
- `D-0777` — fleet.vehiculo
- `D-1070` — trip.calificacion
- `D-1149` — trip.viaje_solicitado
- `D-1150` — trip.viaje_solicitado
- `D-1151` — trip.viaje_solicitado
- `D-1152` — trip.viaje_solicitado
- `D-1153` — trip.viaje_solicitado
- `D-1154` — trip.viaje_solicitado
- `D-1155` — trip.viaje_solicitado
- `D-1156` — trip.viaje_solicitado

### indice_falta (18)

- `D-0168` — auth.usuario
- `D-0330` — fleet.chofer_vehiculo
- `D-0473` — fleet.ingreso_turno
- `D-0762` — fleet.turno_chofer
- `D-0763` — fleet.turno_chofer
- `D-0764` — fleet.turno_chofer
- `D-0765` — fleet.turno_chofer
- `D-0766` — fleet.turno_chofer
- `D-0785` — fleet.vehiculo
- `D-0786` — fleet.vehiculo
- `D-0787` — fleet.vehiculo
- `D-0788` — fleet.vehiculo
- `D-0936` — payment.transaccion
- `D-1022` — tenant.control_base
- `D-1023` — tenant.control_base
- `D-1077` — trip.calificacion
- `D-1093` — trip.historial_estado_viaje
- `D-1157` — trip.viaje_solicitado

### indice_nombre_desalineado (4)

- `D-0169` — auth.usuario
- `D-0789` — fleet.vehiculo
- `D-1159` — trip.viaje_solicitado
- `D-1160` — trip.viaje_solicitado

### indice_sobra (3)

- `D-0331` — fleet.chofer_vehiculo
- `D-0937` — payment.transaccion
- `D-1158` — trip.viaje_solicitado

### nullable_desalineado (25)

- `D-0155` — activo
- `D-0156` — created_at
- `D-0158` — tipo_usuario_id
- `D-0159` — updated_at
- `D-0312` — activo
- `D-0313` — calificacion_promedio
- `D-0314` — created_at
- `D-0315` — estado_laboral
- `D-0316` — estado_panico
- `D-0317` — total_calificaciones
- `D-0319` — ultima_conexion
- `D-0320` — updated_at
- `D-0321` — vehiculo_id
- `D-0767` — activo
- `D-0768` — capacidad
- `D-0769` — control_base_id
- `D-0770` — created_at
- `D-0771` — qr_activo
- `D-0772` — qr_uuid
- `D-0773` — updated_at
- `D-0927` — billetera_id
- `D-0928` — created_at
- `D-1009` — activo
- `D-1010` — created_at
- `D-1016` — updated_at

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

### tipo_desalineado (11)

- `D-0157` — password_hash
- `D-0318` — ubicacion
- `D-0929` — monto
- `D-0930` — saldo_despues
- `D-1011` — email
- `D-1012` — latitud
- `D-1013` — longitud
- `D-1014` — motivo_suspension
- `D-1015` — nombre
- `D-1123` — destino
- `D-1124` — origen

---

## Tier 2 — 863 items

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

- `D-0040` — ubicacion
- `D-0041` — velocidad_kmh

### constraint_desalineada (62)

- `D-0020` — audit.alerta_desvio
- `D-0031` — audit.log_acciones
- `D-0046` — audit.log_gps
- `D-0059` — auth.auditoria_email
- `D-0067` — auth.autorizacion_inicio
- `D-0086` — auth.direccion_frecuente
- `D-0094` — auth.perfil_general
- `D-0102` — auth.refresh_token
- `D-0113` — auth.reset_token
- `D-0122` — auth.taxista_favorito
- `D-0129` — auth.tipo_usuario
- `D-0141` — auth.turno_empleado
- `D-0173` — auth.usuario_empresa
- `D-0183` — auth.usuario_rol
- `D-0210` — corporate.cuenta_corriente
- `D-0235` — corporate.factura_corporativa
- `D-0266` — corporate.movimiento_cuenta
- `D-0283` — corporate.pago_corporativo
- `D-0296` — fleet.categoria_gasto
- `D-0335` — fleet.contrato_qr
- `D-0348` — fleet.contrato_vehiculo
- `D-0386` — fleet.documento_propietario
- `D-0397` — fleet.documento_vehiculo
- `D-0409` — fleet.documentos_chofer
- `D-0425` — fleet.foto_vehiculo
- `D-0433` — fleet.gasto_turno
- `D-0448` — fleet.gasto_vehiculo
- `D-0485` — fleet.liquidacion
- `D-0522` — fleet.liquidacion_ajuste
- `D-0534` — fleet.liquidacion_detalle
- `D-0544` — fleet.liquidacion_estado_historial
- `D-0555` — fleet.mantenimiento_vehiculo
- `D-0563` — fleet.marca
- `D-0571` — fleet.modelo
- `D-0582` — fleet.neumatico_historial_posicion
- `D-0603` — fleet.neumatico_imagen
- `D-0621` — fleet.neumatico_medicion
- `D-0638` — fleet.neumatico_operacion
- `D-0655` — fleet.neumatico_operacion_detalle
- `D-0668` — fleet.neumatico_sugerencia
- `D-0691` — fleet.neumatico_vehiculo
- `D-0715` — fleet.notificacion_vencimiento
- `D-0736` — fleet.propietario_vehiculo
- `D-0792` — geo.ciudad
- `D-0799` — geo.pais
- `D-0805` — geo.provincia
- `D-0812` — notification.notificacion
- `D-0826` — payment.billetera
- `D-0864` — payment.configuracion_tarifa
- `D-0878` — payment.configuracion_tarifa_vehiculo
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

- `D-0069` — auth.autorizacion_inicio
- `D-0097` — auth.perfil_general
- `D-0131` — auth.tipo_usuario
- `D-0213` — corporate.cuenta_corriente
- `D-0237` — corporate.factura_corporativa
- `D-0299` — fleet.categoria_gasto
- `D-0337` — fleet.contrato_qr
- `D-0441` — fleet.gasto_turno
- `D-0565` — fleet.marca
- `D-0903` — payment.metodo_pago
- `D-0946` — public.comercio
- `D-1006` — tenant.configuracion_tenant
- `D-1049` — tenant.factura

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

- `D-0056` — audit.log_gps
- `D-0120` — auth.reset_token
- `D-0819` — notification.notificacion
- `D-0820` — notification.notificacion
- `D-0875` — payment.configuracion_tarifa
- `D-1112` — trip.panico

### nullable_desalineado (107)

- `D-0014` — created_at
- `D-0018` — notificado
- `D-0019` — resuelto
- `D-0030` — created_at
- `D-0042` — created_at
- `D-0045` — viaje_id
- `D-0057` — created_at
- `D-0058` — valid
- `D-0066` — created_at
- `D-0083` — created_at
- `D-0091` — created_at
- `D-0092` — updated_at
- `D-0093` — usuario_id
- `D-0100` — created_at
- `D-0101` — usado
- `D-0111` — created_at
- `D-0112` — usado
- `D-0121` — created_at
- `D-0136` — created_at
- `D-0138` — facturado_total
- `D-0139` — updated_at
- `D-0140` — viajes_gestionados
- `D-0170` — activo
- `D-0171` — created_at
- `D-0172` — rol
- `D-0332` — activo
- `D-0333` — created_at
- `D-0334` — usos
- `D-0345` — created_at
- `D-0346` — estado_contrato
- `D-0385` — created_at
- `D-0395` — created_at
- `D-0396` — updated_at
- `D-0408` — subido_en
- `D-0422` — created_at
- `D-0423` — es_principal
- `D-0424` — orden
- `D-0445` — created_at
- `D-0447` — moneda
- `D-0474` — calculada_en
- `D-0475` — canon
- `D-0476` — comision_chofer
- `D-0477` — created_at
- `D-0478` — estado
- `D-0479` — monto_bruto
- `D-0480` — total_chofer
- `D-0481` — total_gastos
- `D-0482` — total_propietario
- `D-0483` — updated_at
- `D-0484` — version
- ... y 57 mas (ver JSON)

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

### tipo_desalineado (72)

- `D-0015` — distancia_desvio_metros
- `D-0016` — latitud
- `D-0017` — longitud
- `D-0043` — latitud
- `D-0044` — longitud
- `D-0084` — latitud
- `D-0085` — longitud
- `D-0137` — facturado_total
- `D-0181` — fecha_fin
- `D-0182` — fecha_inicio
- `D-0207` — limite_credito
- `D-0208` — saldo_actual
- `D-0209` — saldo_disponible
- `D-0230` — descuento
- `D-0232` — iva
- `D-0233` — subtotal
- `D-0234` — total
- `D-0262` — monto
- `D-0263` — saldo_anterior
- `D-0264` — saldo_nuevo
- `D-0282` — monto
- `D-0446` — km_registro
- `D-0579` — created_at
- `D-0580` — fecha_desmontaje
- `D-0581` — fecha_montaje
- `D-0601` — created_at
- `D-0602` — fecha_subida
- `D-0619` — created_at
- `D-0620` — fecha_medicion
- `D-0635` — created_at
- `D-0636` — fecha_operacion
- `D-0637` — updated_at
- `D-0654` — created_at
- `D-0664` — created_at
- `D-0665` — fecha_atendida
- `D-0666` — fecha_generacion
- `D-0667` — updated_at
- `D-0687` — created_at
- `D-0688` — fecha_alta
- `D-0689` — fecha_baja
- `D-0690` — updated_at
- `D-0823` — saldo
- `D-0835` — distancia_por_ficha
- `D-0839` — metros_por_ficha
- `D-0842` — modo_cobro_tiempo
- `D-0845` — precio_por_ficha
- `D-0847` — precio_por_km
- `D-0848` — precio_por_minuto
- `D-0849` — precio_por_minuto_espera
- `D-0851` — recargo_domingo
- ... y 22 mas (ver JSON)

---

## Tier 3 — 120 items

### comment_desalineado (22)

- `D-0231` — estado
- `D-0265` — tipo_movimiento
- `D-0281` — estado
- `D-0347` — estado_contrato
- `D-0712` — entidad_tipo
- `D-0713` — nivel
- `D-0834` — descripcion
- `D-0836` — distancia_por_ficha
- `D-0837` — hora_fin_nocturno
- `D-0838` — hora_inicio_nocturno
- `D-0841` — modo_calculo
- `D-0844` — moneda
- `D-0846` — precio_por_ficha
- `D-0850` — precio_por_minuto_espera
- `D-0852` — recargo_domingo
- `D-0957` — resultado
- `D-0959` — tipo_qr
- `D-1104` — resuelto_en
- `D-1106` — usuario_id
- `D-1113` — distancia_por_ficha
- `D-1114` — precio_por_ficha
- `D-1115` — precio_por_minuto_espera

### constraint_nombre_desalineado (97)

- `D-0021` — audit.alerta_desvio
- `D-0047` — audit.log_gps
- `D-0048` — audit.log_gps
- `D-0087` — auth.direccion_frecuente
- `D-0095` — auth.perfil_general
- `D-0096` — auth.perfil_general
- `D-0103` — auth.refresh_token
- `D-0114` — auth.reset_token
- `D-0123` — auth.taxista_favorito
- `D-0124` — auth.taxista_favorito
- `D-0142` — auth.turno_empleado
- `D-0143` — auth.turno_empleado
- `D-0174` — auth.usuario_empresa
- `D-0175` — auth.usuario_empresa
- `D-0297` — fleet.categoria_gasto
- `D-0349` — fleet.contrato_vehiculo
- `D-0350` — fleet.contrato_vehiculo
- `D-0351` — fleet.contrato_vehiculo
- `D-0352` — fleet.contrato_vehiculo
- `D-0398` — fleet.documento_vehiculo
- `D-0410` — fleet.documentos_chofer
- `D-0434` — fleet.gasto_turno
- `D-0435` — fleet.gasto_turno
- `D-0449` — fleet.gasto_vehiculo
- `D-0450` — fleet.gasto_vehiculo
- `D-0451` — fleet.gasto_vehiculo
- `D-0486` — fleet.liquidacion
- `D-0487` — fleet.liquidacion
- `D-0488` — fleet.liquidacion
- `D-0489` — fleet.liquidacion
- `D-0490` — fleet.liquidacion
- `D-0491` — fleet.liquidacion
- `D-0492` — fleet.liquidacion
- `D-0493` — fleet.liquidacion
- `D-0494` — fleet.liquidacion
- `D-0523` — fleet.liquidacion_ajuste
- `D-0524` — fleet.liquidacion_ajuste
- `D-0525` — fleet.liquidacion_ajuste
- `D-0535` — fleet.liquidacion_detalle
- `D-0545` — fleet.liquidacion_estado_historial
- `D-0546` — fleet.liquidacion_estado_historial
- `D-0547` — fleet.liquidacion_estado_historial
- `D-0556` — fleet.mantenimiento_vehiculo
- `D-0557` — fleet.mantenimiento_vehiculo
- `D-0572` — fleet.modelo
- `D-0583` — fleet.neumatico_historial_posicion
- `D-0584` — fleet.neumatico_historial_posicion
- `D-0585` — fleet.neumatico_historial_posicion
- `D-0586` — fleet.neumatico_historial_posicion
- `D-0604` — fleet.neumatico_imagen
- ... y 47 mas (ver JSON)

### indice_nombre_desalineado (1)

- `D-0832` — payment.billetera

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
| D-0460 | fleet.ingreso_turno.medio_pago | vocabulario_metodo_pago |
| D-0579 | fleet.neumatico_historial_posicion.created_at | timestamp_naive_vs_tz |
| D-0580 | fleet.neumatico_historial_posicion.fecha_desmontaje | timestamp_naive_vs_tz |
| D-0581 | fleet.neumatico_historial_posicion.fecha_montaje | timestamp_naive_vs_tz |
| D-0601 | fleet.neumatico_imagen.created_at | timestamp_naive_vs_tz |
| D-0602 | fleet.neumatico_imagen.fecha_subida | timestamp_naive_vs_tz |
| D-0619 | fleet.neumatico_medicion.created_at | timestamp_naive_vs_tz |
| D-0620 | fleet.neumatico_medicion.fecha_medicion | timestamp_naive_vs_tz |
| D-0635 | fleet.neumatico_operacion.created_at | timestamp_naive_vs_tz |
| D-0636 | fleet.neumatico_operacion.fecha_operacion | timestamp_naive_vs_tz |
| D-0637 | fleet.neumatico_operacion.updated_at | timestamp_naive_vs_tz |
| D-0654 | fleet.neumatico_operacion_detalle.created_at | timestamp_naive_vs_tz |
| D-0664 | fleet.neumatico_sugerencia.created_at | timestamp_naive_vs_tz |
| D-0665 | fleet.neumatico_sugerencia.fecha_atendida | timestamp_naive_vs_tz |
| D-0666 | fleet.neumatico_sugerencia.fecha_generacion | timestamp_naive_vs_tz |
| D-0667 | fleet.neumatico_sugerencia.updated_at | timestamp_naive_vs_tz |
| D-0687 | fleet.neumatico_vehiculo.created_at | timestamp_naive_vs_tz |
| D-0688 | fleet.neumatico_vehiculo.fecha_alta | timestamp_naive_vs_tz |
| D-0689 | fleet.neumatico_vehiculo.fecha_baja | timestamp_naive_vs_tz |
| D-0690 | fleet.neumatico_vehiculo.updated_at | timestamp_naive_vs_tz |
| D-1012 | tenant.control_base.latitud | orm_mal_db_bien |
| D-1013 | tenant.control_base.longitud | orm_mal_db_bien |

---

## Archivos generados

- `orm_diff.json` — datos completos.
- `orm_diff_reporte.md` — este informe.
- `orm_diff_acciones.csv` — CSV de acciones sugeridas.
