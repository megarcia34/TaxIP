"use client";

import { useState } from "react";
import { ViajesTable } from "./components/ViajesTable";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function ViajesPage() {
  const hoyStr = new Date().toISOString().split("T")[0];
  const [desde, setDesde] = useState(hoyStr);
  const [hasta, setHasta] = useState(hoyStr);

  return (
    <div className="space-y-4 mt-2">
      {/* FILTROS DE FECHA (Sin título, porque el layout ya lo tiene) */}
      <div className="flex flex-wrap items-end gap-4 p-4 bg-card border rounded-lg shadow-sm">
        <div className="space-y-1">
          <Label htmlFor="desde">Desde</Label>
          <Input
            id="desde"
            type="date"
            value={desde}
            onChange={(e) => setDesde(e.target.value)}
            className="w-[160px]"
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="hasta">Hasta</Label>
          <Input
            id="hasta"
            type="date"
            value={hasta}
            onChange={(e) => setHasta(e.target.value)}
            className="w-[160px]"
          />
        </div>
        {(desde !== hoyStr || hasta !== hoyStr) && (
          <button 
            onClick={() => { setDesde(hoyStr); setHasta(hoyStr); }}
            className="text-sm text-blue-500 hover:underline mb-2"
          >
            Volver a Hoy
          </button>
        )}
      </div>

      {/* TABLA (Sin pestañas, porque el layout ya las tiene) */}
      <ViajesTable 
        estadoFiltro={null} 
        desdeFiltro={desde}
        hastaFiltro={hasta}
      />
    </div>
  );
}