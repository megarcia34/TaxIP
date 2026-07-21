"use client";

import { useState, useRef, useEffect } from 'react';
import { createAutocomplete, geocodeAddress } from '@/lib/google-maps';

interface AddressAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSelect: (result: { address: string; lat: number; lng: number }) => void;
  placeholder?: string;
  label?: string;
  required?: boolean;
  className?: string;
}

export function AddressAutocomplete({
  value,
  onChange,
  onSelect,
  placeholder = 'Ingresá una dirección...',
  label,
  required = false,
  className = '',
}: AddressAutocompleteProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isLoading, setIsLoading] = useState(false);
  const autocompleteRef = useRef<any>(null);

  useEffect(() => {
    if (!inputRef.current || !window.google) return;

    // Crear autocomplete - SIN types mixtos
    const autocomplete = new window.google.maps.places.Autocomplete(inputRef.current, {
      types: ['address'], // Solo address, no geocode
      componentRestrictions: { country: 'ar' },
      fields: ['formatted_address', 'geometry', 'place_id', 'name'],
    });

    autocompleteRef.current = autocomplete;

    autocomplete.addListener('place_changed', () => {
      const place = autocomplete.getPlace();
      if (place.geometry && place.geometry.location) {
        onSelect({
          address: place.formatted_address || place.name || inputRef.current?.value || '',
          lat: place.geometry.location.lat(),
          lng: place.geometry.location.lng(),
        });
      }
    });

    return () => {
      // Limpiar
      if (autocompleteRef.current) {
        window.google.maps.event.clearInstanceListeners(autocompleteRef.current);
      }
    };
  }, []);

  const handleBlur = async () => {
    if (value && value.trim() !== '') {
      try {
        setIsLoading(true);
        const result = await geocodeAddress(value);
        if (result) {
          onSelect({
            address: result.formatted_address,
            lat: result.lat,
            lng: result.lng,
          });
        }
      } catch (error) {
        // Si falla, no hacer nada
        console.log('Geocodificación falló:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleBlur();
    }
  };

  return (
    <div className="form-group">
      {label && (
        <label className="form-label">
          {label}
          {required && <span className="optional-text"> *</span>}
        </label>
      )}
      <div style={{ position: 'relative' }}>
        <input
          ref={inputRef}
          type="text"
          className={`form-input ${className}`}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          required={required}
          autoComplete="off"
        />
        {isLoading && (
          <span style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)' }}>
            ⏳
          </span>
        )}
      </div>
      <div style={{ fontSize: '0.7rem', color: '#9CA3AF', marginTop: '0.25rem' }}>
        Escribí una dirección y seleccioná de las sugerencias
      </div>
    </div>
  );
}