"use client";

import { useState } from "react";

const rateTypes = [
  { name: "Micro", base: 2, perKm: 1, perMin: 0.5 },
  { name: "Mini", base: 3, perKm: 1.5, perMin: 0.7 },
  { name: "Prime", base: 4, perKm: 2, perMin: 1 },
  { name: "Sedan", base: 5, perKm: 2.5, perMin: 1.2 },
];

const extras = [
  { name: "Silla de bebé", price: "+$1" },
  { name: "Mascota (1 animal)", price: "+$4" },
  { name: "Tiempo de espera (>10 min)", price: "+$2/min" },
  { name: "Fuera de la ciudad", price: "+$4/km" },
];

export function RatesSection() {
  const [selectedType, setSelectedType] = useState(rateTypes[0]);

  return (
    <section className="section section-gray" id="tarifas">
      <div className="container-custom">
        <h2 className="section-title">Tarifas Transparentes</h2>
        <p className="section-subtitle">
          Conocé el precio antes de viajar. Sin cargos ocultos.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1.5rem", marginBottom: "3rem" }}>
          {rateTypes.map((type) => (
            <div
              key={type.name}
              onClick={() => setSelectedType(type)}
              style={{
                backgroundColor: "#ffffff",
                border: `2px solid ${selectedType.name === type.name ? "#FBBF24" : "#F3F4F6"}`,
                borderRadius: "1rem",
                padding: "1.5rem",
                textAlign: "center",
                cursor: "pointer",
                transition: "all 0.2s ease",
                transform: selectedType.name === type.name ? "translateY(-4px)" : "none",
                boxShadow: selectedType.name === type.name ? "0 10px 15px -3px rgba(0,0,0,0.1)" : "none",
              }}
            >
              <h3 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: "0.5rem" }}>{type.name}</h3>
              <p style={{ fontSize: "2rem", fontWeight: 700, color: "#FBBF24", marginBottom: "0.5rem" }}>${type.base}</p>
              <p style={{ fontSize: "0.875rem", color: "#6B7280" }}>
                +${type.perKm}/km <br /> +${type.perMin}/min
              </p>
            </div>
          ))}
        </div>

        <div style={{ backgroundColor: "#ffffff", borderRadius: "1rem", padding: "2rem", border: "1px solid #F3F4F6", maxWidth: "48rem", margin: "0 auto" }}>
          <h3 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "1.5rem", textAlign: "center" }}>Complementos y Extras</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem" }}>
            {extras.map((extra) => (
              <div key={extra.name} style={{ display: "flex", justifyContent: "space-between", padding: "0.75rem", borderBottom: "1px solid #F3F4F6" }}>
                <span style={{ color: "#4B5563" }}>{extra.name}</span>
                <span style={{ fontWeight: 600, color: "#1a1a1a" }}>{extra.price}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}