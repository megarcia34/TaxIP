# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-03T23:35:31.047702+00:00

## Resumen ejecutivo

- **985 diferencias** en total.
- **Tier 1**: 162 items.
- **Tier 2**: 703 items.
- **Tier 3**: 119 items.
- **Tier 4**: 1 items.
- **22 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| constraint_falta | 427 |
| indice_falta | 193 |
| constraint_nombre_desalineado | 124 |
| constraint_desalineada | 72 |
| nullable_desalineado | 62 |
| tipo_desalineado | 30 |
| comment_desalineado | 29 |
| constraint_sobra | 24 |
| tabla_falta | 10 |
| indice_sobra | 4 |
| indice_nombre_desalineado | 4 |
| columna_falta | 3 |
| schema_falta | 2 |
| tabla_sobra | 1 |

---

## Tier 1 — 162 items

### comment_desalineado (7)

- `D-0413` — declarado_por
- `D-0414` — medio_pago
- `D-0415` — transaccion_id
- `D-0688` — snapshot_dia_contractual
- `D-0913` — latitud
- `D-0914` — longitud
- `D-0950` — solicitado_en

### constraint_desalineada (10)

- `D-0147` — auth.usuario
- `D-0276` — fleet.chofer_vehiculo
- `D-0416` — fleet.ingreso_turno
- `D-0689` — fleet.turno_chofer
- `D-0713` — fleet.vehiculo
- `D-0817` — payment.transaccion
- `D-0857` — tenant.control_base
- `D-0892` — trip.calificacion
- `D-0915` — trip.historial_estado_viaje
- `D-0951` — trip.viaje_solicitado

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
- `D-0690` — fleet.turno_chofer
- `D-0691` — fleet.turno_chofer
- `D-0692` — fleet.turno_chofer
- `D-0714` — fleet.vehiculo
- `D-0818` — payment.transaccion
- `D-0819` — payment.transaccion
- `D-0820` — payment.transaccion
- `D-0858` — tenant.control_base
- `D-0859` — tenant.control_base
- `D-0893` — trip.calificacion
- `D-0894` — trip.calificacion
- `D-0895` — trip.calificacion
- `D-0916` — trip.historial_estado_viaje
- `D-0956` — trip.viaje_solicitado
- `D-0957` — trip.viaje_solicitado
- `D-0958` — trip.viaje_solicitado
- `D-0959` — trip.viaje_solicitado
- `D-0960` — trip.viaje_solicitado
- `D-0961` — trip.viaje_solicitado
- `D-0962` — trip.viaje_solicitado
- `D-0963` — trip.viaje_solicitado

### constraint_sobra (10)

- `D-0716` — fleet.vehiculo
- `D-0896` — trip.calificacion
- `D-0974` — trip.viaje_solicitado
- `D-0975` — trip.viaje_solicitado
- `D-0976` — trip.viaje_solicitado
- `D-0977` — trip.viaje_solicitado
- `D-0978` — trip.viaje_solicitado
- `D-0979` — trip.viaje_solicitado
- `D-0980` — trip.viaje_solicitado
- `D-0981` — trip.viaje_solicitado

### indice_falta (18)

- `D-0155` — auth.usuario
- `D-0284` — fleet.chofer_vehiculo
- `D-0427` — fleet.ingreso_turno
- `D-0701` — fleet.turno_chofer
- `D-0702` — fleet.turno_chofer
- `D-0703` — fleet.turno_chofer
- `D-0704` — fleet.turno_chofer
- `D-0705` — fleet.turno_chofer
- `D-0724` — fleet.vehiculo
- `D-0725` — fleet.vehiculo
- `D-0726` — fleet.vehiculo
- `D-0727` — fleet.vehiculo
- `D-0822` — payment.transaccion
- `D-0862` — tenant.control_base
- `D-0863` — tenant.control_base
- `D-0903` — trip.calificacion
- `D-0918` — trip.historial_estado_viaje
- `D-0982` — trip.viaje_solicitado

### indice_nombre_desalineado (4)

- `D-0156` — auth.usuario
- `D-0728` — fleet.vehiculo
- `D-0984` — trip.viaje_solicitado
- `D-0985` — trip.viaje_solicitado

### indice_sobra (2)

- `D-0285` — fleet.chofer_vehiculo
- `D-0983` — trip.viaje_solicitado

