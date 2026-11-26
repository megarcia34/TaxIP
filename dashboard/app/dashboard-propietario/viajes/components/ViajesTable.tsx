"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import { 
  MapPin, Car, Globe, Smartphone, Building2, Monitor, 
  Download, Share2, FileText 
} from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import api from "@/lib/api/client";
import { MapaViajeModal } from "./MapaViajeModal";

// ============================================
// TIPOS
// ============================================
interface Viaje {
  id: string;
  codigo_correlativo: string;
  estado: string;
  estado_label: string;
  origen_tipo: string;
  fuente_label: string;
  direccion_origen: string;
  direccion_destino: string;
  fecha: string | null;
  iniciado_en: string | null;
  finalizado_en: string | null;
  duracion_minutos: number | null;
  distancia_metros: number | null;
  metodo_pago_label: string | null;
  precio_mostrado: number | null;
  chofer_nombre: string;
  pasajero_nombre: string;
  patente: string;
  motivo_cancelacion: string | null;
}

// ============================================
// HELPER PARA ICONOS DE FUENTE
// ============================================
const getFuenteIcon = (tipo: string) => {
  switch (tipo) {
    case "via_publica": return <span title="Calle"><Car className="h-4 w-4 text-muted-foreground" /></span>;
    case "plataforma": return <span title="App/Landing"><Globe className="h-4 w-4 text-blue-500" /></span>;
    case "qr_comercio": return <span title="Código QR"><Smartphone className="h-4 w-4 text-purple-500" /></span>;
    case "corporativo": return <span title="Corporativo"><Building2 className="h-4 w-4 text-orange-500" /></span>;
    case "despacho_manual": return <span title="Operativo"><Monitor className="h-4 w-4 text-green-500" /></span>;
    default: return <span title="Desconocido"><Globe className="h-4 w-4 text-muted-foreground" /></span>;
  }
};

