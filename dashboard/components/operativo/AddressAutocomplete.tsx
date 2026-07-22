// components/operativo/AddressAutocomplete.tsx

'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { Input } from '@/components/ui/input';
import { Loader2 } from 'lucide-react';

interface AddressAutocompleteProps {
  /** Valor controlado desde el padre */
  value: string;
  /** Callback cuando cambia el valor del input */
  onChange: (value: string) => void;
  /** Callback cuando se selecciona una dirección */
  onSelect: (address: string, lat: number, lng: number, placeId?: string) => void;
  placeholder?: string;
  initialLat?: number | null;
  initialLng?: number | null;
  disabled?: boolean;
  className?: string;
  id?: string;
  label?: string;
  required?: boolean;
}

export function AddressAutocomplete({
  value,
  onChange,
  onSelect,
  placeholder = 'Buscar dirección...',
  initialLat,
  initialLng,
  disabled = false,
  className = '',
  id,
  label,
  required = false,
}: AddressAutocompleteProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const autocompleteRef = useRef<google.maps.places.Autocomplete | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isValidated, setIsValidated] = useState(false);
  const [isGeocoding, setIsGeocoding] = useState(false);

  // ✅ Sincronizar validación cuando value cambia desde el padre
  useEffect(() => {
    if (value && value.trim().length > 0) {
      // Si el value tiene contenido, lo consideramos potencialmente válido
      // pero no marcamos como validado automáticamente
    }
  }, [value]);

  // Inicializar Autocomplete
  useEffect(() => {
    if (!inputRef.current || typeof window === 'undefined') return;
    if (!window.google?.maps?.places) {
      console.warn('Google Places API no cargada');
      return;
    }

    const autocomplete = new window.google.maps.places.Autocomplete(inputRef.current, {
      types: ['geocode', 'establishment'],
      componentRestrictions: { country: 'ar' },
      fields: ['address_components', 'geometry', 'formatted_address', 'place_id', 'name'],
    });

    autocompleteRef.current = autocomplete;

    const listener = autocomplete.addListener('place_changed', () => {
      const place = autocomplete.getPlace();
      if (!place.geometry?.location) return;

      const lat = place.geometry.location.lat();
      const lng = place.geometry.location.lng();
      const address = place.formatted_address || place.name || '';

      if (isNaN(lat) || isNaN(lng)) {
        console.warn('Coordenadas inválidas:', { lat, lng });
        return;
      }

      setIsValidated(true);
      onChange(address);
      onSelect(address, lat, lng, place.place_id);
    });

    return () => {
      window.google.maps.event.removeListener(listener);
    };
  }, [onSelect, onChange]);

  // Geocodificación inversa por coordenadas iniciales
  useEffect(() => {
    if (initialLat && initialLng && value && !isValidated) {
      setIsLoading(true);
      const geocoder = new window.google.maps.Geocoder();
      geocoder.geocode(
        { location: { lat: initialLat, lng: initialLng } },
        (results: google.maps.GeocoderResult[], status: google.maps.GeocoderStatus) => {
          setIsLoading(false);
          if (status === 'OK' && results?.[0]) {
            const address = results[0].formatted_address;
            onChange(address);
            setIsValidated(true);
            onSelect(address, initialLat, initialLng);
          }
        }
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialLat, initialLng]);

  // Geocodificación mejorada - maneja intersecciones y nombres sin número
  const geocodeAddress = useCallback(async (address: string) => {
    if (!address.trim() || address.trim().length < 3) return;

    setIsGeocoding(true);

    try {
      const response = await fetch(
        `https://maps.googleapis.com/maps/api/geocode/json?` +
        `address=${encodeURIComponent(address)}&` +
        `key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&` +
        `language=es&components=country:AR`
      );

      const data = await response.json();

      if (data.status === 'OK' && data.results?.[0]) {
        const result = data.results[0];
        const location = result.geometry.location;
        const formattedAddress = result.formatted_address;

        if (isNaN(location.lat) || isNaN(location.lng)) {
          console.warn('Coordenadas inválidas en geocodificación');
          return;
        }

        onChange(formattedAddress);
        setIsValidated(true);
        onSelect(formattedAddress, location.lat, location.lng);
      } else {
        console.warn('No se encontró la dirección:', address);
      }
    } catch (error) {
      console.warn('Error en geocodificación:', error);
    } finally {
      setIsGeocoding(false);
    }
  }, [onSelect, onChange]);

  // Manejo de blur mejorado
  const handleBlur = useCallback(() => {
    const trimmedValue = value.trim();

    if (isValidated || !trimmedValue || trimmedValue.length < 3) return;

    if (/^-?\d+\.\d+,\s*-?\d+\.\d+$/.test(trimmedValue)) return;

    geocodeAddress(trimmedValue);
  }, [value, isValidated, geocodeAddress]);

  // Manejar cambio manual del input
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    setIsValidated(false);
  };

  // Manejar tecla Enter para geocodificar
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const trimmedValue = value.trim();
      if (trimmedValue && !isValidated && trimmedValue.length >= 3) {
        geocodeAddress(trimmedValue);
      }
    }
  };

  return (
    <div className="relative">
      {label && (
        <label htmlFor={id} className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5 block">
          {label}
          {required && <span className="text-red-500 ml-0.5">*</span>}
        </label>
      )}
      <div className="relative">
        <Input
          ref={inputRef}
          id={id}
          type="text"
          value={value}
          onChange={handleChange}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled || isLoading || isGeocoding}
          className={`pr-10 ${className}`}
          autoComplete="off"
          required={required}
        />
        {(isLoading || isGeocoding) && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
          </div>
        )}
        {isValidated && !isLoading && !isGeocoding && value && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="h-2 w-2 rounded-full bg-green-500" title="Dirección validada" />
          </div>
        )}
      </div>
      {isValidated && value && (
        <p className="text-xs text-green-600 dark:text-green-400 mt-1">
          ✓ Dirección validada
        </p>
      )}
      {!isValidated && value && value.length > 3 && !isLoading && !isGeocoding && (
        <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
          Presiona Enter o selecciona una sugerencia para validar
        </p>
      )}
    </div>
  );
}

export default AddressAutocomplete;