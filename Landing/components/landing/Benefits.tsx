"use client";
import { motion } from "framer-motion";
import { Shield, CreditCard, Clock, Users, Star, Headphones } from "lucide-react";

const benefits = [
  { 
    icon: Shield, 
    title: "Viajes seguros", 
    desc: "Conductores verificados y seguimiento en tiempo real", 
    iconClass: "channel-icon-green" 
  },
  { 
    icon: CreditCard, 
    title: "Múltiples pagos", 
    desc: "Efectivo, tarjetas, QR, billeteras y cuenta corporativa", 
    iconClass: "channel-icon-blue" 
  },
  { 
    icon: Clock, 
    title: "Tarifas transparentes", 
    desc: "Conocé el precio estimado antes de viajar", 
    iconClass: "channel-icon-yellow" 
  },
  { 
    icon: Users, 
    title: "Cobertura amplia", 
    desc: "En toda la ciudad y sus alrededores", 
    iconClass: "channel-icon-purple" 
  },
  { 
    icon: Star, 
    title: "Calificación", 
    desc: "Conductores mejor calificados para tu viaje", 
    iconClass: "channel-icon-orange" 
  },
  { 
    icon: Headphones, 
    title: "Soporte 24/7", 
    desc: "Ayuda disponible en todo momento", 
    iconClass: "channel-icon-red" 
  },
];

export function Benefits() {
  return (
    <section className="section section-white">
      <div className="container-custom">
        <h2 className="section-title">¿Por qué elegir TAXIP?</h2>
        <p className="section-subtitle">
          Todo lo que necesitas para un viaje cómodo y seguro
        </p>
        
        <div className="benefits-grid">
          {benefits.map((benefit, index) => {
            const Icon = benefit.icon;
            return (
              <motion.div
                key={benefit.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <div className="benefit-card">
                  <div className="benefit-content">
                    <div className={`channel-icon ${benefit.iconClass}`}>
                      <Icon className="h-6 w-6" />
                    </div>
                    <div>
                      <h3 className="benefit-title">{benefit.title}</h3>
                      <p className="benefit-desc">{benefit.desc}</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}