# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-04T21:13:11.788617+00:00

## Resumen ejecutivo

- **890 diferencias** en total.
- **Tier 1**: 140 items.
- **Tier 2**: 630 items.
- **Tier 3**: 119 items.
- **Tier 4**: 1 items.
- **7 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| constraint_falta | 427 |
| indice_falta | 180 |
| constraint_nombre_desalineado | 124 |
| constraint_desalineada | 72 |
| comment_desalineado | 29 |
| constraint_sobra | 25 |
| tabla_falta | 10 |
| tipo_desalineado | 9 |
| nullable_desalineado | 4 |
| indice_nombre_desalineado | 3 |
| indice_sobra | 3 |
| schema_falta | 2 |
| tabla_sobra | 1 |
| columna_falta | 1 |

---

## Tier 1 — 140 items

### comment_desalineado (7)

- `D-0348` — declarado_por
- `D-0349` — medio_pago
- `D-0350` — transaccion_id
- `D-0601` — snapshot_dia_contractual
- `D-0819` — latitud
- `D-0820` — longitud
- `D-0856` — solicitado_en

### constraint_desalineada (10)

- `D-0111` — auth.usuario
- `D-0224` — fleet.chofer_vehiculo
- `D-0351` — fleet.ingreso_turno
- `D-0602` — fleet.turno_chofer
- `D-0619` — fleet.vehiculo
- `D-0723` — payment.transaccion
- `D-0763` — tenant.control_base
- `D-0798` — trip.calificacion
- `D-0821` — trip.historial_estado_viaje
- `D-0857` — trip.viaje_solicitado

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
- `D-0603` — fleet.turno_chofer
- `D-0604` — fleet.turno_chofer
- `D-0605` — fleet.turno_chofer
- `D-0620` — fleet.vehiculo
- `D-0724` — payment.transaccion
- `D-0725` — payment.transaccion
- `D-0726` — payment.transaccion
- `D-0764` — tenant.control_base
- `D-0765` — tenant.control_base
- `D-0799` — trip.calificacion
- `D-0800` — trip.calificacion
- `D-0801` — trip.calificacion
- `D-0822` — trip.historial_estado_viaje
- `D-0862` — trip.viaje_solicitado
- `D-0863` — trip.viaje_solicitado
- `D-0864` — trip.viaje_solicitado
- `D-0865` — trip.viaje_solicitado
- `D-0866` — trip.viaje_solicitado
- `D-0867` — trip.viaje_solicitado
- `D-0868` — trip.viaje_solicitado
- `D-0869` — trip.viaje_solicitado

### constraint_sobra (10)

- `D-0622` — fleet.vehiculo
- `D-0802` — trip.calificacion
- `D-0880` — trip.viaje_solicitado
- `D-0881` — trip.viaje_solicitado
- `D-0882` — trip.viaje_solicitado
- `D-0883` — trip.viaje_solicitado
- `D-0884` — trip.viaje_solicitado
- `D-0885` — trip.viaje_solicitado
- `D-0886` — trip.viaje_solicitado
- `D-0887` — trip.viaje_solicitado

### indice_falta (18)

- `D-0119` — auth.usuario
- `D-0232` — fleet.chofer_vehiculo
- `D-0362` — fleet.ingreso_turno
- `D-0614` — fleet.turno_chofer
- `D-0615` — fleet.turno_chofer
- `D-0616` — fleet.turno_chofer
- `D-0617` — fleet.turno_chofer
- `D-0618` — fleet.turno_chofer
- `D-0630` — fleet.vehiculo
- `D-0631` — fleet.vehiculo
- `D-0632` — fleet.vehiculo
- `D-0633` — fleet.vehiculo
- `D-0728` — payment.transaccion
- `D-0768` — tenant.control_base
- `D-0769` — tenant.control_base
- `D-0809` — trip.calificacion
- `D-0824` — trip.historial_estado_viaje
- `D-0888` — trip.viaje_solicitado

### indice_nombre_desalineado (3)

- `D-0120` — auth.usuario
- `D-0634` — fleet.vehiculo
- `D-0890` — trip.viaje_solicitado

### indice_sobra (2)

- `D-0233` — fleet.chofer_vehiculo
- `D-0889` — trip.viaje_solicitado

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

### tipo_desalineado (3)

- `D-0223` — ubicacion
- `D-0854` — destino
- `D-0855` — origen

---

