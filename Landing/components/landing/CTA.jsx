"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Container, Section } from "../layout";
import { Button } from "../ui/Button";

export function CTA() {
  return (
    <Section background="primary" padding="default">
      <Container>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center max-w-3xl mx-auto"
        >
          <h2 className="heading-md text-secondary mb-4">
            ¿Listo para viajar con TAXIP?
          </h2>
          <p className="body-base text-secondary/70 max-w-lg mx-auto mb-8">
            Unite a miles de pasajeros que ya confían en nosotros para sus viajes.
          </p>
          <Link href="/pedir">
            <Button 
              size="lg" 
              variant="secondary" 
              className="text-base font-semibold px-10 group"
            >
              Pedí tu Taxi Ahora
              <ArrowRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </Button>
          </Link>
        </motion.div>
      </Container>
    </Section>
  );
}