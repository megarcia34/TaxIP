"use client";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  ArrowLeft,
  DollarSign,
  Wallet,
  Receipt,
  CheckCircle2,
  AlertCircle,
  Car,
  Globe,
  Smartphone,
  Building2,
  Monitor,
} from "lucide-react";
import { useState } from "react";

// ============================================
// TIPOS (Luego vendrán del backend)
// ============================================
interface DesgloseViaje {
  origen_tipo: string;
  metodo_pago: string;
  cantidad: number;
  total: number;
}

interface Gasto {
  id: string;
  tipo_gasto: string;
  descripcion: string | null;
  monto: number;
  estado_aprobacion: "pendiente" | "aprobado" | "rechazado";
}

interface ConciliacionDetalleMock {
  turno_id: string;
  vehiculo_patente: string;
  chofer_nombre: string;
  tipo_contrato: string;
  recaudacion_viajes: number;
  recaudacion_manual: number;
  recaudacion_total: number;
  recaudacion_efectivo: number;
  recaudacion_electronico: number;
  efectivo_en_mano: number;
  efectivo_declarado: number;
  diferencia_efectivo: number;
  gastos_total: number;
  gastos: Gasto[];
  desglose_viajes: DesgloseViaje[];
  liquidacion_propietario: number;
  liquidacion_chofer: number;
}

// ============================================
// DATOS MOCK
// ============================================
const MOCK: ConciliacionDetalleMock = {
  turno_id: "59008382-e294-431d-ab8e-17c8ca9c44ef",
  vehiculo_patente: "AD240FT",
  chofer_nombre: "Pepe Argento",
  tipo_contrato: "AUTO_GESTION",
  recaudacion_viajes: 5000,
  recaudacion_manual: 1600,
  recaudacion_total: 6600,
  recaudacion_efectivo: 4800,
  recaudacion_electronico: 1800,
  efectivo_en_mano: 4800,
  efectivo_declarado: 4800,
  diferencia_efectivo: 0,
  gastos_total: 1500,
  gastos: [
    {
      id: "g1",
      tipo_gasto: "COMBUSTIBLE",
      descripcion: "Carga de YPF",
      monto: 1500,
      estado_aprobacion: "aprobado",
    },
  ],
  desglose_viajes: [
    { origen_tipo: "via_publica", metodo_pago: "efectivo", cantidad: 5, total: 3000 },
    { origen_tipo: "plataforma", metodo_pago: "efectivo", cantidad: 2, total: 1200 },
    { origen_tipo: "plataforma", metodo_pago: "tarjeta_debito", cantidad: 1, total: 800 },
    { origen_tipo: "qr_comercio", metodo_pago: "qr", cantidad: 1, total: 600 },
    { origen_tipo: "corporativo", metodo_pago: "efectivo", cantidad: 1, total: 1000 },
  ],
  liquidacion_propietario: 5100,
  liquidacion_chofer: 0,
};

// ============================================
// HELPERS
// ============================================
const formatCurrency = (v: number) =>
  new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" }).format(v);

const getOrigenIcon = (tipo: string) => {
  switch (tipo) {
    case "via_publica": return <Car className="h-4 w-4 text-muted-foreground" />;
    case "plataforma": return <Globe className="h-4 w-4 text-blue-500" />;
    case "qr_comercio": return <Smartphone className="h-4 w-4 text-purple-500" />;
    case "corporativo": return <Building2 className="h-4 w-4 text-orange-500" />;
    case "despacho_manual": return <Monitor className="h-4 w-4 text-green-500" />;
    default: return <Globe className="h-4 w-4 text-muted-foreground" />;
  }
};

const getOrigenLabel = (tipo: string) => {
  switch (tipo) {
    case "via_publica": return "Calle";
    case "plataforma": return "App/Landing";
    case "qr_comercio": return "Código QR";
    case "corporativo": return "Corporativo";
    case "despacho_manual": return "Operativo";
    default: return tipo;
  }
};

const getMetodoPagoLabel = (m: string) => {
  switch (m) {
    case "efectivo": return "Efectivo";
    case "tarjeta_debito": return "Tarjeta Débito";
    case "tarjeta_credito": return "Tarjeta Crédito";
    case "qr": return "QR";
    case "transferencia": return "Transferencia";
    default: return m;
  }
};

