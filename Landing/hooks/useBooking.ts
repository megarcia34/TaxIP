"use client";

import { useState, useEffect } from 'react';
import { viajesService } from '@/lib/api';
import { geocodeAddress } from '@/lib/google-maps';

interface FormData {
  nombre: string;
  telefono: string;
  email: string;
  origen: string;
  destino: string;
  tipoVehiculo: string;
  metodoPago: string;
  pasajeros: number;
  equipaje: number;
}

// ============================================
// GEOCODIFICAR CON GOOGLE MAPS REAL
// ============================================
const geocodificar = async (direccion: string): Promise<{ lat: number; lng: number }> => {
  // Si la dirección está vacía, devolver coordenadas por defecto (Tucumán)
  if (!direccion || direccion.trim() === '') {
    return { lat: -26.8083, lng: -65.2176 };
  }

  try {
    console.log('📍 Geocodificando con Google Maps:', direccion);
    const result = await geocodeAddress(direccion);
    
    if (result) {
      console.log('✅ Geocodificación exitosa:', result.lat, result.lng);
      return { lat: result.lat, lng: result.lng };
    }
  } catch (error) {
    console.error('❌ Error geocodificando:', error);
  }

  // Fallback a Tucumán si falla la geocodificación
  console.warn('⚠️ Usando coordenadas de fallback (Tucumán)');
  return { lat: -26.8083, lng: -65.2176 };
};

export function useBooking() {
  const [formData, setFormData] = useState<FormData>({
    nombre: '',
    telefono: '',
    email: '',
    origen: '',
    destino: '',
    tipoVehiculo: 'premium',
    metodoPago: 'efectivo',
    pasajeros: 1,
    equipaje: 0,
  });

  const [precioEstimado, setPrecioEstimado] = useState<number | null>(null);
  const [distanciaKm, setDistanciaKm] = useState<number | null>(null);
  const [tiempoEstimado, setTiempoEstimado] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ============================================
  // CALCULAR PRECIO CUANDO CAMBIAN ORIGEN/DESTINO
  // ============================================
  useEffect(() => {
    const calcular = async () => {
      if (!formData.origen || !formData.destino) {
        setPrecioEstimado(null);
        setDistanciaKm(null);
        setTiempoEstimado(null);
        return;
      }

      try {
        console.log('📍 Origen:', formData.origen);
        console.log('📍 Destino:', formData.destino);

        // Geocodificar origen y destino con Google Maps real
        const [origenCoords, destinoCoords] = await Promise.all([
          geocodificar(formData.origen),
          geocodificar(formData.destino),
        ]);

        console.log('📍 Origen coords:', origenCoords);
        console.log('📍 Destino coords:', destinoCoords);

        // Si las coordenadas son iguales, es un error
        if (origenCoords.lat === destinoCoords.lat && origenCoords.lng === destinoCoords.lng) {
          console.warn('⚠️ Origen y destino tienen las mismas coordenadas');
          setError('Origen y destino parecen ser el mismo lugar. Verificá las direcciones.');
          setPrecioEstimado(null);
          setDistanciaKm(null);
          setTiempoEstimado(null);
          return;
        }

        const response = await viajesService.calcularTarifa({
          origen_lat: origenCoords.lat,
          origen_lng: origenCoords.lng,
          destino_lat: destinoCoords.lat,
          destino_lng: destinoCoords.lng,
        });

        console.log('📊 Respuesta del backend:', response);

        setPrecioEstimado(response.tarifa);
        setDistanciaKm(response.distancia_km);
        setTiempoEstimado(response.tiempo_estimado_min);
        setError(null);
      } catch (err: any) {
        console.error('Error calculando tarifa:', err);
        setError('Error al calcular la tarifa. Intentá nuevamente.');
        setPrecioEstimado(null);
        setDistanciaKm(null);
        setTiempoEstimado(null);
      }
    };

    const timer = setTimeout(calcular, 800);
    return () => clearTimeout(timer);
  }, [formData.origen, formData.destino]);

  // ============================================
  // HANDLE CHANGE
  // ============================================
  const handleChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  // ============================================
  // SOLICITAR VIAJE
  // ============================================
  const solicitarViaje = async (): Promise<string> => {
    setIsSubmitting(true);
    setError(null);

    try {
      console.log('🚕 Solicitando viaje público...');

      // Geocodificar con Google Maps real
      const [origenCoords, destinoCoords] = await Promise.all([
        geocodificar(formData.origen),
        geocodificar(formData.destino),
      ]);

      console.log('📍 Origen geocodificado:', origenCoords);
      console.log('📍 Destino geocodificado:', destinoCoords);

      const response = await viajesService.solicitarViajePublico({
        direccion_origen: formData.origen,
        origen_lat: origenCoords.lat,
        origen_lng: origenCoords.lng,
        direccion_destino: formData.destino,
        destino_lat: destinoCoords.lat,
        destino_lng: destinoCoords.lng,
        metodo_pago: formData.metodoPago,
        precio_estimado: precioEstimado || undefined,
        nombre_pasajero: formData.nombre,
        telefono_pasajero: formData.telefono,
      });

      console.log('✅ Viaje solicitado:', response);
      return response.viaje_id;

    } catch (err: any) {
      console.error('❌ Error solicitando viaje:', err);
      
      let errorMsg = 'Error al procesar el pedido. ';
      if (err.message === 'Network Error') {
        errorMsg += 'No se pudo conectar con el servidor. Verifica que el backend esté corriendo.';
      } else if (err.response?.data?.detail) {
        errorMsg += err.response.data.detail;
      } else {
        errorMsg += err.message || 'Intentá nuevamente.';
      }
      
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const limpiarError = () => setError(null);

  const isValid = () => {
    return (
      formData.nombre.trim() !== '' &&
      formData.telefono.trim() !== '' &&
      formData.origen.trim() !== '' &&
      formData.destino.trim() !== ''
    );
  };

  return {
    formData,
    handleChange,
    precioEstimado,
    distanciaKm,
    tiempoEstimado,
    isSubmitting,
    error,
    isValid,
    solicitarViaje,
    limpiarError,
  };
}