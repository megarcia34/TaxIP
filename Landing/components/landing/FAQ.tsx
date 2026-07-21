"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { Container, Section } from "../layout";

const faqs = [
  {
    question: "¿Cómo solicito un taxi con TAXIP?",
    answer: "Podés solicitar un taxi desde nuestra app móvil, página web, escaneando un código QR en comercios adheridos, o llamando a nuestra central.",
  },
  {
    question: "¿Qué métodos de pago aceptan?",
    answer: "Aceptamos efectivo, tarjetas de crédito/débito, transferencias bancarias, QR, billeteras virtuales y cuenta corporativa.",
  },
  {
    question: "¿Los conductores están verificados?",
    answer: "Sí, todos nuestros conductores pasan por un riguroso proceso de verificación de antecedentes y documentación.",
  },
  {
    question: "¿Cómo sé cuánto va a costar mi viaje?",
    answer: "Te mostramos el precio estimado antes de confirmar el viaje, con total transparencia en el cálculo de tarifas.",
  },
  {
    question: "¿Qué pasa si olvido un objeto en el taxi?",
    answer: "Podés reportar objetos olvidados desde la app o contactando a nuestro centro de ayuda. Tenemos un sistema de gestión de objetos perdidos.",
  },
  {
    question: "¿Puedo programar un viaje con anticipación?",
    answer: "Sí, podés programar viajes con hasta 7 días de anticipación desde nuestra app o página web.",
  },
];

export function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggle = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <Section background="gray" padding="default">
      <Container>
        <div className="text-center max-w-3xl mx-auto mb-12">
          <h2 className="heading-md mb-4">Preguntas frecuentes</h2>
          <p className="body-base text-secondary-light">
            Todo lo que necesitas saber antes de viajar
          </p>
        </div>

        <div className="max-w-3xl mx-auto space-y-3">
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: index * 0.05 }}
              viewport={{ once: true }}
              className="bg-white rounded-2xl shadow-soft border border-secondary/5 overflow-hidden"
            >
              <button
                onClick={() => toggle(index)}
                className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-primary-50/50 transition-colors duration-200"
              >
                <span className="font-medium text-secondary">{faq.question}</span>
                <ChevronDown
                  className={cn(
                    "h-5 w-5 text-secondary-light transition-transform duration-300 flex-shrink-0 ml-4",
                    openIndex === index && "rotate-180"
                  )}
                />
              </button>
              <div
                className={cn(
                  "px-6 overflow-hidden transition-all duration-300",
                  openIndex === index ? "pb-4 max-h-48" : "max-h-0"
                )}
              >
                <p className="text-secondary-light text-sm">{faq.answer}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </Container>
    </Section>
  );
}