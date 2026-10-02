# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-02T14:25:01.122775+00:00

## Resumen ejecutivo

- **1205 diferencias** en total.
- **Tier 1**: 191 items.
- **Tier 2**: 893 items.
- **Tier 3**: 120 items.
- **Tier 4**: 1 items.
- **24 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| constraint_falta | 428 |
| indice_falta | 192 |
| nullable_desalineado | 133 |
| constraint_nombre_desalineado | 124 |
| tipo_desalineado | 102 |
| constraint_desalineada | 72 |
| columna_falta | 69 |
| comment_desalineado | 33 |
| constraint_sobra | 24 |
| tabla_falta | 10 |
| indice_sobra | 9 |
| indice_nombre_desalineado | 4 |
| schema_falta | 2 |
| columna_sobra | 2 |
| tabla_sobra | 1 |

---

## Tier 1 — 191 items

### columna_falta (5)

- `D-0804` — desgaste_manual
- `D-0805` — desgaste_neumaticos
- `D-0806` — fecha_ultimo_cambio_neumaticos
- `D-0807` — km_ultimo_cambio_neumaticos
- `D-0808` — parches_neumaticos

### comment_desalineado (11)

- `D-0486` — declarado_por
- `D-0487` — medio_pago
- `D-0489` — transaccion_id
- `D-0785` — snapshot_dia_contractual
- `D-0813` — created_at
- `D-0815` — qr_activo
- `D-0817` — qr_uuid
- `D-0819` — updated_at
- `D-1134` — latitud
- `D-1135` — longitud
- `D-1171` — solicitado_en

### constraint_desalineada (10)

- `D-0160` — auth.usuario
- `D-0325` — fleet.chofer_vehiculo
- `D-0490` — fleet.ingreso_turno
- `D-0786` — fleet.turno_chofer
- `D-0820` — fleet.vehiculo
- `D-0977` — payment.transaccion
- `D-1063` — tenant.control_base
- `D-1112` — trip.calificacion
- `D-1136` — trip.historial_estado_viaje
- `D-1172` — trip.viaje_solicitado

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
- `D-0326` — fleet.chofer_vehiculo
- `D-0327` — fleet.chofer_vehiculo
- `D-0328` — fleet.chofer_vehiculo
- `D-0787` — fleet.turno_chofer
- `D-0788` — fleet.turno_chofer
- `D-0789` — fleet.turno_chofer
- `D-0821` — fleet.vehiculo
- `D-0978` — payment.transaccion
- `D-0979` — payment.transaccion
- `D-0980` — payment.transaccion
- `D-1064` — tenant.control_base
- `D-1065` — tenant.control_base
- `D-1113` — trip.calificacion
- `D-1114` — trip.calificacion
- `D-1115` — trip.calificacion
- `D-1137` — trip.historial_estado_viaje
- `D-1177` — trip.viaje_solicitado
- `D-1178` — trip.viaje_solicitado
- `D-1179` — trip.viaje_solicitado
- `D-1180` — trip.viaje_solicitado
- `D-1181` — trip.viaje_solicitado
- `D-1182` — trip.viaje_solicitado
- `D-1183` — trip.viaje_solicitado
- `D-1184` — trip.viaje_solicitado

### constraint_sobra (11)

- `D-0798` — fleet.turno_chofer
- `D-0823` — fleet.vehiculo
- `D-1116` — trip.calificacion
- `D-1195` — trip.viaje_solicitado
- `D-1196` — trip.viaje_solicitado
- `D-1197` — trip.viaje_solicitado
- `D-1198` — trip.viaje_solicitado
- `D-1199` — trip.viaje_solicitado
- `D-1200` — trip.viaje_solicitado
- `D-1201` — trip.viaje_solicitado
- `D-1202` — trip.viaje_solicitado

### indice_falta (18)

