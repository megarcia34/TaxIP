"use client";

import { motion } from "framer-motion";
import { Apple, Smartphone, ArrowRight } from "lucide-react";
import { Container, Section } from "../layout";
import { Button } from "../ui/Button";

export function Download() {
  return (
    <Section background="gray" padding="default">
      <Container>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="flex flex-col md:flex-row items-center justify-between gap-8"
        >
          <div className="text-white">
            <h2 className="heading-md mb-4">Descargá la App de TAXIP</h2>
            <p className="body-base text-white/60 max-w-md">
              Rápida, simple y segura. Disponible para iOS y Android.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4">
            <a href="#" className="inline-flex items-center gap-3 px-6 py-3 bg-white/10 hover:bg-white/20 rounded-2xl transition-colors duration-300 border border-white/10">
              <Apple className="h-8 w-8 text-white" />
              <div>
                <div className="text-xs text-white/60">Descargar en</div>
                <div className="text-sm font-semibold text-white">App Store</div>
              </div>
            </a>
            <a href="#" className="inline-flex items-center gap-3 px-6 py-3 bg-white/10 hover:bg-white/20 rounded-2xl transition-colors duration-300 border border-white/10">
              <Smartphone className="h-8 w-8 text-white" />
              <div>
                <div className="text-xs text-white/60">Descargar en</div>
                <div className="text-sm font-semibold text-white">Google Play</div>
              </div>
            </a>
          </div>
        </motion.div>
      </Container>
    </Section>
  );
}