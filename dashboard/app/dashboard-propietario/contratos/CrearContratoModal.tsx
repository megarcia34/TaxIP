'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { useAuth } from '@/hooks/useAuth'
import { useSearchParams } from 'next/navigation'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Loader2 } from 'lucide-react'
import { toast } from 'sonner'

interface Vehiculo {
  id: string
  patente: string
  marca: string
  modelo: string
}

interface Chofer {
  id: string
  email: string
  nombre: string
  apellido: string
  telefono: string
  calificacion_promedio: number
  total_calificaciones: number
}

interface CrearContratoModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
}

export default function CrearContratoModal({
  open,
  onOpenChange,
  onSuccess,
}: CrearContratoModalProps) {
  const { user } = useAuth()
  const searchParams = useSearchParams()
  const isAdmin = user?.rol === 'admin'
  const propietarioId = searchParams?.get('propietario_id')

  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([])
  const [choferes, setChoferes] = useState<Chofer[]>([])
  const [loading, setLoading] = useState(false)
  const [loadingForm, setLoadingForm] = useState(false)

  const [formData, setFormData] = useState({
    vehiculo_id: '',
    chofer_id: '',
    tipo_contrato: 'PORCENTAJE',
    turno_asignado: 'DIURNO',
    porcentaje_chofer: 50,
    monto_diario: 0,
  })

  // Cargar vehículos y choferes
  useEffect(() => {
    if (open) {
      cargarDatos()
    }
  }, [open])

  const cargarDatos = async () => {
    setLoading(true)
    try {
      // 1. Cargar vehículos
      const vehiculosRes = await apiClient.get('/api/propietario/vehiculos')
      setVehiculos(vehiculosRes.data || [])

      // 2. Cargar choferes disponibles
      const choferesRes = await apiClient.get(
        `/api/propietario/choferes/disponibles?turno=${formData.turno_asignado}`
      )
      setChoferes(choferesRes.data || [])
    } catch (error) {
      console.error('Error cargando datos:', error)
      toast.error('Error al cargar datos para el contrato')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoadingForm(true)

    try {
      const payload = {
        vehiculo_id: formData.vehiculo_id,
        chofer_id: formData.chofer_id,
        tipo_contrato: formData.tipo_contrato,
        turno_asignado: formData.turno_asignado,
        porcentaje_chofer: formData.tipo_contrato === 'PORCENTAJE' ? formData.porcentaje_chofer : null,
        monto_diario: formData.tipo_contrato === 'CANON_FIJO' ? formData.monto_diario : null,
      }

      await apiClient.post('/api/propietario/contratos', payload)
      
      toast.success('Contrato creado correctamente')
      onSuccess()
      onOpenChange(false)
      setFormData({
        vehiculo_id: '',
        chofer_id: '',
        tipo_contrato: 'PORCENTAJE',
        turno_asignado: 'DIURNO',
        porcentaje_chofer: 50,
        monto_diario: 0,
      })
    } catch (error: any) {
      console.error('Error creando contrato:', error)
      toast.error(error.response?.data?.detail || 'Error al crear el contrato')
    } finally {
      setLoadingForm(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Nuevo Contrato</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Vehículo</Label>
              <Select
                value={formData.vehiculo_id}
                onValueChange={(v) => setFormData({ ...formData, vehiculo_id: v })}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar vehículo" />
                </SelectTrigger>
                <SelectContent>
                  {vehiculos.map((v) => (
                    <SelectItem key={v.id} value={v.id}>
                      {v.patente} - {v.marca} {v.modelo}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Chofer</Label>
              <Select
                value={formData.chofer_id}
                onValueChange={(v) => setFormData({ ...formData, chofer_id: v })}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar chofer" />
                </SelectTrigger>
                <SelectContent>
                  {choferes.map((c) => (
                    <SelectItem key={c.id} value={c.id}>
                      {c.nombre} {c.apellido} ({c.email})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Tipo de Contrato</Label>
                <Select
                  value={formData.tipo_contrato}
                  onValueChange={(v) => setFormData({ ...formData, tipo_contrato: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="AUTO_GESTION">Auto-gestión</SelectItem>
                    <SelectItem value="PORCENTAJE">A porcentaje</SelectItem>
                    <SelectItem value="CANON_FIJO">Canon fijo</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Turno</Label>
                <Select
                  value={formData.turno_asignado}
                  onValueChange={(v) => setFormData({ ...formData, turno_asignado: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="DIURNO">Diurno</SelectItem>
                    <SelectItem value="NOCTURNO">Nocturno</SelectItem>
                    <SelectItem value="COMPLETO">Completo</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {formData.tipo_contrato === 'PORCENTAJE' && (
              <div className="space-y-2">
                <Label>Porcentaje del Chofer (%)</Label>
                <Input
                  type="number"
                  min="0"
                  max="100"
                  value={formData.porcentaje_chofer}
                  onChange={(e) =>
                    setFormData({ ...formData, porcentaje_chofer: Number(e.target.value) })
                  }
                  required
                />
              </div>
            )}

            {formData.tipo_contrato === 'CANON_FIJO' && (
              <div className="space-y-2">
                <Label>Monto Diario ($)</Label>
                <Input
                  type="number"
                  min="0"
                  value={formData.monto_diario}
                  onChange={(e) =>
                    setFormData({ ...formData, monto_diario: Number(e.target.value) })
                  }
                  required
                />
              </div>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={loadingForm}>
              {loadingForm && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Crear Contrato
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}