## Tier 2 — 630 items

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
- `D-0245` — fleet.contrato_vehiculo
- `D-0282` — fleet.documento_propietario
- `D-0291` — fleet.documento_vehiculo
- `D-0302` — fleet.documentos_chofer
- `D-0315` — fleet.foto_vehiculo
- `D-0323` — fleet.gasto_turno
- `D-0337` — fleet.gasto_vehiculo
- `D-0363` — fleet.liquidacion
- `D-0399` — fleet.liquidacion_ajuste
- `D-0410` — fleet.liquidacion_detalle
- `D-0419` — fleet.liquidacion_estado_historial
- `D-0430` — fleet.mantenimiento_vehiculo
- `D-0437` — fleet.marca
- `D-0444` — fleet.modelo
- `D-0452` — fleet.neumatico_historial_posicion
- `D-0471` — fleet.neumatico_imagen
- `D-0487` — fleet.neumatico_medicion
- `D-0501` — fleet.neumatico_operacion
- `D-0517` — fleet.neumatico_operacion_detalle
- `D-0528` — fleet.neumatico_sugerencia
- `D-0549` — fleet.neumatico_vehiculo
- `D-0570` — fleet.notificacion_vencimiento
- `D-0589` — fleet.propietario_vehiculo
- `D-0635` — geo.ciudad
- `D-0641` — geo.pais
- `D-0645` — geo.provincia
- `D-0650` — notification.notificacion
- `D-0657` — payment.billetera
- `D-0674` — payment.configuracion_tarifa
- `D-0685` — payment.configuracion_tarifa_vehiculo
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
- `D-0331` — fleet.gasto_turno
- `D-0439` — fleet.marca
- `D-0660` — payment.billetera
- `D-0704` — payment.metodo_pago
- `D-0732` — public.comercio
- `D-0760` — tenant.configuracion_tenant
- `D-0781` — tenant.factura

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

- `D-0843` — trip.panico

### nullable_desalineado (4)

- `D-0014` — viaje_id
- `D-0206` — updated_at
- `D-0336` — vehiculo_id
- `D-0429` — vehiculo_id

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

### tipo_desalineado (6)

- `D-0335` — km_registro
- `D-0526` — created_at
- `D-0527` — updated_at
- `D-0547` — fecha_alta
- `D-0548` — fecha_baja
- `D-0836` — ubicacion

---

## Tier 3 — 119 items

### comment_desalineado (22)

- `D-0156` — estado
- `D-0178` — tipo_movimiento
- `D-0193` — estado
- `D-0244` — estado_contrato
- `D-0568` — entidad_tipo
- `D-0569` — nivel
- `D-0665` — descripcion
- `D-0666` — distancia_por_ficha
- `D-0667` — hora_fin_nocturno
- `D-0668` — hora_inicio_nocturno
- `D-0669` — modo_calculo
- `D-0670` — moneda
- `D-0671` — precio_por_ficha
- `D-0672` — precio_por_minuto_espera
- `D-0673` — recargo_domingo
- `D-0742` — resultado
- `D-0743` — tipo_qr
- `D-0835` — resuelto_en
- `D-0837` — usuario_id
- `D-0844` — distancia_por_ficha
- `D-0845` — precio_por_ficha
- `D-0846` — precio_por_minuto_espera

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
- `D-0246` — fleet.contrato_vehiculo
- `D-0247` — fleet.contrato_vehiculo
- `D-0248` — fleet.contrato_vehiculo
- `D-0249` — fleet.contrato_vehiculo
- `D-0292` — fleet.documento_vehiculo
- `D-0303` — fleet.documentos_chofer
- `D-0324` — fleet.gasto_turno
- `D-0325` — fleet.gasto_turno
- `D-0338` — fleet.gasto_vehiculo
- `D-0339` — fleet.gasto_vehiculo
- `D-0340` — fleet.gasto_vehiculo
- `D-0364` — fleet.liquidacion
- `D-0365` — fleet.liquidacion
- `D-0366` — fleet.liquidacion
- `D-0367` — fleet.liquidacion
- `D-0368` — fleet.liquidacion
- `D-0369` — fleet.liquidacion
- `D-0370` — fleet.liquidacion
- `D-0371` — fleet.liquidacion
- `D-0372` — fleet.liquidacion
- `D-0400` — fleet.liquidacion_ajuste
- `D-0401` — fleet.liquidacion_ajuste
- `D-0402` — fleet.liquidacion_ajuste
- `D-0411` — fleet.liquidacion_detalle
- `D-0420` — fleet.liquidacion_estado_historial
- `D-0421` — fleet.liquidacion_estado_historial
- `D-0422` — fleet.liquidacion_estado_historial
- `D-0431` — fleet.mantenimiento_vehiculo
- `D-0432` — fleet.mantenimiento_vehiculo
- `D-0445` — fleet.modelo
- `D-0453` — fleet.neumatico_historial_posicion
- `D-0454` — fleet.neumatico_historial_posicion
- `D-0455` — fleet.neumatico_historial_posicion
- `D-0456` — fleet.neumatico_historial_posicion
- `D-0472` — fleet.neumatico_imagen
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
| D-0349 | fleet.ingreso_turno.medio_pago | vocabulario_metodo_pago |
| D-0526 | fleet.neumatico_sugerencia.created_at | timestamp_naive_vs_tz |
| D-0527 | fleet.neumatico_sugerencia.updated_at | timestamp_naive_vs_tz |
| D-0547 | fleet.neumatico_vehiculo.fecha_alta | timestamp_naive_vs_tz |
| D-0548 | fleet.neumatico_vehiculo.fecha_baja | timestamp_naive_vs_tz |

---

## Archivos generados

- `orm_diff.json` — datos completos.
- `orm_diff_reporte.md` — este informe.
- `orm_diff_acciones.csv` — CSV de acciones sugeridas.
