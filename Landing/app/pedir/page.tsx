"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useBooking } from "@/hooks/useBooking";
import { loadGoogleMapsScript, geocodeAddress } from "@/lib/google-maps";
import { AddressAutocomplete, MapPicker } from "@/components/booking";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";
import { ChevronRight, ChevronDown } from "lucide-react";

// ============================================
// DATOS DE VEHÍCULOS
// ============================================
const VEHICULOS = [
  { 
    id: "standard", 
    nombre: "Standard", 
    icono: "🚗", 
    capacidad: "1-4", 
    equipaje: "2",
    precio: 7530,
    tiempo: "3 mins"
  },
  { 
    id: "premium", 
    nombre: "Premium", 
    icono: "⭐", 
    capacidad: "1-4", 
    equipaje: "4",
    precio: 9530,
    tiempo: "3 mins"
  },
  { 
    id: "camioneta", 
    nombre: "Camioneta", 
    icono: "🚐", 
    capacidad: "1-4", 
    equipaje: "4",
    precio: 10530,
    tiempo: "3 mins"
  },
  { 
    id: "eco", 
    nombre: "Eco", 
    icono: "🌿", 
    capacidad: "1-4", 
    equipaje: "2",
    precio: 6530,
    tiempo: "3 mins"
  },
];

const METODOS_PAGO = [
  { id: "efectivo", nombre: "Efectivo", icono: "💵" },
  { id: "qr", nombre: "QR", icono: "📱" },
  { id: "transferencia", nombre: "Transferencia", icono: "🏦" },
  { id: "tarjeta", nombre: "Tarjeta", icono: "💳" },
];

// ============================================
// FACTORES DE PRECIO POR VEHÍCULO
// ============================================
const FACTORES_VEHICULO: Record<string, number> = {
  'standard': 1.0,
  'premium': 1.3,
  'camioneta': 1.4,
  'eco': 0.9,
};

