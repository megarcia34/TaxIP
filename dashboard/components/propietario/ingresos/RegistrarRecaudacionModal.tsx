'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { toast } from 'sonner'
import { Loader2 } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Vehiculo {
  id: string
  patente: string
  marca: string
  modelo: string
}

interface Props {
  open: boolean
  onClose: () => void
  onSuccess: () => void
  vehiculos: Vehiculo[]
}

export default function RegistrarRecaudacionModal({ open, onClose, onSuccess, vehiculos }: Props) {
  const [loading, setLoading] = useState(false)
  const [vehiculoId, setVehiculoId] = useState('')
  const [monto, setMonto] = useState('')
  const [fecha, setFecha] = useState(new Date().toISOString().split('T')[0])
  const [descripcion, setDescripcion] = useState('')

  console.log('RegistrarRecaudacionModal - vehiculos recibidos:', vehiculos)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!vehiculoId) {
      toast.error('Selecciona un vehículo')
      return
    }
    
    if (!monto || parseFloat(monto) <= 0) {
      toast.error('Ingresa un monto válido')
      return
    }
    
    setLoading(true)

    const token = localStorage.getItem('prop_token')
    if (!token) {
      toast.error('No hay sesión activa')
      setLoading(false)
      return
    }

    try {
      const res = await fetch(`${API_URL}/api/propietario/ingresos/recaudacion-manual`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          vehiculo_id: vehiculoId,
          monto: parseFloat(monto),
          fecha: fecha,
          descripcion: descripcion || undefined
        })
      })

      if (res.ok) {
        toast.success('Recaudación manual registrada correctamente')
        setVehiculoId('')
        setMonto('')
        setDescripcion('')
        setFecha(new Date().toISOString().split('T')[0])
        onSuccess()
      } else {
        const error = await res.json()
        toast.error(error.detail || 'Error al registrar')
      }
    } catch (error) {
      console.error('Error:', error)
      toast.error('Error de conexión')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setVehiculoId('')
    setMonto('')
    setDescripcion('')
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Declarar recaudación en efectivo</DialogTitle>
          <DialogDescription>
            Registra recaudación manual realizada fuera de la plataforma
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Vehículo *</Label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={vehiculoId}
              onChange={(e) => setVehiculoId(e.target.value)}
              required
            >
              <option value="">Seleccionar vehículo</option>
              {vehiculos.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.patente} - {v.marca} {v.modelo}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <Label>Monto ($) *</Label>
            <Input
              type="number"
              min="0"
              step="100"
              placeholder="Ej: 25000"
              value={monto}
              onChange={(e) => setMonto(e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label>Fecha *</Label>
            <Input
              type="date"
              value={fecha}
              onChange={(e) => setFecha(e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label>Descripción (opcional)</Label>
            <Textarea
              placeholder="Ej: Viaje a la costa, recaudación del día..."
              value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)}
              rows={2}
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              Registrar
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}