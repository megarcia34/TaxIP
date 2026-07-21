import Link from "next/link";
import Image from "next/image";

export function Footer() {
  return (
    <footer className="footer">
      <div className="container-custom">
        <div className="footer-grid">
          {/* Brand */}
          <div className="footer-brand">
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Image
                src="/logos/logo-footer.png"
                alt="TAXIP"
                width={40}
                height={40}
                style={{ objectFit: "contain" }}
              />
              <span style={{ fontSize: "1.25rem", fontWeight: 700 }}>TAXIP</span>
            </div>
            <p>La nueva forma de pedir un taxi. Rápido, seguro y confiable.</p>
          </div>

          {/* Plataforma */}
          <div>
            <h4 className="footer-title">Plataforma</h4>
            <ul className="footer-links">
              <li><Link href="/#como-funciona">Cómo funciona</Link></li>
              <li><Link href="/#beneficios">Beneficios</Link></li>
              <li><Link href="/descargar">Descargar App</Link></li>
            </ul>
          </div>

          {/* Ecosistema */}
          <div>
            <h4 className="footer-title">Ecosistema</h4>
            <ul className="footer-links">
              <li><Link href="/empresa-operadora">Empresa Operadora</Link></li>
              <li><Link href="/propietarios">Propietarios</Link></li>
              <li><Link href="/conductores">Conductores</Link></li>
              <li><Link href="/empresas">Empresas</Link></li>
              <li><Link href="/comercios">Comercios</Link></li>
            </ul>
          </div>

          {/* Contacto */}
          <div>
            <h4 className="footer-title">Contacto</h4>
            <ul className="footer-contact">
              <li>San Miguel de Tucumán, Argentina</li>
              <li>+54 381 123-4567</li>
              <li>info@taxip.com.ar</li>
              <li>Disponible 24/7</li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="footer-bottom">
          <span>&copy; {new Date().getFullYear()} TAXIP. Todos los derechos reservados.</span>
          <div className="footer-bottom-links">
            <Link href="/terminos">Términos</Link>
            <Link href="/privacidad">Privacidad</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}