"use client";

import Link from "next/link";

export default function EcosistemaPage() {
  const servicios = [
    {
      id: "propietarios",
      icon: "🚗",
      title: "Propietarios",
      desc: "Sumá tus vehículos a la plataforma TAXIP y generá ingresos adicionales. Gestioná tu flota de manera eficiente y conectá con miles de pasajeros.",
      href: "/propietarios",
      cta: "Conocer más →"
    },
    {
      id: "comercios",
      icon: "🏪",
      title: "Comercios",
      desc: "Ofrecé a tus clientes la posibilidad de pedir un taxi desde tu local. Generá códigos QR personalizados y sumá valor a tu negocio.",
      href: "/comercios",
      cta: "Conocer más →"
    },
    {
      id: "empresas",
      icon: "🏢",
      title: "Empresas",
      desc: "Optimizá los traslados de tu equipo con viajes corporativos. Facturación consolidada, gestión de flota y seguimiento en tiempo real.",
      href: "/empresas",
      cta: "Conocer más →"
    }
  ];

  return (
    <div className="ecosistema-page">
      {/* HERO */}
      <section className="ecosistema-hero">
        <div className="container-custom">
          <div className="ecosistema-hero-content">
            <h1 className="ecosistema-hero-title">
              🚀 ¿Quieres ofrecer tus servicios con TAXIP?
            </h1>
            <p className="ecosistema-hero-desc">
              Conocé los beneficios de cada módulo y sumate a la plataforma de movilidad líder
            </p>
          </div>
        </div>
      </section>

      {/* GRID DE SERVICIOS */}
      <section className="section section-white">
        <div className="container-custom">
          <div className="servicios-grid">
            {servicios.map((servicio) => (
              <div key={servicio.id} className="servicio-card">
                <div className="servicio-icon">{servicio.icon}</div>
                <h3 className="servicio-title">{servicio.title}</h3>
                <p className="servicio-desc">{servicio.desc}</p>
                <Link href={servicio.href} className="servicio-link">
                  {servicio.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA FINAL */}
      <section className="section section-gray">
        <div className="container-custom">
          <div className="ecosistema-footer-cta">
            <h2>¿Listo para empezar?</h2>
            <p>
              Contactanos y te ayudamos a dar el primer paso en la plataforma TAXIP
            </p>
            <a
              href={`https://wa.me/${process.env.NEXT_PUBLIC_WHATSAPP_NUMBER || "5491123456789"}`}
              target="_blank"
              rel="noopener noreferrer"
              className="cta-whatsapp-btn"
            >
              📱 Contactar a Ventas
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}