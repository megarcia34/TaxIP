import type { Metadata } from "next";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import "./styles/globals.css";

export const metadata: Metadata = {
  title: "TAXIP - La nueva forma de pedir un taxi",
  description: "Rápido, seguro y confiable. Conectamos pasajeros con los mejores conductores.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body>
        <Navbar />
        <main style={{ paddingTop: 0 }}>{children}</main>
        <Footer />
      </body>
    </html>
  );
}