- `D-0168` — auth.usuario
- `D-0333` — fleet.chofer_vehiculo
- `D-0501` — fleet.ingreso_turno
- `D-0799` — fleet.turno_chofer
- `D-0800` — fleet.turno_chofer
- `D-0801` — fleet.turno_chofer
- `D-0802` — fleet.turno_chofer
- `D-0803` — fleet.turno_chofer
- `D-0831` — fleet.vehiculo
- `D-0832` — fleet.vehiculo
- `D-0833` — fleet.vehiculo
- `D-0834` — fleet.vehiculo
- `D-0982` — payment.transaccion
- `D-1068` — tenant.control_base
- `D-1069` — tenant.control_base
- `D-1123` — trip.calificacion
- `D-1139` — trip.historial_estado_viaje
- `D-1203` — trip.viaje_solicitado

### indice_nombre_desalineado (3)

- `D-0169` — auth.usuario
- `D-0835` — fleet.vehiculo
- `D-1205` — trip.viaje_solicitado

### indice_sobra (3)

- `D-0334` — fleet.chofer_vehiculo
- `D-0983` — payment.transaccion
- `D-1204` — trip.viaje_solicitado

### nullable_desalineado (25)

- `D-0155` — activo
- `D-0156` — created_at
- `D-0158` — tipo_usuario_id
- `D-0159` — updated_at
- `D-0312` — activo
- `D-0314` — calificacion_promedio
- `D-0315` — created_at
- `D-0316` — estado_laboral
- `D-0317` — estado_panico
- `D-0320` — total_calificaciones
- `D-0322` — ultima_conexion
- `D-0323` — updated_at
- `D-0324` — vehiculo_id
- `D-0809` — activo
- `D-0810` — capacidad
- `D-0811` — control_base_id
- `D-0812` — created_at
- `D-0814` — qr_activo
- `D-0816` — qr_uuid
- `D-0818` — updated_at
- `D-0973` — billetera_id
- `D-0974` — created_at
- `D-1055` — activo
- `D-1056` — created_at
- `D-1062` — updated_at

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

### tipo_desalineado (18)

- `D-0157` — password_hash
- `D-0313` — calificacion_promedio
- `D-0318` — latitud
- `D-0319` — longitud
- `D-0321` — ubicacion
- `D-0488` — monto
- `D-0782` — estado
- `D-0783` — km_final
- `D-0784` — km_inicial
- `D-0975` — monto
- `D-0976` — saldo_despues
- `D-1057` — email
- `D-1058` — latitud
- `D-1059` — longitud
- `D-1060` — motivo_suspension
- `D-1061` — nombre
- `D-1169` — destino
- `D-1170` — origen

---

## Tier 2 — 893 items

### columna_falta (64)

| Tabla | Cantidad |
|---|---|
| tenant.configuracion_tenant | 23 |
| fleet.documento_vehiculo | 16 |
| corporate.cuenta_corriente | 10 |
| corporate.movimiento_cuenta | 6 |
| corporate.factura_corporativa | 4 |
| auth.direccion_frecuente | 2 |
| auth.usuario_rol | 1 |
| corporate.pago_corporativo | 1 |
| fleet.propietario_vehiculo | 1 |

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
- `D-0338` — fleet.contrato_qr
- `D-0356` — fleet.contrato_vehiculo
- `D-0395` — fleet.documento_propietario
- `D-0423` — fleet.documento_vehiculo
- `D-0435` — fleet.documentos_chofer
- `D-0451` — fleet.foto_vehiculo
- `D-0461` — fleet.gasto_turno
- `D-0475` — fleet.gasto_vehiculo
- `D-0513` — fleet.liquidacion
- `D-0550` — fleet.liquidacion_ajuste
- `D-0563` — fleet.liquidacion_detalle
- `D-0573` — fleet.liquidacion_estado_historial
- `D-0584` — fleet.mantenimiento_vehiculo
- `D-0592` — fleet.marca
- `D-0600` — fleet.modelo
- `D-0612` — fleet.neumatico_historial_posicion
- `D-0633` — fleet.neumatico_imagen
- `D-0651` — fleet.neumatico_medicion
- `D-0668` — fleet.neumatico_operacion
- `D-0687` — fleet.neumatico_operacion_detalle
- `D-0700` — fleet.neumatico_sugerencia
- `D-0723` — fleet.neumatico_vehiculo
- `D-0747` — fleet.notificacion_vencimiento
- `D-0770` — fleet.propietario_vehiculo
- `D-0838` — geo.ciudad
- `D-0845` — geo.pais
- `D-0851` — geo.provincia
- `D-0858` — notification.notificacion
- `D-0872` — payment.billetera
- `D-0910` — payment.configuracion_tarifa
- `D-0924` — payment.configuracion_tarifa_vehiculo
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
- `D-0340` — fleet.contrato_qr
- `D-0469` — fleet.gasto_turno
- `D-0594` — fleet.marca
- `D-0949` — payment.metodo_pago
- `D-0992` — public.comercio
- `D-1052` — tenant.configuracion_tenant
- `D-1095` — tenant.factura

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
- `D-0865` — notification.notificacion
- `D-0866` — notification.notificacion
- `D-0921` — payment.configuracion_tarifa
- `D-1158` — trip.panico

