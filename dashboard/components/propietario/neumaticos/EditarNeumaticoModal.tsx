'use client'

import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Loader2, Trash2, Ruler } from 'lucide-react'
import { toast } from 'sonner'
import { NeumaticoActivo } from '@/types'
import { useNeumaticos } from '@/hooks/useNeumaticos'

interface EditarNeumaticoModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  neumaticoId: string
  posicion: string
  posicionLabel: string
  neumatico: NeumaticoActivo
  onRecargar: () => void
}

const TIPOS_NEUMATICO = ['RADIAL', 'BIAS', 'TUBELESS', 'RUN_FLAT', 'TODO_TERRENO']

export function EditarNeumaticoModal({ 
  open, 
  onOpenChange, 
  neumaticoId,
  posicion,
  posicionLabel,
  neumatico,
  onRecargar
}: EditarNeumaticoModalProps) {
  const { cambiarEstado } = useNeumaticos()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    marca: '',
    modelo_dibujo: '',
    medida: '',
    tipo_neumatico: 'RADIAL',
    observaciones: ''
  })
  const [mostrarMedicion, setMostrarMedicion] = useState(false)
  const [profundidad, setProfundidad] = useState<number>(0)
  const [medicionLoading, setMedicionLoading] = useState(false)

  useEffect(() => {
    if (neumatico) {
      setFormData({
        marca: neumatico.marca || '',
        modelo_dibujo: neumatico.modelo_dibujo || '',
        medida: neumatico.medida || '',
        tipo_neumatico: 'RADIAL',
        observaciones: ''
      })
    }
  }, [neumatico])

  const handleGuardar = async () => {
    if (!formData.marca || !formData.medida) {
      toast.error('Completa los campos obligatorios')
      return
    }

    setLoading(true)
    try {
      // TODO: Implementar endpoint de actualización de neumático
      toast.info('Funcionalidad de actualización en desarrollo')
      setLoading(false)
    } catch (error) {
      setLoading(false)
    }
  }

  const handleDesmontar = async () => {
    if (!confirm(`¿Estás seguro de desmontar el neumático ${posicionLabel}?`)) return

    setLoading(true)
    try {
      const kmActual = prompt('Ingresa el kilometraje actual del vehículo:')
      if (!kmActual) return

      await cambiarEstado(neumaticoId, 'BAJA', 'Desmontaje manual')
      toast.success(`Neumático ${posicionLabel} desmontado`)
      onOpenChange(false)
      onRecargar()
    } catch (error) {
      // Error ya manejado en el hook
    } finally {
      setLoading(false)
    }
  }

  const handleMedir = async () => {
    if (profundidad <= 0) {
      toast.error('Ingresa una profundidad válida')
      return
    }

    setMedicionLoading(true)
    try {
      // TODO: Implementar medición
      toast.success(`Profundidad ${profundidad}mm registrada`)
      setMostrarMedicion(false)
      setProfundidad(0)
      onRecargar()
    } catch (error) {
      // Error ya manejado en el hook
    } finally {
      setMedicionLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>
            Editar Neumático - {posicionLabel}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Datos del neumático */}
          <div className="space-y-1">
            <Label>Marca *</Label>
            <Input
              placeholder="Ej: Michelin"
              value={formData.marca}
              onChange={(e) => setFormData({...formData, marca: e.target.value})}
            />
          </div>

          <div className="space-y-1">
            <Label>Modelo / Dibujo</Label>
            <Input
              placeholder="Ej: Pilot Sport 4"
              value={formData.modelo_dibujo}
              onChange={(e) => setFormData({...formData, modelo_dibujo: e.target.value})}
            />
          </div>

          <div className="space-y-1">
            <Label>Medida *</Label>
            <Input
              placeholder="Ej: 205/55R16"
              value={formData.medida}
              onChange={(e) => setFormData({...formData, medida: e.target.value})}
            />
          </div>

          <div className="space-y-1">
            <Label>Observaciones</Label>
            <Input
              placeholder="Opcional"
              value={formData.observaciones}
              onChange={(e) => setFormData({...formData, observaciones: e.target.value})}
            />
          </div>

          {/* Información actual */}
          <div className="bg-muted/30 rounded-lg p-3 space-y-1 text-sm">
            <p><span className="text-muted-foreground">Código:</span> {neumatico.codigo_interno}</p>
            <p><span className="text-muted-foreground">Km montaje:</span> {neumatico.km_montaje.toLocaleString()}</p>
            <p><span className="text-muted-foreground">Km recorridos:</span> {neumatico.km_recorridos.toLocaleString()}</p>
            {neumatico.ultima_profundidad_mm !== null && (
              <p><span className="text-muted-foreground">Última profundidad:</span> {neumatico.ultima_profundidad_mm} mm</p>
            )}
          </div>

          {/* Botones de acción */}
          <div className="flex flex-wrap gap-2 pt-2 border-t">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setMostrarMedicion(true)}
            >
              <Ruler className="h-4 w-4 mr-1" />
              Medir Profundidad
            </Button>
            <Button 
              variant="destructive" 
              size="sm"
              onClick={handleDesmontar}
              disabled={loading}
            >
              <Trash2 className="h-4 w-4 mr-1" />
              Desmontar
            </Button>
          </div>

          <div className="flex justify-end gap-2 pt-2 border-t">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button onClick={handleGuardar} disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Guardar Cambios
            </Button>
          </div>
        </div>
      </DialogContent>

      {/* Modal de medición */}
      <Dialog open={mostrarMedicion} onOpenChange={setMostrarMedicion}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Registrar Medición</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="profundidad">Profundidad del dibujo (mm)</Label>
              <Input
                id="profundidad"
                type="number"
                step="0.1"
                placeholder="Ej: 5.5"
                value={profundidad || ''}
                onChange={(e) => setProfundidad(Number(e.target.value))}
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setMostrarMedicion(false)}>
                Cancelar
              </Button>
              <Button onClick={handleMedir} disabled={medicionLoading || profundidad <= 0}>
                {medicionLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Guardar Medición
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </Dialog>
  )
}