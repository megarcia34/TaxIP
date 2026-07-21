"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "../ui/Button";

export function Hero() {
  return (
    <section className="min-h-[calc(100vh-80px)] flex items-center justify-center bg-white">
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-16 md:py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex flex-col items-center text-center space-y-8 max-w-4xl mx-auto"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-50 rounded-full text-sm text-secondary">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            Disponible en toda la provincia
          </div>

          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight">
            La nueva forma de{" "}
            <span className="bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
              pedir un taxi
            </span>
          </h1>

          <p className="text-lg md:text-xl text-secondary-light max-w-2xl leading-relaxed">
            Rápido, seguro y confiable. Conectamos pasajeros con los mejores
            conductores en San Miguel de Tucumán y toda la provincia.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 pt-4">
            <Link href="/pedir">
              <Button size="lg" className="text-base font-semibold px-10">
                Pedí tu Taxi Ahora
              </Button>
            </Link>
            <Link href="/ecosistema">
              <Button variant="outline" size="lg" className="text-base font-semibold px-10">
                Conocé el Ecosistema
              </Button>
            </Link>
          </div>

          <div className="flex flex-wrap justify-center gap-8 pt-8 text-sm text-secondary-light">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-green-500"></span>
              Conductores verificados
            </div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-green-500"></span>
              24/7 disponible
            </div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-green-500"></span>
              Múltiples pagos
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}