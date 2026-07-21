"use client";

import Link from "next/link";
import Image from "next/image";

export default function PropietariosPage() {
  const beneficios = [
    {
      icon: "💰",
      title: "Ganá más",
      desc: "Ingresos recurrentes por cada vehículo activo en tu municipio. Sumá todos los vehículos que quieras."
    },
    {
      icon: "📊",
      title: "Control total",
      desc: "Dashboard en tiempo real para gestionar tu flota, ver ganancias y controlar cada vehículo desde tu celular."
    },
    {
      icon: "🛡️",
      title: "Sin preocupaciones",
      desc: "Nosotros gestionamos los conductores y los viajes. Vos solo disfrutás de tus ingresos."
    },
    {
      icon: "🛒",
      title: "Descuentos en comercios",
      desc: "Comprá repuestos, talleres y servicios en comercios adheridos con descuentos exclusivos para propietarios TAXIP."
    },
    {
      icon: "🔒",
      title: "Seguros preferenciales",
      desc: "Contratá seguros para tus vehículos con tarifas especiales y pagá desde tu cuenta TAXIP."
    },
    {
      icon: "💳",
      title: "Pagos con dinero en cuenta",
      desc: "Usá el saldo de tus ganancias para pagar servicios, repuestos, seguros y todo lo que necesites."
    }
  ];

  const pasos = [
    {
      number: "1",
      title: "Registrá tus vehículos",
      desc: "Completá el registro de tu flota en la plataforma TAXIP. Te guiamos paso a paso."
    },
    {
      number: "2",
      title: "Asigná conductores",
      desc: "Nosotros te ayudamos a encontrar conductores o podés asignar los tuyos. Vos decidís."
    },
    {
      number: "3",
      title: "Empezá a generar ingresos",
      desc: "Tus vehículos comienzan a trabajar dentro de tu municipio. Ganás por cada viaje realizado."
    },
    {
      number: "4",
      title: "Ahorrá y crecé",
      desc: "Usá tus ganancias para mantener tus vehículos con descuentos, contratar seguros y hacer crecer tu flota."
    }
  ];

  const testimonios = [
    {
      nombre: "Juan Pérez",
      ciudad: "San Miguel",
      texto: "Con TAXIP, mis vehículos generan ingresos todo el día. Además, ahorro en mantenimiento con los descuentos en comercios adheridos. El dashboard me permite controlar todo desde mi celular."
    },
    {
      nombre: "María Gómez",
      ciudad: "Morón",
      texto: "El modelo por municipio me da tranquilidad. Sé que mis vehículos operan en mi zona sin competencia externa. Y poder pagar seguros y repuestos desde la cuenta TAXIP es un golazo."
    }
  ];

  const whatsappNumber = process.env.NEXT_PUBLIC_WHATSAPP_NUMBER || "5491123456789";
  const whatsappUrl = `https://wa.me/${whatsappNumber}?text=Hola%2C%20quiero%20ser%20propietario%20en%20TAXIP`;

  return (
    <div className="propietarios-page">
      {/* ============================================ */}
      {/* HERO */}
      {/* ============================================ */}
      <section className="propietarios-hero">
        <div className="container-custom">
          <div className="propietarios-hero-content">
            <h1 className="propietarios-hero-title">
              🚗 Sumá tus vehículos a <span className="highlight">TAXIP</span>
            </h1>
            <p className="propietarios-hero-desc">
              Generá ingresos adicionales con tu flota de vehículos y accedé a beneficios exclusivos
            </p>
            <div className="propietarios-hero-cta">
              <a href={whatsappUrl} target="_blank" rel="noopener noreferrer" className="btn-whatsapp-hero">
                📱 Quiero ser Propietario
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* BENEFICIOS */}
      {/* ============================================ */}
      <section className="section section-white">
        <div className="container-custom">
          <h2 className="section-title">Beneficios exclusivos</h2>
          <p className="section-subtitle">
            Todo lo que necesitas para hacer crecer tu negocio con TAXIP
          </p>

          <div className="beneficios-grid">
            {beneficios.map((beneficio) => (
              <div key={beneficio.title} className="beneficio-card">
                <div className="beneficio-icon">{beneficio.icon}</div>
                <h3 className="beneficio-title">{beneficio.title}</h3>
                <p className="beneficio-desc">{beneficio.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* MODELO DE OPERACIÓN POR MUNICIPIO */}
      {/* ============================================ */}
      <section className="section section-gray">
        <div className="container-custom">
          <h2 className="section-title">📍 Operá dentro de tu municipio</h2>
          <p className="section-subtitle">
            Cada municipio es una zona exclusiva. Conocé cómo funciona el modelo TAXIP
          </p>

          <div className="municipio-grid">
            <div className="municipio-card municipio-info">
              <div className="municipio-icon">🏙️</div>
              <h3>Tu municipio, tu zona</h3>
              <p>Cada municipio es un tenant independiente. Tus vehículos operan dentro de tu jurisdicción.</p>
            </div>

            <div className="municipio-card municipio-ok">
              <div className="municipio-icon">✅</div>
              <h3>Viajes dentro del municipio</h3>
              <p>Tus vehículos toman pedidos dentro de tu municipio. Mercado exclusivo para vos.</p>
            </div>

            <div className="municipio-card municipio-ok">
              <div className="municipio-icon">🚗</div>
              <h3>Viajes fuera del municipio</h3>
              <p>Podés transportar pasajeros a otros municipios, pero debés regresar vacío.</p>
            </div>

            <div className="municipio-card municipio-error">
              <div className="municipio-icon">❌</div>
              <h3>Sin pedidos fuera</h3>
              <p>No se pueden tomar pedidos fuera de tu jurisdicción. Respetamos las normativas municipales.</p>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* ECOSISTEMA DE BENEFICIOS */}
      {/* ============================================ */}
      <section className="section section-white">
        <div className="container-custom">
          <h2 className="section-title">💰 Un ecosistema que te cuida</h2>
          <p className="section-subtitle">
            Ganás, ahorrás y gastás con beneficios. Todo en un solo lugar
          </p>

          <div className="ecosistema-beneficios">
            <div className="ecosistema-flujo">
              <div className="flujo-paso ganar">
                <span className="flujo-icon">💰</span>
                <span className="flujo-label">Ganás dinero</span>
                <span className="flujo-arrow">↓</span>
              </div>
              <div className="flujo-paso cuenta">
                <span className="flujo-icon">💳</span>
                <span className="flujo-label">Dinero en cuenta</span>
                <span className="flujo-arrow">↓</span>
              </div>
              <div className="flujo-paso gastar">
                <span className="flujo-icon">🛒</span>
                <span className="flujo-label">Gastás con descuentos</span>
                <div className="flujo-opciones">
                  <span className="opcion">🛒 Comercios</span>
                  <span className="opcion">🔒 Seguros</span>
                  <span className="opcion">🛠️ Talleres</span>
                </div>
              </div>
            </div>
            <p className="ecosistema-desc">
              <strong>Ciclo virtuoso:</strong> Ganás por los viajes → Ahorrás en tus gastos → Invertís en tu flota
            </p>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* CÓMO FUNCIONA */}
      {/* ============================================ */}
      <section className="section section-gray">
        <div className="container-custom">
          <h2 className="section-title">¿Cómo funciona?</h2>
          <p className="section-subtitle">
            Empezá a generar ingresos en 4 pasos simples
          </p>

          <div className="pasos-grid">
            {pasos.map((paso) => (
              <div key={paso.number} className="paso-card">
                <div className="paso-number">{paso.number}</div>
                <h3 className="paso-title">{paso.title}</h3>
                <p className="paso-desc">{paso.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* ESTADÍSTICAS */}
      {/* ============================================ */}
      <section className="section section-yellow">
        <div className="container-custom">
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-number">+2.850</div>
              <div className="stat-label">Conductores activos</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">+50.000</div>
              <div className="stat-label">Viajes realizados</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">+1.200</div>
              <div className="stat-label">Vehículos en plataforma</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">+200</div>
              <div className="stat-label">Comercios adheridos</div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* TESTIMONIOS */}
      {/* ============================================ */}
      <section className="section section-white">
        <div className="container-custom">
          <h2 className="section-title">⭐ Lo que dicen los propietarios</h2>
          <p className="section-subtitle">
            Historias reales de propietarios que ya confían en TAXIP
          </p>

          <div className="testimonios-grid">
            {testimonios.map((testimonio, index) => (
              <div key={index} className="testimonio-card">
                <div className="testimonio-icon">"</div>
                <p className="testimonio-texto">{testimonio.texto}</p>
                <div className="testimonio-autor">
                  <strong>{testimonio.nombre}</strong>
                  <span>{testimonio.ciudad}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* SOPORTE 24/7 */}
      {/* ============================================ */}
      <section className="section section-gray">
        <div className="container-custom">
          <div className="soporte-content">
            <div className="soporte-icon">🛡️</div>
            <h2>Soporte 24/7 para vos y tus conductores</h2>
            <p>
              Asistencia disponible las 24 horas, los 7 días de la semana.
              <br />
              <span className="soporte-ia">🤖 Actual: Asistencia con IA vía WhatsApp</span>
              <span className="soporte-operadores">👤 Futuro: Operadores humanos especializados</span>
            </p>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* CTA FINAL */}
      {/* ============================================ */}
      <section className="section cta-final">
        <div className="container-custom">
          <div className="cta-content">
            <h2 className="cta-title">¿Listo para sumar tus vehículos a TAXIP?</h2>
            <p className="cta-desc">
              Contactanos y te ayudamos a dar el primer paso. Empezá a generar ingresos hoy mismo.
            </p>
            <div className="cta-buttons">
              <a href={whatsappUrl} target="_blank" rel="noopener noreferrer" className="btn-whatsapp-cta">
                📱 Contactar a Ventas
              </a>
              <Link href="/ecosistema" className="btn-secundario">
                Conocé más sobre el ecosistema
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}