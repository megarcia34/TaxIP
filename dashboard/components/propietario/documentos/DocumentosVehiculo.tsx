'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Loader2, RefreshCw, FileText, Upload, Eye, Trash2, Plus, AlertCircle, CheckCircle } from 'lucide-react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { toast } from 'sonner'
import { useDocumentos } from '@/hooks/useDocumentos'

interface DocumentosVehiculoProps {
  vehiculoId: string
}

const TIPOS_DOCUMENTO = [
  { value: 'SEGURO', label: 'Seguro' },
  { value: 'VTV', label: 'VTV / ITV' },
  { value: 'CEDULA', label: 'Cédula Verde' },
  { value: 'PATENTE', label: 'Patente' },
  { value: 'LICENCIA', label: 'Licencia de Conducir' },
  { value: 'OTRO', label: 'Otro' },
]

const estadoColorMap: Record<string, string> = {
  vigente: 'bg-green-100 text-green-800 border-green-200',
  proximo: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  vencido: 'bg-red-100 text-red-800 border-red-200',
}

const estadoLabelMap: Record<string, string> = {
  vigente: '✅ Vigente',
  proximo: '⚠️ Próximo a vencer',
  vencido: '❌ Vencido',
}

export function DocumentosVehiculo({ vehiculoId }: DocumentosVehiculoProps) {
  const {
    documentos,
    loading,
    subirDocumento,
    eliminarDocumento,
    recargar,
    total,
    vigentes,
    proximos,
    vencidos,
    getFaltantes
  } = useDocumentos(vehiculoId)

  const [modalOpen, setModalOpen] = useState(false)
  const [subiendo, setSubiendo] = useState(false)
  const [formData, setFormData] = useState({
    tipo_documento: '',
    numero: '',
    fecha_emision: '',
    fecha_vencimiento: '',
    observaciones: '',
    url_imagen: '',
  })

  const faltantes = getFaltantes()
  const tieneTodos = faltantes.length === 0

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.tipo_documento || !formData.numero || !formData.fecha_vencimiento) {
      toast.error('Completa todos los campos obligatorios')
      return
    }

    setSubiendo(true)
    try {
      await subirDocumento({
        tipo_documento: formData.tipo_documento,
        numero: formData.numero,
        fecha_emision: formData.fecha_emision || null,
        fecha_vencimiento: formData.fecha_vencimiento,
        observaciones: formData.observaciones || null,
        url_imagen: formData.url_imagen || null,
      })
      setModalOpen(false)
      setFormData({
        tipo_documento: '',
        numero: '',
        fecha_emision: '',
        fecha_vencimiento: '',
        observaciones: '',
        url_imagen: '',
      })
    } finally {
      setSubiendo(false)
    }
  }

  const handleEliminar = async (id: string, tipo: string) => {
    if (confirm(`¿Eliminar documento ${tipo}?`)) {
      await eliminarDocumento(id)
    }
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
            <FileText className="h-5 w-5" />
            Documentos del Vehículo
            <span className="text-sm font-normal text-muted-foreground">
              ({total} subidos)
            </span>
            {tieneTodos ? (
              <Badge className="bg-green-100 text-green-800">✅ Completos</Badge>
            ) : (
              <Badge className="bg-yellow-100 text-yellow-800">⚠️ Faltan {faltantes.length}</Badge>
            )}
          </h3>
          <div className="flex gap-4 mt-1 text-xs text-muted-foreground">
            <span>✅ Vigentes: {vigentes}</span>
            <span>⚠️ Próximos: {proximos}</span>
            <span>❌ Vencidos: {vencidos}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => recargar()}>
            <RefreshCw className="h-4 w-4 mr-1" />
            Actualizar
          </Button>
          <Button size="sm" onClick={() => setModalOpen(true)}>
            <Plus className="h-4 w-4 mr-1" />
            Subir Documento
          </Button>
        </div>
      </div>

      {/* Lista de documentos */}
      {documentos.length === 0 ? (
        <Card className="border-dashed border-yellow-200 bg-yellow-50/30">
          <CardContent className="py-8 text-center">
            <FileText className="h-12 w-12 mx-auto text-yellow-500 mb-3" />
            <p className="text-yellow-700 font-medium">No hay documentos subidos</p>
            <p className="text-yellow-600 text-sm mt-1">
              Sube los documentos requeridos: SEGURO, VTV y CÉDULA
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {documentos.map((doc) => (
            <Card key={doc.id} className="border-2 hover:border-primary/30 transition-colors">
              <CardContent className="pt-4 pb-3">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium text-sm">{doc.tipo_documento}</p>
                    <p className="text-xs text-muted-foreground">N° {doc.numero}</p>
                  </div>
                  <Badge className={estadoColorMap[doc.estado] || 'bg-gray-100'}>
                    {estadoLabelMap[doc.estado] || doc.estado}
                  </Badge>
                </div>

                <div className="mt-2 space-y-1 text-xs">
                  {doc.fecha_vencimiento && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Vence:</span>
                      <span>{new Date(doc.fecha_vencimiento).toLocaleDateString()}</span>
                    </div>
                  )}
                  {doc.dias_para_vencer !== null && doc.dias_para_vencer !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Días restantes:</span>
                      <span className={doc.dias_para_vencer < 0 ? 'text-red-600 font-medium' : ''}>
                        {doc.dias_para_vencer < 0 ? 'Vencido' : `${doc.dias_para_vencer} días`}
                      </span>
                    </div>
                  )}
                  {doc.observaciones && (
                    <p className="text-muted-foreground truncate">{doc.observaciones}</p>
                  )}
                </div>

                <div className="flex gap-1 mt-3 pt-2 border-t">
                  {doc.url_archivo && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => window.open(doc.url_archivo!, '_blank')}
                    >
                      <Eye className="h-3 w-3 mr-1" />
                      Ver
                    </Button>
                  )}
                  <Button
                    variant="destructive"
                    size="sm"
                    className="flex-1"
                    onClick={() => handleEliminar(doc.id, doc.tipo_documento)}
                  >
                    <Trash2 className="h-3 w-3 mr-1" />
                    Eliminar
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Modal subir documento */}
      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Subir Documento
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label>Tipo de Documento *</Label>
              <Select
                value={formData.tipo_documento}
                onValueChange={(val) => setFormData({ ...formData, tipo_documento: val })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar tipo" />
                </SelectTrigger>
                <SelectContent>
                  {TIPOS_DOCUMENTO.map((t) => (
                    <SelectItem key={t.value} value={t.value}>
                      {t.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Número *</Label>
              <Input
                placeholder="Ej: 123456"
                value={formData.numero}
                onChange={(e) => setFormData({ ...formData, numero: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Fecha de Emisión</Label>
                <Input
                  type="date"
                  value={formData.fecha_emision}
                  onChange={(e) => setFormData({ ...formData, fecha_emision: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Fecha de Vencimiento *</Label>
                <Input
                  type="date"
                  required
                  value={formData.fecha_vencimiento}
                  onChange={(e) => setFormData({ ...formData, fecha_vencimiento: e.target.value })}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Observaciones</Label>
              <Input
                placeholder="Opcional"
                value={formData.observaciones}
                onChange={(e) => setFormData({ ...formData, observaciones: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label>URL de Imagen</Label>
              <Input
                placeholder="https://..."
                value={formData.url_imagen}
                onChange={(e) => setFormData({ ...formData, url_imagen: e.target.value })}
              />
              <p className="text-xs text-muted-foreground">Opcional - Link a la imagen del documento</p>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t">
              <Button type="button" variant="outline" onClick={() => setModalOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={subiendo}>
                {subiendo ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Subir Documento
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}