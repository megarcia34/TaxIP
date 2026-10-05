# Reporte de Diff ORM vs DB

**Fecha:** 2026-10-05T11:52:30.068080+00:00

## Resumen ejecutivo

- **490 diferencias** en total.
- **Tier 1**: 80 items.
- **Tier 2**: 298 items.
- **Tier 3**: 111 items.
- **Tier 4**: 1 items.
- **2 items requieren decision manual.**

### Por clasificacion

| Clasificacion | Cantidad |
|---|---|
| indice_falta | 172 |
| constraint_nombre_desalineado | 124 |
| constraint_desalineada | 72 |
| constraint_falta | 61 |
| comment_desalineado | 20 |
| constraint_sobra | 17 |
| tabla_falta | 10 |
| nullable_desalineado | 4 |
| indice_nombre_desalineado | 3 |
| indice_sobra | 3 |
| schema_falta | 2 |
| tabla_sobra | 1 |
| columna_falta | 1 |

---

## Tier 1 — 80 items

### comment_desalineado (6)

- `D-0188` — declarado_por
- `D-0189` — transaccion_id
- `D-0324` — snapshot_dia_contractual
- `D-0452` — latitud
- `D-0453` — longitud
- `D-0474` — solicitado_en

### constraint_desalineada (10)

- `D-0062` — auth.usuario
- `D-0114` — fleet.chofer_vehiculo
- `D-0190` — fleet.ingreso_turno
- `D-0325` — fleet.turno_chofer
- `D-0334` — fleet.vehiculo
- `D-0391` — payment.transaccion
- `D-0421` — tenant.control_base
- `D-0440` — trip.calificacion
- `D-0454` — trip.historial_estado_viaje
- `D-0475` — trip.viaje_solicitado

### constraint_falta (10)

- `D-0066` — auth.usuario
- `D-0118` — fleet.chofer_vehiculo
- `D-0336` — fleet.vehiculo
- `D-0338` — fleet.vehiculo
- `D-0339` — fleet.vehiculo
- `D-0445` — trip.calificacion
- `D-0476` — trip.viaje_solicitado
- `D-0477` — trip.viaje_solicitado
- `D-0478` — trip.viaje_solicitado
- `D-0479` — trip.viaje_solicitado

### constraint_nombre_desalineado (27)

- `D-0063` — auth.usuario
- `D-0064` — auth.usuario
- `D-0065` — auth.usuario
- `D-0115` — fleet.chofer_vehiculo
- `D-0116` — fleet.chofer_vehiculo
- `D-0117` — fleet.chofer_vehiculo
- `D-0326` — fleet.turno_chofer
- `D-0327` — fleet.turno_chofer
- `D-0328` — fleet.turno_chofer
- `D-0335` — fleet.vehiculo
- `D-0392` — payment.transaccion
- `D-0393` — payment.transaccion
- `D-0394` — payment.transaccion
- `D-0422` — tenant.control_base
- `D-0423` — tenant.control_base
- `D-0441` — trip.calificacion
- `D-0442` — trip.calificacion
- `D-0443` — trip.calificacion
- `D-0455` — trip.historial_estado_viaje
- `D-0480` — trip.viaje_solicitado
- `D-0481` — trip.viaje_solicitado
- `D-0482` — trip.viaje_solicitado
- `D-0483` — trip.viaje_solicitado
- `D-0484` — trip.viaje_solicitado
- `D-0485` — trip.viaje_solicitado
- `D-0486` — trip.viaje_solicitado
- `D-0487` — trip.viaje_solicitado

### constraint_sobra (2)

- `D-0337` — fleet.vehiculo
- `D-0444` — trip.calificacion

### indice_falta (18)

- `D-0067` — auth.usuario
- `D-0119` — fleet.chofer_vehiculo
- `D-0191` — fleet.ingreso_turno
- `D-0329` — fleet.turno_chofer
- `D-0330` — fleet.turno_chofer
- `D-0331` — fleet.turno_chofer
- `D-0332` — fleet.turno_chofer
- `D-0333` — fleet.turno_chofer
- `D-0340` — fleet.vehiculo
- `D-0341` — fleet.vehiculo
- `D-0342` — fleet.vehiculo
- `D-0343` — fleet.vehiculo
- `D-0395` — payment.transaccion
- `D-0424` — tenant.control_base
- `D-0425` — tenant.control_base
- `D-0446` — trip.calificacion
- `D-0456` — trip.historial_estado_viaje
- `D-0488` — trip.viaje_solicitado

