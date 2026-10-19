// D:\ataxip\dashboard\app\dashboard-propietario\metricas-fallbacks\page.tsx
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Loader2, TrendingDown, AlertTriangle } from 'lucide-react';
import { useMetricasFallbacks } from '@/hooks/propietario/useMetricasFallbacks';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

export default function MetricasFallbacksPage() {
  const [propietarioId, setPropietarioId] = useState<string | null>(null);
  const { data, isLoading } = useMetricasFallbacks();

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      setPropietarioId(params.get('propietario_id'));
    }
  }, []);

  const backHref =
    propietarioId
      ? `/admin/propietarios?propietario_id=${propietarioId}`
      : '/dashboard-propietario';

  const formatFecha = (fecha: string) => {
    try {
      return format(new Date(fecha), 'dd/MM/yyyy HH:mm', { locale: es });
    } catch {
      return fecha;
    }
  };

  const formatMoney = (n: number | null) => {
    if (n === null || n === undefined) return '-';
    return `$${n.toLocaleString('es-AR')}`;
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  const total = data?.total ?? 0;
  const fallbacks = data?.fallbacks ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href={backHref}>
          <Button variant="outline" size="icon" type="button">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div className="flex-1 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Metricas de fallbacks</h1>
            <p className="text-muted-foreground">
              Viajes con precios estimados por fallback del sistema de tarifas
            </p>
          </div>
          <Badge
            className={`text-lg px-4 py-2 ${
              total > 0 ? 'bg-yellow-500 hover:bg-yellow-600' : 'bg-green-500 hover:bg-green-600'
            }`}
          >
            {total} {total === 1 ? 'fallback' : 'fallbacks'}
          </Badge>
        </div>
      </div>

      {total === 0 ? (
        <Card>
          <CardContent className="text-center py-12 text-muted-foreground">
            <TrendingDown className="h-16 w-16 mx-auto mb-4 text-green-500/50" />
            <p className="text-lg font-medium">Sin fallbacks registrados</p>
            <p className="text-sm">Todos los precios se calcularon correctamente</p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-yellow-500" />
              Listado de viajes afectados
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {fallbacks.map((f) => (
                <div key={f.id} className="border rounded-lg p-4 hover:shadow-sm transition-shadow">
                  <div className="flex justify-between items-start gap-3 flex-wrap">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        {f.patente && (
                          <Badge variant="outline" className="font-mono">
                            {f.patente}
                          </Badge>
                        )}
                        <span className="text-sm text-muted-foreground">
                          {formatFecha(f.fecha)}
                        </span>
                      </div>
                      {f.origen && f.destino && (
                        <div className="mt-1 text-sm">
                          <span className="text-muted-foreground">{f.origen}</span>
                          <span className="mx-2 text-muted-foreground">a</span>
                          <span className="font-medium">{f.destino}</span>
                        </div>
                      )}
                      <div className="mt-2 text-sm">
                        <span className="text-muted-foreground">Motivo:</span>{' '}
                        <span className="font-medium">{f.motivo}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-muted-foreground">Precio estimado</div>
                      <div className="font-semibold">{formatMoney(f.precio_estimado)}</div>
                      {f.precio_cobrado !== null && (
                        <>
                          <div className="text-xs text-muted-foreground mt-1">Cobrado</div>
                          <div className="font-semibold">{formatMoney(f.precio_cobrado)}</div>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}