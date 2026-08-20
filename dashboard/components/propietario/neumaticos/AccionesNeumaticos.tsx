'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { RotateCw, RefreshCw } from 'lucide-react'

interface AccionesNeumaticosProps {
  vehiculoId: string
  onRotar: (km: number) => Promise<void>
  onRecargar: () => void
}

export function AccionesNeumaticos({ vehiculoId, onRotar, onRecargar }: AccionesNeumaticosProps) {
  const [rotarOpen, setRotarOpen] = useState(false)
  const [kmRotacion, setKmRotacion] = useState<number>(0)
  const [loading, setLoading] = useState(false)

  const handleRotar = async () => {
    if (kmRotacion <= 0) return
    setLoading(true)
    try {
      await onRotar(kmRotacion)
      setRotarOpen(false)
      setKmRotacion(0)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardContent className="py-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={onRecargar}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Recargar
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <Dialog open={rotarOpen} onOpenChange={setRotarOpen}>
            <DialogTrigger asChild>
              <Button size="sm">
                <RotateCw className="h-4 w-4 mr-2" />
                Rotar Neumáticos
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Rotar Neumáticos</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <Label htmlFor="km-rotacion">Kilometraje actual del vehículo</Label>
                  <Input
                    id="km-rotacion"
                    type="number"
                    placeholder="Ej: 25000"
                    value={kmRotacion || ''}
                    onChange={(e) => setKmRotacion(Number(e.target.value))}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Ingresa el kilometraje actual para registrar la rotación
                  </p>
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setRotarOpen(false)}>
                    Cancelar
                  </Button>
                  <Button onClick={handleRotar} disabled={loading || kmRotacion <= 0}>
                    {loading ? 'Rotando...' : 'Confirmar Rotación'}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </CardContent>
    </Card>
  )
}