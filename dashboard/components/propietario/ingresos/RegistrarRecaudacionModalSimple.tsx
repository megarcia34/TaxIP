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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!vehiculoId) {
      toast.error('Selecciona un vehículo (copia el ID de abajo)')
      return
    }
    
    setLoading(true)

    const token = localStorage.getItem('prop_token')
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
        toast.success('Recaudación manual registrada')
        onSuccess()
      } else {
        const error = await res.json()
        toast.error(error.detail || 'Error')
      }
    } catch (error) {
      toast.error('Error de conexión')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Declarar recaudación</DialogTitle>
          <DialogDescription>Registra recaudación manual</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Vehículo ID *</Label>
            <Input
              placeholder="Pega el ID del vehículo"
              value={vehiculoId}
              onChange={(e) => setVehiculoId(e.target.value)}
              required
            />
            <p className="text-xs text-muted-foreground">
              IDs disponibles: {vehiculos.map(v => `${v.patente}: ${v.id}`).join(', ')}
            </p>
          </div>

          <div className="space-y-2">
            <Label>Monto ($)</Label>
            <Input
              type="number"
              value={monto}
              onChange={(e) => setMonto(e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label>Fecha</Label>
            <Input type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} required />
          </div>

          <div className="space-y-2">
            <Label>Descripción</Label>
            <Textarea value={descripcion} onChange={(e) => setDescripcion(e.target.value)} rows={2} />
          </div>

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={onClose}>Cancelar</Button>
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