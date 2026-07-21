'use client'

import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { toast } from 'sonner'
import { Loader2 } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Vehiculo {
  id: string
  patente: string
  marca: string
  modelo: string
  chofer_asignado: string | null
}

interface ChoferDisponible {
  id: string
  email: string
  nombre: string | null
  apellido: string | null
  telefono: string | null
  calificacion_promedio: number | null
}

interface Props {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

const TIPOS_CONTRATO = [
  { value: 'AUTO_GESTION', label: 'Auto-gestionado (dueño maneja)' },
  { value: 'PORCENTAJE', label: 'Chofer a porcentaje' },
  { value: 'CANON_FIJO', label: 'Alquiler fijo (canon diario)' },
]

const TURNOS = [
  { value: 'DIURNO', label: 'Diurno' },
  { value: 'NOCTURNO', label: 'Nocturno' },
  { value: 'COMPLETO', label: 'Completo' },
]

export default function CrearContratoModal({ open, onClose, onSuccess }: Props) {
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([])
  const [choferesDisponibles, setChoferesDisponibles] = useState<ChoferDisponible[]>([])
  const [loading, setLoading] = useState(false)
  const [cargandoChoferes, setCargandoChoferes] = useState(false)

  const [formData, setFormData] = useState({
    vehiculo_id: '',
    chofer_id: '',
    tipo_contrato: 'PORCENTAJE',
    turno_asignado: 'COMPLETO',
    porcentaje_chofer: '',
    monto_diario: '',
  })

  // Cargar vehículos del propietario
  useEffect(() => {
    if (!open) return

    const cargarVehiculos = async () => {
      const token = localStorage.getItem('prop_token')
      if (!token) return
      
      try {
        const res = await fetch(`${API_URL}/api/propietario/vehiculos`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          setVehiculos(data)
        }
      } catch (error) {
        console.error('Error cargando vehículos:', error)
      }
    }
    cargarVehiculos()
  }, [open])

  // Cargar choferes disponibles cuando cambia el turno
  useEffect(() => {
    if (!formData.turno_asignado) return

    const cargarChoferes = async () => {
      setCargandoChoferes(true)
      const token = localStorage.getItem('prop_token')
      if (!token) return
      
      try {
        const res = await fetch(`${API_URL}/api/propietario/choferes/disponibles?turno=${formData.turno_asignado}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          setChoferesDisponibles(data)
        }
      } catch (error) {
        console.error('Error cargando choferes:', error)
      } finally {
        setCargandoChoferes(false)
      }
    }
    cargarChoferes()
  }, [formData.turno_asignado, open])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    const payload: any = {
      vehiculo_id: formData.vehiculo_id,
      chofer_id: formData.chofer_id,
      tipo_contrato: formData.tipo_contrato,
      turno_asignado: formData.turno_asignado,
    }

    if (formData.tipo_contrato === 'PORCENTAJE') {
      payload.porcentaje_chofer = parseFloat(formData.porcentaje_chofer)
    }
    if (formData.tipo_contrato === 'CANON_FIJO') {
      payload.monto_diario = parseFloat(formData.monto_diario)
    }

    const token = localStorage.getItem('prop_token')
    try {
      const res = await fetch(`${API_URL}/api/propietario/contratos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      })

      if (res.ok) {
        toast.success('Contrato creado exitosamente')
        onSuccess()
      } else {
        const error = await res.json()
        toast.error(error.detail || 'Error al crear contrato')
      }
    } catch (error) {
      toast.error('Error de conexión')
    } finally {
      setLoading(false)
    }
  }

  const vehiculoSeleccionado = vehiculos.find(v => v.id === formData.vehiculo_id)
  const mostrarAlertaChofer = vehiculoSeleccionado?.chofer_asignado && formData.tipo_contrato !== 'AUTO_GESTION'

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Nuevo contrato</DialogTitle>
          <DialogDescription>
            Selecciona el vehículo, tipo de contrato y chofer
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Vehículo */}
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

          {/* Tipo de contrato */}
          <div className="space-y-2">
            <Label>Tipo de contrato</Label>
            <Select
              value={formData.tipo_contrato}
              onValueChange={(v) => setFormData({ ...formData, tipo_contrato: v, porcentaje_chofer: '', monto_diario: '' })}
              required
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar tipo" />
              </SelectTrigger>
              <SelectContent>
                {TIPOS_CONTRATO.map((t) => (
                  <SelectItem key={t.value} value={t.value}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Turno */}
          <div className="space-y-2">
            <Label>Turno</Label>
            <Select
              value={formData.turno_asignado}
              onValueChange={(v) => setFormData({ ...formData, turno_asignado: v })}
              required
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar turno" />
              </SelectTrigger>
              <SelectContent>
                {TURNOS.map((t) => (
                  <SelectItem key={t.value} value={t.value}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Campos específicos según tipo */}
          {formData.tipo_contrato === 'PORCENTAJE' && (
            <div className="space-y-2">
              <Label>Porcentaje del chofer (%)</Label>
              <Input
                type="number"
                min="0"
                max="100"
                step="1"
                placeholder="Ej: 40"
                value={formData.porcentaje_chofer}
                onChange={(e) => setFormData({ ...formData, porcentaje_chofer: e.target.value })}
                required
              />
              <p className="text-xs text-muted-foreground">
                El dueño recibe el {100 - (parseFloat(formData.porcentaje_chofer) || 0)}%
              </p>
            </div>
          )}

          {formData.tipo_contrato === 'CANON_FIJO' && (
            <div className="space-y-2">
              <Label>Monto diario ($)</Label>
              <Input
                type="number"
                min="0"
                step="1000"
                placeholder="Ej: 15000"
                value={formData.monto_diario}
                onChange={(e) => setFormData({ ...formData, monto_diario: e.target.value })}
                required
              />
              <p className="text-xs text-muted-foreground">
                El chofer paga este monto diario, el excedente es su ganancia
              </p>
            </div>
          )}

          {formData.tipo_contrato === 'AUTO_GESTION' && (
            <div className="p-3 bg-blue-50 rounded-md text-sm text-blue-700">
              ℹ️ En modalidad auto-gestionado, el dueño conduce su propio vehículo.
              El chofer asignado será el mismo propietario.
            </div>
          )}

          {/* Chofer (solo si no es auto-gestión) */}
          {formData.tipo_contrato !== 'AUTO_GESTION' && (
            <div className="space-y-2">
              <Label>Chofer</Label>
              {cargandoChoferes ? (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Buscando choferes disponibles...
                </div>
              ) : (
                <Select
                  value={formData.chofer_id}
                  onValueChange={(v) => setFormData({ ...formData, chofer_id: v })}
                  required
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar chofer" />
                  </SelectTrigger>
                  <SelectContent>
                    {choferesDisponibles.map((c) => (
                      <SelectItem key={c.id} value={c.id}>
                        {c.nombre} {c.apellido} - {c.email} {c.calificacion_promedio && `⭐ ${c.calificacion_promedio}`}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
              {mostrarAlertaChofer && (
                <p className="text-xs text-amber-600">
                  ⚠️ Este vehículo ya tiene un chofer asignado. Al crear este contrato, se reasignará.
                </p>
              )}
            </div>
          )}

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              Crear contrato
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}