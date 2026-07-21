"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/Button";

// ============================================
// DATOS
// ============================================

// Hero Carousel
const heroSlides = [
  {
    image: "/images/926x0_86795_20250623110130.jpg",
    title: "La nueva forma de pedir un taxi",
    description: "Rápido, seguro y confiable. Conectamos pasajeros con los mejores conductores.",
  },
  {
    image: "/images/images.jpg",
    title: "Viajá con TAXIP",
    description: "Conductores verificados y seguimiento en tiempo real.",
  },
];

// Channels
const channels = [
  { icon: "📱", title: "App móvil", desc: "Pedí tu taxi desde nuestra aplicación", iconClass: "channel-icon-blue" },
  { icon: "🌐", title: "Página web", desc: "Solicita tu viaje desde tu navegador", iconClass: "channel-icon-purple" },
  { icon: "📲", title: "Código QR", desc: "Escanea y pedí tu taxi al instante", iconClass: "channel-icon-green" },
  { icon: "🏢", title: "Empresas", desc: "Tu empresa gestiona tus viajes", iconClass: "channel-icon-orange" },
  { icon: "🏪", title: "Comercios", desc: "Pedí tu taxi en comercios adheridos", iconClass: "channel-icon-red" },
  { icon: "📍", title: "En la calle", desc: "Tomalo en la calle como siempre", iconClass: "channel-icon-yellow" },
];

// Benefits
const benefits = [
  { icon: "🛡️", title: "Viajes seguros", desc: "Conductores verificados y seguimiento en tiempo real" },
  { icon: "💳", title: "Múltiples pagos", desc: "Efectivo, tarjetas, QR, billeteras y cuenta corporativa" },
  { icon: "💰", title: "Tarifas transparentes", desc: "Conocé el precio estimado antes de viajar" },
  { icon: "📍", title: "Cobertura amplia", desc: "En toda la ciudad y sus alrededores" },
  { icon: "⭐", title: "Calificación", desc: "Conductores mejor calificados para tu viaje" },
  { icon: "📞", title: "Soporte 24/7", desc: "Ayuda disponible en todo momento" },
];

// Payment Methods
const paymentMethods = [
  { icon: "💳", title: "Tarjeta", desc: "Débito y crédito", image: "/images/tarjeta_pago.jpg" },
  { icon: "📱", title: "QR", desc: "Escaneá y pagá", image: "/images/qr_pago.jpg" },
  { icon: "🏦", title: "Transferencia", desc: "Bancaria o virtual", image: "/images/transferencia_pago.jpg" },
  { icon: "💵", title: "Efectivo", desc: "Pagá al finalizar", image: null },
];

// Vehicle Types
const vehicleTypes = [
  { icon: "🚗", title: "Standard", desc: "4 pasajeros", price: "Tarifa base" },
  { icon: "👑", title: "Premium", desc: "Mayor comodidad", price: "+30%" },
  { icon: "🌿", title: "Eco", desc: "Bajo consumo", price: "Tarifa base" },
  { icon: "🚐", title: "XXL", desc: "Hasta 8 pasajeros", price: "+50%" },
];

// Stats Data - NÚMEROS ENTEROS (sin decimales)
const statsData = [
  { 
    end: 50256, 
    label: "Viajes realizados", 
    suffix: "+",
  },
  { 
    end: 2850, 
    label: "Conductores activos", 
    suffix: "+",
  },
  { 
    end: 1200, 
    label: "Coches disponibles",
  },
  { 
    end: 45120, 
    label: "Calificaciones positivas",
    suffix: "+",
  },
];

// Ecosystem
const ecosystemItems = [
  { icon: "🏢", title: "Empresa Operadora", desc: "Gestioná tu flota de vehículos y conductores", href: "/empresa-operadora" },
  { icon: "🚗", title: "Propietarios", desc: "Administrá tus vehículos y generá ingresos", href: "/propietarios" },
  { icon: "👤", title: "Conductores", desc: "Unite a la plataforma y conseguí más viajes", href: "/conductores" },
  { icon: "🏛️", title: "Empresas", desc: "Viajes corporativos con facturación consolidada", href: "/empresas" },
  { icon: "🏪", title: "Comercios", desc: "Generá QR y ofrecé taxis a tus clientes", href: "/comercios" },
];

