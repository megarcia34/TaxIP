"use client";

import { AnimatedCounter } from "./AnimatedCounter";

const statsData = [
  { 
    value: 50000, 
    label: "Viajes realizados", 
    suffix: "+",
    decimals: 0,
    format: (v: number) => `${v.toLocaleString()}+`
  },
  { 
    value: 500, 
    label: "Conductores activos", 
    suffix: "+",
    decimals: 0,
    format: (v: number) => `${v.toLocaleString()}+`
  },
  { 
    value: 350, 
    label: "Vehículos disponibles",
    decimals: 0,
    format: (v: number) => `${v.toLocaleString()}`
  },
  { 
    value: 4.9, 
    label: "Calificación promedio",
    decimals: 1,
    format: (v: number) => `${v.toFixed(1)}★`
  },
];

export function Stats() {
  return (
    <section className="section section-white" style={{ paddingTop: "2rem", paddingBottom: "2rem" }}>
      <div className="container-custom">
        <div className="stats-grid">
          {statsData.map((stat) => (
            <AnimatedCounter
              key={stat.label}
              end={stat.value}
              label={stat.label}
              suffix={stat.suffix || ""}
              decimals={stat.decimals || 0}
              format={stat.format}
            />
          ))}
        </div>
      </div>
    </section>
  );
}