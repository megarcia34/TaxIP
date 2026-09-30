/**
 * Hook de ubicación. (VERSIÓN CON LOGS TEMPORALES DE DIAGNÓSTICO v2)
 *
 * Cambios v2:
 * - accuracy: High (en vez de Balanced) para que iOS respete timeInterval.
 * - Logs en cleanup y AppState para diagnosticar desmontaje/background.
 */
import { useEffect, useRef, useState } from 'react';
import { AppState } from 'react-native';
import * as Location from 'expo-location';
import { ubicacionService } from '@/services/ubicacion.service';
import { websocketService } from '@/services/websocket.service';
import type { Coordenada } from '@/types/ubicacion.types';
import { useTurnoStore } from '@/stores/turno.store';

const INTERVALO_MOVIMIENTO_MS = 10_000;
const INTERVALO_DETENIDO_MS = 30_000;
const UMBRAL_MOVIMIENTO_METROS = 10;

export function useUbicacion() {
  const [coordenada, setCoordenada] = useState<Coordenada | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const ultimaCoordenadaRef = useRef<Coordenada | null>(null);
  const ultimoEnvioRef = useRef<number>(0);
  const suscripcionRef = useRef<Location.LocationSubscription | null>(null);

  useEffect(() => {
    let montado = true;

    (async () => {
      setIsLoading(true);
      console.log('[Ubicación] arrancando hook');
      try {
        const ok = await ubicacionService.pedirPermisos();
        console.log('[Ubicación] permisos:', ok);
        if (!montado) return;

        if (!ok) {
          setError('Permisos de ubicación denegados');
          return;
        }

        try {
          const inicial = await obtenerCoordenadaInicial();
          console.log('[Ubicación] inicial:', inicial);
          if (!montado) return;
          if (inicial) {
            setCoordenada(inicial);
            ultimaCoordenadaRef.current = inicial;
            ultimoEnvioRef.current = Date.now();
            enviarPorWS(inicial);
          }
        } catch (e: any) {
          console.warn('[Ubicación] no se pudo obtener la inicial:', e?.message);
        }

        console.log('[Ubicación] iniciando watchPositionAsync');
        suscripcionRef.current = await Location.watchPositionAsync(
          {
            accuracy: Location.Accuracy.High,
            distanceInterval: UMBRAL_MOVIMIENTO_METROS,
            timeInterval: INTERVALO_MOVIMIENTO_MS,
          },
          (loc) => {
            if (!montado) return;
            const coord: Coordenada = {
              lat: loc.coords.latitude,
              lng: loc.coords.longitude,
            };
            console.log('[Ubicación] callback disparado:', coord);
            setCoordenada(coord);
            evaluarYEnviar(coord);
          }
        );

        console.log('[Ubicación] watchPositionAsync OK');
        setError(null);
      } catch (e: any) {
        console.warn('[Ubicación] error al iniciar tracking:', e?.message);
        if (!montado) return;
        setError(e?.message ?? 'Error al iniciar tracking');
      } finally {
        if (montado) setIsLoading(false);
      }
    })();

    const appStateSub = AppState.addEventListener('change', (state) => {
      console.log('[Ubicación] AppState:', state);
    });

    return () => {
      console.log('[Ubicación] cleanup — desmontando hook');
      montado = false;
      appStateSub.remove();
      if (suscripcionRef.current) {
        suscripcionRef.current.remove();
        suscripcionRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function evaluarYEnviar(nueva: Coordenada): void {
    const ahora = Date.now();
    const ultima = ultimaCoordenadaRef.current;
    const desdeUltimoEnvio = ahora - ultimoEnvioRef.current;

    let enMovimiento = true;
    if (ultima) {
      const distancia = distanciaMetros(ultima, nueva);
      enMovimiento = distancia > UMBRAL_MOVIMIENTO_METROS;
      console.log(
        `[Ubicación] evaluar: distancia=${distancia.toFixed(1)}m ` +
          `desdeUltimoEnvio=${(desdeUltimoEnvio / 1000).toFixed(1)}s ` +
          `enMovimiento=${enMovimiento}`
      );
    }

    const intervalo = enMovimiento
      ? INTERVALO_MOVIMIENTO_MS
      : INTERVALO_DETENIDO_MS;

    if (desdeUltimoEnvio >= intervalo) {
      console.log('[Ubicación] → ENVIANDO por WS');
      enviarPorWS(nueva);
      ultimoEnvioRef.current = ahora;
      ultimaCoordenadaRef.current = nueva;
    } else {
      console.log(
        `[Ubicación] → NO envía (faltan ${(
          (intervalo - desdeUltimoEnvio) / 1000
        ).toFixed(1)}s)`
      );
    }
  }

  function enviarPorWS(coord: Coordenada): void {
    const turnoActivo = useTurnoStore.getState().turnoActivo;
    console.log(
      '[Ubicación] enviarPorWS — turnoActivo =',
      turnoActivo ? turnoActivo.id : 'null',
      'WS conectado =',
      websocketService.estaConectado()
    );

    if (!turnoActivo) {
      console.log('[Ubicación] → BLOQUEADO (sin turno activo)');
      return;
    }

    console.log('[Ubicación] → ws.enviar location_update', coord);
    websocketService.enviar({
      type: 'location_update',
      data: { lat: coord.lat, lng: coord.lng },
    });
  }

  return { coordenada, error, isLoading };
}

async function obtenerCoordenadaInicial(): Promise<Coordenada | null> {
  const { status } = await Location.getForegroundPermissionsAsync();
  if (status !== 'granted') return null;

  const loc = await Location.getLastKnownPositionAsync({
    maxAge: 60_000,
    requiredAccuracy: 200,
  });
  if (!loc) {
    const current = await Location.getCurrentPositionAsync({
      accuracy: Location.Accuracy.High,
    });
    return { lat: current.coords.latitude, lng: current.coords.longitude };
  }
  return { lat: loc.coords.latitude, lng: loc.coords.longitude };
}

function distanciaMetros(a: Coordenada, b: Coordenada): number {
  const R = 6_371_000;
  const dLat = toRad(b.lat - a.lat);
  const dLng = toRad(b.lng - a.lng);
  const lat1 = toRad(a.lat);
  const lat2 = toRad(b.lat);

  const x =
    Math.sin(dLat / 2) ** 2 +
    Math.sin(dLng / 2) ** 2 * Math.cos(lat1) * Math.cos(lat2);
  return 2 * R * Math.asin(Math.sqrt(x));
}

function toRad(grados: number): number {
  return (grados * Math.PI) / 180;
}