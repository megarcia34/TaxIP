# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-05T10:56:58.344741+00:00

## Resumen ejecutivo

- **515 diferencias** en total.
- **Tier 1**: 97 items.
- **Tier 2**: 306 items.
- **Tier 3**: 111 items.
- **Tier 4**: 1 items.
- **2 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| indice_falta | 180 |
| constraint_nombre_desalineado | 124 |
| constraint_desalineada | 72 |
| constraint_falta | 69 |
| constraint_sobra | 25 |
| comment_desalineado | 20 |
| tabla_falta | 10 |
| nullable_desalineado | 4 |
| indice_nombre_desalineado | 4 |
| indice_sobra | 3 |
| schema_falta | 2 |
| tabla_sobra | 1 |
| columna_falta | 1 |

---

## Tier 1 — 97 items

### comment_desalineado (6)

- `D-0196` — declarado_por
- `D-0197` — transaccion_id
- `D-0332` — snapshot_dia_contractual
- `D-0460` — latitud
- `D-0461` — longitud
- `D-0482` — solicitado_en

### constraint_desalineada (10)

- `D-0070` — auth.usuario
- `D-0122` — fleet.chofer_vehiculo
- `D-0198` — fleet.ingreso_turno
- `D-0333` — fleet.turno_chofer
- `D-0342` — fleet.vehiculo
- `D-0399` — payment.transaccion
- `D-0429` — tenant.control_base
- `D-0448` — trip.calificacion
- `D-0462` — trip.historial_estado_viaje
- `D-0483` — trip.viaje_solicitado

### constraint_falta (18)

- `D-0074` — auth.usuario
- `D-0126` — fleet.chofer_vehiculo
- `D-0344` — fleet.vehiculo
- `D-0346` — fleet.vehiculo
- `D-0347` — fleet.vehiculo
- `D-0453` — trip.calificacion
- `D-0484` — trip.viaje_solicitado
- `D-0485` — trip.viaje_solicitado
- `D-0486` — trip.viaje_solicitado
- `D-0487` — trip.viaje_solicitado
- `D-0496` — trip.viaje_solicitado
- `D-0497` — trip.viaje_solicitado
- `D-0498` — trip.viaje_solicitado
- `D-0499` — trip.viaje_solicitado
- `D-0500` — trip.viaje_solicitado
- `D-0501` — trip.viaje_solicitado
- `D-0502` — trip.viaje_solicitado
- `D-0503` — trip.viaje_solicitado

### constraint_nombre_desalineado (27)

- `D-0071` — auth.usuario
- `D-0072` — auth.usuario
- `D-0073` — auth.usuario
- `D-0123` — fleet.chofer_vehiculo
- `D-0124` — fleet.chofer_vehiculo
- `D-0125` — fleet.chofer_vehiculo
- `D-0334` — fleet.turno_chofer
- `D-0335` — fleet.turno_chofer
- `D-0336` — fleet.turno_chofer
- `D-0343` — fleet.vehiculo
- `D-0400` — payment.transaccion
- `D-0401` — payment.transaccion
- `D-0402` — payment.transaccion
- `D-0430` — tenant.control_base
- `D-0431` — tenant.control_base
- `D-0449` — trip.calificacion
- `D-0450` — trip.calificacion
- `D-0451` — trip.calificacion
- `D-0463` — trip.historial_estado_viaje
- `D-0488` — trip.viaje_solicitado
- `D-0489` — trip.viaje_solicitado
- `D-0490` — trip.viaje_solicitado
- `D-0491` — trip.viaje_solicitado
- `D-0492` — trip.viaje_solicitado
- `D-0493` — trip.viaje_solicitado
- `D-0494` — trip.viaje_solicitado
- `D-0495` — trip.viaje_solicitado

### constraint_sobra (10)

- `D-0345` — fleet.vehiculo
- `D-0452` — trip.calificacion
- `D-0504` — trip.viaje_solicitado
- `D-0505` — trip.viaje_solicitado
- `D-0506` — trip.viaje_solicitado
- `D-0507` — trip.viaje_solicitado
- `D-0508` — trip.viaje_solicitado
- `D-0509` — trip.viaje_solicitado
- `D-0510` — trip.viaje_solicitado
- `D-0511` — trip.viaje_solicitado

### indice_falta (18)

