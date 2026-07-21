"use client";
import Link from "next/link";

const blogPosts = [
  {
    title: "5 consejos para viajar seguro en taxi",
    excerpt: "Descubre cómo garantizar tu seguridad y la de tu familia en cada viaje con TAXIP.",
    date: "14 Jul 2026",
    image: "https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?auto=format&fit=crop&q=80&w=400&h=250",
    slug: "consejos-viajar-seguro",
  },
  {
    title: "Cómo funciona el sistema de tarifas",
    excerpt: "Te explicamos paso a paso cómo calculamos tu viaje para que siempre tengas total transparencia.",
    date: "10 Jul 2026",
    image: "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&q=80&w=400&h=250",
    slug: "sistema-tarifas",
  },
  {
    title: "Nuevas zonas de cobertura en Tucumán",
    excerpt: "Ampliamos nuestro servicio a nuevos barrios para que siempre tengas un TAXIP cerca.",
    date: "05 Jul 2026",
    image: "https://images.unsplash.com/photo-1556122071-e404ea5dd779?auto=format&fit=crop&q=80&w=400&h=250",
    slug: "nuevas-zonas-cobertura",
  },
];

export function BlogPreview() {
  return (
    <section className="section section-white">
      <div className="container-custom">
        <h2 className="section-title">Últimas Novedades</h2>
        <p className="section-subtitle">
          Consejos, noticias y actualizaciones del ecosistema TAXIP
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "2rem" }}>
          {blogPosts.map((post) => (
            <article key={post.slug} style={{ backgroundColor: "#ffffff", borderRadius: "1rem", overflow: "hidden", border: "1px solid #F3F4F6", transition: "all 0.3s ease" }}>
              <div style={{ height: "200px", overflow: "hidden" }}>
                <img 
                  src={post.image} 
                  alt={post.title} 
                  style={{ width: "100%", height: "100%", objectFit: "cover" }} 
                />
              </div>
              <div style={{ padding: "1.5rem" }}>
                <p style={{ fontSize: "0.875rem", color: "#9CA3AF", marginBottom: "0.5rem" }}>{post.date}</p>
                <h3 style={{ fontSize: "1.125rem", fontWeight: 600, color: "#1a1a1a", marginBottom: "0.75rem", lineHeight: 1.4 }}>{post.title}</h3>
                <p style={{ fontSize: "0.875rem", color: "#6B7280", marginBottom: "1rem", lineHeight: 1.6 }}>{post.excerpt}</p>
                <Link href={`/blog/${post.slug}`} style={{ fontSize: "0.875rem", fontWeight: 600, color: "#F59E0B", textDecoration: "none" }}>
                  Leer más →
                </Link>
              </div>
            </article>
          ))}
        </div>

        <div style={{ textAlign: "center", marginTop: "3rem" }}>
          <Link href="/blog" style={{ fontSize: "1rem", fontWeight: 600, color: "#F59E0B", textDecoration: "none" }}>
            Ver todas las entradas →
          </Link>
        </div>
      </div>
    </section>
  );
}