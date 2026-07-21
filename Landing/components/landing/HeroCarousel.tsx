"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "../ui/Button";

const slides = [
  {
    id: 1,
    icon: "",
    title: "Pedí tu Taxi en Segundos",
    description: "Desde la app, web o llamando. Múltiples canales a tu disposición",
    cta: "Pedir Taxi Ahora",
    href: "/pedir",
    bgGradient: "linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%)",
  },
  {
    id: 2,
    icon: "💰",
    title: "Tarifas Transparentes",
    description: "Conocé el precio antes de viajar. Sin cargos ocultos",
    cta: "Ver Tarifas",
    href: "/#tarifas",
    bgGradient: "linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%)",
  },
  {
    id: 3,
    icon: "🕐",
    title: "Disponibles 24/7",
    description: "Siempre hay un TAXIP cerca tuyo. Cobertura en toda la provincia",
    cta: "Descargar App",
    href: "/descargar",
    bgGradient: "linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%)",
  },
];

export function HeroCarousel() {
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 5000);

    return () => clearInterval(timer);
  }, []);

  const goToSlide = (index: number) => {
    setCurrentSlide(index);
  };

  const currentSlideData = slides[currentSlide];

  return (
    <section className="hero-carousel" style={{ background: currentSlideData.bgGradient }}>
      <div className="carousel-content">
        <div className="carousel-icon">{currentSlideData.icon}</div>
        
        <h1 className="carousel-title">
          {currentSlideData.title}
        </h1>
        
        <p className="carousel-description">
          {currentSlideData.description}
        </p>
        
        <div className="carousel-buttons">
          <Link href={currentSlideData.href}>
            <Button size="lg" variant="primary">
              {currentSlideData.cta}
            </Button>
          </Link>
          
          <Link href="/ecosistema">
            <Button size="lg" variant="outline">
              Conocé el Ecosistema
            </Button>
          </Link>
        </div>

        <div className="carousel-features">
          <span className="carousel-feature">
            <span className="carousel-dot-green"></span>
            Conductores verificados
          </span>
          <span className="carousel-feature">
            <span className="carousel-dot-green"></span>
            24/7 disponible
          </span>
          <span className="carousel-feature">
            <span className="carousel-dot-green"></span>
            Múltiples pagos
          </span>
        </div>

        {/* Carousel Indicators */}
        <div className="carousel-indicators">
          {slides.map((_, index) => (
            <button
              key={index}
              onClick={() => goToSlide(index)}
              className={`carousel-indicator ${
                index === currentSlide ? "carousel-indicator-active" : ""
              }`}
              aria-label={`Slide ${index + 1}`}
            />
          ))}
        </div>
      </div>
    </section>
  );
}