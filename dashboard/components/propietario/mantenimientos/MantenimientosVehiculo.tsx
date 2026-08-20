'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Loader2, RefreshCw, Wrench, Plus, Eye, Trash2, Calendar, DollarSign, MapPin } from 'lucide-react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { toast } from 'sonner'
import { useMantenimientos, TIPOS_MANTENIMIENTO } from '@/hooks/useMantenimientos'

interface MantenimientosVehiculoProps {
  vehiculoId: string
}

export function MantenimientosVehiculo({ vehiculoId }: MantenimientosVehiculoProps) {
  const {
    mantenimientos,
    loading,
    registrarMantenimiento,
    recargar,
    total,
    ultimo
  } = useMantenimientos(vehiculoId)

  const [modalOpen, setModalOpen] = useState(false)
  const [registrando, setRegistrando] = useState(false)
  const [formData, setFormData] = useState({
    tipo_servicio: '',
    taller_nombre: '',
    taller_direccion: '',
    costo: '',
    kilometraje: '',
    observaciones: '',
    fecha_servicio: new Date().toISOString().split('T')[0],
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.tipo_servicio || !formData.fecha_servicio) {
      toast.error('Completa todos los campos obligatorios')
      return
    }

    setRegistrando(true)
    try {
      await registrarMantenimiento({
        vehiculo_id: vehiculoId,
        tipo_servicio: formData.tipo_servicio,
        taller_nombre: formData.taller_nombre || null,
        taller_direccion: formData.taller_direccion || null,
        costo: formData.costo ? parseFloat(formData.costo) : null,
        kilometraje: formData.kilometraje ? parseInt(formData.kilometraje) : null,
        observaciones: formData.observaciones || null,
        fecha_servicio: formData.fecha_servicio,
      })
      setModalOpen(false)
      setFormData({
        tipo_servicio: '',
        taller_nombre: '',
        taller_direccion: '',
        costo: '',
        kilometraje: '',
        observaciones: '',
        fecha_servicio: new Date().toISOString().split('T')[0],
      })
    } finally {
      setRegistrando(false)
    }
  }

  const getTipoLabel = (tipo: string) => {
    const found = TIPOS_MANTENIMIENTO.find(t => t.value === tipo)
    return found?.label || tipo
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium flex items-center gap-2">
            <Wrench className="h-5 w-5" />
            Mantenimientos del Vehículo
            <span className="text-sm font-normal text-muted-foreground">
              ({total} registrados)
            </span>
            {total > 0 ? (
              <Badge className="bg-green-100 text-green-800">✅ Registrados</Badge>
            ) : (
              <Badge className="bg-yellow-100 text-yellow-800">⚠️ Sin registros</Badge>
            )}
          </h3>
          {ultimo && (
            <p className="text-xs text-muted-foreground mt-1">
              Último: {getTipoLabel(ultimo.tipo_servicio)} - {new Date(ultimo.fecha_servicio).toLocaleDateString()}
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => recargar()}>
            <RefreshCw className="h-4 w-4 mr-1" />
            Actualizar
          </Button>
          <Button size="sm" onClick={() => setModalOpen(true)}>
            <Plus className="h-4 w-4 mr-1" />
            Registrar
          </Button>
        </div>
      </div>

      {/* Lista de mantenimientos */}
      {mantenimientos.length === 0 ? (
        <Card className="border-dashed border-yellow-200 bg-yellow-50/30">
          <CardContent className="py-8 text-center">
            <Wrench className="h-12 w-12 mx-auto text-yellow-500 mb-3" />
            <p className="text-yellow-700 font-medium">No hay mantenimientos registrados</p>
            <p className="text-yellow-600 text-sm mt-1">
              Registra el primer mantenimiento para mantener el vehículo en buen estado
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {mantenimientos.map((m) => (
            <Card key={m.id} className="border-2 hover:border-primary/30 transition-colors">
              <CardContent className="pt-4 pb-3">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium text-sm">{getTipoLabel(m.tipo_servicio)}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(m.fecha_servicio).toLocaleDateString()}
                    </p>
                  </div>
                  {m.costo && (
                    <Badge variant="outline" className="font-medium">
                      ${m.costo.toLocaleString()}
                    </Badge>
                  )}
                </div>

                <div className="mt-2 space-y-1 text-xs">
                  {m.taller_nombre && (
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <MapPin className="h-3 w-3" />
                      <span>{m.taller_nombre}</span>
                    </div>
                  )}
                  {m.kilometraje && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Kilometraje:</span>
                      <span>{m.kilometraje.toLocaleString()} km</span>
                    </div>
                  )}
                  {m.observaciones && (
                    <p className="text-muted-foreground truncate text-xs">{m.observaciones}</p>
                  )}
                </div>

                <div className="flex gap-1 mt-3 pt-2 border-t">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Eye className="h-3 w-3 mr-1" />
                    Ver
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Modal registrar mantenimiento */}
      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Wrench className="h-5 w-5" />
              Registrar Mantenimiento
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label>Tipo de Servicio *</Label>
              <Select
                value={formData.tipo_servicio}
                onValueChange={(val) => setFormData({ ...formData, tipo_servicio: val })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar tipo" />
                </SelectTrigger>
                <SelectContent>
                  {TIPOS_MANTENIMIENTO.map((t) => (
                    <SelectItem key={t.value} value={t.value}>
                      {t.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Fecha *</Label>
                <Input
                  type="date"
                  required
                  value={formData.fecha_servicio}
                  onChange={(e) => setFormData({ ...formData, fecha_servicio: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Kilometraje</Label>
                <Input
                  type="number"
                  placeholder="Ej: 15000"
                  value={formData.kilometraje}
                  onChange={(e) => setFormData({ ...formData, kilometraje: e.target.value })}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Taller</Label>
              <Input
                placeholder="Nombre del taller"
                value={formData.taller_nombre}
                onChange={(e) => setFormData({ ...formData, taller_nombre: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label>Dirección del Taller</Label>
              <Input
                placeholder="Dirección"
                value={formData.taller_direccion}
                onChange={(e) => setFormData({ ...formData, taller_direccion: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label>Costo</Label>
              <Input
                type="number"
                placeholder="Ej: 15000"
                value={formData.costo}
                onChange={(e) => setFormData({ ...formData, costo: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label>Observaciones</Label>
              <Textarea
                placeholder="Detalles adicionales..."
                value={formData.observaciones}
                onChange={(e) => setFormData({ ...formData, observaciones: e.target.value })}
                rows={2}
              />
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t">
              <Button type="button" variant="outline" onClick={() => setModalOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={registrando}>
                {registrando ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Registrar Mantenimiento
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}