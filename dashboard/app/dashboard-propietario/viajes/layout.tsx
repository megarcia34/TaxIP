"use client";

import { usePathname, useRouter } from "next/navigation";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api/client";

export default function ViajesLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();

  const { data: resumen } = useQuery({
    queryKey: ["viajes", "resumen"],
    queryFn: async () => {
      const { data } = await api.get("/viajes/resumen");
      return data;
    },
    refetchInterval: 30000,
  });

  const currentTab = pathname.split("/").pop() || "todos";

  const handleTabChange = (value: string) => {
    if (value === "todos") router.push("/dashboard-propietario/viajes");
    else router.push(`/dashboard-propietario/viajes/${value}`);
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Viajes</h2>
        <p className="text-muted-foreground">Gestión e historial completo de tu flota.</p>
      </div>

      <Tabs value={currentTab} onValueChange={handleTabChange} className="w-full">
        <TabsList className="grid w-full max-w-4xl grid-cols-6">
          <TabsTrigger value="pendientes" className="gap-2">
            Pendientes
            {resumen?.pendiente > 0 && (
              <Badge variant="destructive" className="px-1.5 py-0 text-xs">
                {resumen.pendiente}
              </Badge>
            )}
          </TabsTrigger>
          
          <TabsTrigger value="en-curso" className="gap-2">
            En Curso
            {resumen?.en_curso > 0 && (
              <Badge variant="default" className="bg-blue-500 px-1.5 py-0 text-xs">
                {resumen.en_curso}
              </Badge>
            )}
          </TabsTrigger>
          
          <TabsTrigger value="finalizados">Finalizados</TabsTrigger>
          <TabsTrigger value="cancelados">Cancelados</TabsTrigger>
          <TabsTrigger value="todos">Todos</TabsTrigger>
          <TabsTrigger value="route-map">Route Map</TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="mt-2">
        {children}
      </div>
    </div>
  );
}