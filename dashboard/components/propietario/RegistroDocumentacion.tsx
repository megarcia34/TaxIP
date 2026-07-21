'use client'

import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { FileText } from 'lucide-react'

interface Props {
  data: any
  updateData: (data: any) => void
}

export default function RegistroDocumentacion({ data, updateData }: Props) {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, field: string) => {
    const file = e.target.files?.[0] || null
    updateData({ [field]: file })
  }

  const renderFileInput = (label: string, field: string, accept: string = "image/*") => (
    <div className="space-y-2">
      <Label>{label}</Label>
      <div className="flex items-center gap-2">
        <Input
          type="file"
          accept={accept}
          onChange={(e) => handleFileChange(e, field)}
          className="flex-1"
        />
        {data[field] && (
          <span className="text-xs text-green-600">✓ Archivo seleccionado</span>
        )}
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      <div className="grid gap-4">
        {renderFileInput("Documento de Identidad (frente) *", "documento_frente")}
        {renderFileInput("Documento de Identidad (dorso)", "documento_dorso")}
        {renderFileInput("Licencia de Conducir", "licencia_conducir")}
      </div>

      <Card className="bg-muted/50">
        <CardContent className="p-4 text-sm text-muted-foreground">
          <div className="flex items-start gap-2">
            <FileText className="h-4 w-4 mt-0.5" />
            <div>
              <p>Formatos aceptados: JPG, PNG, PDF (máx. 5MB por archivo)</p>
              <p className="text-xs mt-1">La documentación será verificada por el administrador.</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}