- `D-0075` — auth.usuario
- `D-0127` — fleet.chofer_vehiculo
- `D-0199` — fleet.ingreso_turno
- `D-0337` — fleet.turno_chofer
- `D-0338` — fleet.turno_chofer
- `D-0339` — fleet.turno_chofer
- `D-0340` — fleet.turno_chofer
- `D-0341` — fleet.turno_chofer
- `D-0348` — fleet.vehiculo
- `D-0349` — fleet.vehiculo
- `D-0350` — fleet.vehiculo
- `D-0351` — fleet.vehiculo
- `D-0403` — payment.transaccion
- `D-0432` — tenant.control_base
- `D-0433` — tenant.control_base
- `D-0454` — trip.calificacion
- `D-0464` — trip.historial_estado_viaje
- `D-0512` — trip.viaje_solicitado

### indice_nombre_desalineado (4)

- `D-0076` — auth.usuario
- `D-0352` — fleet.vehiculo
- `D-0514` — trip.viaje_solicitado
- `D-0515` — trip.viaje_solicitado

### indice_sobra (2)

- `D-0128` — fleet.chofer_vehiculo
- `D-0513` — trip.viaje_solicitado

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

---

## Tier 2 — 306 items

### columna_falta (1)

- `D-0081` — control_base_id

### constraint_desalineada (62)

- `D-0015` — audit.alerta_desvio
- `D-0020` — audit.log_acciones
- `D-0026` — audit.log_gps
- `D-0032` — auth.auditoria_email
- `D-0034` — auth.autorizacion_inicio
- `D-0039` — auth.direccion_frecuente
- `D-0042` — auth.perfil_general
- `D-0047` — auth.refresh_token
- `D-0052` — auth.reset_token
- `D-0056` — auth.taxista_favorito
- `D-0060` — auth.tipo_usuario
- `D-0065` — auth.turno_empleado
- `D-0077` — auth.usuario_empresa
- `D-0082` — auth.usuario_rol
- `D-0086` — corporate.cuenta_corriente
- `D-0094` — corporate.factura_corporativa
- `D-0103` — corporate.movimiento_cuenta
- `D-0110` — corporate.pago_corporativo
- `D-0115` — fleet.categoria_gasto
- `D-0129` — fleet.contrato_qr
- `D-0136` — fleet.contrato_vehiculo
- `D-0159` — fleet.documento_propietario
- `D-0164` — fleet.documento_vehiculo
- `D-0169` — fleet.documentos_chofer
- `D-0176` — fleet.foto_vehiculo
- `D-0180` — fleet.gasto_turno
- `D-0189` — fleet.gasto_vehiculo
- `D-0200` — fleet.liquidacion
- `D-0211` — fleet.liquidacion_ajuste
- `D-0216` — fleet.liquidacion_detalle
- `D-0219` — fleet.liquidacion_estado_historial
- `D-0225` — fleet.mantenimiento_vehiculo
- `D-0229` — fleet.marca
- `D-0234` — fleet.modelo
- `D-0239` — fleet.neumatico_historial_posicion
- `D-0251` — fleet.neumatico_imagen
- `D-0262` — fleet.neumatico_medicion
- `D-0271` — fleet.neumatico_operacion
- `D-0281` — fleet.neumatico_operacion_detalle
- `D-0287` — fleet.neumatico_sugerencia
- `D-0300` — fleet.neumatico_vehiculo
- `D-0314` — fleet.notificacion_vencimiento
- `D-0325` — fleet.propietario_vehiculo
- `D-0353` — geo.ciudad
- `D-0357` — geo.pais
- `D-0359` — geo.provincia
- `D-0362` — notification.notificacion
- `D-0365` — payment.billetera
- `D-0373` — payment.configuracion_tarifa
- `D-0376` — payment.configuracion_tarifa_vehiculo
- ... y 12 mas (ver JSON)

### constraint_falta (51)

| Tabla | Cantidad |
|---|---|
| fleet.contrato_vehiculo | 11 |
| corporate.cuenta_corriente | 3 |
| fleet.neumatico_sugerencia | 3 |
| fleet.neumatico_vehiculo | 3 |
| fleet.notificacion_vencimiento | 3 |
| corporate.movimiento_cuenta | 2 |
| payment.pago_empresa | 2 |
| public.escaneo_qr | 2 |
| auth.autorizacion_inicio | 1 |
| auth.refresh_token | 1 |
| auth.tipo_usuario | 1 |
| auth.turno_empleado | 1 |
| auth.usuario_rol | 1 |
| corporate.factura_corporativa | 1 |
| fleet.categoria_gasto | 1 |
| fleet.contrato_qr | 1 |
| fleet.documento_propietario | 1 |
| fleet.documentos_chofer | 1 |
| fleet.gasto_turno | 1 |
| fleet.marca | 1 |
| fleet.modelo | 1 |
| fleet.neumatico_historial_posicion | 1 |
| fleet.neumatico_imagen | 1 |
| fleet.neumatico_medicion | 1 |
| fleet.neumatico_operacion | 1 |
| fleet.propietario_vehiculo | 1 |
| payment.billetera | 1 |
| payment.configuracion_tarifa_vehiculo | 1 |
| public.comercio | 1 |
| tenant.factura | 1 |