### nullable_desalineado (108)

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
- `D-0335` — activo
- `D-0336` — created_at
- `D-0337` — usos
- `D-0349` — created_at
- `D-0350` — estado_contrato
- `D-0393` — created_at
- `D-0394` — updated_at
- `D-0420` — created_at
- `D-0422` — updated_at
- `D-0434` — subido_en
- `D-0448` — created_at
- `D-0449` — es_principal
- `D-0450` — orden
- `D-0473` — created_at
- `D-0474` — moneda
- `D-0502` — calculada_en
- `D-0503` — canon
- `D-0504` — comision_chofer
- `D-0505` — created_at
- `D-0506` — estado
- `D-0507` — monto_bruto
- `D-0508` — total_chofer
- `D-0509` — total_gastos
- `D-0510` — total_propietario
- `D-0511` — updated_at
- ... y 58 mas (ver JSON)

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

### tipo_desalineado (84)

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
- `D-0348` — canon_diario
- `D-0352` — km_incluidos_dia
- `D-0353` — monto_diario
- `D-0354` — porcentaje_chofer
- `D-0355` — valor_km_excedente
- `D-0421` — numero
- `D-0459` — km_registro
- `D-0460` — monto
- `D-0562` — meta_data
- `D-0608` — created_at
- `D-0609` — eje_posicion
- `D-0610` — fecha_desmontaje
- `D-0611` — fecha_montaje
- `D-0631` — created_at
- `D-0632` — fecha_subida
- `D-0649` — created_at
- `D-0650` — fecha_medicion
- `D-0665` — created_at
- `D-0666` — fecha_operacion
- `D-0667` — updated_at
- `D-0684` — created_at
- `D-0685` — posicion_antes
- `D-0686` — posicion_despues
- `D-0696` — created_at
- `D-0697` — fecha_atendida
- `D-0698` — fecha_generacion
- `D-0699` — updated_at
- `D-0719` — created_at
- `D-0720` — fecha_alta
- ... y 34 mas (ver JSON)

---

## Tier 3 — 120 items

### comment_desalineado (22)

