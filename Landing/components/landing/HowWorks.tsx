"use client";

import { motion } from "framer-motion";
import { MapPin, Users, Car, Star } from "lucide-react";
import { Container, Section } from "../layout";

const steps = [
  {
    icon: MapPin,
    title: "Solicitá tu taxi",
    description: "Ingresá tu origen y destino, y elegí el tipo de vehículo",
    step: "1",
  },
  {
    icon: Users,
    title: "Asignación automática",
    description: "El sistema asigna el chofer más cercano a tu ubicación",
    step: "2",
  },
  {
    icon: Car,
    title: "Viajá seguro",
    description: "Seguí tu viaje en tiempo real con GPS y tracking",
    step: "3",
  },
  {
    icon: Star,
    title: "Calificá tu experiencia",
    description: "Valorá a tu conductor y ayudanos a mejorar",
    step: "4",
  },
];

export function HowWorks() {
  return (
    <Section background="gray" padding="default">
      <Container>
        <div className="text-center max-w-3xl mx-auto mb-12">
          <h2 className="heading-md mb-4">¿Cómo funciona TAXIP?</h2>
          <p className="body-base text-secondary-light">
            En simples pasos, tenés tu taxi en la puerta
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.15 }}
                viewport={{ once: true }}
                className="text-center relative"
              >
                {/* Step number */}
                <div className="relative mb-6">
                  <div className="w-20 h-20 rounded-full bg-primary-100 mx-auto flex items-center justify-center relative">
                    <span className="text-3xl font-bold text-primary">{step.step}</span>
                  </div>
                  <div className="absolute inset-0 w-20 h-20 rounded-full bg-primary/20 mx-auto animate-pulse"></div>
                </div>

                <div className="w-14 h-14 rounded-full bg-primary-50 text-primary flex items-center justify-center mx-auto mb-4">
                  <Icon className="h-7 w-7" />
                </div>

                <h3 className="text-lg font-semibold mb-2">{step.title}</h3>
                <p className="text-sm text-secondary-light">{step.description}</p>

                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-16 left-[calc(50%+50px)] w-[calc(100%-100px)] h-0.5 bg-primary-200">
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 border-t-2 border-r-2 border-primary-300 rotate-45"></div>
                  </div>
                )}
              </motion.div>
            );
          })}
        </div>
      </Container>
    </Section>
  );
}