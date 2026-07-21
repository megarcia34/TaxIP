"use client";

import { motion } from "framer-motion";
import { 
  Smartphone, 
  Globe, 
  QrCode, 
  Building2, 
  Store, 
  MapPin 
} from "lucide-react";

const channels = [
  {
    icon: Smartphone,
    title: "App móvil",
    description: "Pedí tu taxi desde nuestra aplicación",
    bg: "bg-blue-50",
    text: "text-blue-600",
  },
  {
    icon: Globe,
    title: "Página web",
    description: "Solicita tu viaje desde tu navegador",
    bg: "bg-purple-50",
    text: "text-purple-600",
  },
  {
    icon: QrCode,
    title: "Código QR",
    description: "Escanea y pedí tu taxi al instante",
    bg: "bg-green-50",
    text: "text-green-600",
  },
  {
    icon: Building2,
    title: "Empresas",
    description: "Tu empresa gestiona tus viajes",
    bg: "bg-orange-50",
    text: "text-orange-600",
  },
  {
    icon: Store,
    title: "Comercios",
    description: "Pedí tu taxi en comercios adheridos",
    bg: "bg-red-50",
    text: "text-red-600",
  },
  {
    icon: MapPin,
    title: "En la calle",
    description: "Tomalo en la calle como siempre",
    bg: "bg-yellow-50",
    text: "text-yellow-600",
  },
];

export function Channels() {
  return (
    <section className="py-16 md:py-20 bg-muted">
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <h2 className="text-2xl md:text-3xl lg:text-4xl font-semibold tracking-tight mb-4">
            ¿Cómo querés pedir tu taxi?
          </h2>
          <p className="text-secondary-light text-base leading-relaxed">
            Elegí la forma que más te convenga y viajá con TAXIP
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {channels.map((channel, index) => {
            const Icon = channel.icon;
            return (
              <motion.div
                key={channel.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="bg-white rounded-2xl border border-secondary/5 p-6 text-center hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-default shadow-soft"
              >
                <div className={`w-14 h-14 rounded-2xl ${channel.bg} flex items-center justify-center mx-auto mb-4`}>
                  <Icon className={`h-7 w-7 ${channel.text}`} />
                </div>
                <h3 className="text-lg font-semibold mb-2 text-secondary">{channel.title}</h3>
                <p className="text-sm text-secondary-light">{channel.description}</p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}