- `D-0231` — estado
- `D-0265` — tipo_movimiento
- `D-0281` — estado
- `D-0351` — estado_contrato
- `D-0744` — entidad_tipo
- `D-0745` — nivel
- `D-0880` — descripcion
- `D-0882` — distancia_por_ficha
- `D-0883` — hora_fin_nocturno
- `D-0884` — hora_inicio_nocturno
- `D-0887` — modo_calculo
- `D-0890` — moneda
- `D-0892` — precio_por_ficha
- `D-0896` — precio_por_minuto_espera
- `D-0898` — recargo_domingo
- `D-1003` — resultado
- `D-1005` — tipo_qr
- `D-1150` — resuelto_en
- `D-1152` — usuario_id
- `D-1159` — distancia_por_ficha
- `D-1160` — precio_por_ficha
- `D-1161` — precio_por_minuto_espera

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
- `D-0357` — fleet.contrato_vehiculo
- `D-0358` — fleet.contrato_vehiculo
- `D-0359` — fleet.contrato_vehiculo
- `D-0360` — fleet.contrato_vehiculo
- `D-0424` — fleet.documento_vehiculo
- `D-0436` — fleet.documentos_chofer
- `D-0462` — fleet.gasto_turno
- `D-0463` — fleet.gasto_turno
- `D-0476` — fleet.gasto_vehiculo
- `D-0477` — fleet.gasto_vehiculo
- `D-0478` — fleet.gasto_vehiculo
- `D-0514` — fleet.liquidacion
- `D-0515` — fleet.liquidacion
- `D-0516` — fleet.liquidacion
- `D-0517` — fleet.liquidacion
- `D-0518` — fleet.liquidacion
- `D-0519` — fleet.liquidacion
- `D-0520` — fleet.liquidacion
- `D-0521` — fleet.liquidacion
- `D-0522` — fleet.liquidacion
- `D-0551` — fleet.liquidacion_ajuste
- `D-0552` — fleet.liquidacion_ajuste
- `D-0553` — fleet.liquidacion_ajuste
- `D-0564` — fleet.liquidacion_detalle
- `D-0574` — fleet.liquidacion_estado_historial
- `D-0575` — fleet.liquidacion_estado_historial
- `D-0576` — fleet.liquidacion_estado_historial
- `D-0585` — fleet.mantenimiento_vehiculo
- `D-0586` — fleet.mantenimiento_vehiculo
- `D-0601` — fleet.modelo
- `D-0613` — fleet.neumatico_historial_posicion
- `D-0614` — fleet.neumatico_historial_posicion
- `D-0615` — fleet.neumatico_historial_posicion
- `D-0616` — fleet.neumatico_historial_posicion
- `D-0634` — fleet.neumatico_imagen
- ... y 47 mas (ver JSON)

### indice_nombre_desalineado (1)

- `D-0878` — payment.billetera

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
| D-0487 | fleet.ingreso_turno.medio_pago | vocabulario_metodo_pago |
| D-0608 | fleet.neumatico_historial_posicion.created_at | timestamp_naive_vs_tz |
| D-0610 | fleet.neumatico_historial_posicion.fecha_desmontaje | timestamp_naive_vs_tz |
| D-0611 | fleet.neumatico_historial_posicion.fecha_montaje | timestamp_naive_vs_tz |
| D-0631 | fleet.neumatico_imagen.created_at | timestamp_naive_vs_tz |
| D-0632 | fleet.neumatico_imagen.fecha_subida | timestamp_naive_vs_tz |
| D-0649 | fleet.neumatico_medicion.created_at | timestamp_naive_vs_tz |
| D-0650 | fleet.neumatico_medicion.fecha_medicion | timestamp_naive_vs_tz |
| D-0665 | fleet.neumatico_operacion.created_at | timestamp_naive_vs_tz |
| D-0666 | fleet.neumatico_operacion.fecha_operacion | timestamp_naive_vs_tz |
| D-0667 | fleet.neumatico_operacion.updated_at | timestamp_naive_vs_tz |
| D-0684 | fleet.neumatico_operacion_detalle.created_at | timestamp_naive_vs_tz |
| D-0696 | fleet.neumatico_sugerencia.created_at | timestamp_naive_vs_tz |
| D-0697 | fleet.neumatico_sugerencia.fecha_atendida | timestamp_naive_vs_tz |
| D-0698 | fleet.neumatico_sugerencia.fecha_generacion | timestamp_naive_vs_tz |
| D-0699 | fleet.neumatico_sugerencia.updated_at | timestamp_naive_vs_tz |
| D-0719 | fleet.neumatico_vehiculo.created_at | timestamp_naive_vs_tz |
| D-0720 | fleet.neumatico_vehiculo.fecha_alta | timestamp_naive_vs_tz |
| D-0721 | fleet.neumatico_vehiculo.fecha_baja | timestamp_naive_vs_tz |
| D-0722 | fleet.neumatico_vehiculo.updated_at | timestamp_naive_vs_tz |
| D-1058 | tenant.control_base.latitud | orm_mal_db_bien |
| D-1059 | tenant.control_base.longitud | orm_mal_db_bien |

---

## Archivos generados

- `orm_diff.json` — datos completos.
- `orm_diff_reporte.md` — este informe.
- `orm_diff_acciones.csv` — CSV de acciones sugeridas.
