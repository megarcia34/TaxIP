'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Loader2 } from 'lucide-react'
import { useNeumaticos } from '@/hooks/useNeumaticos'
import { toast } from 'sonner'
import { PopupDocumentacion } from './PopupDocumentacion'

interface NeumaticoForm {
  marca: string
  modelo_dibujo: string
  medida: string
  tipo_neumatico: string
  posicion: string
  observaciones: string
}

const TIPOS_NEUMATICO = ['RADIAL', 'BIAS', 'TUBELESS', 'RUN_FLAT', 'TODO_TERRENO']
const POSICIONES = ['DI', 'DD', 'TI', 'TD']
const POSICIONES_LABELS: Record<string, string> = {
  DI: 'Delantero Izquierdo',
  DD: 'Delantero Derecho',
  TI: 'Trasero Izquierdo',
  TD: 'Trasero Derecho',
}

interface MontarNeumaticosModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  vehiculoId: string
  onSuccess: () => void
  activos?: any  // ← NUEVO: prop para obtener la patente
}

export function MontarNeumaticosModal({ 
  open, 
  onOpenChange, 
  vehiculoId, 
  onSuccess,
  activos  // ← NUEVO: recibir activos
}: MontarNeumaticosModalProps) {
  const { montar } = useNeumaticos()
  const [loading, setLoading] = useState(false)
  const [kmVehiculo, setKmVehiculo] = useState<number>(0)
  const [neumaticos, setNeumaticos] = useState<NeumaticoForm[]>([
    { marca: '', modelo_dibujo: '', medida: '', tipo_neumatico: 'RADIAL', posicion: 'DI', observaciones: '' },
    { marca: '', modelo_dibujo: '', medida: '', tipo_neumatico: 'RADIAL', posicion: 'DD', observaciones: '' },
    { marca: '', modelo_dibujo: '', medida: '', tipo_neumatico: 'RADIAL', posicion: 'TI', observaciones: '' },
    { marca: '', modelo_dibujo: '', medida: '', tipo_neumatico: 'RADIAL', posicion: 'TD', observaciones: '' },
  ])
  const [mostrarPopupDoc, setMostrarPopupDoc] = useState(false)

  const updateNeumatico = (index: number, field: keyof NeumaticoForm, value: string | number) => {
    const nuevos = [...neumaticos]
    nuevos[index] = { ...nuevos[index], [field]: value as string }
    setNeumaticos(nuevos)
  }

  const handleSubmit = async () => {
    const incompletos = neumaticos.some(n => !n.marca || !n.medida)
    if (incompletos) {
      toast.error('Completa todos los campos (Marca, Modelo, Medida y Posición)')
      return
    }

    if (kmVehiculo <= 0) {
      toast.error('Ingresa el kilometraje actual del vehículo')
      return
    }

    setLoading(true)
    try {
      const payload = {
        neumaticos: neumaticos.map(n => ({
          marca: n.marca,
          modelo_dibujo: n.modelo_dibujo || undefined,
          medida: n.medida,
          tipo_neumatico: n.tipo_neumatico,
          posicion: n.posicion as 'DI' | 'DD' | 'TI' | 'TD',
          observaciones: n.observaciones || undefined,
        })),
        km_vehiculo_actual: kmVehiculo,
        observaciones_generales: 'Montaje inicial de neumáticos'
      }

      await montar(vehiculoId, payload)
      onSuccess()
      onOpenChange(false)
      
      setMostrarPopupDoc(true)
      
    } catch (error) {
      // Error ya manejado en el hook
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setNeumaticos([
      { marca: '', modelo_dibujo: '', medida: '', tipo_neumatico: 'RADIAL', posicion: 'DI', observaciones: '' },
      { marca: '', modelo_dibujo: '', medida: '', tipo_neumatico: 'RADIAL', posicion: 'DD', observaciones: '' },
      { marca: '', modelo_dibujo: '', medida: '', tipo_neumatico: 'RADIAL', posicion: 'TI', observaciones: '' },
      { marca: '', modelo_dibujo: '', medida: '', tipo_neumatico: 'RADIAL', posicion: 'TD', observaciones: '' },
    ])
    setKmVehiculo(0)
  }

  return (
    <>
      <Dialog open={open} onOpenChange={(val) => {
        if (!val) resetForm()
        onOpenChange(val)
      }}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Montar Neumáticos</DialogTitle>
            <DialogDescription>
              Registra los 4 neumáticos principales del vehículo para completar el registro.
              <br />
              <span className="text-yellow-600 font-medium">⚠️ Este paso es obligatorio.</span>
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Kilometraje */}
            <div className="space-y-1">
              <Label htmlFor="km">Kilometraje actual del vehículo *</Label>
              <Input
                id="km"
                type="number"
                placeholder="Ej: 15000"
                value={kmVehiculo || ''}
                onChange={(e) => setKmVehiculo(Number(e.target.value))}
                className="max-w-xs"
              />
            </div>

            {/* Neumáticos */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {neumaticos.map((n, index) => (
                <div key={index} className="border rounded-lg p-3 space-y-2 bg-muted/20">
                  <div className="flex justify-between items-center">
                    <Label className="text-sm font-medium">
                      {POSICIONES_LABELS[n.posicion]}
                    </Label>
                    <span className="text-xs text-muted-foreground">
                      {index + 1}/4
                    </span>
                  </div>

                  <div className="space-y-1.5">
                    <div>
                      <Label className="text-xs">Marca *</Label>
                      <Input
                        className="text-sm h-8"
                        placeholder="Ej: Michelin"
                        value={n.marca}
                        onChange={(e) => updateNeumatico(index, 'marca', e.target.value)}
                      />
                    </div>

                    <div>
                      <Label className="text-xs">Modelo / Dibujo</Label>
                      <Input
                        className="text-sm h-8"
                        placeholder="Ej: Pilot Sport 4"
                        value={n.modelo_dibujo}
                        onChange={(e) => updateNeumatico(index, 'modelo_dibujo', e.target.value)}
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <Label className="text-xs">Medida *</Label>
                        <Input
                          className="text-sm h-8"
                          placeholder="Ej: 205/55R16"
                          value={n.medida}
                          onChange={(e) => updateNeumatico(index, 'medida', e.target.value)}
                        />
                      </div>
                      <div>
                        <Label className="text-xs">Tipo</Label>
                        <Select
                          value={n.tipo_neumatico}
                          onValueChange={(val) => updateNeumatico(index, 'tipo_neumatico', val)}
                        >
                          <SelectTrigger className="h-8 text-sm">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {TIPOS_NEUMATICO.map(t => (
                              <SelectItem key={t} value={t}>{t}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div>
                      <Label className="text-xs">Observaciones</Label>
                      <Input
                        className="text-sm h-8"
                        placeholder="Opcional"
                        value={n.observaciones}
                        onChange={(e) => updateNeumatico(index, 'observaciones', e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Botones */}
            <div className="flex justify-end gap-2 pt-2 border-t">
              <Button variant="outline" onClick={() => onOpenChange(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSubmit} disabled={loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Guardar Neumáticos
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Popup de documentación - usando activos recibido como prop */}
      <PopupDocumentacion
        open={mostrarPopupDoc}
        onOpenChange={setMostrarPopupDoc}
        vehiculoId={vehiculoId}
        patente={activos?.patente || ''}
      />
    </>
  )
}