"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Image from "next/image";

export function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const pathname = usePathname();
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Cerrar menú al cambiar de página
  useEffect(() => {
    setIsMobileMenuOpen(false);
    setIsDropdownOpen(false);
  }, [pathname]);

  // Cerrar dropdown al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const isActive = (path: string) => {
    return pathname === path || pathname?.startsWith(path + "/");
  };

  // Número de WhatsApp desde variables de entorno
  const whatsappNumber = process.env.NEXT_PUBLIC_WHATSAPP_NUMBER || "5491123456789";
  const whatsappUrl = `https://wa.me/${whatsappNumber}`;

  // Opciones del desplegable "Ingreso al Sistema"
  const loginOptions = [
  { label: "👤 Conductores", href: "http://localhost:3000/login?role=conductor" },
  { label: "🚗 Propietarios", href: "http://localhost:3000/login?role=propietario" },
  { label: "🏢 Empresas", href: "http://localhost:3000/login?role=empresa" },
  { label: "🏛️ Empleados", href: "http://localhost:3000/login?role=operador" },
]

  return (
    <header className={`navbar ${isScrolled ? "navbar-scrolled" : ""}`}>
      <div className="navbar-inner">
        {/* Logo */}
        <Link href="/" className="navbar-logo">
          <div className="navbar-logo-box">
            <Image
              src="/logos/logo-small.png"
              alt="TAXIP"
              width={32}
              height={32}
              priority
            />
          </div>
          <span className="navbar-logo-text">TAXIP</span>
        </Link>

        {/* Links Desktop */}
        <nav className="navbar-links">
          {/* Dropdown: Ingreso al Sistema */}
          <div className="navbar-dropdown" ref={dropdownRef}>
            <button
              className={`navbar-dropdown-btn ${isDropdownOpen ? "active" : ""}`}
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              aria-expanded={isDropdownOpen}
            >
              Ingreso al Sistema
              <svg
                className={`dropdown-arrow ${isDropdownOpen ? "open" : ""}`}
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M6 9l6 6 6-6" />
              </svg>
            </button>

            <div className={`navbar-dropdown-menu ${isDropdownOpen ? "open" : ""}`}>
              {loginOptions.map((option) => (
                <Link
                  key={option.label}
                  href={option.href}
                  className="navbar-dropdown-item"
                  onClick={() => setIsDropdownOpen(false)}
                >
                  {option.label}
                </Link>
              ))}
            </div>
          </div>

          <Link
            href="/descargar"
            className={isActive("/descargar") ? "active" : ""}
          >
            Descargas
          </Link>

          <a
            href={whatsappUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="navbar-whatsapp"
          >
            <span className="whatsapp-icon">📱</span>
            Contáctenos
          </a>
        </nav>

        {/* Mobile Menu Button */}
        <button
          className="navbar-mobile-btn"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-label="Toggle menu"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            {isMobileMenuOpen ? (
              <path d="M18 6L6 18M6 6l12 12" />
            ) : (
              <>
                <path d="M4 6h16" />
                <path d="M4 12h16" />
                <path d="M4 18h16" />
              </>
            )}
          </svg>
        </button>
      </div>

      {/* Mobile Menu */}
      <div className={`navbar-mobile-menu ${isMobileMenuOpen ? "open" : ""}`}>
        {/* Ingreso al Sistema - Mobile */}
        <div className="mobile-dropdown-section">
          <div className="mobile-dropdown-label">Ingreso al Sistema</div>
          {loginOptions.map((option) => (
            <Link
              key={option.label}
              href={option.href}
              className="mobile-dropdown-item"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              {option.label}
            </Link>
          ))}
        </div>

        <div className="divider" />

        <Link href="/descargar" onClick={() => setIsMobileMenuOpen(false)}>
          Descargas
        </Link>

        <a
          href={whatsappUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="mobile-whatsapp"
          onClick={() => setIsMobileMenuOpen(false)}
        >
          <span className="whatsapp-icon">📱</span>
          Contáctenos
        </a>
      </div>
    </header>
  );
}