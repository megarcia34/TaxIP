# TAXIP — REFERENCIA DE MIGRACIONES Y BASE DE DATOS

## Propósito

Este documento contiene decisiones y antecedentes relevantes sobre
la estructura de la base de datos TAXIP.

Su función es servir como elemento de consulta durante futuros
desarrollos y migraciones.

No constituye un procedimiento obligatorio ni bloquea el desarrollo.

---

## 1. ESTRUCTURAS LEGACY ANALIZADAS

### auth.usuario_rol

Campo:

- control_base_id

Situación analizada:

- 0 registros con valor
- 2 registros NULL

Decisión:

- Puede eliminarse cuando corresponda.

---

### fleet.vehiculo

Campos legacy:

- desgaste_manual
- desgaste_neumaticos
- parches_neumaticos
- fecha_ultimo_cambio_neumaticos
- km_ultimo_cambio_neumaticos

Situación:

Existen datos históricos en estos campos.

Existe un nuevo sistema de neumáticos:

- neumatico_vehiculo
- neumatico_medicion

Antes de eliminar los campos legacy debe considerarse
el destino de la información histórica.

---

### fleet.chofer_vehiculo

Campos legacy:

- estado_aprobacion
- total_viajes

Existen datos históricos.

Antes de eliminar estos campos debe considerarse el significado
de la información existente y su eventual reemplazo.

---

### fleet.propietario_vehiculo

Campo:

- updated_at

Existen datos históricos.

Su eliminación debe considerarse según el modelo actual y su utilización.

---

### fleet.documento_vehiculo

Se detectaron columnas legacy sin datos.

Son candidatas a eliminación cuando corresponda.

---

### tenant.configuracion_tenant

Se detectaron columnas legacy sin datos.

Son candidatas a eliminación cuando corresponda.

IMPORTANTE:

No eliminar:

- canon_mensual_por_vehiculo
- porcentaje_taxip_por_viaje

Estos campos forman parte de la configuración vigente.

---

## 2. TABLAS SIN ACTIVIDAD

Se detectaron tablas existentes en la base de datos sin registros.

La ausencia de registros NO significa necesariamente que sean legacy.

Algunas pueden corresponder a funcionalidades todavía pendientes
de desarrollo.

Ejemplos:

- comunicacion.conversacion
- comunicacion.mensaje
- comunicacion.email_enviado
- rentabilidad.*
- audit.alertas_vencimiento

Antes de eliminar una de estas estructuras debe conocerse
su propósito dentro de la plataforma.

---

## 3. RENTABILIDAD HISTÓRICA

### rentabilidad.rentabilidad_diaria_vehiculo

Se detectaron registros históricos.

Cantidad identificada:

- 31 registros

No considerar automáticamente esta tabla como eliminable.

Primero debe determinarse si los datos tienen utilidad histórica,
funcional o si existe una estructura que los reemplace.

---

## 4. PRINCIPIOS DE REFERENCIA

Una diferencia entre ORM y base de datos no implica automáticamente
que una estructura deba eliminarse.

Una tabla sin registros no implica automáticamente que sea legacy.

Una columna con datos históricos requiere considerar esos datos
antes de eliminarla.

Una estructura puede existir en la base de datos aunque el módulo
correspondiente todavía no esté desarrollado.

---

## 5. ARQUITECTURA DE REFERENCIA

### Recaudación

`IngresoTurno` es la fuente de verdad para ingresos y recaudación.

### Jornadas

El sistema utiliza jornadas flexibles.

### Autorización de inicio

`turno_contractual` se conserva como metadata en:

`auth.autorizacion_inicio`

### Legacy de recaudación

Los antiguos campos de recaudación eliminados del código
no deben volver a utilizarse como fuente de verdad.

---

## 6. NOTA

Este documento es exclusivamente una referencia.

No constituye un procedimiento obligatorio.

No bloquea el desarrollo.

Su objetivo es conservar las decisiones y hallazgos obtenidos
durante el análisis de la base de datos, para poder consultarlos
cuando una futura modificación o migración afecte alguno de estos
elementos.

Si una futura decisión requiere información que no está contemplada
en este documento, debe analizarse el estado real de la base de datos
y del código en ese momento.