### nullable_desalineado (20)

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
- `D-0706` — activo
- `D-0707` — capacidad
- `D-0708` — control_base_id
- `D-0709` — created_at
- `D-0710` — qr_activo
- `D-0711` — qr_uuid
- `D-0712` — updated_at

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

### tipo_desalineado (4)

- `D-0144` — password_hash
- `D-0272` — ubicacion
- `D-0948` — destino
- `D-0949` — origen

---

## Tier 2 — 703 items

### columna_falta (3)

- `D-0068` — email
- `D-0069` — telefono
- `D-0167` — control_base_id

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
- `D-0428` — fleet.liquidacion
- `D-0464` — fleet.liquidacion_ajuste
- `D-0475` — fleet.liquidacion_detalle
- `D-0484` — fleet.liquidacion_estado_historial
- `D-0495` — fleet.mantenimiento_vehiculo
- `D-0503` — fleet.marca
- `D-0511` — fleet.modelo
- `D-0522` — fleet.neumatico_historial_posicion
- `D-0543` — fleet.neumatico_imagen
- `D-0561` — fleet.neumatico_medicion
- `D-0578` — fleet.neumatico_operacion
- `D-0595` — fleet.neumatico_operacion_detalle
- `D-0608` — fleet.neumatico_sugerencia
- `D-0631` — fleet.neumatico_vehiculo
- `D-0655` — fleet.notificacion_vencimiento
- `D-0676` — fleet.propietario_vehiculo
- `D-0729` — geo.ciudad
- `D-0735` — geo.pais
- `D-0739` — geo.provincia
- `D-0744` — notification.notificacion
- `D-0751` — payment.billetera
- `D-0768` — payment.configuracion_tarifa
- `D-0779` — payment.configuracion_tarifa_vehiculo
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

### constraint_sobra (14)

- `D-0056` — auth.autorizacion_inicio
- `D-0084` — auth.perfil_general
- `D-0118` — auth.tipo_usuario
- `D-0187` — corporate.cuenta_corriente
- `D-0203` — corporate.factura_corporativa
- `D-0253` — fleet.categoria_gasto
- `D-0291` — fleet.contrato_qr
- `D-0395` — fleet.gasto_turno
- `D-0505` — fleet.marca
- `D-0754` — payment.billetera
- `D-0798` — payment.metodo_pago
- `D-0826` — public.comercio
- `D-0854` — tenant.configuracion_tenant
- `D-0875` — tenant.factura

### indice_falta (175)

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
| payment.billetera | 2 |
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
| payment.configuracion_tarifa | 1 |
| payment.factura_empresa | 1 |
| payment.metodo_pago | 1 |
| tenant.configuracion_tenant | 1 |
| tenant.empresa | 1 |
| trip.objeto_olvidado | 1 |
| trip.panico | 1 |
| trip.tipo_vehiculo | 1 |

### indice_sobra (2)

- `D-0107` — auth.reset_token
- `D-0937` — trip.panico

### nullable_desalineado (42)

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
- `D-0494` — created_at
- `D-0502` — created_at
- `D-0510` — created_at
- `D-0650` — created_at
- `D-0651` — email_enviado
- `D-0654` — sms_enviado
- `D-0674` — created_at
- `D-0675` — porcentaje_participacion

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

### tipo_desalineado (26)

- `D-0071` — latitud
- `D-0072` — longitud
- `D-0124` — facturado_total
- `D-0168` — fecha_fin
- `D-0169` — fecha_inicio
- `D-0400` — km_registro
- `D-0519` — created_at
- `D-0520` — fecha_desmontaje
- `D-0521` — fecha_montaje
- `D-0541` — created_at
- `D-0542` — fecha_subida
- `D-0559` — created_at
- `D-0560` — fecha_medicion
- `D-0575` — created_at
- `D-0576` — fecha_operacion
- `D-0577` — updated_at
- `D-0594` — created_at
- `D-0604` — created_at
- `D-0605` — fecha_atendida
- `D-0606` — fecha_generacion
- `D-0607` — updated_at
- `D-0627` — created_at
- `D-0628` — fecha_alta
- `D-0629` — fecha_baja
- `D-0630` — updated_at
- `D-0930` — ubicacion

---

## Tier 3 — 119 items

### comment_desalineado (22)

