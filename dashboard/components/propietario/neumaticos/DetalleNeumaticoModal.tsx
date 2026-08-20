'use client'

import { useEffect, useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Loader2, Clock, Ruler, Wrench, History } from 'lucide-react'
import { neumaticosAPI } from '@/lib/api/neumaticos'
import { toast } from 'sonner'
import { Neumatico } from '@/lib/api/neumaticos'

interface DetalleNeumaticoModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  neumaticoId: string
  onMedir: (neumaticoId: string, profundidad: number) => Promise<void>
  onDesmontar: (neumaticoId: string, motivo: string) => Promise<void>
  onRecargar: () => void
}

// Definir el tipo de estado de color para evitar any
type EstadoColor = 'VERDE' | 'AMARILLO' | 'ROJO'

// Definir el tipo de medición
interface MedicionItem {
  id: string
  fecha: string
  profundidad_mm: number
  estado_color: EstadoColor
  medido_por: string | null
  observaciones: string | null
}

// Definir el tipo de operación
interface OperacionItem {
  tipo: string
  fecha: string
  km_vehiculo: number
  descripcion: string | null
}

export function DetalleNeumaticoModal({
  open,
  onOpenChange,
  neumaticoId,
  onMedir,
  onDesmontar,
  onRecargar
}: DetalleNeumaticoModalProps) {
  const [neumatico, setNeumatico] = useState<Neumatico | null>(null)
  const [loading, setLoading] = useState(true)
  const [medicionOpen, setMedicionOpen] = useState(false)
  const [profundidad, setProfundidad] = useState<number>(0)
  const [medicionLoading, setMedicionLoading] = useState(false)
  const [desmontando, setDesmontando] = useState(false)

  const cargarDetalle = async () => {
    setLoading(true)
    try {
      const data = await neumaticosAPI.getOne(neumaticoId)
      setNeumatico(data)
    } catch (error) {
      console.error('Error cargando detalle:', error)
      toast.error('Error al cargar detalle del neumático')
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
      await onMedir(neumaticoId, profundidad)
      setMedicionOpen(false)
      setProfundidad(0)
      await cargarDetalle()
      onRecargar()
    } finally {
      setMedicionLoading(false)
    }
  }

  const handleDesmontar = async () => {
    setDesmontando(true)
    try {
      await onDesmontar(neumaticoId, 'CAMBIO_POR_DESGASTE')
      onOpenChange(false)
      onRecargar()
    } finally {
      setDesmontando(false)
    }
  }

  useEffect(() => {
    if (open && neumaticoId) {
      cargarDetalle()
    }
  }, [open, neumaticoId])

  if (loading) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-2xl">
          <div className="flex justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  if (!neumatico) {
    return null
  }

  const colorMap: Record<EstadoColor, string> = {
    VERDE: 'bg-green-100 text-green-800',
    AMARILLO: 'bg-yellow-100 text-yellow-800',
    ROJO: 'bg-red-100 text-red-800',
  }

  const posicionLabels: Record<string, string> = {
    DI: 'Delantero Izquierdo',
    DD: 'Delantero Derecho',
    TI: 'Trasero Izquierdo',
    TD: 'Trasero Derecho',
    REPUESTO: 'Repuesto',
  }

  const estadoLabels: Record<string, { label: string; className: string }> = {
    ACTIVO: { label: 'Activo', className: 'bg-green-100 text-green-800' },
    BAJA: { label: 'En Baja', className: 'bg-yellow-100 text-yellow-800' },
    DESECHADO: { label: 'Desechado', className: 'bg-red-100 text-red-800' },
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <span>{neumatico.codigo_interno}</span>
            <Badge className={colorMap[neumatico.estado_color]}>
              {neumatico.estado_color}
            </Badge>
            <Badge className={estadoLabels[neumatico.estado]?.className}>
              {estadoLabels[neumatico.estado]?.label}
            </Badge>
          </DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="text-muted-foreground">Marca:</span>
            <span className="font-medium ml-2">{neumatico.marca}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Modelo:</span>
            <span className="font-medium ml-2">{neumatico.modelo_dibujo || '--'}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Medida:</span>
            <span className="font-medium ml-2">{neumatico.medida || '--'}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Posición:</span>
            <span className="font-medium ml-2">{neumatico.posicion_actual ? posicionLabels[neumatico.posicion_actual] : 'No asignado'}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Km totales:</span>
            <span className="font-medium ml-2">{neumatico.km_totales_acumulados.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Km en posición:</span>
            <span className="font-medium ml-2">{neumatico.km_en_posicion_actual?.toLocaleString() || '--'}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Última profundidad:</span>
            <span className="font-medium ml-2">{neumatico.ultima_profundidad_mm ?? '--'} mm</span>
          </div>
          <div>
            <span className="text-muted-foreground">Fecha alta:</span>
            <span className="font-medium ml-2">{new Date(neumatico.fecha_alta).toLocaleDateString()}</span>
          </div>
        </div>

        <Tabs defaultValue="mediciones" className="mt-4">
          <TabsList>
            <TabsTrigger value="mediciones" className="flex items-center gap-1">
              <Ruler className="h-4 w-4" />
              Mediciones
            </TabsTrigger>
            <TabsTrigger value="operaciones" className="flex items-center gap-1">
              <History className="h-4 w-4" />
              Operaciones
            </TabsTrigger>
          </TabsList>

          <TabsContent value="mediciones" className="mt-4 space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Historial de mediciones</span>
              <Button size="sm" onClick={() => setMedicionOpen(true)}>
                <Ruler className="h-4 w-4 mr-2" />
                Medir
              </Button>
            </div>

            {neumatico.mediciones && neumatico.mediciones.length > 0 ? (
              neumatico.mediciones.map((m: MedicionItem) => (
                <div key={m.id} className="flex justify-between items-center border-b py-2 text-sm">
                  <div className="flex items-center gap-2">
                    <Badge className={colorMap[m.estado_color]}>
                      {m.estado_color}
                    </Badge>
                    <span>{m.profundidad_mm} mm</span>
                    <span className="text-muted-foreground">{m.observaciones}</span>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {new Date(m.fecha).toLocaleDateString()}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-muted-foreground text-sm">No hay mediciones registradas</p>
            )}
          </TabsContent>

          <TabsContent value="operaciones" className="mt-4 space-y-3">
            {neumatico.operaciones && neumatico.operaciones.length > 0 ? (
              neumatico.operaciones.map((op: OperacionItem, index: number) => (
                <div key={index} className="flex justify-between items-center border-b py-2 text-sm">
                  <div>
                    <span className="font-medium">{op.tipo}</span>
                    <span className="text-muted-foreground ml-2">{op.descripcion}</span>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {new Date(op.fecha).toLocaleDateString()}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-muted-foreground text-sm">No hay operaciones registradas</p>
            )}
          </TabsContent>
        </Tabs>

        <div className="flex justify-end gap-2 mt-4 pt-4 border-t">
          {neumatico.estado === 'ACTIVO' && (
            <Button variant="destructive" size="sm" onClick={handleDesmontar} disabled={desmontando}>
              {desmontando ? 'Desmontando...' : 'Desmontar'}
            </Button>
          )}
          <Button variant="outline" size="sm" onClick={() => onOpenChange(false)}>
            Cerrar
          </Button>
        </div>

        {/* Modal de medición */}
        <Dialog open={medicionOpen} onOpenChange={setMedicionOpen}>
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
                <p className="text-xs text-muted-foreground mt-1">
                  Ingresa la profundidad del surco del neumático en milímetros
                </p>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setMedicionOpen(false)}>
                  Cancelar
                </Button>
                <Button onClick={handleMedir} disabled={medicionLoading || profundidad <= 0}>
                  {medicionLoading ? 'Guardando...' : 'Guardar Medición'}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </DialogContent>
    </Dialog>
  )
}