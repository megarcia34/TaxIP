'use client'

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { FileText, Shield, User, Truck, Wrench, FileCheck, ArrowRight } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface PopupDocumentacionProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  vehiculoId: string
  patente: string
}

export function PopupDocumentacion({ open, onOpenChange, vehiculoId, patente }: PopupDocumentacionProps) {
  const router = useRouter()

  const handleIrDocumentos = () => {
    onOpenChange(false)
    // Redirigir a la pestaña de documentos del vehículo
    router.push(`/dashboard-propietario/vehiculos/${vehiculoId}?tab=documentos`)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="bg-blue-100 p-2 rounded-full">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <DialogTitle className="text-lg">📄 ¡Casi listo!</DialogTitle>
              <DialogDescription className="text-sm">
                Tu vehículo {patente} ya está registrado
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Para una adecuada configuración de la plataforma y sacarle el mayor rédito posible al uso de la misma, 
            te recomendamos cargar la documentación de tu vehículo.
          </p>

          <div className="bg-muted/30 rounded-lg p-3">
            <p className="text-xs font-medium text-muted-foreground mb-2">Documentos recomendados:</p>
            <div className="grid grid-cols-2 gap-2">
              <div className="flex items-center gap-2 text-xs">
                <Truck className="h-3.5 w-3.5 text-blue-500" />
                <span>Cédula Verde</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <User className="h-3.5 w-3.5 text-blue-500" />
                <span>Licencia</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <Shield className="h-3.5 w-3.5 text-blue-500" />
                <span>Seguro</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <Wrench className="h-3.5 w-3.5 text-blue-500" />
                <span>ITV / VTV</span>
              </div>
            </div>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <p className="text-xs text-yellow-700">
              💡 Con estos documentos recibirás alertas de vencimiento y tendrás una gestión completa de tu flota.
            </p>
          </div>
        </div>

        <DialogFooter className="flex flex-col sm:flex-row gap-2">
          <Button variant="outline" className="w-full sm:w-auto" onClick={() => onOpenChange(false)}>
            Ahora no
          </Button>
          <Button className="w-full sm:w-auto" onClick={handleIrDocumentos}>
            <FileText className="h-4 w-4 mr-2" />
            Ir a Documentos
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}