// ============================================
// COMPONENTE PRINCIPAL
// ============================================
export function ViajesTable({ 
  estadoFiltro,
  desdeFiltro,
  hastaFiltro,
  onVerRuta 
}: { 
  estadoFiltro?: string | null;
  desdeFiltro?: string | null;
  hastaFiltro?: string | null;
  onVerRuta?: (id: string) => void; 
}) {
  const [viajeSeleccionado, setViajeSeleccionado] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["viajes", "historial", estadoFiltro, desdeFiltro, hastaFiltro],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (estadoFiltro) params.append("estado", estadoFiltro);
      if (desdeFiltro) params.append("desde", desdeFiltro);
      if (hastaFiltro) params.append("hasta", hastaFiltro);
      
      const { data } = await api.get(`/viajes/historial?${params.toString()}`);
      return data.viajes as Viaje[];
    },
    refetchInterval: 30000,
  });

  // ============================================
  // FUNCIONES DE EXPORTACIÓN
  // ============================================
  const exportarExcel = () => {
    if (!data || data.length === 0) return;
    const headers = ['ID Viaje', 'Fecha', 'Estado', 'Chofer', 'Patente', 'Pasajero', 'Origen', 'Destino', 'Inicio', 'Fin', 'Duración', 'Distancia', 'Monto', 'Metodo Pago'];
    const rows = data.map(v => [
      v.codigo_correlativo, v.fecha || '', v.estado_label, v.chofer_nombre, v.patente, v.pasajero_nombre,
      `"${v.direccion_origen || ''}"`, `"${v.direccion_destino || ''}"`,
      v.iniciado_en ? format(new Date(v.iniciado_en), "HH:mm") : '',
      v.finalizado_en ? format(new Date(v.finalizado_en), "HH:mm") : '',
      v.duracion_minutos ? `${v.duracion_minutos} min` : '',
      v.distancia_metros ? `${(v.distancia_metros / 1000).toFixed(1)} km` : '',
      v.precio_mostrado ? `$${v.precio_mostrado}` : '', v.metodo_pago_label || ''
    ]);
    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'application/vnd.ms-excel;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `viajes_${new Date().toISOString().split('T')[0]}.xls`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exportarPDF = () => { window.print(); };

  const compartirWhatsApp = () => {
    if (!data || data.length === 0) return;
    let texto = `*Resumen de Viajes - ${new Date().toLocaleDateString()}*\n\n`;
    data.slice(0, 10).forEach(v => {
      texto += `🚖 *${v.codigo_correlativo}* (${v.estado_label})\n`;
      texto += `👤 ${v.chofer_nombre} - ${v.patente}\n`;
      texto += `📍 ${v.direccion_origen?.split(',')[0] || '—'} -> ${v.direccion_destino?.split(',')[0] || '—'}\n`;
      texto += `💰 $${v.precio_mostrado || 0} (${v.metodo_pago_label || 'Efectivo'})\n\n`;
    });
    if (data.length > 10) texto += `_...y ${data.length - 10} viajes más._`;
    window.open(`https://wa.me/?text=${encodeURIComponent(texto)}`, '_blank');
  };

  // ============================================
  // RENDER
  // ============================================
  if (isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-16 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* BARRA DE ACCIONES */}
      <div className="flex flex-wrap justify-end gap-2 px-1 print:hidden">
        <Button variant="outline" size="sm" onClick={exportarExcel} disabled={!data?.length}>
          <Download className="h-4 w-4 mr-2" /> Excel
        </Button>
        <Button variant="outline" size="sm" onClick={exportarPDF} disabled={!data?.length}>
          <FileText className="h-4 w-4 mr-2" /> PDF
        </Button>
        <Button variant="outline" size="sm" onClick={compartirWhatsApp} disabled={!data?.length} className="text-green-600 hover:text-green-700 hover:bg-green-50">
          <Share2 className="h-4 w-4 mr-2" /> Compartir
        </Button>
      </div>

      <div className="rounded-md border bg-card overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[50px]">#</TableHead>
              <TableHead className="w-[120px]">ID Viaje</TableHead>
              <TableHead className="w-[60px]">Fuente</TableHead>
              <TableHead>Chofer / Patente</TableHead>
              <TableHead>Pasajero</TableHead>
              <TableHead>Origen</TableHead>
              <TableHead>Destino</TableHead>
              <TableHead>Fecha / Inicio</TableHead>
              <TableHead>Fin</TableHead>
              <TableHead>Duración</TableHead>
              <TableHead>Distancia</TableHead>
              <TableHead>Pago / Monto</TableHead>
              <TableHead className="text-right print:hidden">Ruta</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.length === 0 && (
              <TableRow>
                <TableCell colSpan={13} className="h-24 text-center text-muted-foreground">
                  No hay viajes para mostrar en este rango de fechas.
                </TableCell>
              </TableRow>
            )}

            {data?.map((viaje, index) => (
              <TableRow key={viaje.id} className="hover:bg-muted/50 transition-colors">
                <TableCell className="text-muted-foreground text-xs">{index + 1}</TableCell>
                <TableCell className="font-medium text-xs">{viaje.codigo_correlativo}</TableCell>
                <TableCell><div className="flex justify-center">{getFuenteIcon(viaje.origen_tipo)}</div></TableCell>
                <TableCell>
                  <div className="flex flex-col">
                    <span className="font-medium text-sm">{viaje.chofer_nombre}</span>
                    <span className="text-xs text-muted-foreground">{viaje.patente}</span>
                  </div>
                </TableCell>
                <TableCell className="text-sm">{viaje.pasajero_nombre}</TableCell>
                <TableCell className="max-w-[200px]">
                  <div className="flex flex-col">
                    <span className="text-sm truncate" title={viaje.direccion_origen}>{viaje.direccion_origen?.split(',')[0] || "—"}</span>
                    <span className="text-xs text-muted-foreground truncate" title={viaje.direccion_origen}>{viaje.direccion_origen?.split(',')[1] || "—"}</span>
                  </div>
                </TableCell>
                <TableCell className="max-w-[200px]">
                  <div className="flex flex-col">
                    <span className="text-sm truncate" title={viaje.direccion_destino}>{viaje.direccion_destino?.split(',')[0] || "—"}</span>
                    <span className="text-xs text-muted-foreground truncate" title={viaje.direccion_destino}>{viaje.direccion_destino?.split(',')[1] || "—"}</span>
                  </div>
                </TableCell>
                {/* FECHA Y HORA JUNTAS */}
                <TableCell>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">{viaje.fecha || "—"}</span>
                    <span className="text-xs text-muted-foreground">
                      {viaje.iniciado_en ? format(new Date(viaje.iniciado_en), "HH:mm", { locale: es }) : "—"}
                    </span>
                  </div>
                </TableCell>
                <TableCell className="text-sm">{viaje.finalizado_en ? format(new Date(viaje.finalizado_en), "HH:mm", { locale: es }) : "—"}</TableCell>
                <TableCell className="text-sm">{viaje.duracion_minutos ? `${viaje.duracion_minutos} min` : "—"}</TableCell>
                <TableCell className="text-sm">{viaje.distancia_metros ? `${(viaje.distancia_metros / 1000).toFixed(1)} km` : "—"}</TableCell>
                <TableCell>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">
                      {viaje.precio_mostrado ? new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" }).format(viaje.precio_mostrado) : "—"}
                    </span>
                    <span className="text-xs text-muted-foreground">{viaje.metodo_pago_label || "—"}</span>
                  </div>
                </TableCell>
                <TableCell className="text-right print:hidden">
                  <button 
                    onClick={() => {
                      if (onVerRuta) {
                        onVerRuta(viaje.id); 
                      } else {
                        setViajeSeleccionado(viaje.id); 
                      }
                    }} 
                    className="inline-flex items-center justify-center rounded-full bg-blue-500 p-2 text-white hover:bg-blue-600 transition-colors" 
                    title="Ver Ruta"
                  >
                    <MapPin className="h-4 w-4" />
                  </button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <MapaViajeModal viajeId={viajeSeleccionado} onClose={() => setViajeSeleccionado(null)} />
    </div>
  );
}