// ============================================
// COMPONENTE PRINCIPAL
// ============================================
export default function PedirPage() {
  const router = useRouter();
  const {
    formData,
    handleChange,
    isSubmitting,
    error,
    isValid,
    solicitarViaje,
    limpiarError,
  } = useBooking();

  const [mapsLoaded, setMapsLoaded] = useState(false);
  const [mapsLoading, setMapsLoading] = useState(true);
  const [mapError, setMapError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [viajeId, setViajeId] = useState<string | null>(null);
  
  // ============================================
  // ESTADOS DE ACORDEÓN
  // ============================================
  const [vehiculoOpen, setVehiculoOpen] = useState(false);
  const [pagoOpen, setPagoOpen] = useState(false);
  
  // ============================================
  // ESTADOS DE VALIDACIÓN DE EMAIL
  // ============================================
  const [emailValid, setEmailValid] = useState<boolean | null>(null);
  const [emailValidating, setEmailValidating] = useState(false);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [emailWarning, setEmailWarning] = useState<string | null>(null);
  const [emailValidationDetails, setEmailValidationDetails] = useState<any>(null);
  const [emailTouched, setEmailTouched] = useState(false);
  const emailTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isEmailValidatingRef = useRef(false);

  // Coordenadas para el mapa
  const [originCoords, setOriginCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [destCoords, setDestCoords] = useState<{ lat: number; lng: number } | null>(null);
  
  // ============================================
  // DATOS DE RUTA REAL DEL MAPA
  // ============================================
  const [routeDistanceKm, setRouteDistanceKm] = useState<number | null>(null);
  const [routeDurationMin, setRouteDurationMin] = useState<number | null>(null);
  const [precioFinal, setPrecioFinal] = useState<number | null>(null);

  // ============================================
  // FUNCIÓN: CALCULAR PRECIO CON DISTANCIA REAL
  // ============================================
  const actualizarPrecioConRutaReal = useCallback(async (distanciaKm: number) => {
    if (!originCoords || !destCoords) return;
    
    try {
      const response = await api.post('/api/public/viajes/calcular-tarifa', null, {
        params: {
          origen_lat: originCoords.lat,
          origen_lng: originCoords.lng,
          destino_lat: destCoords.lat,
          destino_lng: destCoords.lng,
        },
      });
      
      const distanciaBase = response.data.distancia_km || 1;
      const tarifaBase = response.data.tarifa || 0;
      const factor = distanciaKm / distanciaBase;
      const precioBase = Math.round(tarifaBase * factor);
      
      // Aplicar factor del vehículo seleccionado
      const factorVehiculo = FACTORES_VEHICULO[formData.tipoVehiculo] || 1.0;
      const precioCalculado = Math.round(precioBase * factorVehiculo);
      
      setPrecioFinal(precioCalculado);
      setRouteDistanceKm(distanciaKm);
      setRouteDurationMin(Math.round(distanciaKm * 2.5));
      
    } catch (err) {
      console.error('Error actualizando precio:', err);
    }
  }, [originCoords, destCoords, formData.tipoVehiculo]);

  // ============================================
  // HANDLE ROUTE CALCULATED
  // ============================================
  const handleRouteCalculated = useCallback((data: { distance: number; duration: number }) => {
    actualizarPrecioConRutaReal(data.distance);
  }, [actualizarPrecioConRutaReal]);

  // ============================================
  // ACTUALIZAR PRECIO AL CAMBIAR VEHÍCULO
  // ============================================
  useEffect(() => {
    if (routeDistanceKm !== null) {
      actualizarPrecioConRutaReal(routeDistanceKm);
    }
  }, [formData.tipoVehiculo]);

  // ============================================
  // CARGAR GOOGLE MAPS
  // ============================================
  useEffect(() => {
    const loadMaps = async () => {
      setMapsLoading(true);
      try {
        await loadGoogleMapsScript();
        setMapsLoaded(true);
        setMapError(null);
      } catch (err) {
        console.error('Error cargando Google Maps:', err);
        setMapError('No se pudo cargar el mapa. Verifica tu conexión.');
      } finally {
        setMapsLoading(false);
      }
    };
    loadMaps();
  }, []);

  // ============================================
  // GEOCODIFICAR DIRECCIONES
  // ============================================
  useEffect(() => {
    const geocode = async () => {
      if (!mapsLoaded) return;
      const origen = formData.origen;
      if (origen && origen.trim() !== '') {
        try {
          const result = await geocodeAddress(origen);
          if (result) setOriginCoords({ lat: result.lat, lng: result.lng });
        } catch (e) {
          console.error('Error geocodificando origen:', e);
        }
      } else {
        setOriginCoords(null);
      }
    };

    const timer = setTimeout(geocode, 600);
    return () => clearTimeout(timer);
  }, [formData.origen, mapsLoaded]);

  useEffect(() => {
    const geocode = async () => {
      if (!mapsLoaded) return;
      const destino = formData.destino;
      if (destino && destino.trim() !== '') {
        try {
          const result = await geocodeAddress(destino);
          if (result) setDestCoords({ lat: result.lat, lng: result.lng });
        } catch (e) {
          console.error('Error geocodificando destino:', e);
        }
      } else {
        setDestCoords(null);
      }
    };

    const timer = setTimeout(geocode, 600);
    return () => clearTimeout(timer);
  }, [formData.destino, mapsLoaded]);

  // ============================================
  // VALIDAR EMAIL
  // ============================================
  const validarEmail = useCallback(async (email: string) => {
    if (!email || email.trim() === '') {
      setEmailValid(null);
      setEmailError(null);
      setEmailWarning(null);
      setEmailValidationDetails(null);
      setEmailValidating(false);
      isEmailValidatingRef.current = false;
      return;
    }

    if (!email.includes('@') || !email.includes('.')) {
      setEmailValid(false);
      setEmailError('Formato de email inválido');
      setEmailWarning('❌ Formato de email inválido');
      setEmailValidationDetails(null);
      setEmailValidating(false);
      isEmailValidatingRef.current = false;
      return;
    }

    const cacheKey = `email_valid_${email}`;
    try {
      const cached = sessionStorage.getItem(cacheKey);
      if (cached) {
        const data = JSON.parse(cached);
        const cachedTime = sessionStorage.getItem(`${cacheKey}_time`);
        if (cachedTime && Date.now() - parseInt(cachedTime) < 300000) {
          setEmailValidationDetails(data);
          if (data.valid) {
            setEmailValid(true);
            setEmailError(null);
            setEmailWarning(null);
          } else {
            setEmailValid(false);
            setEmailError(data.reason || 'Email inválido');
            setEmailWarning(`❌ ${data.reason || 'Email inválido'}`);
          }
          setEmailValidating(false);
          isEmailValidatingRef.current = false;
          return;
        }
      }
    } catch (e) {}

    setEmailValidating(true);
    isEmailValidatingRef.current = true;
    setEmailError(null);
    setEmailWarning(null);
    setEmailValid(null);

    try {
      const response = await api.post('/api/verificacion/validar-email', null, {
        params: { 
          email: email,
          strict: true
        },
        timeout: 12000
      });
      
      const data = response.data;
      setEmailValidationDetails(data);
      
      try {
        sessionStorage.setItem(cacheKey, JSON.stringify(data));
        sessionStorage.setItem(`${cacheKey}_time`, Date.now().toString());
      } catch (e) {}
      
      if (data.valid) {
        setEmailValid(true);
        setEmailError(null);
        setEmailWarning(null);
      } else {
        setEmailValid(false);
        let errorMsg = data.reason || 'Email inválido';
        if (data.reason && data.reason.includes('Timeout')) {
          errorMsg = '⏰ No se pudo verificar el email. Verifica que el dominio exista.';
        } else if (data.buzon_existe === false) {
          errorMsg = '❌ El buzón de email no existe. Verifica la dirección.';
        }
        if (data.suggestions && data.suggestions.length > 0) {
          errorMsg += ` ¿Quisiste decir: ${data.suggestions[0].suggestion}?`;
        }
        setEmailError(errorMsg);
        setEmailWarning(`❌ ${errorMsg}`);
      }
    } catch (err: any) {
      console.error('Error validando email:', err);
      setEmailValid(false);
      let errorMsg = '❌ No se pudo verificar el email. ';
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        errorMsg += 'El servidor no respondió a tiempo. Verifica el dominio.';
      } else if (err.message === 'Network Error') {
        errorMsg += 'No hay conexión con el servidor. Verifica tu red.';
      } else {
        errorMsg += 'Intentá nuevamente.';
      }
      setEmailError(errorMsg);
      setEmailWarning(errorMsg);
    } finally {
      setEmailValidating(false);
      isEmailValidatingRef.current = false;
    }
  }, []);

  // ============================================
  // HANDLE EMAIL CHANGE
  // ============================================
  const handleEmailChange = (value: string) => {
    handleChange('email', value);
    setEmailTouched(true);
    
    if (!value || value.trim() === '') {
      setEmailValid(null);
      setEmailError(null);
      setEmailWarning(null);
      setEmailValidationDetails(null);
      setEmailValidating(false);
      if (emailTimerRef.current) {
        clearTimeout(emailTimerRef.current);
        emailTimerRef.current = null;
      }
      return;
    }
    
    if (emailValid !== null && !emailValidating) {
      setEmailValid(null);
      setEmailError(null);
      setEmailWarning(null);
    }
    
    if (emailTimerRef.current) {
      clearTimeout(emailTimerRef.current);
      emailTimerRef.current = null;
    }
    
    if (value.includes('@') && value.includes('.')) {
      emailTimerRef.current = setTimeout(() => {
        if (!isEmailValidatingRef.current) {
          validarEmail(value);
        }
        emailTimerRef.current = null;
      }, 1500);
    } else if (value.trim() !== '') {
      setEmailValid(false);
      setEmailError('Formato de email inválido');
      setEmailWarning('❌ Formato de email inválido');
    }
  };

  const handleEmailBlur = () => {
    setEmailTouched(true);
    if (emailTimerRef.current) {
      clearTimeout(emailTimerRef.current);
      emailTimerRef.current = null;
    }
    const email = formData.email;
    if (email && email.trim() !== '' && email.includes('@') && email.includes('.')) {
      if (!isEmailValidatingRef.current) {
        validarEmail(email);
      }
    } else if (email && email.trim() !== '') {
      setEmailValid(false);
      setEmailError('Formato de email inválido');
      setEmailWarning('❌ Formato de email inválido');
    } else {
      setEmailValid(null);
      setEmailError(null);
      setEmailWarning(null);
    }
  };

  const handleEmailKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (emailTimerRef.current) {
        clearTimeout(emailTimerRef.current);
        emailTimerRef.current = null;
      }
      const email = formData.email;
      if (email && email.trim() !== '' && email.includes('@') && email.includes('.')) {
        if (!isEmailValidatingRef.current) {
          validarEmail(email);
        }
      }
    }
  };

  const handleOriginSelect = (result: { address: string; lat: number; lng: number }) => {
    handleChange('origen', result.address);
    setOriginCoords({ lat: result.lat, lng: result.lng });
  };

  const handleDestSelect = (result: { address: string; lat: number; lng: number }) => {
    handleChange('destino', result.address);
    setDestCoords({ lat: result.lat, lng: result.lng });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    limpiarError();

    if (formData.email && formData.email.trim() !== '') {
      if (isEmailValidatingRef.current) {
        setEmailError('⏳ Esperando verificación del email...');
        return;
      }
      if (emailValid !== true) {
        await validarEmail(formData.email);
        if (emailValid !== true) {
          setEmailError('Email inválido. Por favor, verifica la dirección.');
          return;
        }
      }
    }

    if (!isValid()) return;

    try {
      const id = await solicitarViaje();
      setViajeId(id);
      setSubmitSuccess(true);
      setTimeout(() => {
        router.push(`/pedir/seguimiento/${id}`);
      }, 2000);
    } catch (err) {}
  };

  const isFormValid = () => {
    if (!isValid()) return false;
    if (formData.email && formData.email.trim() !== '') {
      if (emailValid !== true) return false;
      if (isEmailValidatingRef.current) return false;
    }
    return true;
  };

  const vehiculoSeleccionado = VEHICULOS.find(v => v.id === formData.tipoVehiculo);
  const pagoSeleccionado = METODOS_PAGO.find(p => p.id === formData.metodoPago);

  if (submitSuccess) {
    return (
      <div className="pedir-page">
        <div className="pedir-container" style={{ maxWidth: "48rem", margin: "0 auto" }}>
          <div style={{ backgroundColor: "#ffffff", borderRadius: "1rem", padding: "3rem 2rem", textAlign: "center", boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)" }}>
            <div style={{ fontSize: "4rem", marginBottom: "1rem" }}>✅</div>
            <h2 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>¡Viaje solicitado!</h2>
            <p style={{ color: "#6B7280", marginBottom: "1.5rem" }}>Estamos buscando un chofer para ti. Te redirigiremos al seguimiento...</p>
            <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
              <Link href={`/pedir/seguimiento/${viajeId}`}><Button>Ver seguimiento</Button></Link>
              <Link href="/"><Button variant="outline">Volver al inicio</Button></Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="pedir-page">
      <div className="pedir-container">
        <div className="pedir-form-section">
          <h1 className="form-section-title">🚕 Solicitar Taxi</h1>

          {error && (
            <div style={{ backgroundColor: "#FEF2F2", border: "1px solid #EF4444", borderRadius: "0.75rem", padding: "1rem", marginBottom: "1.5rem", color: "#991B1B", fontSize: "0.875rem" }}>
              ❌ {error}
            </div>
          )}

          {mapError && (
            <div style={{ backgroundColor: "#FEF3C7", border: "1px solid #F59E0B", borderRadius: "0.75rem", padding: "1rem", marginBottom: "1.5rem", color: "#92400E", fontSize: "0.875rem" }}>
              ⚠️ {mapError}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Nombre completo <span className="optional-text">*</span></label>
              <input type="text" className="form-input" placeholder="Ej: Juan Pérez" value={formData.nombre} onChange={(e) => handleChange("nombre", e.target.value)} required />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Teléfono <span className="optional-text">*</span></label>
                <input type="tel" className="form-input" placeholder="+54 9 381 123-4567" value={formData.telefono} onChange={(e) => handleChange("telefono", e.target.value)} required />
              </div>
              <div className="form-group">
                <label className="form-label">Email <span className="optional-text">(opcional)</span></label>
                <div style={{ position: "relative" }}>
                  <input
                    type="email"
                    className={`form-input ${emailValid === true && formData.email ? "border-green-500" : ""} ${emailValid === false && formData.email ? "border-red-500" : ""}`}
                    style={{ borderColor: emailValid === true && formData.email ? "#22C55E" : emailValid === false && formData.email ? "#EF4444" : "", paddingRight: "2.5rem" }}
                    placeholder="tu@email.com"
                    value={formData.email}
                    onChange={(e) => handleEmailChange(e.target.value)}
                    onBlur={handleEmailBlur}
                    onKeyDown={handleEmailKeyDown}
                  />
                  {emailValidating && <span style={{ position: "absolute", right: "12px", top: "50%", transform: "translateY(-50%)" }}>⏳</span>}
                  {emailValid === true && !emailValidating && formData.email && <span style={{ position: "absolute", right: "12px", top: "50%", transform: "translateY(-50%)", color: "#22C55E" }}>✅</span>}
                  {emailValid === false && !emailValidating && formData.email && <span style={{ position: "absolute", right: "12px", top: "50%", transform: "translateY(-50%)", color: "#EF4444" }}>❌</span>}
                </div>
                {emailValidating && <div style={{ fontSize: "0.75rem", color: "#F59E0B", marginTop: "0.25rem" }}>⏳ Verificando email...</div>}
                {emailError && emailTouched && !emailValidating && <div style={{ fontSize: "0.75rem", color: "#EF4444", marginTop: "0.25rem" }}>❌ {emailError}</div>}
                {emailValid === true && emailTouched && formData.email && !emailError && !emailValidating && (
                  <div style={{ fontSize: "0.75rem", color: "#22C55E", marginTop: "0.25rem" }}>
                    ✅ Email verificado{emailValidationDetails?.domain && <span style={{ color: "#6B7280", marginLeft: "0.5rem" }}>· {emailValidationDetails.domain}</span>}
                  </div>
                )}
                {(!formData.email || formData.email.trim() === '') && <div style={{ fontSize: "0.7rem", color: "#9CA3AF", marginTop: "0.25rem" }}>Opcional - Para verificación y auditoría</div>}
                {formData.email && emailValid === null && !emailValidating && emailTouched && <div style={{ fontSize: "0.7rem", color: "#9CA3AF", marginTop: "0.25rem" }}>El email se verificará al dejar de escribir</div>}
              </div>
            </div>

            {/* Origen */}
            <AddressAutocomplete
              value={formData.origen}
              onChange={(value) => handleChange("origen", value)}
              onSelect={handleOriginSelect}
              placeholder="Dirección de recogida"
              label="Origen"
              required
            />

            {/* Destino */}
            <AddressAutocomplete
              value={formData.destino}
              onChange={(value) => handleChange("destino", value)}
              onSelect={handleDestSelect}
              placeholder="Tu destino"
              label="Destino"
              required
            />

            {/* ============================================ */}
            {/* ACORDEÓN: TIPO DE VEHÍCULO */}
            {/* ============================================ */}
            <div className="form-group">
              <div
                onClick={() => setVehiculoOpen(!vehiculoOpen)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "0.75rem 0",
                  cursor: "pointer",
                  borderBottom: "1px solid #E5E7EB",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  <span style={{ fontSize: "1.25rem" }}>🚗</span>
                  <span style={{ fontWeight: 500, color: "#1a1a1a" }}>
                    {vehiculoSeleccionado ? vehiculoSeleccionado.nombre : "Seleccionar vehículo"}
                  </span>
                  {vehiculoSeleccionado && precioFinal !== null && precioFinal > 0 && (
                    <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "#F59E0B" }}>
                      · ${precioFinal.toLocaleString()}
                    </span>
                  )}
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  {vehiculoSeleccionado && routeDurationMin !== null && (
                    <span style={{ fontSize: "0.7rem", color: "#6B7280" }}>
                      ⏱️ {routeDurationMin} min
                    </span>
                  )}
                  {vehiculoOpen ? (
                    <ChevronDown className="h-5 w-5 text-gray-400" />
                  ) : (
                    <ChevronRight className="h-5 w-5 text-gray-400" />
                  )}
                </div>
              </div>

              {vehiculoOpen && (
                <div style={{ marginTop: "0.5rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                  {VEHICULOS.map((vehiculo) => {
                    const isSelected = formData.tipoVehiculo === vehiculo.id;
                    // Precio estimado para este vehículo
                    let precioVehiculo = null;
                    if (precioFinal !== null && precioFinal > 0) {
                      const factor = FACTORES_VEHICULO[vehiculo.id] || 1.0;
                      precioVehiculo = Math.round(precioFinal / FACTORES_VEHICULO[formData.tipoVehiculo] * factor);
                    }
                    
                    return (
                      <div
                        key={vehiculo.id}
                        onClick={() => {
                          handleChange("tipoVehiculo", vehiculo.id);
                          setVehiculoOpen(false);
                        }}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          padding: "0.75rem 1rem",
                          borderRadius: "0.75rem",
                          border: isSelected ? "2px solid #FBBF24" : "2px solid #E5E7EB",
                          backgroundColor: isSelected ? "#FFFBEB" : "#ffffff",
                          cursor: "pointer",
                          transition: "all 0.2s ease",
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                          <span style={{ fontSize: "1.25rem" }}>{vehiculo.icono}</span>
                          <div>
                            <div style={{ fontWeight: 600, color: "#1a1a1a", fontSize: "0.9rem" }}>
                              {vehiculo.nombre}
                            </div>
                            <div style={{ fontSize: "0.7rem", color: "#6B7280" }}>
                              👤 {vehiculo.capacidad} · 🧳 {vehiculo.equipaje}
                            </div>
                          </div>
                        </div>
                        <div style={{ textAlign: "right" }}>
                          <div style={{ fontWeight: 700, color: "#F59E0B", fontSize: "0.9rem" }}>
                            {precioVehiculo !== null && precioVehiculo > 0 
                              ? `$ ${precioVehiculo.toLocaleString()}` 
                              : '$ ---'}
                          </div>
                          <div style={{ fontSize: "0.65rem", color: "#6B7280" }}>
                            ⏱️ {routeDurationMin !== null ? `${routeDurationMin} min` : 'Calculando...'}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* ============================================ */}
            {/* ACORDEÓN: MÉTODO DE PAGO */}
            {/* ============================================ */}
            <div className="form-group">
              <div
                onClick={() => setPagoOpen(!pagoOpen)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "0.75rem 0",
                  cursor: "pointer",
                  borderBottom: "1px solid #E5E7EB",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  <span style={{ fontSize: "1.25rem" }}>💳</span>
                  <span style={{ fontWeight: 500, color: "#1a1a1a" }}>
                    {pagoSeleccionado ? pagoSeleccionado.nombre : "Pagar en el vehículo"}
                  </span>
                </div>
                <div>
                  {pagoOpen ? (
                    <ChevronDown className="h-5 w-5 text-gray-400" />
                  ) : (
                    <ChevronRight className="h-5 w-5 text-gray-400" />
                  )}
                </div>
              </div>

              {pagoOpen && (
                <div style={{ marginTop: "0.5rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                  {METODOS_PAGO.map((metodo) => {
                    const isSelected = formData.metodoPago === metodo.id;
                    return (
                      <div
                        key={metodo.id}
                        onClick={() => {
                          handleChange("metodoPago", metodo.id);
                          setPagoOpen(false);
                        }}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "0.75rem",
                          padding: "0.75rem 1rem",
                          borderRadius: "0.75rem",
                          border: isSelected ? "2px solid #FBBF24" : "2px solid #E5E7EB",
                          backgroundColor: isSelected ? "#FFFBEB" : "#ffffff",
                          cursor: "pointer",
                          transition: "all 0.2s ease",
                        }}
                      >
                        <span style={{ fontSize: "1.25rem" }}>{metodo.icono}</span>
                        <span style={{ fontWeight: 500, color: "#1a1a1a" }}>{metodo.nombre}</span>
                        {isSelected && (
                          <span style={{ marginLeft: "auto", color: "#FBBF24", fontWeight: 700 }}>✓</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Pasajeros + Equipaje */}
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Pasajeros</label>
                <div className="counter-group">
                  <div className="counter-controls">
                    <button type="button" className="counter-btn" onClick={() => handleChange("pasajeros", Math.max(1, formData.pasajeros - 1))}>−</button>
                    <span className="counter-value">{formData.pasajeros}</span>
                    <button type="button" className="counter-btn" onClick={() => handleChange("pasajeros", Math.min(6, formData.pasajeros + 1))}>+</button>
                  </div>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Equipaje</label>
                <div className="counter-group">
                  <div className="counter-controls">
                    <button type="button" className="counter-btn" onClick={() => handleChange("equipaje", Math.max(0, formData.equipaje - 1))}>−</button>
                    <span className="counter-value">{formData.equipaje}</span>
                    <button type="button" className="counter-btn" onClick={() => handleChange("equipaje", Math.min(4, formData.equipaje + 1))}>+</button>
                  </div>
                </div>
              </div>
            </div>

            {/* Nota para el conductor */}
            <div className="form-group">
              <label className="form-label">Nota para el conductor</label>
              <input
                type="text"
                className="form-input"
                placeholder="Ej: Ingreso por calle lateral, portón negro, etc."
                value={formData.nota_conductor || ''}
                onChange={(e) => handleChange("nota_conductor", e.target.value)}
              />
            </div>

            {/* ============================================ */}
            {/* PRECIO ESTIMADO - SOLO DATOS REALES */}
            {/* ============================================ */}
            {precioFinal !== null && precioFinal > 0 && (
              <div className="price-estimate">
                <div className="price-label">🚕 Precio estimado</div>
                <div className="price-value">
                  ${precioFinal.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div style={{ fontSize: "0.75rem", color: "#6B7280", marginTop: "0.25rem" }}>
                  {vehiculoSeleccionado && (
                    <span style={{ fontWeight: 500, color: "#1a1a1a" }}>
                      {vehiculoSeleccionado.nombre} · 
                    </span>
                  )}
                  {routeDistanceKm !== null ? `${routeDistanceKm.toFixed(1)} km` : 'Calculando distancia...'}
                  {routeDurationMin !== null && ` · ~${routeDurationMin} min`}
                </div>
              </div>
            )}

            {/* ============================================ */}
            {/* BOTÓN SUBMIT */}
            {/* ============================================ */}
            <button
              type="submit"
              className="submit-btn"
              disabled={!isFormValid() || isSubmitting || !mapsLoaded}
            >
              {isSubmitting ? (
                "⏳ Buscando chofer..."
              ) : !mapsLoaded ? (
                "⏳ Cargando mapa..."
              ) : !isValid() ? (
                "Complete los campos obligatorios"
              ) : formData.email && emailValid === false ? (
                "❌ Email inválido - Corregir"
              ) : formData.email && emailValidating ? (
                "⏳ Verificando email..."
              ) : formData.email && emailValid === null && emailTouched ? (
                "⏳ Validando email..."
              ) : (
                `Pedir Taxi ${precioFinal && precioFinal > 0 ? `· $${precioFinal.toLocaleString()}` : ""}`
              )}
            </button>

            {/* Limpiar formulario */}
            <div style={{ textAlign: "center", marginTop: "1rem" }}>
              <button
                type="button"
                onClick={() => {
                  handleChange("nombre", "");
                  handleChange("telefono", "");
                  handleChange("email", "");
                  handleChange("origen", "");
                  handleChange("destino", "");
                  handleChange("tipoVehiculo", "standard");
                  handleChange("metodoPago", "efectivo");
                  handleChange("pasajeros", 1);
                  handleChange("equipaje", 0);
                  handleChange("nota_conductor", "");
                  setOriginCoords(null);
                  setDestCoords(null);
                  setEmailValid(null);
                  setEmailError(null);
                  setEmailWarning(null);
                  setEmailValidationDetails(null);
                  setEmailTouched(false);
                  limpiarError();
                  setPrecioFinal(null);
                  setRouteDistanceKm(null);
                  setRouteDurationMin(null);
                }}
                style={{
                  fontSize: "0.875rem",
                  color: "#6B7280",
                  background: "transparent",
                  border: "none",
                  cursor: "pointer",
                }}
              >
                🗑️ Limpiar formulario
              </button>
            </div>

            <div style={{ textAlign: "center", marginTop: "0.5rem" }}>
              <Link href="/" style={{ fontSize: "0.875rem", color: "#6B7280" }}>← Volver al inicio</Link>
            </div>
          </form>
        </div>

        <div className="pedir-map-section">
          {mapsLoading ? (
            <div style={{ width: "100%", height: "100%", minHeight: "500px", backgroundColor: "#F3F4F6", display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", color: "#6B7280", borderRadius: "1rem" }}>
              <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>⏳</div>
              <p style={{ fontWeight: 500 }}>Cargando mapa...</p>
              <p style={{ fontSize: "0.75rem", marginTop: "0.5rem" }}>Verificando Google Maps...</p>
            </div>
          ) : mapsLoaded ? (
            <MapPicker
              origin={originCoords ? { ...originCoords, address: formData.origen } : null}
              destination={destCoords ? { ...destCoords, address: formData.destino } : null}
              height="100%"
              showRoute={!!(originCoords && destCoords)}
              onRouteCalculated={handleRouteCalculated}
            />
          ) : (
            <div style={{ width: "100%", height: "100%", minHeight: "500px", backgroundColor: "#FEF2F2", display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", color: "#991B1B", borderRadius: "1rem" }}>
              <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>⚠️</div>
              <p style={{ fontWeight: 500 }}>Error al cargar el mapa</p>
              <p style={{ fontSize: "0.75rem", marginTop: "0.5rem" }}>Verifica tu conexión a internet</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}