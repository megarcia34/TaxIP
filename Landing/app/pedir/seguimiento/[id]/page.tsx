"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { MapPicker } from "@/components/booking";
import { loadGoogleMapsScript } from "@/lib/google-maps";

// ============================================
// PIPELINE DE ESTADOS
// ============================================
const ESTADOS = [
  { id: "pendiente", label: "Buscando", icon: "🔍", desc: "Buscando un chofer disponible" },
  { id: "aceptado", label: "Confirmado", icon: "✅", desc: "Chofer confirmó tu viaje" },
  { id: "en_curso", label: "En camino", icon: "🚗", desc: "Te estás moviendo hacia tu destino" },
  { id: "finalizado", label: "Completado", icon: "✅", desc: "¡Viaje finalizado!" },
];

const ESTADO_ORDEN = ["pendiente", "aceptado", "en_curso", "finalizado"];

// ============================================
// COMPONENTE PRINCIPAL
// ============================================
export default function SeguimientoPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [viaje, setViaje] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [estadoActual, setEstadoActual] = useState<string>("pendiente");
  const [mapsLoaded, setMapsLoaded] = useState(false);

  // ============================================
  // CARGAR GOOGLE MAPS
  // ============================================
  useEffect(() => {
    const loadMaps = async () => {
      try {
        await loadGoogleMapsScript();
        setMapsLoaded(true);
      } catch (err) {
        console.error('Error cargando Google Maps:', err);
      }
    };
    loadMaps();
  }, []);

  // ============================================
  // CARGAR DATOS DEL VIAJE (SOLO ENDPOINT PÚBLICO)
  // ============================================
  const cargarViaje = async () => {
    if (!id) return;

    try {
      setLoading(true);
      console.log('📋 Cargando viaje público ID:', id);
      
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      // ✅ USAR SOLO EL ENDPOINT PÚBLICO (sin autenticación)
      const response = await fetch(`${API_URL}/api/public/viajes/${id}/estado`);
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('✅ Datos del viaje:', data);
      setViaje(data);
      setEstadoActual(data.estado || "pendiente");
      setError(null);
    } catch (err: any) {
      console.error("Error cargando viaje:", err);
      setError(err.message || "No se pudo cargar el seguimiento");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarViaje();
    const interval = setInterval(cargarViaje, 10000);
    return () => clearInterval(interval);
  }, [id]);

  // ============================================
  // CANCELAR VIAJE (SOLO ENDPOINT PÚBLICO)
  // ============================================
  const cancelarViaje = async () => {
    if (!confirm("¿Seguro que quieres cancelar este viaje?")) return;

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/public/viajes/${id}/cancelar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ motivo: "Cancelado por el pasajero" }),
      });

      if (!response.ok) {
        throw new Error('Error al cancelar el viaje');
      }

      setEstadoActual("cancelado");
      alert("✅ Viaje cancelado correctamente");
      await cargarViaje();
    } catch (err) {
      console.error("Error cancelando viaje:", err);
      alert("❌ Error al cancelar el viaje");
    }
  };

  // ============================================
  // RENDER - CARGA
  // ============================================
  if (loading) {
    return (
      <div className="pedir-page">
        <div className="pedir-container" style={{ maxWidth: "48rem", margin: "0 auto" }}>
          <div style={{ textAlign: "center", padding: "3rem" }}>
            <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>⏳</div>
            <p style={{ color: "#6B7280" }}>Cargando seguimiento...</p>
          </div>
        </div>
      </div>
    );
  }

  // ============================================
  // RENDER - ERROR
  // ============================================
  if (error) {
    return (
      <div className="pedir-page">
        <div className="pedir-container" style={{ maxWidth: "48rem", margin: "0 auto" }}>
          <div
            style={{
              backgroundColor: "#ffffff",
              borderRadius: "1rem",
              padding: "2rem",
              textAlign: "center",
              boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
            }}
          >
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>❌</div>
            <h2 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "0.5rem" }}>
              Error
            </h2>
            <p style={{ color: "#6B7280", marginBottom: "1.5rem" }}>{error}</p>
            <div style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
              <button
                onClick={() => {
                  setLoading(true);
                  setError(null);
                  cargarViaje();
                }}
                style={{
                  padding: "0.5rem 1.5rem",
                  backgroundColor: "#FBBF24",
                  color: "#1a1a1a",
                  border: "none",
                  borderRadius: "0.75rem",
                  cursor: "pointer",
                  fontWeight: 600,
                }}
              >
                Reintentar
              </button>
              <Link href="/pedir">
                <Button>Volver a solicitar</Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ============================================
  // RENDER - NO ENCONTRADO
  // ============================================
  if (!viaje) {
    return (
      <div className="pedir-page">
        <div className="pedir-container" style={{ maxWidth: "48rem", margin: "0 auto" }}>
          <div
            style={{
              backgroundColor: "#ffffff",
              borderRadius: "1rem",
              padding: "2rem",
              textAlign: "center",
              boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
            }}
          >
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🔍</div>
            <h2 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "0.5rem" }}>
              Viaje no encontrado
            </h2>
            <p style={{ color: "#6B7280", marginBottom: "1.5rem" }}>
              No pudimos encontrar el viaje que buscas.
            </p>
            <Link href="/pedir">
              <Button>Volver a solicitar</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // ============================================
  // RENDER - PRINCIPAL
  // ============================================
  const idxActual = ESTADO_ORDEN.indexOf(estadoActual);
  const esCancelado = estadoActual === "cancelado";
  const esFinalizado = estadoActual === "finalizado";

  const originCoords = viaje.origen_lat && viaje.origen_lng
    ? { lat: viaje.origen_lat, lng: viaje.origen_lng }
    : null;
  const destCoords = viaje.destino_lat && viaje.destino_lng
    ? { lat: viaje.destino_lat, lng: viaje.destino_lng }
    : null;

  return (
    <div className="pedir-page">
      <div className="pedir-container" style={{ maxWidth: "64rem", margin: "0 auto" }}>
        <div
          style={{
            backgroundColor: "#ffffff",
            borderRadius: "1rem",
            padding: "2rem",
            boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
          }}
        >
          {/* Header */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
            <h1 style={{ fontSize: "1.25rem", fontWeight: 700 }}>
              {esCancelado ? "🚫 Viaje Cancelado" : esFinalizado ? "✅ Viaje Completado" : "🚕 Seguimiento del Viaje"}
            </h1>
            <span style={{ fontSize: "0.75rem", color: "#6B7280" }}>
              #{viaje.id?.slice(0, 8) || "N/A"}
            </span>
          </div>

          {/* Grid: Info + Mapa */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
            {/* Columna izquierda - Info y pipeline */}
            <div>
              {/* Info del viaje */}
              <div
                style={{
                  backgroundColor: "#F9FAFB",
                  borderRadius: "0.75rem",
                  padding: "1rem",
                  marginBottom: "1.5rem",
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "0.5rem",
                }}
              >
                <div>
                  <div style={{ fontSize: "0.7rem", color: "#9CA3AF", textTransform: "uppercase" }}>Origen</div>
                  <div style={{ fontSize: "0.875rem", fontWeight: 500 }}>{viaje.direccion_origen || "No especificado"}</div>
                </div>
                <div>
                  <div style={{ fontSize: "0.7rem", color: "#9CA3AF", textTransform: "uppercase" }}>Destino</div>
                  <div style={{ fontSize: "0.875rem", fontWeight: 500 }}>{viaje.direccion_destino || "No especificado"}</div>
                </div>
                <div>
                  <div style={{ fontSize: "0.7rem", color: "#9CA3AF", textTransform: "uppercase" }}>Pasajero</div>
                  <div style={{ fontSize: "0.875rem", fontWeight: 500 }}>{viaje.pasajero_nombre || "N/A"}</div>
                </div>
                <div>
                  <div style={{ fontSize: "0.7rem", color: "#9CA3AF", textTransform: "uppercase" }}>Precio</div>
                  <div style={{ fontSize: "0.875rem", fontWeight: 600, color: "#F59E0B" }}>
                    ${viaje.precio_final?.toLocaleString() || viaje.precio_estimado?.toLocaleString() || "N/A"}
                  </div>
                </div>
                {viaje.chofer_nombre && (
                  <div style={{ gridColumn: "span 2" }}>
                    <div style={{ fontSize: "0.7rem", color: "#9CA3AF", textTransform: "uppercase" }}>Chofer</div>
                    <div style={{ fontSize: "0.875rem", fontWeight: 500 }}>{viaje.chofer_nombre}</div>
                  </div>
                )}
              </div>

              {/* Pipeline de estados */}
              {!esCancelado && (
                <div style={{ marginBottom: "1.5rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", position: "relative", padding: "0 0.5rem" }}>
                    <div
                      style={{
                        position: "absolute",
                        top: "1.75rem",
                        left: "1.5rem",
                        right: "1.5rem",
                        height: "3px",
                        backgroundColor: "#E5E7EB",
                        zIndex: 0,
                      }}
                    >
                      <div
                        style={{
                          width: `${(idxActual / (ESTADO_ORDEN.length - 1)) * 100}%`,
                          height: "100%",
                          backgroundColor: "#FBBF24",
                          transition: "width 0.5s ease",
                        }}
                      />
                    </div>

                    {ESTADOS.map((estado, index) => {
                      const isCompleted = index <= idxActual;
                      const isActive = index === idxActual;

                      return (
                        <div
                          key={estado.id}
                          style={{
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            zIndex: 1,
                            flex: 1,
                          }}
                        >
                          <div
                            style={{
                              width: "2.5rem",
                              height: "2.5rem",
                              borderRadius: "9999px",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              fontSize: "1.25rem",
                              backgroundColor: isCompleted ? "#FBBF24" : "#E5E7EB",
                              border: isActive ? "3px solid #F59E0B" : "none",
                              transition: "all 0.3s ease",
                              boxShadow: isActive ? "0 0 0 4px rgba(251,191,36,0.2)" : "none",
                            }}
                          >
                            {estado.icon}
                          </div>
                          <div
                            style={{
                              fontSize: "0.65rem",
                              fontWeight: isActive ? 600 : 400,
                              color: isActive ? "#1a1a1a" : "#6B7280",
                              marginTop: "0.5rem",
                              textAlign: "center",
                              maxWidth: "70px",
                              transition: "all 0.3s ease",
                            }}
                          >
                            {estado.label}
                          </div>
                          {isActive && (
                            <div
                              style={{
                                fontSize: "0.6rem",
                                color: "#F59E0B",
                                marginTop: "0.25rem",
                                fontWeight: 500,
                              }}
                            >
                              ◀ Actual
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  <div
                    style={{
                      marginTop: "1.5rem",
                      padding: "1rem",
                      backgroundColor: "#FFFBEB",
                      borderRadius: "0.75rem",
                      textAlign: "center",
                      border: "1px solid rgba(251,191,36,0.3)",
                    }}
                  >
                    <p style={{ fontSize: "0.875rem", color: "#1a1a1a" }}>
                      {ESTADOS.find(e => e.id === estadoActual)?.desc || "Procesando..."}
                    </p>
                    {!esFinalizado && (
                      <p style={{ fontSize: "0.7rem", color: "#6B7280", marginTop: "0.25rem" }}>
                        🔄 Actualizando automáticamente...
                      </p>
                    )}
                  </div>
                </div>
              )}

              {esCancelado && (
                <div
                  style={{
                    padding: "1.5rem",
                    backgroundColor: "#FEF2F2",
                    borderRadius: "0.75rem",
                    textAlign: "center",
                    border: "1px solid #EF4444",
                    marginBottom: "1.5rem",
                  }}
                >
                  <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>🚫</div>
                  <p style={{ fontWeight: 600, color: "#991B1B" }}>Este viaje ha sido cancelado</p>
                  <p style={{ fontSize: "0.875rem", color: "#6B7280" }}>
                    Si necesitas ayuda, contacta a nuestro soporte.
                  </p>
                </div>
              )}

              {/* Botones */}
              <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
                {!esCancelado && !esFinalizado && (
                  <button
                    onClick={cancelarViaje}
                    style={{
                      padding: "0.5rem 1.5rem",
                      border: "1px solid #EF4444",
                      borderRadius: "0.75rem",
                      backgroundColor: "transparent",
                      color: "#EF4444",
                      cursor: "pointer",
                      fontSize: "0.875rem",
                      fontWeight: 500,
                      transition: "all 0.2s ease",
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = "#FEF2F2";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = "transparent";
                    }}
                  >
                    Cancelar Viaje
                  </button>
                )}
                <Link href="/" style={{ marginLeft: "auto" }}>
                  <Button variant="outline" size="sm">Volver al inicio</Button>
                </Link>
                {esFinalizado && (
                  <Link href="/pedir">
                    <Button size="sm">Solicitar otro viaje</Button>
                  </Link>
                )}
              </div>
            </div>

            {/* Columna derecha - Mapa */}
            <div style={{ minHeight: "400px" }}>
              {mapsLoaded ? (
                <MapPicker
                  origin={originCoords ? { ...originCoords } : null}
                  destination={destCoords ? { ...destCoords } : null}
                  height="100%"
                  showRoute={!!(originCoords && destCoords)}
                />
              ) : (
                <div
                  style={{
                    width: "100%",
                    height: "100%",
                    minHeight: "400px",
                    backgroundColor: "#F3F4F6",
                    borderRadius: "1rem",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#6B7280",
                  }}
                >
                  Cargando mapa...
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}