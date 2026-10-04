# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-04T21:18:46.418728+00:00

## Resumen ejecutivo

- **887 diferencias** en total.
- **Tier 1**: 141 items.
- **Tier 2**: 626 items.
- **Tier 3**: 119 items.
- **Tier 4**: 1 items.
- **3 items requieren decision manual.**

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
| tipo_desalineado | 5 |
| nullable_desalineado | 4 |
| indice_nombre_desalineado | 4 |
| indice_sobra | 3 |
| schema_falta | 2 |
| tabla_sobra | 1 |
| columna_falta | 1 |

---

## Tier 1 — 141 items

### comment_desalineado (7)

- `D-0348` — declarado_por
- `D-0349` — medio_pago
- `D-0350` — transaccion_id
- `D-0597` — snapshot_dia_contractual
- `D-0815` — latitud
- `D-0816` — longitud
- `D-0852` — solicitado_en

### constraint_desalineada (10)

- `D-0111` — auth.usuario
- `D-0224` — fleet.chofer_vehiculo
- `D-0351` — fleet.ingreso_turno
- `D-0598` — fleet.turno_chofer
- `D-0615` — fleet.vehiculo
- `D-0719` — payment.transaccion
- `D-0759` — tenant.control_base
- `D-0794` — trip.calificacion
- `D-0817` — trip.historial_estado_viaje
- `D-0853` — trip.viaje_solicitado

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
- `D-0599` — fleet.turno_chofer
- `D-0600` — fleet.turno_chofer
- `D-0601` — fleet.turno_chofer
- `D-0616` — fleet.vehiculo
- `D-0720` — payment.transaccion
- `D-0721` — payment.transaccion
- `D-0722` — payment.transaccion
- `D-0760` — tenant.control_base
- `D-0761` — tenant.control_base
- `D-0795` — trip.calificacion
- `D-0796` — trip.calificacion
- `D-0797` — trip.calificacion
- `D-0818` — trip.historial_estado_viaje
- `D-0858` — trip.viaje_solicitado
- `D-0859` — trip.viaje_solicitado
- `D-0860` — trip.viaje_solicitado
- `D-0861` — trip.viaje_solicitado
- `D-0862` — trip.viaje_solicitado
- `D-0863` — trip.viaje_solicitado
- `D-0864` — trip.viaje_solicitado
- `D-0865` — trip.viaje_solicitado

### constraint_sobra (10)

- `D-0618` — fleet.vehiculo
- `D-0798` — trip.calificacion
- `D-0876` — trip.viaje_solicitado
- `D-0877` — trip.viaje_solicitado
- `D-0878` — trip.viaje_solicitado
- `D-0879` — trip.viaje_solicitado
- `D-0880` — trip.viaje_solicitado
- `D-0881` — trip.viaje_solicitado
- `D-0882` — trip.viaje_solicitado
- `D-0883` — trip.viaje_solicitado

### indice_falta (18)

- `D-0119` — auth.usuario
- `D-0232` — fleet.chofer_vehiculo
- `D-0362` — fleet.ingreso_turno
- `D-0610` — fleet.turno_chofer
- `D-0611` — fleet.turno_chofer
- `D-0612` — fleet.turno_chofer
- `D-0613` — fleet.turno_chofer
- `D-0614` — fleet.turno_chofer
- `D-0626` — fleet.vehiculo
- `D-0627` — fleet.vehiculo
- `D-0628` — fleet.vehiculo
- `D-0629` — fleet.vehiculo
- `D-0724` — payment.transaccion
- `D-0764` — tenant.control_base
- `D-0765` — tenant.control_base
- `D-0805` — trip.calificacion
- `D-0820` — trip.historial_estado_viaje
- `D-0884` — trip.viaje_solicitado

### indice_nombre_desalineado (4)

- `D-0120` — auth.usuario
- `D-0630` — fleet.vehiculo
- `D-0886` — trip.viaje_solicitado
- `D-0887` — trip.viaje_solicitado

### indice_sobra (2)

- `D-0233` — fleet.chofer_vehiculo
- `D-0885` — trip.viaje_solicitado

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

### tipo_desalineado (3)

- `D-0223` — ubicacion
- `D-0850` — destino
- `D-0851` — origen

---

## Tier 2 — 626 items

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
- `D-0526` — fleet.neumatico_sugerencia
- `D-0545` — fleet.neumatico_vehiculo
- `D-0566` — fleet.notificacion_vencimiento
- `D-0585` — fleet.propietario_vehiculo
- `D-0631` — geo.ciudad
- `D-0637` — geo.pais
- `D-0641` — geo.provincia
- `D-0646` — notification.notificacion
- `D-0653` — payment.billetera
- `D-0670` — payment.configuracion_tarifa
- `D-0681` — payment.configuracion_tarifa_vehiculo
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
- `D-0656` — payment.billetera
- `D-0700` — payment.metodo_pago
- `D-0728` — public.comercio
- `D-0756` — tenant.configuracion_tenant
- `D-0777` — tenant.factura

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

- `D-0839` — trip.panico

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

### tipo_desalineado (2)

- `D-0335` — km_registro
- `D-0832` — ubicacion

---

## Tier 3 — 119 items

### comment_desalineado (22)

- `D-0156` — estado
- `D-0178` — tipo_movimiento
- `D-0193` — estado
- `D-0244` — estado_contrato
- `D-0564` — entidad_tipo
- `D-0565` — nivel
- `D-0661` — descripcion
- `D-0662` — distancia_por_ficha
- `D-0663` — hora_fin_nocturno
- `D-0664` — hora_inicio_nocturno
- `D-0665` — modo_calculo
- `D-0666` — moneda
- `D-0667` — precio_por_ficha
- `D-0668` — precio_por_minuto_espera
- `D-0669` — recargo_domingo
- `D-0738` — resultado
- `D-0739` — tipo_qr
- `D-0831` — resuelto_en
- `D-0833` — usuario_id
- `D-0840` — distancia_por_ficha
- `D-0841` — precio_por_ficha
- `D-0842` — precio_por_minuto_espera

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

---

## Archivos generados

- `orm_diff.json` — datos completos.
- `orm_diff_reporte.md` — este informe.
- `orm_diff_acciones.csv` — CSV de acciones sugeridas.