- `D-0200` — estado
- `D-0222` — tipo_movimiento
- `D-0237` — estado
- `D-0301` — estado_contrato
- `D-0652` — entidad_tipo
- `D-0653` — nivel
- `D-0759` — descripcion
- `D-0760` — distancia_por_ficha
- `D-0761` — hora_fin_nocturno
- `D-0762` — hora_inicio_nocturno
- `D-0763` — modo_calculo
- `D-0764` — moneda
- `D-0765` — precio_por_ficha
- `D-0766` — precio_por_minuto_espera
- `D-0767` — recargo_domingo
- `D-0836` — resultado
- `D-0837` — tipo_qr
- `D-0929` — resuelto_en
- `D-0931` — usuario_id
- `D-0938` — distancia_por_ficha
- `D-0939` — precio_por_ficha
- `D-0940` — precio_por_minuto_espera

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
- `D-0429` — fleet.liquidacion
- `D-0430` — fleet.liquidacion
- `D-0431` — fleet.liquidacion
- `D-0432` — fleet.liquidacion
- `D-0433` — fleet.liquidacion
- `D-0434` — fleet.liquidacion
- `D-0435` — fleet.liquidacion
- `D-0436` — fleet.liquidacion
- `D-0437` — fleet.liquidacion
- `D-0465` — fleet.liquidacion_ajuste
- `D-0466` — fleet.liquidacion_ajuste
- `D-0467` — fleet.liquidacion_ajuste
- `D-0476` — fleet.liquidacion_detalle
- `D-0485` — fleet.liquidacion_estado_historial
- `D-0486` — fleet.liquidacion_estado_historial
- `D-0487` — fleet.liquidacion_estado_historial
- `D-0496` — fleet.mantenimiento_vehiculo
- `D-0497` — fleet.mantenimiento_vehiculo
- `D-0512` — fleet.modelo
- `D-0523` — fleet.neumatico_historial_posicion
- `D-0524` — fleet.neumatico_historial_posicion
- `D-0525` — fleet.neumatico_historial_posicion
- `D-0526` — fleet.neumatico_historial_posicion
- `D-0544` — fleet.neumatico_imagen
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
| D-0414 | fleet.ingreso_turno.medio_pago | vocabulario_metodo_pago |
| D-0519 | fleet.neumatico_historial_posicion.created_at | timestamp_naive_vs_tz |
| D-0520 | fleet.neumatico_historial_posicion.fecha_desmontaje | timestamp_naive_vs_tz |
| D-0521 | fleet.neumatico_historial_posicion.fecha_montaje | timestamp_naive_vs_tz |
| D-0541 | fleet.neumatico_imagen.created_at | timestamp_naive_vs_tz |
| D-0542 | fleet.neumatico_imagen.fecha_subida | timestamp_naive_vs_tz |
| D-0559 | fleet.neumatico_medicion.created_at | timestamp_naive_vs_tz |
| D-0560 | fleet.neumatico_medicion.fecha_medicion | timestamp_naive_vs_tz |
| D-0575 | fleet.neumatico_operacion.created_at | timestamp_naive_vs_tz |
| D-0576 | fleet.neumatico_operacion.fecha_operacion | timestamp_naive_vs_tz |
| D-0577 | fleet.neumatico_operacion.updated_at | timestamp_naive_vs_tz |
| D-0594 | fleet.neumatico_operacion_detalle.created_at | timestamp_naive_vs_tz |
| D-0604 | fleet.neumatico_sugerencia.created_at | timestamp_naive_vs_tz |
| D-0605 | fleet.neumatico_sugerencia.fecha_atendida | timestamp_naive_vs_tz |
| D-0606 | fleet.neumatico_sugerencia.fecha_generacion | timestamp_naive_vs_tz |
| D-0607 | fleet.neumatico_sugerencia.updated_at | timestamp_naive_vs_tz |
| D-0627 | fleet.neumatico_vehiculo.created_at | timestamp_naive_vs_tz |
| D-0628 | fleet.neumatico_vehiculo.fecha_alta | timestamp_naive_vs_tz |
| D-0629 | fleet.neumatico_vehiculo.fecha_baja | timestamp_naive_vs_tz |
| D-0630 | fleet.neumatico_vehiculo.updated_at | timestamp_naive_vs_tz |

---

## Archivos generados

- `orm_diff.json` — datos completos.
- `orm_diff_reporte.md` — este informe.
- `orm_diff_acciones.csv` — CSV de acciones sugeridas.
