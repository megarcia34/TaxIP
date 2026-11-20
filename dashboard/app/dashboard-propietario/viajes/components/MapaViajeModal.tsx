"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { MapaRutaViaje } from "./MapaRutaViaje";

interface MapaViajeModalProps {
  viajeId: string | null;
  onClose: () => void;
}

export function MapaViajeModal({ viajeId, onClose }: MapaViajeModalProps) {
  // Log para ver si el modal se renderiza y con qué ID
  console.log('🟡 Renderizando MapaViajeModal. viajeId:', viajeId);

  if (!viajeId) return null;

  return (
    <Dialog open={!!viajeId} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-5xl h-[85vh] flex flex-col p-0 overflow-hidden">
        <DialogHeader className="p-4 border-b">
          <DialogTitle>Detalle del Viaje y Ruta</DialogTitle>
        </DialogHeader>
        
        <div className="flex-1 relative bg-muted">
          <MapaRutaViaje viajeId={viajeId} />
        </div>
      </DialogContent>
    </Dialog>
  );
}