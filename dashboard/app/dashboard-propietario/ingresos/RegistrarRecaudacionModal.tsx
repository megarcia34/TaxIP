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

interface RegistrarRecaudacionModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
}

export default function RegistrarRecaudacionModal({
  open,
  onOpenChange,
  onSuccess,
}: RegistrarRecaudacionModalProps) {
  const { user } = useAuth()
  const searchParams = useSearchParams()
  const isAdmin = user?.rol === 'admin'
  const propietarioId = searchParams?.get('propietario_id')

  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([])
  const [loading, setLoading] = useState(false)
  const [loadingForm, setLoadingForm] = useState(false)

  const [formData, setFormData] = useState({
    vehiculo_id: '',
    monto: 0,
    descripcion: '',
    fecha: new Date().toISOString().split('T')[0],
  })

  useEffect(() => {
    if (open) {
      cargarVehiculos()
    }
  }, [open])

  const cargarVehiculos = async () => {
    setLoading(true)
    try {
      const res = await apiClient.get('/api/propietario/vehiculos')
      setVehiculos(res.data || [])
    } catch (error) {
      console.error('Error cargando vehículos:', error)
      toast.error('Error al cargar vehículos')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoadingForm(true)

    try {
      await apiClient.post('/api/propietario/ingresos/recaudacion-manual', formData)
      
      toast.success('Recaudación registrada correctamente')
      onSuccess()
      onOpenChange(false)
      setFormData({
        vehiculo_id: '',
        monto: 0,
        descripcion: '',
        fecha: new Date().toISOString().split('T')[0],
      })
    } catch (error: any) {
      console.error('Error registrando recaudación:', error)
      toast.error(error.response?.data?.detail || 'Error al registrar recaudación')
    } finally {
      setLoadingForm(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Registrar Recaudación Manual</DialogTitle>
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
              <Label>Monto ($)</Label>
              <Input
                type="number"
                min="0"
                step="0.01"
                value={formData.monto}
                onChange={(e) =>
                  setFormData({ ...formData, monto: Number(e.target.value) })
                }
                required
              />
            </div>

            <div className="space-y-2">
              <Label>Descripción</Label>
              <Input
                value={formData.descripcion}
                onChange={(e) =>
                  setFormData({ ...formData, descripcion: e.target.value })
                }
                placeholder="Descripción de la recaudación..."
              />
            </div>

            <div className="space-y-2">
              <Label>Fecha</Label>
              <Input
                type="date"
                value={formData.fecha}
                onChange={(e) =>
                  setFormData({ ...formData, fecha: e.target.value })
                }
                required
              />
            </div>
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
              Registrar
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}