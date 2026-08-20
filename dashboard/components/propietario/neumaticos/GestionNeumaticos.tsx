'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Car, Edit, Plus, Loader2, AlertTriangle, Ruler, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
// ✅ Importar desde @/lib/api/neumaticos (no desde @/types)
import { NeumaticoActivo } from '@/lib/api/neumaticos'
import { useNeumaticos } from '@/hooks/useNeumaticos'

// ✅ Definir el tipo de posición permitida
type Posicion = 'DI' | 'DD' | 'TI' | 'TD'

// ✅ Tipar POSICIONES como array de Posicion
const POSICIONES: Posicion[] = ['DI', 'DD', 'TI', 'TD']

const POSICIONES_LABELS: Record<Posicion, string> = {
  DI: 'Delantero Izquierdo',
  DD: 'Delantero Derecho',
  TI: 'Trasero Izquierdo',
  TD: 'Trasero Derecho',
}

const TIPOS_NEUMATICO = ['RADIAL', 'BIAS', 'TUBELESS', 'RUN_FLAT', 'TODO_TERRENO']

const colorMap: Record<string, string> = {
  VERDE: 'bg-green-100 text-green-800 border-green-200',
  AMARILLO: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  ROJO: 'bg-red-100 text-red-800 border-red-200',
}

// ✅ Definir el tipo para activos
type ActivosMap = {
  DI?: NeumaticoActivo | null
  DD?: NeumaticoActivo | null
  TI?: NeumaticoActivo | null
  TD?: NeumaticoActivo | null
} | null

interface GestionNeumaticosProps {
  vehiculoId: string
  activos: ActivosMap
  onRecargar: () => void
}

// ✅ Tipo para el payload de montaje
interface MontarPayload {
  neumaticos: {
    marca: string
    modelo_dibujo?: string
    medida: string
    tipo_neumatico: string
    posicion: Posicion
    observaciones?: string
  }[]
  km_vehiculo_actual: number
  observaciones_generales?: string
}

