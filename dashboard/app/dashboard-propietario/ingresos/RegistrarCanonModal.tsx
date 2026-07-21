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

interface Contrato {
  id: string
  patente: string
  monto_diario: number
}

interface RegistrarCanonModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
}

export default function RegistrarCanonModal({
  open,
  onOpenChange,
  onSuccess,
}: RegistrarCanonModalProps) {
  const { user } = useAuth()
  const searchParams = useSearchParams()
  const isAdmin = user?.rol === 'admin'
  const propietarioId = searchParams?.get('propietario_id')

  const [contratos, setContratos] = useState<Contrato[]>([])
  const [loading, setLoading] = useState(false)
  const [loadingForm, setLoadingForm] = useState(false)

  const [formData, setFormData] = useState({
    contrato_id: '',
    monto: 0,
    fecha_pago: new Date().toISOString().split('T')[0],
  })

  useEffect(() => {
    if (open) {
      cargarContratos()
    }
  }, [open])

  const cargarContratos = async () => {
    setLoading(true)
    try {
      const res = await apiClient.get('/api/propietario/contratos?activo=true')
      setContratos(res.data || [])
    } catch (error) {
      console.error('Error cargando contratos:', error)
      toast.error('Error al cargar contratos')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoadingForm(true)

    try {
      await apiClient.post('/api/propietario/ingresos/canon/pagar', formData)
      
      toast.success('Pago de canon registrado correctamente')
      onSuccess()
      onOpenChange(false)
      setFormData({
        contrato_id: '',
        monto: 0,
        fecha_pago: new Date().toISOString().split('T')[0],
      })
    } catch (error: any) {
      console.error('Error registrando canon:', error)
      toast.error(error.response?.data?.detail || 'Error al registrar pago de canon')
    } finally {
      setLoadingForm(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Registrar Pago de Canon</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Contrato</Label>
              <Select
                value={formData.contrato_id}
                onValueChange={(v) => {
                  const contrato = contratos.find(c => c.id === v)
                  setFormData({
                    ...formData,
                    contrato_id: v,
                    monto: contrato?.monto_diario || 0,
                  })
                }}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar contrato" />
                </SelectTrigger>
                <SelectContent>
                  {contratos.map((c) => (
                    <SelectItem key={c.id} value={c.id}>
                      {c.patente} - ${c.monto_diario}/día
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
              <Label>Fecha de Pago</Label>
              <Input
                type="date"
                value={formData.fecha_pago}
                onChange={(e) =>
                  setFormData({ ...formData, fecha_pago: e.target.value })
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