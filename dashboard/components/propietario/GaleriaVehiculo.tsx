'use client'

import { useState, useEffect, useRef } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { 
  ChevronLeft, ChevronRight, Plus, Upload, 
  Trash2, Star, Image as ImageIcon, X, Loader2
} from 'lucide-react'
import { apiClient } from '@/lib/api'
import { toast } from 'sonner'
import { CldUploadWidget } from 'next-cloudinary'

// ============================================================
// TIPOS
// ============================================================

interface FotoVehiculo {
  id: string
  url: string
  public_id: string
  descripcion: string | null
  orden: number
  es_principal: boolean
  created_at: string
}

interface GaleriaVehiculoProps {
  vehiculoId: string
  onFotosChange?: (fotos: FotoVehiculo[]) => void
  compact?: boolean
}

// ============================================================
// COMPONENTE PRINCIPAL
// ============================================================

export function GaleriaVehiculo({ vehiculoId, onFotosChange, compact = false }: GaleriaVehiculoProps) {
  const [fotos, setFotos] = useState<FotoVehiculo[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [showDescripcion, setShowDescripcion] = useState(false)
  const [descripcionTemp, setDescripcionTemp] = useState('')
  const [fotoEditando, setFotoEditando] = useState<string | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // ============================================================
  // CARGAR FOTOS
  // ============================================================

  const cargarFotos = async () => {
    if (!vehiculoId) return
    
    setLoading(true)
    try {
      const res = await apiClient.get(`/api/propietario/fotos/vehiculos/${vehiculoId}`)
      const data = res.data || []
      setFotos(data)
      
      const principalIndex = data.findIndex((f: FotoVehiculo) => f.es_principal)
      setSelectedIndex(principalIndex >= 0 ? principalIndex : 0)
      
      if (onFotosChange) {
        onFotosChange(data)
      }
    } catch (error) {
      console.error('Error cargando fotos:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    cargarFotos()
  }, [vehiculoId])

  // ============================================================
  // NAVEGACIÓN
  // ============================================================

  const fotoAnterior = () => {
    setSelectedIndex((prev) => (prev > 0 ? prev - 1 : fotos.length - 1))
  }

  const fotoSiguiente = () => {
    setSelectedIndex((prev) => (prev < fotos.length - 1 ? prev + 1 : 0))
  }

  const seleccionarFoto = (index: number) => {
    setSelectedIndex(index)
  }

  // ============================================================
  // SUBIR FOTO
  // ============================================================

  const subirFoto = async (file: File, esPrincipal: boolean = false) => {
    setUploading(true)
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('es_principal', String(esPrincipal))
      
      await apiClient.post(
        `/api/propietario/fotos/vehiculos/${vehiculoId}`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      )
      
      toast.success('📸 Foto subida correctamente')
      await cargarFotos()
    } catch (error) {
      console.error('Error subiendo foto:', error)
      toast.error('Error al subir la foto')
    } finally {
      setUploading(false)
    }
  }

  // ============================================================
  // ELIMINAR FOTO
  // ============================================================

  const eliminarFoto = async (fotoId: string) => {
    if (!confirm('¿Estás seguro de que quieres eliminar esta foto?')) return
    
    try {
      await apiClient.delete(`/api/propietario/fotos/${fotoId}`)
      toast.success('🗑️ Foto eliminada correctamente')
      await cargarFotos()
    } catch (error) {
      console.error('Error eliminando foto:', error)
      toast.error('Error al eliminar la foto')
    }
  }

  // ============================================================
  // MARCAR COMO PRINCIPAL
  // ============================================================

  const marcarPrincipal = async (fotoId: string) => {
    try {
      await apiClient.patch(`/api/propietario/fotos/${fotoId}/principal`)
      toast.success('⭐ Foto marcada como principal')
      await cargarFotos()
    } catch (error) {
      console.error('Error marcando como principal:', error)
      toast.error('Error al marcar como principal')
    }
  }

  // ============================================================
  // RENDER - LOADING
  // ============================================================

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full min-h-[200px]">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    )
  }

  // ============================================================
  // RENDER - SIN FOTOS
  // ============================================================

  if (fotos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[200px] text-center border rounded-lg bg-gray-50/50 p-4">
        <div className="w-12 h-12 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-2">
          <ImageIcon className="h-6 w-6 text-gray-400" />
        </div>
        <p className="text-xs text-muted-foreground">Sin fotos del vehículo</p>
        
        <CldUploadWidget
          uploadPreset={process.env.NEXT_PUBLIC_CLOUDINARY_UPLOAD_PRESET || 'documentos_preset'}
          options={{
            folder: `vehiculos/${vehiculoId}`,
            resourceType: 'image',
            maxFileSize: 5000000,
            cropping: true,
            croppingAspectRatio: 1.33,
          }}
          onSuccess={(result) => {
            const info = result.info as { secure_url: string; public_id: string }
            if (info?.secure_url) {
              fetch(info.secure_url)
                .then(res => res.blob())
                .then(blob => {
                  const file = new File([blob], 'vehiculo.jpg', { type: 'image/jpeg' })
                  subirFoto(file, true)
                })
            }
          }}
        >
          {({ open }) => (
            <Button 
              size="sm" 
              variant="outline" 
              onClick={() => open()} 
              disabled={uploading}
              className="mt-2 h-7 px-3 text-xs"
            >
              {uploading ? (
                <Loader2 className="h-3 w-3 animate-spin" />
              ) : (
                <Upload className="h-3 w-3" />
              )}
              <span className="ml-1">Subir foto</span>
            </Button>
          )}
        </CldUploadWidget>
      </div>
    )
  }

  const fotoActual = fotos[selectedIndex]
  const totalFotos = fotos.length

  // ============================================================
  // RENDER - CARRUSEL
  // ============================================================

  return (
    <div ref={containerRef} className="h-full flex flex-col">
      
      {/* ============================================================
      IMAGEN PRINCIPAL - CENTRADA HORIZONTAL Y VERTICALMENTE
      ============================================================ */}
      <div 
        className="relative rounded-lg overflow-hidden bg-gray-100 flex-1 flex items-center justify-center"
        style={{ 
          minHeight: compact ? '120px' : '200px',
        }}
      >
        <img
          src={fotoActual.url}
          alt={`Foto ${selectedIndex + 1} del vehículo`}
          className="max-w-full max-h-full object-contain"
        />
        
        {fotoActual.es_principal && (
          <Badge className="absolute top-1 left-1 bg-yellow-500 text-white border-0 text-[10px] px-1.5 py-0.5">
            ⭐ Principal
          </Badge>
        )}

        {totalFotos > 1 && (
          <>
            <button
              onClick={fotoAnterior}
              className="absolute left-1 top-1/2 -translate-y-1/2 p-0.5 rounded-full bg-black/50 text-white hover:bg-black/70 transition-colors"
            >
              <ChevronLeft className="h-5 w-5" />
            </button>
            <button
              onClick={fotoSiguiente}
              className="absolute right-1 top-1/2 -translate-y-1/2 p-0.5 rounded-full bg-black/50 text-white hover:bg-black/70 transition-colors"
            >
              <ChevronRight className="h-5 w-5" />
            </button>

            {/* INDICADORES DE POSICIÓN */}
            <div className="absolute bottom-1 left-1/2 -translate-x-1/2 flex gap-1">
              {fotos.map((_, index) => (
                <button
                  key={index}
                  onClick={() => seleccionarFoto(index)}
                  className={`h-1 rounded-full transition-all ${
                    index === selectedIndex 
                      ? 'w-3 bg-white' 
                      : 'w-1 bg-white/50 hover:bg-white/70'
                  }`}
                />
              ))}
            </div>
          </>
        )}
      </div>

      {/* ============================================================
      CONTADOR DE FOTOS + ACCIONES
      ============================================================ */}
      <div className="flex justify-between items-center mt-1 flex-shrink-0">
        <span className="text-xs text-muted-foreground">
          Foto {selectedIndex + 1} de {totalFotos}
        </span>
        <div className="flex gap-1">
          <CldUploadWidget
            uploadPreset={process.env.NEXT_PUBLIC_CLOUDINARY_UPLOAD_PRESET || 'documentos_preset'}
            options={{
              folder: `vehiculos/${vehiculoId}`,
              resourceType: 'image',
              maxFileSize: 5000000,
              cropping: true,
              croppingAspectRatio: 1.33,
            }}
            onSuccess={(result) => {
              const info = result.info as { secure_url: string; public_id: string }
              if (info?.secure_url) {
                fetch(info.secure_url)
                  .then(res => res.blob())
                  .then(blob => {
                    const file = new File([blob], 'vehiculo.jpg', { type: 'image/jpeg' })
                    subirFoto(file, false)
                  })
              }
            }}
          >
            {({ open }) => (
              <Button 
                size="sm" 
                variant="ghost" 
                onClick={() => open()}
                disabled={uploading}
                className="h-6 px-2 text-xs"
              >
                {uploading ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <Plus className="h-3 w-3" />
                )}
              </Button>
            )}
          </CldUploadWidget>
          {!fotoActual.es_principal && (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => marcarPrincipal(fotoActual.id)}
              className="h-6 px-2 text-xs"
            >
              <Star className="h-3 w-3 text-yellow-500" />
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              setFotoEditando(fotoActual.id)
              setDescripcionTemp(fotoActual.descripcion || '')
              setShowDescripcion(true)
            }}
            className="h-6 px-2 text-xs"
          >
            ✏️
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => eliminarFoto(fotoActual.id)}
            className="h-6 px-2 text-xs text-red-500 hover:text-red-700 hover:bg-red-50"
          >
            <Trash2 className="h-3 w-3" />
          </Button>
        </div>
      </div>

      {/* ============================================================
      MINIATURAS - CENTRADAS
      ============================================================ */}
      {totalFotos > 1 && (
        <div className="flex justify-center mt-1 flex-shrink-0">
          <div className="flex gap-1.5 overflow-x-auto pb-1 scrollbar-thin scrollbar-thumb-gray-300 max-w-full">
            {fotos.map((foto, index) => (
              <button
                key={foto.id}
                onClick={() => seleccionarFoto(index)}
                className={`relative flex-shrink-0 rounded overflow-hidden border-2 transition-all ${
                  index === selectedIndex 
                    ? 'border-primary ring-1 ring-primary/20' 
                    : 'border-transparent hover:border-gray-300'
                }`}
                style={{ width: compact ? '40px' : '60px', height: compact ? '40px' : '60px' }}
              >
                <img
                  src={foto.url}
                  alt={`Miniatura ${index + 1}`}
                  className="w-full h-full object-cover"
                />
                {foto.es_principal && (
                  <div className="absolute top-0 right-0 bg-yellow-500 text-white text-[6px] px-0.5 py-0.5 rounded-bl">
                    ★
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ============================================================
      MODAL DESCRIPCIÓN
      ============================================================ */}
      {showDescripcion && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-semibold">Editar descripción</h3>
              <button
                onClick={() => setShowDescripcion(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <Label className="text-sm">Descripción</Label>
                <Input
                  value={descripcionTemp}
                  onChange={(e) => setDescripcionTemp(e.target.value)}
                  placeholder="Ej: Foto frontal, Daño en paragolpes, etc."
                  className="mt-1"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  className="flex-1"
                  onClick={async () => {
                    try {
                      await apiClient.patch(
                        `/api/propietario/fotos/${fotoEditando}/descripcion`,
                        { descripcion: descripcionTemp }
                      )
                      toast.success('Descripción actualizada')
                      await cargarFotos()
                      setShowDescripcion(false)
                    } catch (error) {
                      toast.error('Error al actualizar la descripción')
                    }
                  }}
                >
                  Guardar
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setShowDescripcion(false)}
                >
                  Cancelar
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}