### indice_nombre_desalineado (3)

- `D-0068` — auth.usuario
- `D-0344` — fleet.vehiculo
- `D-0490` — trip.viaje_solicitado

### indice_sobra (2)

- `D-0120` — fleet.chofer_vehiculo
- `D-0489` — trip.viaje_solicitado

### tabla_falta (2)

- `D-0004` — auth.codigo_metadatos
- `D-0005` — auth.codigo_verificacion

---

## Tier 2 — 298 items

### columna_falta (1)

- `D-0073` — control_base_id

### constraint_desalineada (62)

- `D-0015` — audit.alerta_desvio
- `D-0018` — audit.log_acciones
- `D-0020` — audit.log_gps
- `D-0024` — auth.auditoria_email
- `D-0026` — auth.autorizacion_inicio
- `D-0031` — auth.direccion_frecuente
- `D-0034` — auth.perfil_general
- `D-0039` — auth.refresh_token
- `D-0044` — auth.reset_token
- `D-0048` — auth.taxista_favorito
- `D-0052` — auth.tipo_usuario
- `D-0057` — auth.turno_empleado
- `D-0069` — auth.usuario_empresa
- `D-0074` — auth.usuario_rol
- `D-0078` — corporate.cuenta_corriente
- `D-0086` — corporate.factura_corporativa
- `D-0095` — corporate.movimiento_cuenta
- `D-0102` — corporate.pago_corporativo
- `D-0107` — fleet.categoria_gasto
- `D-0121` — fleet.contrato_qr
- `D-0128` — fleet.contrato_vehiculo
- `D-0151` — fleet.documento_propietario
- `D-0156` — fleet.documento_vehiculo
- `D-0161` — fleet.documentos_chofer
- `D-0168` — fleet.foto_vehiculo
- `D-0172` — fleet.gasto_turno
- `D-0181` — fleet.gasto_vehiculo
- `D-0192` — fleet.liquidacion
- `D-0203` — fleet.liquidacion_ajuste
- `D-0208` — fleet.liquidacion_detalle
- `D-0211` — fleet.liquidacion_estado_historial
- `D-0217` — fleet.mantenimiento_vehiculo
- `D-0221` — fleet.marca
- `D-0226` — fleet.modelo
- `D-0231` — fleet.neumatico_historial_posicion
- `D-0243` — fleet.neumatico_imagen
- `D-0254` — fleet.neumatico_medicion
- `D-0263` — fleet.neumatico_operacion
- `D-0273` — fleet.neumatico_operacion_detalle
- `D-0279` — fleet.neumatico_sugerencia
- `D-0292` — fleet.neumatico_vehiculo
- `D-0306` — fleet.notificacion_vencimiento
- `D-0317` — fleet.propietario_vehiculo
- `D-0345` — geo.ciudad
- `D-0349` — geo.pais
- `D-0351` — geo.provincia
- `D-0354` — notification.notificacion
- `D-0357` — payment.billetera
- `D-0365` — payment.configuracion_tarifa
- `D-0368` — payment.configuracion_tarifa_vehiculo
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

- `D-0028` — auth.autorizacion_inicio
- `D-0037` — auth.perfil_general
- `D-0046` — auth.reset_token
- `D-0054` — auth.tipo_usuario
- `D-0081` — corporate.cuenta_corriente
- `D-0088` — corporate.factura_corporativa
- `D-0110` — fleet.categoria_gasto
- `D-0123` — fleet.contrato_qr
- `D-0176` — fleet.gasto_turno
- `D-0223` — fleet.marca
- `D-0360` — payment.billetera
- `D-0378` — payment.metodo_pago
- `D-0399` — public.comercio
- `D-0419` — tenant.configuracion_tenant
- `D-0434` — tenant.factura

### indice_falta (154)

