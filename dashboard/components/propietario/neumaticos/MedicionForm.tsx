'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Ruler } from 'lucide-react'
import { toast } from 'sonner'

interface MedicionFormProps {
  neumaticoId: string
  onMedir: (profundidad: number, observaciones?: string) => Promise<void>
  trigger?: React.ReactNode
}

export function MedicionForm({ neumaticoId, onMedir, trigger }: MedicionFormProps) {
  const [open, setOpen] = useState(false)
  const [profundidad, setProfundidad] = useState<number>(0)
  const [observaciones, setObservaciones] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (profundidad <= 0) {
      toast.error('Ingresa una profundidad válida')
      return
    }
    setLoading(true)
    try {
      await onMedir(profundidad, observaciones || undefined)
      setOpen(false)
      setProfundidad(0)
      setObservaciones('')
    } catch (error) {
      // Error ya manejado en el hook
    } finally {
      setLoading(false)
    }
  }

  const defaultTrigger = (
    <Button size="sm">
      <Ruler className="h-4 w-4 mr-2" />
      Medir
    </Button>
  )

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || defaultTrigger}
      </DialogTrigger>
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
          <div>
            <Label htmlFor="observaciones">Observaciones (opcional)</Label>
            <Textarea
              id="observaciones"
              placeholder="Ej: Desgaste uniforme, medición de rutina..."
              value={observaciones}
              onChange={(e) => setObservaciones(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={handleSubmit} disabled={loading || profundidad <= 0}>
              {loading ? 'Guardando...' : 'Guardar Medición'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}