// How Works Carousel
const howWorksSlides = [
  { icon: "📱", title: "Pide tu taxi", desc: "Completá tu origen y destino, y elegí el tipo de vehículo" },
  { icon: "🚗", title: "Observa la llegada", desc: "Seguí tu taxi en tiempo real con GPS y tracking" },
  { icon: "💳", title: "Paga tu taxi", desc: "Elegí tu método de pago: efectivo, tarjeta, QR o transferencia" },
  { icon: "⭐", title: "Califica tu viaje", desc: "Valorá a tu conductor y ayudanos a mejorar" },
];

// FAQ
const faqs = [
  { q: "¿Cómo solicito un taxi con TAXIP?", a: "Podés solicitar un taxi desde nuestra app móvil, página web, escaneando un código QR en comercios adheridos, o llamando a nuestra central." },
  { q: "¿Qué métodos de pago aceptan?", a: "Aceptamos efectivo, tarjetas de crédito/débito, transferencias bancarias, QR, billeteras virtuales y cuenta corporativa." },
  { q: "¿Los conductores están verificados?", a: "Sí, todos nuestros conductores pasan por un riguroso proceso de verificación de antecedentes y documentación." },
  { q: "¿Cómo sé cuánto va a costar mi viaje?", a: "Te mostramos el precio estimado antes de confirmar el viaje, con total transparencia en el cálculo de tarifas." },
  { q: "¿Qué pasa si olvido un objeto en el taxi?", a: "Podés reportar objetos olvidados desde la app o contactando a nuestro centro de ayuda." },
  { q: "¿Puedo programar un viaje con anticipación?", a: "Sí, podés programar viajes con hasta 7 días de anticipación desde nuestra app o página web." },
];

// ============================================
// COMPONENTE: CONTADOR ANIMADO (SIN DECIMALES)
// ============================================
interface AnimatedCounterProps {
  end: number;
  label: string;
  duration?: number;
  suffix?: string;
}

