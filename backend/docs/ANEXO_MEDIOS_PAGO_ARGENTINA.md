# ANEXO — Medios de Pago en Argentina

**Ultima actualizacion:** 2026-10-13
**Contexto:** analisis de preautorizaciones y cobros electronicos para
el modulo 4 (viaje de calle) de la app chofer.

**Aplicacion en TaxIP:** ver seccion final "Aplicacion al proyecto".

---

## 1. Como funciona la Preautorizacion en Argentina

Existen dos mundos segun la tecnologia de pago.

### A. Tarjetas de Credito vs. Tarjetas de Debito

**Tarjetas de Credito:**

- La preautorizacion bloquea un cupo sobre el limite de la tarjeta.
- **No genera movimiento de cobro** ni liquidacion financiera.
- Si el viaje se cancela, la retencion se anula instantaneamente.

**Tarjetas de Debito:**

- La red bancaria y de adquirencia (Visa Debito / Mastercard Debito)
  **no admite una "reserva virtual" sin tocar el dinero**.
- Para efectivizar la reserva, la procesadora debe **restar
  preventivamente el saldo real** de la cuenta bancaria / virtual del
  usuario.
- Si el viaje se cancela, el comercio emite la anulacion / reversa, pero
  **la devolucion en cuenta corriente puede demorar entre 24 horas y 5
  dias habiles** debido a las marcas y bancos emisores.

### B. Pagos con "Dinero en Cuenta" (CVU / Billeteras Virtuales)

Si la transaccion es directa desde la billetera mediante dinero en
cuenta (Mercado Pago, Uala, MODO):

- **No existe el estandar de preautorizacion** en el protocolo de
  transferencias o DEBIN.
- Se ejecuta un **cobro inmediato**.
- Ante una cancelacion, la billetera / plataforma debe procesar un
  **Reembolso / Refund programatico** (via API).

---

## 2. Disponibilidad en Billeteras / Pasarelas

Las apps de transporte **no interactuan solo como billeteras de usuario
final**, sino a traves de sus **pasarelas de pago (APIs)**.

| Billetera / Pasarela | Preautorizacion (`capture: false`) | Comportamiento en Debito | Mecanismo de Reversa |
|----------------------|------------------------------------|--------------------------|----------------------|
| **Mercado Pago** (API / Checkout) | Si (via parametro `capture: false`) | Impacta como cobro cautelar retenido en saldo bancario. | Se cancela via API (`PUT /v1/payments/{id}` con `status=cancelled`). La acreditacion depende del emisor. |
| **MODO** (via adquirente Payway / Fiserv) | Si (sujeto a reglas del adquirente subyacente) | Bloquea saldo de la caja de ahorro / cuenta bancaria vinculada. | Se libera el hold; el tiempo de reflejo en homebanking varia segun el banco. |
| **Uala** (Uala Bis) | No nativo para cobros diferidos tipo transporte | Disenado para cobros directos de venta inmediata (POS / Checkout). | Requiere efectuar un Refund total del cobro realizado. |
| **Pasarelas de adquirencia directa** (Payway / Clover / Fiserv) | Si | Solucion estandar de TPV / Pasarela para hoteles, alquiler de autos, movilidad. | Transaccion de "Anulacion de Preautorizacion". |

---

## 3. Desafio Operativo del Modelo

### Caso de uso: viajes / movilidad

**1. Efecto "Saldo Bloqueado" para el usuario:**

- Al solicitar el viaje por $5.000 ARS con tarjeta de debito, la
  preautorizacion **debita inmediatamente $5.000 ARS** de su cuenta.
- Si cancela a los 30 segundos, aunque el backend envie la reversa
  instantaneamente a Mercado Pago / Pasarela, la red bancaria del
  cliente podria tardar **entre 24h y 72h** en acreditarle de vuelta esos
  $5.000 ARS.
- **Suele generar quejas de soporte** por "doble cobro" o "falta de
  devolucion".

**2. Diferencia de tarifa (importe estimado vs. importe final):**

- **Inicio del viaje:** se preautoriza por un estimado (ej. $5.000).
- **Fin del viaje:**
  - Si el importe final es mayor (ej. $5.800 por trafico o desvio): se
    ejecuta una **captura parcial / total** o se procesa un cobro
    complementario.
  - Si el importe final es menor (ej. $4.200): se captura $4.200 y el
    remanente de $800 **se libera automaticamente**.

---

## 4. Recomendacion Arquitectonica

Si estas disenando este esquema para una app de movilidad en Argentina:

### 1. Usa la API de Integracion de Pasarela

**Ejemplo: Mercado Pago Developers.**

- Configura las transacciones con el parametro de **reserva diferida**
  (`capture: false`) al asignar el viaje.
- Al finalizar la carrera, ejecuta la llamada de **captura**
  (`capture: true`).
- Si el viaje no se realiza, ejecuta la **cancelacion**.

### 2. Claridad en la UX/UI

**Avisa expresamente en la app:**

> "Se realizara una retencion temporal de $X en tu tarjeta de debito /
> credito. Si el viaje se cancela, la retencion se liberara segun los
> tiempos de tu entidad bancaria."

### 3. Alternativa con Dinero en Cuenta

Si la billetera opera con **saldo virtual (CVU)**:

- Es mas eficiente solicitar una **autorizacion de debito recurrente /
  tokenizado** y ejecutar el cobro **unicamente al finalizar el viaje**.
- O bien, usar un **fondo de garantia / wallet interno** de la propia
  app para evitar la friccion bancaria en las reversas.

---

## 5. Aplicacion al proyecto TaxIP

**Contexto del proyecto:**

- **Momento 1 (hoy):** viajes comunes pagan con `efectivo`,
  `tarjeta_debito`, `qr`, `transferencia`. **La plataforma no retiene
  fondos.**
- **Momento 2 (futuro):** viajes corporativos con cuenta corriente.
- **Momento 3 (futuro):** billetera TaxIP con saldo.

**Aplicacion en el modulo 4 (viaje de calle):**

- **Hoy:** el chofer cobra con `efectivo` (registro manual), `qr` o
  `transferencia` (QR generado por el backend).
- **Preautorizaciones:** **NO aplican al Momento 1**, porque la
  plataforma no procesa pagos de tarjeta. Los pagos electronicos van
  directo a la cuenta del propietario.
- **Cuando se implemente el Momento 3 (billetera TaxIP):** aplicar las
  recomendaciones de esta seccion.

**Decisiones pendientes:**

- **Cuando se integre MercadoPago (largo plazo, deuda `F4`):** usar
  `capture: false` + `capture: true`.
- **UX:** avisar al pasajero sobre retenciones segun la recomendacion 2.
- **Billetera TaxIP (Momento 3):** preferir autorizacion tokenizada +
  cobro al finalizar (recomendacion 3).

---

**FIN DEL DOCUMENTO**