// ============================================
// COMPONENTE PRINCIPAL
// ============================================
export function ConciliacionDetalleView() {
  const detalle = MOCK; // Cuando esté listo, esto vendrá del backend.
  const [gastos, setGastos] = useState(detalle.gastos);

  const handleAprobar = (id: string) => {
    setGastos(gastos.map((g) => (g.id === id ? { ...g, estado_aprobacion: "aprobado" } : g)));
  };

  const handleRechazar = (id: string) => {
    setGastos(gastos.map((g) => (g.id === id ? { ...g, estado_aprobacion: "rechazado" } : g)));
  };

  return (
    <div className="space-y-6 pb-10">
      {/* HEADER */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon">
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold">
            Conciliar Turno · {detalle.vehiculo_patente}
          </h1>
          <p className="text-sm text-muted-foreground">
            {detalle.chofer_nombre} · {detalle.tipo_contrato}
          </p>
        </div>
      </div>

      {/* 1. TARJETAS SUPERIORES */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1">
              <DollarSign className="h-3 w-3" /> Recaudación Total
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{formatCurrency(detalle.recaudacion_total)}</p>
            <p className="text-xs text-muted-foreground">
              Viajes {formatCurrency(detalle.recaudacion_viajes)} + Manual {formatCurrency(detalle.recaudacion_manual)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1">
              <Wallet className="h-3 w-3" /> Efectivo en Mano
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{formatCurrency(detalle.efectivo_en_mano)}</p>
            <p className="text-xs text-muted-foreground">
              Declarado: {formatCurrency(detalle.efectivo_declarado)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1">
              <Receipt className="h-3 w-3" /> Gastos
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-red-500">
              {formatCurrency(detalle.gastos_total)}
            </p>
            <p className="text-xs text-muted-foreground">{gastos.length} gasto(s)</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1">
              {detalle.diferencia_efectivo === 0 ? (
                <CheckCircle2 className="h-3 w-3 text-green-600" />
              ) : (
                <AlertCircle className="h-3 w-3 text-red-500" />
              )}
              Diferencia Efectivo
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p
              className={`text-2xl font-bold ${
                detalle.diferencia_efectivo === 0 ? "text-green-600" : "text-red-500"
              }`}
            >
              {formatCurrency(detalle.diferencia_efectivo)}
            </p>
            <p className="text-xs text-muted-foreground">
              {detalle.diferencia_efectivo === 0 ? "Caja cuadrada" : "Revisar diferencia"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 2. ESTADO DE CUENTA */}
      <Card>
        <CardHeader>
          <CardTitle>Estado de Cuenta del Turno</CardTitle>
          <CardDescription>
            Operación matemática de ingresos, gastos y liquidación final.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[220px]">Concepto</TableHead>
                <TableHead>Detalle</TableHead>
                <TableHead className="text-right">Ingresos</TableHead>
                <TableHead className="text-right">Egresos</TableHead>
                <TableHead className="text-right">Saldo</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Recaudación Viajes</TableCell>
                <TableCell className="text-muted-foreground">
                  {detalle.desglose_viajes.reduce((acc, v) => acc + v.cantidad, 0)} viajes finalizados
                </TableCell>
                <TableCell className="text-right text-green-600 font-medium">
                  {formatCurrency(detalle.recaudacion_viajes)}
                </TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right">—</TableCell>
              </TableRow>

              <TableRow>
                <TableCell className="font-medium">Gastos Declarados</TableCell>
                <TableCell className="text-muted-foreground">
                  {gastos.length} gasto(s) declarado(s)
                </TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right text-red-500 font-medium">
                  {formatCurrency(detalle.gastos_total)}
                </TableCell>
                <TableCell className="text-right">—</TableCell>
              </TableRow>

              <TableRow className="bg-muted/50 font-semibold">
                <TableCell colSpan={2}>Subtotal Operativo</TableCell>
                <TableCell className="text-right">
                  {formatCurrency(detalle.recaudacion_viajes)}
                </TableCell>
                <TableCell className="text-right">
                  {formatCurrency(detalle.gastos_total)}
                </TableCell>
                <TableCell className="text-right text-lg">
                  {formatCurrency(detalle.recaudacion_viajes - detalle.gastos_total)}
                </TableCell>
              </TableRow>

              <TableRow>
                <TableCell className="font-medium">Efectivo Calculado</TableCell>
                <TableCell className="text-muted-foreground">
                  Viajes efectivo + Manual
                </TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right">
                  {formatCurrency(detalle.efectivo_en_mano)}
                </TableCell>
              </TableRow>

              <TableRow>
                <TableCell className="font-medium">Efectivo Declarado</TableCell>
                <TableCell className="text-muted-foreground">
                  Entregado por el chofer
                </TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right font-bold">
                  {formatCurrency(detalle.efectivo_declarado)}
                </TableCell>
              </TableRow>

              <TableRow>
                <TableCell className="font-medium">Diferencia de Caja</TableCell>
                <TableCell className="text-muted-foreground">
                  Declarado - Calculado
                </TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell
                  className={`text-right font-bold ${
                    detalle.diferencia_efectivo === 0
                      ? "text-green-600"
                      : "text-red-500"
                  }`}
                >
                  {formatCurrency(detalle.diferencia_efectivo)}
                </TableCell>
              </TableRow>

              <TableRow className="bg-primary/5">
                <TableCell colSpan={5} className="font-bold text-primary py-3">
                  Resultado de la Liquidación (Contrato {detalle.tipo_contrato})
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">A favor del Propietario</TableCell>
                <TableCell className="text-muted-foreground">
                  (Recaudación - Gastos)
                </TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right font-bold text-primary">
                  {formatCurrency(detalle.liquidacion_propietario)}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">A favor del Chofer</TableCell>
                <TableCell className="text-muted-foreground">
                  (Comisión / Salario)
                </TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right">—</TableCell>
                <TableCell className="text-right font-bold">
                  {formatCurrency(detalle.liquidacion_chofer)}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* 3. DESGLOSE DE VIAJES */}
      <Card>
        <CardHeader>
          <CardTitle>Resumen de Operación (Viajes)</CardTitle>
          <CardDescription>
            Desglose de los viajes por canal y método de pago.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Canal</TableHead>
                <TableHead>Método de Pago</TableHead>
                <TableHead className="text-right">Cantidad</TableHead>
                <TableHead className="text-right">Total</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {detalle.desglose_viajes.map((item, idx) => (
                <TableRow key={idx}>
                  <TableCell className="flex items-center gap-2">
                    {getOrigenIcon(item.origen_tipo)}
                    <span>{getOrigenLabel(item.origen_tipo)}</span>
                  </TableCell>
                  <TableCell>{getMetodoPagoLabel(item.metodo_pago)}</TableCell>
                  <TableCell className="text-right">{item.cantidad}</TableCell>
                  <TableCell className="text-right font-medium">
                    {formatCurrency(item.total)}
                  </TableCell>
                </TableRow>
              ))}
              <TableRow className="bg-muted/50 font-semibold">
                <TableCell colSpan={2}>TOTAL</TableCell>
                <TableCell className="text-right">
                  {detalle.desglose_viajes.reduce((acc, v) => acc + v.cantidad, 0)}
                </TableCell>
                <TableCell className="text-right">
                  {formatCurrency(detalle.recaudacion_viajes)}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* 4. GASTOS DECLARADOS */}
      <Card>
        <CardHeader>
          <CardTitle>Gastos Declarados ({gastos.length})</CardTitle>
          <CardDescription>
            Aprobá o rechazá los gastos declarados por el chofer.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Tipo</TableHead>
                <TableHead>Descripción</TableHead>
                <TableHead className="text-right">Monto</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead className="text-right">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {gastos.map((g) => (
                <TableRow key={g.id}>
                  <TableCell className="font-medium">{g.tipo_gasto}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {g.descripcion || "—"}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(g.monto)}
                  </TableCell>
                  <TableCell>
                    {g.estado_aprobacion === "aprobado" && (
                      <Badge className="bg-green-100 text-green-700">Aprobado</Badge>
                    )}
                    {g.estado_aprobacion === "pendiente" && (
                      <Badge className="bg-yellow-100 text-yellow-700">Pendiente</Badge>
                    )}
                    {g.estado_aprobacion === "rechazado" && (
                      <Badge className="bg-red-100 text-red-700">Rechazado</Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-right space-x-2">
                    {g.estado_aprobacion === "pendiente" && (
                      <>
                        <Button size="sm" variant="outline" onClick={() => handleRechazar(g.id)}>
                          Rechazar
                        </Button>
                        <Button size="sm" onClick={() => handleAprobar(g.id)}>
                          Aprobar
                        </Button>
                      </>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* 5. BOTÓN CERRAR */}
      <div className="flex justify-end">
        <Button size="lg" className="px-8">
          Cerrar Conciliación
        </Button>
      </div>
    </div>
  );
}