function AnimatedCounter({ end, label, duration = 2500, suffix = "" }: AnimatedCounterProps) {
  const [count, setCount] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const [hasAnimated, setHasAnimated] = useState(false);
  const elementRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasAnimated) {
            setIsVisible(true);
          }
        });
      },
      { threshold: 0.3, rootMargin: "0px 0px -50px 0px" }
    );

    if (elementRef.current) {
      observer.observe(elementRef.current);
    }

    return () => {
      if (elementRef.current) {
        observer.unobserve(elementRef.current);
      }
    };
  }, [hasAnimated]);

  useEffect(() => {
    if (!isVisible || hasAnimated) return;

    let startTime: number;
    let animationId: number;

    const updateCounter = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      const currentValue = end * easeOutQuart;

      setCount(currentValue);

      if (progress < 1) {
        animationId = requestAnimationFrame(updateCounter);
      } else {
        setCount(end);
        setHasAnimated(true);
      }
    };

    animationId = requestAnimationFrame(updateCounter);

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, [isVisible, end, duration, hasAnimated]);

  const formattedCount = Math.round(count).toLocaleString();

  return (
    <div ref={elementRef} style={{ textAlign: "center" }}>
      <div className="stat-value">{formattedCount}{suffix}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

// ============================================
// COMPONENTE PRINCIPAL
// ============================================

export default function Home() {
  // Hero Carousel
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % heroSlides.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  // How Works Carousel
  const [howWorksIndex, setHowWorksIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setHowWorksIndex((prev) => (prev + 1) % howWorksSlides.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      {/* ============================================ */}
      {/* HERO CARRUSEL - PANTALLA COMPLETA */}
      {/* ============================================ */}
      <section 
        className="hero-carousel" 
        style={{ 
          minHeight: "100vh", 
          height: "100vh",
          padding: 0,
          margin: 0,
          position: "relative",
          overflow: "hidden"
        }}
      >
        {heroSlides.map((slide, index) => (
          <div
            key={index}
            style={{
              display: currentSlide === index ? "block" : "none",
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              width: "100%",
              height: "100%",
              backgroundImage: `url(${slide.image})`,
              backgroundSize: "cover",
              backgroundPosition: "center",
              backgroundRepeat: "no-repeat",
            }}
          >
            {/* Overlay oscuro */}
            <div
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: "rgba(0,0,0,0.5)",
                zIndex: 1,
              }}
            ></div>

            {/* Contenido centrado */}
            <div
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                zIndex: 2,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                padding: "2rem",
                textAlign: "center",
              }}
            >
              <div style={{ maxWidth: "56rem", margin: "0 auto" }}>
                {/* Badge */}
                <div
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "0.5rem",
                    padding: "0.5rem 1rem",
                    backgroundColor: "rgba(255, 255, 255, 0.15)",
                    backdropFilter: "blur(8px)",
                    borderRadius: "9999px",
                    fontSize: "0.875rem",
                    color: "#ffffff",
                    marginBottom: "1.5rem",
                  }}
                >
                  <span className="hero-badge-dot">
                    <span className="ping"></span>
                    <span className="dot"></span>
                  </span>
                  Disponible en toda la provincia
                </div>

                {/* Logo */}
                <div style={{ marginBottom: "1.5rem" }}>
                  <Image
                    src="/logos/logo-principal.png"
                    alt="TAXIP"
                    width={280}
                    height={100}
                    priority
                    style={{ objectFit: "contain", margin: "0 auto" }}
                  />
                </div>

                {/* Título */}
                <h1
                  style={{
                    fontSize: "2.25rem",
                    fontWeight: 700,
                    letterSpacing: "-0.025em",
                    color: "#ffffff",
                    marginBottom: "1rem",
                    lineHeight: "1.2",
                  }}
                  className="md:text-5xl lg:text-6xl"
                >
                  {slide.title}
                </h1>

                {/* Descripción */}
                <p
                  style={{
                    fontSize: "1.125rem",
                    lineHeight: "1.75",
                    color: "rgba(255,255,255,0.85)",
                    maxWidth: "42rem",
                    margin: "0 auto 2rem",
                  }}
                >
                  {slide.description}
                </p>

                {/* Botones */}
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "1rem",
                    justifyContent: "center",
                    marginBottom: "3rem",
                  }}
                >
                  <Link href="/pedir">
                    <Button size="lg" style={{ fontSize: "1.125rem", padding: "1rem 2rem" }}>
                      Pedí tu Taxi Ahora
                    </Button>
                  </Link>
                  <Link href="/ecosistema">
                    <Button
                      variant="outline"
                      size="lg"
                      style={{
                        fontSize: "1.125rem",
                        padding: "1rem 2rem",
                        borderColor: "rgba(255,255,255,0.3)",
                        color: "#ffffff",
                      }}
                    >
                      Trabaja con Nosotros
                    </Button>
                  </Link>
                </div>

                {/* Features */}
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    justifyContent: "center",
                    gap: "2rem",
                    fontSize: "0.875rem",
                    color: "rgba(255,255,255,0.8)",
                  }}
                >
                  <span className="feature">
                    <span className="dot-green"></span>
                    Conductores verificados
                  </span>
                  <span className="feature">
                    <span className="dot-green"></span>
                    24/7 disponible
                  </span>
                  <span className="feature">
                    <span className="dot-green"></span>
                    Múltiples pagos
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Indicadores */}
        <div
          style={{
            position: "absolute",
            bottom: "2rem",
            left: "50%",
            transform: "translateX(-50%)",
            display: "flex",
            gap: "0.75rem",
            zIndex: 10,
          }}
        >
          {heroSlides.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentSlide(index)}
              style={{
                width: "0.75rem",
                height: "0.75rem",
                borderRadius: "9999px",
                border: "2px solid #FBBF24",
                backgroundColor: currentSlide === index ? "#FBBF24" : "transparent",
                cursor: "pointer",
                transition: "all 0.3s ease",
              }}
              aria-label={`Slide ${index + 1}`}
            />
          ))}
        </div>
      </section>

      {/* ============================================ */}
      {/* STATS - CONTADORES ANIMADOS */}
      {/* ============================================ */}
      <section className="section section-yellow" style={{ paddingTop: "2rem", paddingBottom: "2rem" }}>
        <div className="container-custom">
          <div className="stats-grid">
            {statsData.map((stat) => (
              <AnimatedCounter
                key={stat.label}
                end={stat.end}
                label={stat.label}
                suffix={stat.suffix || ""}
              />
            ))}
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* MÉTODOS DE PAGO                              */}
      {/* ============================================ */}
      <section className="section section-gray">
        <div className="container-custom">
          <h2 className="section-title">Pagá como quieras</h2>
          <p className="section-subtitle">
            Elegí el método de pago que más te convenga
          </p>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "1.5rem",
              maxWidth: "64rem",
              margin: "0 auto",
            }}
          >
            {paymentMethods.map((method) => (
              <div
                key={method.title}
                style={{
                  backgroundColor: "#ffffff",
                  border: "1px solid #F3F4F6",
                  borderRadius: "1rem",
                  padding: "1.5rem",
                  textAlign: "center",
                  transition: "all 0.3s ease",
                  cursor: "default",
                }}
                className="hover:shadow-xl hover:-translate-y-1"
              >
                {method.image ? (
                  <div
                    style={{
                      width: "100%",
                      height: "120px",
                      borderRadius: "0.75rem",
                      overflow: "hidden",
                      marginBottom: "1rem",
                    }}
                  >
                    <Image
                      src={method.image}
                      alt={method.title}
                      width={200}
                      height={120}
                      style={{ objectFit: "cover", width: "100%", height: "100%" }}
                    />
                  </div>
                ) : (
                  <div
                    style={{
                      fontSize: "3rem",
                      marginBottom: "0.5rem",
                    }}
                  >
                    {method.icon}
                  </div>
                )}
                <h3 style={{ fontSize: "1.125rem", fontWeight: 600, color: "#1a1a1a", marginBottom: "0.25rem" }}>
                  {method.title}
                </h3>
                <p style={{ fontSize: "0.875rem", color: "#6B7280" }}>{method.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* CHANNELS - "¿Cómo querés pedir tu taxi?" */}
      {/* ============================================ */}
      <section className="section section-gray" style={{ paddingTop: "0" }}>
        <div className="container-custom">
          <h2 className="section-title">¿Cómo querés pedir tu taxi?</h2>
          <p className="section-subtitle">
            Elegí la forma que más te convenga y viajá con TAXIP
          </p>

          <div className="channels-grid">
            {channels.map((channel) => (
              <div key={channel.title} className="channel-card">
                <div className={`channel-icon ${channel.iconClass}`}>
                  {channel.icon}
                </div>
                <h3 className="channel-title">{channel.title}</h3>
                <p className="channel-desc">{channel.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* BENEFITS */}
      {/* ============================================ */}
      <section className="section section-white">
        <div className="container-custom">
          <h2 className="section-title">¿Por qué elegir TAXIP?</h2>
          <p className="section-subtitle">
            Todo lo que necesitas para un viaje cómodo y seguro
          </p>

          <div className="benefits-grid">
            {benefits.map((benefit) => (
              <div key={benefit.title} className="benefit-card">
                <div className="benefit-content">
                  <span className="benefit-icon">{benefit.icon}</span>
                  <div>
                    <h3 className="benefit-title">{benefit.title}</h3>
                    <p className="benefit-desc">{benefit.desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* TIPOS DE VEHÍCULO */}
      {/* ============================================ */}
      <section className="section section-white" style={{ paddingTop: "0" }}>
        <div className="container-custom">
          <h2 className="section-title">Elegí tu vehículo</h2>
          <p className="section-subtitle">
            Diferentes opciones para diferentes necesidades
          </p>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "1.5rem",
              maxWidth: "64rem",
              margin: "0 auto",
            }}
          >
            {vehicleTypes.map((vehicle) => (
              <div
                key={vehicle.title}
                style={{
                  backgroundColor: "#ffffff",
                  border: "2px solid #F3F4F6",
                  borderRadius: "1rem",
                  padding: "1.5rem",
                  textAlign: "center",
                  transition: "all 0.3s ease",
                  cursor: "default",
                }}
                className="hover:border-yellow-400 hover:shadow-xl hover:-translate-y-1"
              >
                <div style={{ fontSize: "3rem", marginBottom: "0.5rem" }}>{vehicle.icon}</div>
                <h3 style={{ fontSize: "1.125rem", fontWeight: 600, color: "#1a1a1a", marginBottom: "0.25rem" }}>
                  {vehicle.title}
                </h3>
                <p style={{ fontSize: "0.875rem", color: "#6B7280", marginBottom: "0.25rem" }}>{vehicle.desc}</p>
                <p style={{ fontSize: "0.75rem", color: "#F59E0B", fontWeight: 600 }}>{vehicle.price}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* ECOSYSTEM */}
      {/* ============================================ */}
      <section className="section section-white">
        <div className="container-custom">
          <h2 className="section-title">El ecosistema TAXIP</h2>
          <p className="section-subtitle">
            Una plataforma que conecta a todos los actores del servicio de taxis
          </p>

          <div className="ecosystem-grid">
            {ecosystemItems.map((item) => (
              <Link key={item.title} href={item.href}>
                <div className="ecosystem-card">
                  <div className="ecosystem-icon">{item.icon}</div>
                  <h3 className="ecosystem-title">{item.title}</h3>
                  <p className="ecosystem-desc">{item.desc}</p>
                  <span className="ecosystem-link">Conocer más →</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* HOW WORKS (CARRUSEL) */}
      {/* ============================================ */}
      <section className="section section-gray" style={{ position: "relative", overflow: "hidden" }}>
        <div className="container-custom">
          <h2 className="section-title">¿Cómo funciona TAXIP?</h2>
          <p className="section-subtitle">
            En simples pasos, tenés tu taxi en la puerta
          </p>

          <div style={{ maxWidth: "48rem", margin: "0 auto", position: "relative" }}>
            {howWorksSlides.map((slide, index) => (
              <div
                key={index}
                style={{
                  display: howWorksIndex === index ? "block" : "none",
                  animation: "fadeIn 0.5s ease-in",
                  textAlign: "center",
                  padding: "2rem",
                  backgroundColor: "#ffffff",
                  borderRadius: "1rem",
                  border: "1px solid #F3F4F6",
                }}
              >
                <div style={{ fontSize: "4rem", marginBottom: "1rem" }}>{slide.icon}</div>
                <h3 style={{ fontSize: "1.5rem", fontWeight: 600, color: "#1a1a1a", marginBottom: "0.5rem" }}>
                  {slide.title}
                </h3>
                <p style={{ fontSize: "1rem", color: "#6B7280", maxWidth: "32rem", margin: "0 auto" }}>
                  {slide.desc}
                </p>
              </div>
            ))}

            {/* Indicadores */}
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                gap: "0.75rem",
                marginTop: "2rem",
              }}
            >
              {howWorksSlides.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setHowWorksIndex(index)}
                  style={{
                    width: "0.75rem",
                    height: "0.75rem",
                    borderRadius: "9999px",
                    border: "2px solid #FBBF24",
                    backgroundColor: howWorksIndex === index ? "#FBBF24" : "transparent",
                    cursor: "pointer",
                    transition: "all 0.3s ease",
                  }}
                  aria-label={`Slide ${index + 1}`}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* DOWNLOAD */}
      {/* ============================================ */}
      <section className="section section-dark">
        <div className="container-custom">
          <div className="download-content">
            <div className="download-text">
              <h2 className="download-title">Descargá la App de TAXIP</h2>
              <p className="download-desc">
                Rápida, simple y segura. Disponible para iOS y Android.
              </p>
            </div>
            <div className="download-buttons">
              <a href="#" className="download-btn">
                <span className="download-btn-icon">🍎</span>
                <div>
                  <div className="download-btn-label">Descargar en</div>
                  <div className="download-btn-text">App Store</div>
                </div>
              </a>
              <a href="#" className="download-btn">
                <span className="download-btn-icon">📱</span>
                <div>
                  <div className="download-btn-label">Descargar en</div>
                  <div className="download-btn-text">Google Play</div>
                </div>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* FAQ */}
      {/* ============================================ */}
      <section className="section section-gray">
        <div className="container-custom">
          <h2 className="section-title">Preguntas frecuentes</h2>
          <p className="section-subtitle">
            Todo lo que necesitas saber antes de viajar
          </p>

          <div className="faq-list">
            {faqs.map((faq, index) => (
              <div key={index} className="faq-item">
                <h3 className="faq-question">{faq.q}</h3>
                <p className="faq-answer">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* CTA FINAL */}
      {/* ============================================ */}
      <section className="section" style={{ backgroundColor: "#FBBF24" }}>
        <div className="container-custom">
          <div className="cta-content">
            <h2 className="cta-title">¿Listo para viajar con TAXIP?</h2>
            <p className="cta-desc">
              Unite a miles de pasajeros que ya confían en nosotros para sus viajes.
            </p>
            <Link href="/pedir">
              <Button variant="secondary" size="lg">
                Pedí tu Taxi Ahora →
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}