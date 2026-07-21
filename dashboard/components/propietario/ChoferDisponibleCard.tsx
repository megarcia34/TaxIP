'use client';

import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Star, Phone, Mail } from 'lucide-react';
import { ChoferDisponible } from '@/types/propietario';

interface Props {
  chofer: ChoferDisponible;
  onContratar: (choferId: string) => void;
}

export function ChoferDisponibleCard({ chofer, onContratar }: Props) {
  return (
    <Card className="w-full max-w-sm">
      <CardHeader>
        <CardTitle className="flex justify-between items-center">
          <span>{chofer.nombre} {chofer.apellido}</span>
          <Badge variant="outline" className="flex gap-1">
            <Star className="h-3 w-3 fill-yellow-500 text-yellow-500" />
            {chofer.calificacion_promedio?.toFixed(1) || 'Nuevo'}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Mail className="h-4 w-4" />
          <span>{chofer.email}</span>
        </div>
        {chofer.telefono && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Phone className="h-4 w-4" />
            <span>{chofer.telefono}</span>
          </div>
        )}
        <div className="text-xs text-muted-foreground">
          {chofer.total_calificaciones} calificaciones
        </div>
      </CardContent>
      <CardFooter>
        <Button className="w-full" onClick={() => onContratar(chofer.id)}>
          Iniciar contratación
        </Button>
      </CardFooter>
    </Card>
  );
}