import { NextRequest, NextResponse } from 'next/server'
import { apiClient } from '@/lib/api'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Calcular tarifa
export async function POST(request: NextRequest) {
  const body = await request.json()
  const { origen_lat, origen_lng, destino_lat, destino_lng } = body
  
  if (!origen_lat || !origen_lng || !destino_lat || !destino_lng) {
    return NextResponse.json(
      { success: false, error: 'Faltan coordenadas' },
      { status: 400 }
    )
  }
  
  try {
    // Calcular distancia usando Google Maps o fórmula directa
    const distancia_km = calcularDistancia(origen_lat, origen_lng, destino_lat, destino_lng)
    const tarifa_base = 150  // Valor por defecto
    const precio_por_km = 50   // Valor por defecto
    const tarifa = tarifa_base + (distancia_km * precio_por_km)
    const minutos = Math.round(distancia_km * 2) // 2 min por km aprox
    
    return NextResponse.json({
      success: true,
      tarifa: Math.round(tarifa),
      distancia: `${distancia_km.toFixed(1)} km`,
      tiempo: `${minutos} min`,
    })
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Error al calcular tarifa' },
      { status: 500 }
    )
  }
}

// Solicitar viaje
export async function PUT(request: NextRequest) {
  const body = await request.json()
  const { direccion_origen, origen_lat, origen_lng, direccion_destino, destino_lat, destino_lng, metodo_pago, precio_estimado } = body
  
  try {
    // Crear solicitud en el backend
    const response = await fetch(`${API_URL}/api/viajes/solicitar`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        direccion_origen,
        origen_lat,
        origen_lng,
        direccion_destino,
        destino_lat,
        destino_lng,
        metodo_pago: metodo_pago || 'efectivo',
        precio_estimado,
      }),
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      return NextResponse.json(
        { success: false, detail: data.detail || 'Error al solicitar viaje' },
        { status: response.status }
      )
    }
    
    return NextResponse.json({
      success: true,
      viaje_id: data.id,
      mensaje: 'Viaje solicitado correctamente',
    })
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Error al conectar con el servidor' },
      { status: 500 }
    )
  }
}

// Función auxiliar para calcular distancia entre dos puntos (Haversine formula)
function calcularDistancia(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371 // Radio de la Tierra en km
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
  return R * c
}