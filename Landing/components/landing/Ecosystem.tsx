"use client";
import { motion } from "framer-motion";
import Link from "next/link";
import { Building2, Car, Users, Store, MapPin } from "lucide-react";

const ecosystemItems = [
  {
    icon: Building2,
    title: "Empresa Operadora",
    desc: "Gestioná tu flota de vehículos y conductores",
    href: "/empresa-operadora",
    iconClass: "channel-icon-blue",
  },
  {
    icon: Car,
    title: "Propietarios",
    desc: "Administrá tus vehículos y generá ingresos",
    href: "/propietarios",
    iconClass: "channel-icon-purple",
  },
  {
    icon: Users,
    title: "Conductores",
    desc: "Unite a la plataforma y conseguí más viajes",
    href: "/conductores",
    iconClass: "channel-icon-green",
  },
  {
    icon: Store,
    title: "Empresas",
    desc: "Viajes corporativos con facturación consolidada",
    href: "/empresas",
    iconClass: "channel-icon-orange",
  },
  {
    icon: MapPin,
    title: "Comercios",
    desc: "Generá QR y ofrecé taxis a tus clientes",
    href: "/comercios",
    iconClass: "channel-icon-red",
  },
];

export function Ecosystem() {
  return (
    <section className="section section-white">
      <div className="container-custom">
        <h2 className="section-title">El ecosistema TAXIP</h2>
        <p className="section-subtitle">
          Una plataforma que conecta a todos los actores del servicio de taxis
        </p>
        
        <div className="ecosystem-grid">
          {ecosystemItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Link href={item.href}>
                  <div className="ecosystem-card">
                    <div className={`ecosystem-icon ${item.iconClass}`}>
                      <Icon className="h-6 w-6" />
                    </div>
                    <h3 className="ecosystem-title">{item.title}</h3>
                    <p className="ecosystem-desc">{item.desc}</p>
                    <span className="ecosystem-link">Conocer más →</span>
                  </div>
                </Link>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}