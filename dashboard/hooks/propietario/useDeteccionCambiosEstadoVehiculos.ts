// D:\ataxip\dashboard\hooks\propietario\useDeteccionCambiosEstadoVehiculos.ts
'use client';

import { useEffect, useState } from 'react';

const STORAGE_KEY = 'taxip_vehiculos_estado_anterior';

export interface VehiculoCambioEstado {
  id: string;
  patente: string;
  estado_anterior: string;
  estado_actual: 'aprobado' | 'rechazado';
}

interface EstadoGuardado {
  [vehiculoId: string]: string;
}

export function useDeteccionCambiosEstadoVehiculos(vehiculos: any[]) {
  const [cambios, setCambios] = useState<VehiculoCambioEstado[]>([]);

  useEffect(() => {
    if (!vehiculos || vehiculos.length === 0) return;

    let estadoAnterior: EstadoGuardado = {};
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) estadoAnterior = JSON.parse(raw);
    } catch {
      estadoAnterior = {};
    }

    const cambiosDetectados: VehiculoCambioEstado[] = [];
    const estadoNuevo: EstadoGuardado = {};

    vehiculos.forEach((v: any) => {
      estadoNuevo[v.id] = v.estado_aprobacion;

      const anterior = estadoAnterior[v.id];
      if (
        anterior === 'en_revision' &&
        (v.estado_aprobacion === 'aprobado' || v.estado_aprobacion === 'rechazado')
      ) {
        cambiosDetectados.push({
          id: v.id,
          patente: v.patente,
          estado_anterior: anterior,
          estado_actual: v.estado_aprobacion,
        });
      }
    });

    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(estadoNuevo));
    } catch {}

    if (cambiosDetectados.length > 0) {
      setCambios(cambiosDetectados);
    }
  }, [vehiculos]);

  const marcarComoVisto = () => {
    setCambios([]);
  };

  return { cambios, marcarComoVisto };
}