export function GestionNeumaticos({ vehiculoId, activos, onRecargar }: GestionNeumaticosProps) {
  const { montar, medir, desmontar } = useNeumaticos()
  const [modalOpen, setModalOpen] = useState(false)
  const [modalPosicion, setModalPosicion] = useState<Posicion | null>(null)
  const [modalNeumatico, setModalNeumatico] = useState<NeumaticoActivo | null>(null)
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    marca: '',
    modelo_dibujo: '',
    medida: '',
    tipo_neumatico: 'RADIAL',
    posicion: '' as Posicion | '',
    observaciones: '',
    km_vehiculo_actual: 0
  })

  // Estados para medición
  const [mostrarMedicion, setMostrarMedicion] = useState(false)
  const [profundidad, setProfundidad] = useState<number>(0)
  const [medicionLoading, setMedicionLoading] = useState(false)

  const handleAbrirModal = (posicion: Posicion, neumatico: NeumaticoActivo | null) => {
    setModalPosicion(posicion)
    setModalNeumatico(neumatico)
    
    if (neumatico) {
      setFormData({
        marca: neumatico.marca || '',
        modelo_dibujo: neumatico.modelo_dibujo || '',
        medida: neumatico.medida || '',
        tipo_neumatico: 'RADIAL',
        posicion: posicion,
        observaciones: '',
        km_vehiculo_actual: neumatico.km_montaje || 0
      })
    } else {
      setFormData({
        marca: '',
        modelo_dibujo: '',
        medida: '',
        tipo_neumatico: 'RADIAL',
        posicion: posicion,
        observaciones: '',
        km_vehiculo_actual: 0
      })
    }
    
    setModalOpen(true)
  }

  const handleGuardar = async () => {
    if (!formData.marca || !formData.medida || !formData.posicion) {
      toast.error('Completa todos los campos obligatorios')
      return
    }

    if (formData.km_vehiculo_actual <= 0) {
      toast.error('Ingresa el kilometraje actual')
      return
    }

    setLoading(true)
    try {
      if (modalNeumatico) {
        // ✅ Editar neumático existente - actualizar en backend
        toast.info('Funcionalidad de edición en desarrollo')
        setModalOpen(false)
        onRecargar()
        setLoading(false)
        return
      }

      // Montar neumático nuevo (solo para posiciones vacías)
      const payload: MontarPayload = {
        neumaticos: [{
          marca: formData.marca,
          modelo_dibujo: formData.modelo_dibujo || undefined,
          medida: formData.medida,
          tipo_neumatico: formData.tipo_neumatico,
          posicion: formData.posicion as Posicion,
          observaciones: formData.observaciones || undefined,
        }],
        km_vehiculo_actual: formData.km_vehiculo_actual,
        observaciones_generales: `Montaje de neumático en ${POSICIONES_LABELS[formData.posicion as Posicion]}`
      }

      await montar(vehiculoId, payload)
      toast.success(`Neumático montado en ${POSICIONES_LABELS[formData.posicion as Posicion]}`)
      setModalOpen(false)
      onRecargar()
    } catch (error) {
      // Error ya manejado en el hook
    } finally {
      setLoading(false)
    }
  }

  // ✅ Función para manejar medición
  const handleMedir = async () => {
    if (profundidad <= 0) {
      toast.error('Ingresa una profundidad válida')
      return
    }

    if (!modalNeumatico) {
      toast.error('No hay neumático seleccionado')
      return
    }

    setMedicionLoading(true)
    try {
      await medir(modalNeumatico.id, profundidad)
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

  // ✅ Función para manejar desmontaje
  const handleDesmontar = async () => {
    if (!modalNeumatico) {
      toast.error('No hay neumático seleccionado')
      return
    }

    const kmActual = prompt('Ingresa el kilometraje actual del vehículo:')
    if (kmActual === null) return
    
    const kmNum = Number(kmActual)
    if (isNaN(kmNum) || kmNum <= 0) {
      toast.error('Ingresa un kilometraje válido')
      return
    }

    if (!confirm(`¿Estás seguro de desmontar el neumático ${modalPosicion ? POSICIONES_LABELS[modalPosicion] : ''}?`)) {
      return
    }

    setLoading(true)
    try {
      await desmontar(modalNeumatico.id, kmNum, 'CAMBIO_POR_DESGASTE')
      toast.success(`Neumático ${modalPosicion ? POSICIONES_LABELS[modalPosicion] : ''} desmontado`)
      setModalOpen(false)
      onRecargar()
    } catch (error) {
      // Error ya manejado en el hook
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {POSICIONES.map((pos) => {
          const neumatico = activos?.[pos] || null
          const tiene = neumatico !== null

          return (
            <Card key={pos} className={`border-2 ${tiene ? 'border-green-200' : 'border-dashed border-gray-200'}`}>
              <CardContent className="pt-4 pb-3">
                <div className="flex justify-between items-start">
                  <span className="text-sm font-medium text-muted-foreground">
                    {POSICIONES_LABELS[pos]}
                  </span>
                  {tiene && neumatico && (
                    <Badge className={`${colorMap[neumatico.estado_color] || 'bg-gray-100'} text-xs`}>
                      {neumatico.estado_color}
                    </Badge>
                  )}
                </div>

                {tiene && neumatico ? (
                  <div className="mt-2">
                    <p className="font-medium text-sm">{neumatico.marca}</p>
                    <p className="text-xs text-muted-foreground">{neumatico.modelo_dibujo || '--'}</p>
                    <p className="text-xs text-muted-foreground">{neumatico.medida || '--'}</p>
                    <div className="mt-2 flex justify-between text-xs">
                      <span className="text-muted-foreground">Km:</span>
                      <span>{neumatico.km_montaje?.toLocaleString() || 0}</span>
                    </div>
                    {neumatico.ultima_profundidad_mm !== null && neumatico.ultima_profundidad_mm !== undefined && (
                      <div className="flex justify-between text-xs">
                        <span className="text-muted-foreground">Prof:</span>
                        <span>{neumatico.ultima_profundidad_mm} mm</span>
                      </div>
                    )}
                    {neumatico.sugerencia && (
                      <div className="mt-1 p-1.5 bg-yellow-50 rounded text-xs text-yellow-700 flex items-center gap-1">
                        <AlertTriangle className="h-3 w-3" />
                        <span className="truncate">{neumatico.sugerencia}</span>
                      </div>
                    )}
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="mt-2 w-full"
                      onClick={() => handleAbrirModal(pos, neumatico)}
                    >
                      <Edit className="h-3 w-3 mr-1" />
                      Editar
                    </Button>
                  </div>
                ) : (
                  <div className="mt-4 text-center text-muted-foreground">
                    <Car className="h-8 w-8 mx-auto opacity-30" />
                    <p className="text-sm">Vacío</p>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="mt-2 w-full"
                      onClick={() => handleAbrirModal(pos, null)}
                    >
                      <Plus className="h-3 w-3 mr-1" />
                      Montar
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Modal unificado */}
      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {modalNeumatico ? 'Editar Neumático' : 'Montar Neumático'} 
              {' '}- {modalPosicion ? POSICIONES_LABELS[modalPosicion] : ''}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
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
              <Label>Tipo de Neumático</Label>
              <Select
                value={formData.tipo_neumatico}
                onValueChange={(val) => setFormData({...formData, tipo_neumatico: val})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TIPOS_NEUMATICO.map(t => (
                    <SelectItem key={t} value={t}>{t}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {!modalNeumatico && (
              <div className="space-y-1">
                <Label>Kilometraje actual *</Label>
                <Input
                  type="number"
                  placeholder="Ej: 15000"
                  value={formData.km_vehiculo_actual || ''}
                  onChange={(e) => setFormData({...formData, km_vehiculo_actual: Number(e.target.value)})}
                />
              </div>
            )}

            <div className="space-y-1">
              <Label>Observaciones</Label>
              <Input
                placeholder="Opcional"
                value={formData.observaciones}
                onChange={(e) => setFormData({...formData, observaciones: e.target.value})}
              />
            </div>

            {/* ✅ Botones de acción para neumático existente */}
            {modalNeumatico && (
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
            )}

            <div className="flex justify-end gap-2 pt-2 border-t">
              <Button variant="outline" onClick={() => setModalOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleGuardar} disabled={loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                {modalNeumatico ? 'Actualizar' : 'Guardar'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* ✅ Modal de medición */}
      <Dialog open={mostrarMedicion} onOpenChange={setMostrarMedicion}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Registrar Medición - {modalPosicion ? POSICIONES_LABELS[modalPosicion] : ''}</DialogTitle>
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
              <p className="text-xs text-muted-foreground mt-1">
                Rango: 0 - 20 mm
              </p>
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
    </div>
  )
}