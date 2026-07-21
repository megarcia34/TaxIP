'use client'

import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { toast } from 'sonner'
import { Loader2 } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Contrato {
  id: string
  patente: string
  monto_diario: number
  chofer_nombre: string
  chofer_apellido: string | null
}

interface Props {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

export default function RegistrarCanonModal({ open, onClose, onSuccess }: Props) {
  const [loading, setLoading] = useState(false)
  const [contratos, setContratos] = useState<Contrato[]>([])
  const [contratoId, setContratoId] = useState('')
  const [monto, setMonto] = useState('')
  const [fechaPago, setFechaPago] = useState(new Date().toISOString().split('T')[0])

  const cargarContratos = async () => {
    const token = localStorage.getItem('prop_token')
    if (!token) return

    try {
      const res = await fetch(`${API_URL}/api/propietario/contratos?activo=true`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        const contratosCanon = data.filter((c: any) => c.tipo_contrato === 'CANON_FIJO' && c.activo === true)
        setContratos(contratosCanon)
      }
    } catch (error) {
      console.error('Error cargando contratos:', error)
    }
  }

  useEffect(() => {
    if (open) {
      cargarContratos()
      setContratoId('')
      setMonto('')
    }
  }, [open])

  const contratoSeleccionado = contratos.find(c => c.id === contratoId)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!contratoId) {
      toast.error('Selecciona un contrato')
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
      const res = await fetch(`${API_URL}/api/propietario/ingresos/canon/pagar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          contrato_id: contratoId,
          fecha_pago: fechaPago,
          monto: parseFloat(monto)
        })
      })

      if (res.ok) {
        toast.success('Pago de canon registrado correctamente')
        setContratoId('')
        setMonto('')
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
    setContratoId('')
    setMonto('')
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Registrar pago de canon</DialogTitle>
          <DialogDescription>
            Registra el pago del canon diario recibido de un chofer
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Contrato (canon fijo) *</Label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={contratoId}
              onChange={(e) => {
                const id = e.target.value
                setContratoId(id)
                const contrato = contratos.find(c => c.id === id)
                if (contrato) {
                  setMonto(contrato.monto_diario.toString())
                }
              }}
              required
            >
              <option value="">Seleccionar contrato</option>
              {contratos.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.patente} - {c.chofer_nombre} {c.chofer_apellido || ''} (${c.monto_diario}/día)
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <Label>Monto pagado ($) *</Label>
            <Input
              type="number"
              min="0"
              step="100"
              placeholder="Monto del canon"
              value={monto}
              onChange={(e) => setMonto(e.target.value)}
              required
            />
            {contratoSeleccionado && (
              <p className="text-xs text-muted-foreground">
                Canon diario establecido: ${contratoSeleccionado.monto_diario}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label>Fecha de pago *</Label>
            <Input
              type="date"
              value={fechaPago}
              onChange={(e) => setFechaPago(e.target.value)}
              required
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              Registrar pago
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}