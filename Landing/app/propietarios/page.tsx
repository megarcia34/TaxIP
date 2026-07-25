"use client";

import Link from "next/link";
import Image from "next/image";
import styles from "./page.module.css";

export default function PropietariosPage() {
  // ✅ URL del Dashboard desde variable de entorno
  const dashboardUrl = process.env.NEXT_PUBLIC_DASHBOARD_URL || "http://localhost:3000";

  const beneficiosExtras = [
    { icon: "🛒", title: "Descuentos en comercios adheridos" },
    { icon: "🔒", title: "Seguros preferenciales" },
    { icon: "💳", title: "Pagos con saldo en cuenta" },
    { icon: "📊", title: "Reportes automáticos" },
    { icon: "🛡️", title: "Soporte 24/7" },
  ];

  const pasos = [
    {
      number: "1",
      title: "Registrá tus vehículos",
      desc: "Completá el registro de tu flota en la plataforma TAXIP. Te guiamos paso a paso.",
      image: "/images/propietarios/paso-registro.jpg"
    },
    {
      number: "2",
      title: "Asigná conductores",
      desc: "Nosotros te ayudamos a encontrar conductores o podés asignar los tuyos. Vos decidís.",
      image: "/images/propietarios/paso-conductores.jpg"
    },
    {
      number: "3",
      title: "Empezá a generar ingresos",
      desc: "Tus vehículos comienzan a trabajar dentro de tu municipio. Ganás por cada viaje realizado.",
      image: "/images/propietarios/paso-ingresos.jpg"
    },
    {
      number: "4",
      title: "Ahorrá y crecé",
      desc: "Usá tus ganancias para mantener tus vehículos con descuentos, contratar seguros y hacer crecer tu flota.",
      image: "/images/propietarios/paso-ahorro.jpg"
    }
  ];

  const whatsappNumber = process.env.NEXT_PUBLIC_WHATSAPP_NUMBER || "5491123456789";
  const whatsappUrl = `https://wa.me/${whatsappNumber}?text=Hola%2C%20quiero%20ser%20propietario%20en%20TAXIP`;

  return (
    <div className={styles["propietarios-page"]}>
      {/* ============================================ */}
      {/* HERO CON SLIDER */}
      {/* ============================================ */}
      <section className={styles["propietarios-hero"]}>
        <div className={styles["hero-slider"]}>
          <div className={`${styles["hero-slide"]} ${styles["hero-slide-1"]}`}>
            <div className={styles["hero-overlay"]}></div>
            <div className="container-custom">
              <div className={styles["hero-content"]}>
                <h1 className={styles["hero-title"]}>
                  Hacé que tus <span className={styles["highlight"]}>taxis</span> trabajen para vos
                </h1>
                <p className={styles["hero-desc"]}>
                  Ingresos seguros mientras vos descansás. Sumá tus vehículos a la plataforma de movilidad líder.
                </p>
                <Link href={`${dashboardUrl}/registro/propietario`} className={styles["btn-whatsapp-hero"]}>
                  📱 Registrarme como Propietario
                </Link>
              </div>
            </div>
          </div>
          <div className={`${styles["hero-slide"]} ${styles["hero-slide-2"]}`}>
            <div className={styles["hero-overlay"]}></div>
            <div className="container-custom">
              <div className={styles["hero-content"]}>
                <h1 className={styles["hero-title"]}>
                  Vos ponés el <span className={styles["highlight"]}>vehículo</span>, nosotros los viajes
                </h1>
                <p className={styles["hero-desc"]}>
                  Gestionamos conductores, viajes y pagos. Vos solo disfrutás de tus ingresos.
                </p>
                <Link href={`${dashboardUrl}/registro/propietario`} className={styles["btn-whatsapp-hero"]}>
                  📱 Registrarme como Propietario
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* STATS */}
      {/* ============================================ */}
      <section className="section section-yellow" style={{ paddingTop: "2rem", paddingBottom: "2rem" }}>
        <div className="container-custom">
          <div className={styles["stats-grid"]}>
            <div className={styles["stat-item"]}>
              <div className={styles["stat-number"]}>+2.850</div>
              <div className={styles["stat-label"]}>Conductores activos</div>
            </div>
            <div className={styles["stat-item"]}>
              <div className={styles["stat-number"]}>+50.000</div>
              <div className={styles["stat-label"]}>Viajes realizados</div>
            </div>
            <div className={styles["stat-item"]}>
              <div className={styles["stat-number"]}>+1.200</div>
              <div className={styles["stat-label"]}>Vehículos en plataforma</div>
            </div>
            <div className={styles["stat-item"]}>
              <div className={styles["stat-number"]}>+200</div>
              <div className={styles["stat-label"]}>Comercios adheridos</div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* EMPEZÁ A GANAR MÁS CON TAXIP */}
      {/* ============================================ */}
      <section className="section section-white">
        <div className="container-custom">
          <h2 className="section-title">🚀 Empezá a ganar más con TAXIP</h2>
          <p className="section-subtitle">
            Todo lo que necesitás para hacer crecer tu negocio
          </p>

          {/* Tarjetas principales */}
          <div className={styles["beneficios-principales"]}>
            {/* Tarjeta 1 - Celular */}
            <div className={styles["beneficio-principal"]}>
              <div className={styles["beneficio-principal-imagen"]}>
                <Image
                  src="/images/propietarios/1784808968_celular.png"
                  alt="Gestioná tu flota desde tu celular"
                  width={400}
                  height={300}
                  className={styles["beneficio-principal-img"]}
                />
              </div>
              <div className={styles["beneficio-principal-contenido"]}>
                <h3 className={styles["beneficio-principal-titulo"]}>
                  📱 Gestioná tu flota desde tu celular
                </h3>
                <p className={styles["beneficio-principal-subtitulo"]}>
                  Todo el control de tu negocio en la palma de tu mano
                </p>
                <ul className={styles["beneficio-principal-lista"]}>
                  <li>✓ Controlá cada vehículo en tiempo real</li>
                  <li>✓ Seguí ingresos y gastos desde cualquier lugar</li>
                  <li>✓ Gestioná conductores, viajes y mantenimientos</li>
                  <li>✓ Dashboard intuitivo con reportes en vivo</li>
                </ul>
                <Link href={`${dashboardUrl}/registro/propietario`} className={styles["beneficio-principal-cta"]}>
                  Conocer más →
                </Link>
              </div>
            </div>

            {/* Tarjeta 2 - Conductores */}
            <div className={`${styles["beneficio-principal"]} ${styles["beneficio-principal-reverse"]}`}>
              <div className={styles["beneficio-principal-contenido"]}>
                <h3 className={styles["beneficio-principal-titulo"]}>
                  👩‍💼 Conectá con los mejores conductores
                </h3>
                <p className={styles["beneficio-principal-subtitulo"]}>
                  Elegí el modelo de negocio que más te convenga
                </p>
                <ul className={styles["beneficio-principal-lista"]}>
                  <li>✓ Encontrá conductores calificados para tu flota</li>
                  <li>✓ Tres modelos: porcentaje, canon fijo o auto-gestión</li>
                  <li>✓ Liquidaciones automáticas y control de pagos</li>
                  <li>✓ Perfiles verificados y con calificaciones</li>
                </ul>
                <Link href={`${dashboardUrl}/registro/propietario`} className={styles["beneficio-principal-cta"]}>
                  Administrá tu equipo →
                </Link>
              </div>
              <div className={styles["beneficio-principal-imagen"]}>
                <Image
                  src="/images/propietarios/1784807736_dueña.png"
                  alt="Conectá con los mejores conductores"
                  width={400}
                  height={300}
                  className={styles["beneficio-principal-img"]}
                />
              </div>
            </div>
          </div>

          {/* Beneficios adicionales - íconos pequeños */}
          <div className={styles["beneficios-extras"]}>
            {beneficiosExtras.map((item) => (
              <div key={item.icon} className={styles["beneficio-extra"]}>
                <span className={styles["beneficio-extra-icono"]}>{item.icon}</span>
                <span className={styles["beneficio-extra-texto"]}>{item.title}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============================================ */}
{/* JARALLAX - ¿POR QUÉ ELEGIR TAXIP? */}
{/* ============================================ */}
<section className={styles["section-jarallax"]}>
  <div className={styles["jarallax-overlay"]}></div>
  <div className="container-custom">
    <div className={styles["jarallax-content"]}>
      <div className={styles["jarallax-grid"]}>
        <div className={styles["jarallax-texto"]}>
          <h2>¿Por qué elegir TAXIP?</h2>
          <p>
            Somos la plataforma de movilidad que conecta a propietarios con conductores y pasajeros.
            <br />
            <span className={styles["jarallax-highlight"]}>Sumá tu vehículo y empezá a generar ingresos</span>
          </p>
        </div>
        <div className={styles["jarallax-imagen"]}>
          <Image
            src="/images/propietarios/1784937480_chofer_app.png"
            alt="Conductores TAXIP"
            width={500}
            height={400}
            className={styles["jarallax-img"]}
          />
        </div>
      </div>
    </div>
  </div>
</section>
      {/* ============================================ */}
      {/* CÓMO FUNCIONA */}
      {/* ============================================ */}
      <section className="section section-white">
        <div className="container-custom">
          <h2 className="section-title">¿Cómo funciona?</h2>
          <p className="section-subtitle">
            Empezá a generar ingresos en 4 pasos simples
          </p>

          <div className={styles["pasos-grid"]}>
            {pasos.map((paso) => (
              <div key={paso.number} className={styles["paso-card"]}>
                <div className={styles["paso-imagen"]}>
                  <img src={paso.image} alt={paso.title} className={styles["paso-image"]} />
                  <div className={styles["paso-number"]}>{paso.number}</div>
                </div>
                <h3 className={styles["paso-title"]}>{paso.title}</h3>
                <p className={styles["paso-desc"]}>{paso.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* CTA FINAL */}
      {/* ============================================ */}
      <section className={`section ${styles["cta-final"]}`}>
        <div className="container-custom">
          <div className="cta-content">
            <h2 className={styles["cta-title"]}>¿Listo para sumar tus vehículos a TAXIP?</h2>
            <p className={styles["cta-desc"]}>
              Contactanos y te ayudamos a dar el primer paso. Empezá a generar ingresos hoy mismo.
            </p>
            <div className={styles["cta-buttons"]}>
              <a href={whatsappUrl} target="_blank" rel="noopener noreferrer" className={styles["btn-whatsapp-cta"]}>
                📱 Contactar a Ventas
              </a>
              <Link href="/ecosistema" className={styles["btn-secundario"]}>
                ← Volver al ecosistema
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}