| Tabla | Cantidad |
|---|---|
| fleet.contrato_vehiculo | 7 |
| fleet.notificacion_vencimiento | 7 |
| fleet.neumatico_historial_posicion | 6 |
| fleet.neumatico_vehiculo | 6 |
| public.escaneo_qr | 6 |
| corporate.factura_corporativa | 5 |
| fleet.neumatico_imagen | 5 |
| fleet.neumatico_operacion | 5 |
| fleet.neumatico_sugerencia | 5 |
| payment.pago_empresa | 5 |
| tenant.factura | 5 |
| fleet.contrato_qr | 4 |
| fleet.documentos_chofer | 4 |
| fleet.neumatico_medicion | 4 |
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
| audit.alerta_desvio | 1 |
| audit.log_acciones | 1 |
| audit.log_gps | 1 |
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

- `D-0468` — trip.panico

### nullable_desalineado (4)

- `D-0014` — viaje_id
- `D-0106` — updated_at
- `D-0180` — vehiculo_id
- `D-0216` — vehiculo_id

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

- `D-0085` — estado
- `D-0094` — tipo_movimiento
- `D-0101` — estado
- `D-0304` — entidad_tipo
- `D-0305` — nivel
- `D-0363` — descripcion
- `D-0364` — modo_calculo
- `D-0402` — resultado
- `D-0403` — tipo_qr
- `D-0462` — resuelto_en
- `D-0463` — usuario_id
- `D-0469` — distancia_por_ficha
- `D-0470` — precio_por_ficha
- `D-0471` — precio_por_minuto_espera

### constraint_nombre_desalineado (97)

- `D-0016` — audit.alerta_desvio
- `D-0021` — audit.log_gps
- `D-0022` — audit.log_gps
- `D-0032` — auth.direccion_frecuente
- `D-0035` — auth.perfil_general
- `D-0036` — auth.perfil_general
- `D-0040` — auth.refresh_token
- `D-0045` — auth.reset_token
- `D-0049` — auth.taxista_favorito
- `D-0050` — auth.taxista_favorito
- `D-0058` — auth.turno_empleado
- `D-0059` — auth.turno_empleado
- `D-0070` — auth.usuario_empresa
- `D-0071` — auth.usuario_empresa
- `D-0108` — fleet.categoria_gasto
- `D-0129` — fleet.contrato_vehiculo
- `D-0130` — fleet.contrato_vehiculo
- `D-0131` — fleet.contrato_vehiculo
- `D-0132` — fleet.contrato_vehiculo
- `D-0157` — fleet.documento_vehiculo
- `D-0162` — fleet.documentos_chofer
- `D-0173` — fleet.gasto_turno
- `D-0174` — fleet.gasto_turno
- `D-0182` — fleet.gasto_vehiculo
- `D-0183` — fleet.gasto_vehiculo
- `D-0184` — fleet.gasto_vehiculo
- `D-0193` — fleet.liquidacion
- `D-0194` — fleet.liquidacion
- `D-0195` — fleet.liquidacion
- `D-0196` — fleet.liquidacion
- `D-0197` — fleet.liquidacion
- `D-0198` — fleet.liquidacion
- `D-0199` — fleet.liquidacion
- `D-0200` — fleet.liquidacion
- `D-0201` — fleet.liquidacion
- `D-0204` — fleet.liquidacion_ajuste
- `D-0205` — fleet.liquidacion_ajuste
- `D-0206` — fleet.liquidacion_ajuste
- `D-0209` — fleet.liquidacion_detalle
- `D-0212` — fleet.liquidacion_estado_historial
- `D-0213` — fleet.liquidacion_estado_historial
- `D-0214` — fleet.liquidacion_estado_historial
- `D-0218` — fleet.mantenimiento_vehiculo
- `D-0219` — fleet.mantenimiento_vehiculo
- `D-0227` — fleet.modelo
- `D-0232` — fleet.neumatico_historial_posicion
- `D-0233` — fleet.neumatico_historial_posicion
- `D-0234` — fleet.neumatico_historial_posicion
- `D-0235` — fleet.neumatico_historial_posicion
- `D-0244` — fleet.neumatico_imagen
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