### constraint_sobra (15)

- `D-0036` — auth.autorizacion_inicio
- `D-0045` — auth.perfil_general
- `D-0054` — auth.reset_token
- `D-0062` — auth.tipo_usuario
- `D-0089` — corporate.cuenta_corriente
- `D-0096` — corporate.factura_corporativa
- `D-0118` — fleet.categoria_gasto
- `D-0131` — fleet.contrato_qr
- `D-0184` — fleet.gasto_turno
- `D-0231` — fleet.marca
- `D-0368` — payment.billetera
- `D-0386` — payment.metodo_pago
- `D-0407` — public.comercio
- `D-0427` — tenant.configuracion_tenant
- `D-0442` — tenant.factura

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

- `D-0476` — trip.panico

### nullable_desalineado (4)

- `D-0014` — viaje_id
- `D-0114` — updated_at
- `D-0188` — vehiculo_id
- `D-0224` — vehiculo_id

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

---

## Tier 3 — 111 items

### comment_desalineado (14)

- `D-0093` — estado
- `D-0102` — tipo_movimiento
- `D-0109` — estado
- `D-0312` — entidad_tipo
- `D-0313` — nivel
- `D-0371` — descripcion
- `D-0372` — modo_calculo
- `D-0410` — resultado
- `D-0411` — tipo_qr
- `D-0470` — resuelto_en
- `D-0471` — usuario_id
- `D-0477` — distancia_por_ficha
- `D-0478` — precio_por_ficha
- `D-0479` — precio_por_minuto_espera

### constraint_nombre_desalineado (97)

- `D-0016` — audit.alerta_desvio
- `D-0027` — audit.log_gps
- `D-0028` — audit.log_gps
- `D-0040` — auth.direccion_frecuente
- `D-0043` — auth.perfil_general
- `D-0044` — auth.perfil_general
- `D-0048` — auth.refresh_token
- `D-0053` — auth.reset_token
- `D-0057` — auth.taxista_favorito
- `D-0058` — auth.taxista_favorito
- `D-0066` — auth.turno_empleado
- `D-0067` — auth.turno_empleado
- `D-0078` — auth.usuario_empresa
- `D-0079` — auth.usuario_empresa
- `D-0116` — fleet.categoria_gasto
- `D-0137` — fleet.contrato_vehiculo
- `D-0138` — fleet.contrato_vehiculo
- `D-0139` — fleet.contrato_vehiculo
- `D-0140` — fleet.contrato_vehiculo
- `D-0165` — fleet.documento_vehiculo
- `D-0170` — fleet.documentos_chofer
- `D-0181` — fleet.gasto_turno
- `D-0182` — fleet.gasto_turno
- `D-0190` — fleet.gasto_vehiculo
- `D-0191` — fleet.gasto_vehiculo
- `D-0192` — fleet.gasto_vehiculo
- `D-0201` — fleet.liquidacion
- `D-0202` — fleet.liquidacion
- `D-0203` — fleet.liquidacion
- `D-0204` — fleet.liquidacion
- `D-0205` — fleet.liquidacion
- `D-0206` — fleet.liquidacion
- `D-0207` — fleet.liquidacion
- `D-0208` — fleet.liquidacion
- `D-0209` — fleet.liquidacion
- `D-0212` — fleet.liquidacion_ajuste
- `D-0213` — fleet.liquidacion_ajuste
- `D-0214` — fleet.liquidacion_ajuste
- `D-0217` — fleet.liquidacion_detalle
- `D-0220` — fleet.liquidacion_estado_historial
- `D-0221` — fleet.liquidacion_estado_historial
- `D-0222` — fleet.liquidacion_estado_historial
- `D-0226` — fleet.mantenimiento_vehiculo
- `D-0227` — fleet.mantenimiento_vehiculo
- `D-0235` — fleet.modelo
- `D-0240` — fleet.neumatico_historial_posicion
- `D-0241` — fleet.neumatico_historial_posicion
- `D-0242` — fleet.neumatico_historial_posicion
- `D-0243` — fleet.neumatico_historial_posicion
- `D-0252` — fleet.neumatico_imagen
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

---

## Archivos generados

- `orm_diff.json` — datos completos.
- `orm_diff_reporte.md` — este informe.
- `orm_diff_acciones.csv` — CSV de acciones sugeridas.
