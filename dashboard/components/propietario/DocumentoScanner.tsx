'use client'

import { useState, useRef, useCallback } from 'react'
import Webcam from 'react-webcam'
import Tesseract from 'tesseract.js'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { toast } from 'sonner'
import { Camera, Upload, X, Loader2, Scan, FileText, Cloud, CheckCircle } from 'lucide-react'

// ====== DEFINICIÓN DE TIPOS ======
type DocumentoData = {
  tipo?: string
  tipo_documento?: string
  numero?: string
  fecha_emision?: string
  fecha_vencimiento?: string
  observaciones?: string
  nombre?: string
  apellido?: string
  documento?: string
  vehiculoId?: string
  choferId?: string
  url_imagen?: string
  public_id?: string
  [key: string]: any
}

// ====== INTERFAZ DE PROPS ======
interface DocumentoScannerProps {
  vehiculoId: string
  onSuccess?: (data: DocumentoData) => void
  onClose?: () => void
}

// ====== CONSTANTES ======
const TIPOS_DOCUMENTOS = [
  { value: 'seguro', label: 'Seguro' },
  { value: 'vtv', label: 'VTV' },
  { value: 'habilitacion', label: 'Habilitación Municipal' },
  { value: 'licencia', label: 'Licencia de Conducir' },
  { value: 'dni', label: 'DNI' },
  { value: 'cedula_verde', label: 'Cédula Verde' },
  { value: 'carnet', label: 'Carnet' },
  { value: 'certificado_medico', label: 'Certificado Médico' },
  { value: 'antecedentes', label: 'Antecedentes Penales' },
]

// ====== FUNCIONES DE DETECCIÓN (Reemplazan a ParserFactory) ======
function detectarTipoDocumento(text: string): string {
  const cleanText = text.toLowerCase()
  
  if (cleanText.includes('licencia') || cleanText.includes('conducir')) {
    return 'licencia'
  }
  if (cleanText.includes('dni') || cleanText.includes('documento nacional de identidad')) {
    return 'dni'
  }
  if (cleanText.includes('vtv') || cleanText.includes('verificacion tecnica')) {
    return 'vtv'
  }
  if (cleanText.includes('seguro') || cleanText.includes('cobertura')) {
    return 'seguro'
  }
  if (cleanText.includes('cedula') || cleanText.includes('cédula')) {
    return 'cedula_verde'
  }
  if (cleanText.includes('habilitacion') || cleanText.includes('municipal')) {
    return 'habilitacion'
  }
  if (cleanText.includes('carnet')) {
    return 'carnet'
  }
  if (cleanText.includes('medico') || cleanText.includes('aptitud')) {
    return 'certificado_medico'
  }
  if (cleanText.includes('antecedentes') || cleanText.includes('penales')) {
    return 'antecedentes'
  }
  
  return 'desconocido'
}

function extraerDatosBasicos(text: string): Partial<DocumentoData> {
  const datos: Partial<DocumentoData> = {}
  
  // Buscar números (DNI, licencia, etc.)
  const numeroMatch = text.match(/\b(\d{6,10})\b/)
  if (numeroMatch) {
    datos.numero = numeroMatch[1]
  }
  
  // Buscar fechas en formato DD/MM/YYYY o DD-MM-YYYY
  const fechaMatch = text.match(/(\d{2})[\/\-](\d{2})[\/\-](\d{4})/)
  if (fechaMatch) {
    const day = fechaMatch[1]
    const month = fechaMatch[2]
    const year = fechaMatch[3]
    const fecha = `${year}-${month}-${day}`
    
    // Si no hay fecha de emisión, asumimos que es vencimiento
    if (!datos.fecha_emision) {
      datos.fecha_vencimiento = fecha
    }
  }
  
  // Buscar nombre
  const nombreMatch = text.match(/[A-Z][a-záéíóú]+\s+[A-Z][a-záéíóú]+/)
  if (nombreMatch) {
    datos.nombre = nombreMatch[0]
  }
  
  return datos
}

// ====== COMPONENTE PRINCIPAL ======
export function DocumentoScanner({ vehiculoId, onSuccess, onClose }: DocumentoScannerProps) {
  const [mode, setMode] = useState<'camera' | 'upload'>('camera')
  const [image, setImage] = useState<string | null>(null)
  const [processing, setProcessing] = useState(false)
  const [uploadResult, setUploadResult] = useState<{ url: string; public_id: string } | null>(null)
  
  const [extractedData, setExtractedData] = useState<Partial<DocumentoData>>({})
  const [tipoDetectado, setTipoDetectado] = useState<string | null>(null)
  const [formData, setFormData] = useState<Partial<DocumentoData>>({
    tipo_documento: '',
    numero: '',
    fecha_emision: '',
    fecha_vencimiento: '',
    observaciones: ''
  })
  const [showForm, setShowForm] = useState(false)
  const [ocrProgress, setOcrProgress] = useState(0)

  const webcamRef = useRef<Webcam>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const capturePhoto = useCallback(() => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot()
      if (imageSrc) {
        setImage(imageSrc)
        uploadToCloudinary(imageSrc)
      }
    }
  }, [webcamRef])

  const uploadToCloudinary = async (imageSrc: string) => {
    setProcessing(true)
    setOcrProgress(0)
    try {
      const response = await fetch(imageSrc)
      const blob = await response.blob()
      const file = new File([blob], 'documento.jpg', { type: 'image/jpeg' })
      
      const formData = new FormData()
      formData.append('file', file)
      formData.append('upload_preset', process.env.NEXT_PUBLIC_CLOUDINARY_UPLOAD_PRESET || 'documentos_preset')
      formData.append('folder', 'documentos')
      
      const cloudName = process.env.NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME || 'sfy4qupi'
      const uploadResponse = await fetch(
        `https://api.cloudinary.com/v1_1/${cloudName}/image/upload`,
        { method: 'POST', body: formData }
      )
      
      const result = await uploadResponse.json()
      
      if (result.secure_url) {
        setUploadResult({ url: result.secure_url, public_id: result.public_id })
        toast.success('✅ Imagen subida a Cloudinary')
        await processOCR(imageSrc)
      } else {
        throw new Error('Error al subir a Cloudinary')
      }
    } catch (error) {
      console.error('Error:', error)
      toast.error('Error al subir la imagen')
      setShowForm(true)
    } finally {
      setProcessing(false)
    }
  }

  const processOCR = async (imageSrc: string) => {
    try {
      toast.info('🔍 Analizando documento con OCR...')
      
      const result = await Tesseract.recognize(
        imageSrc,
        'spa+eng',
        {
          logger: (m) => {
            if (m.status === 'recognizing text') {
              const progress = Math.round(m.progress * 100)
              setOcrProgress(progress)
            }
          }
        }
      )
      
      const text = result.data.text
      console.log('📄 TEXTO EXTRAÍDO COMPLETO:')
      console.log('========================================')
      console.log(text)
      console.log('========================================')
      console.log(`📊 Confianza OCR: ${result.data.confidence}%`)
      
      // ✅ DETECTAR TIPO (sin ParserFactory)
      const tipo = detectarTipoDocumento(text)
      setTipoDetectado(tipo)
      
      // ✅ EXTRAER DATOS BÁSICOS (sin GenericParser)
      const datosExtraidos = extraerDatosBasicos(text)
      
      let extracted: Partial<DocumentoData> = {}
      
      if (datosExtraidos.numero || datosExtraidos.nombre) {
        extracted = {
          ...datosExtraidos,
          tipo_documento: tipo !== 'desconocido' ? tipo : '',
        }
        const tipoLabel = getTipoLabel(tipo)
        toast.success(`✅ Datos de ${tipoLabel} extraídos automáticamente`)
      } else {
        toast.warning('⚠️ No se pudieron extraer datos. Ingresa la información manualmente.')
      }
      
      setExtractedData(extracted)
      
      setFormData({
        tipo_documento: extracted.tipo_documento || '',
        numero: extracted.numero || '',
        fecha_emision: extracted.fecha_emision || '',
        fecha_vencimiento: extracted.fecha_vencimiento || '',
        observaciones: extracted.observaciones || ''
      })
      
      setShowForm(true)
      
    } catch (error) {
      console.error('Error en OCR:', error)
      toast.error('Error al procesar el documento')
      setShowForm(true)
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    
    const reader = new FileReader()
    reader.onload = (e) => {
      const imageSrc = e.target?.result as string
      setImage(imageSrc)
      uploadToCloudinary(imageSrc)
    }
    reader.readAsDataURL(file)
  }

  const handleSubmit = () => {
    const finalData: DocumentoData = {
      tipo_documento: formData.tipo_documento || extractedData.tipo_documento || '',
      numero: formData.numero || extractedData.numero || '',
      fecha_emision: formData.fecha_emision || extractedData.fecha_emision || '',
      fecha_vencimiento: formData.fecha_vencimiento || extractedData.fecha_vencimiento || '',
      observaciones: formData.observaciones || extractedData.observaciones || '',
      url_imagen: uploadResult?.url,
      public_id: uploadResult?.public_id,
      vehiculoId: vehiculoId
    }
    
    if (!finalData.tipo_documento) {
      toast.error('Selecciona un tipo de documento')
      return
    }
    if (!finalData.numero) {
      toast.error('El número del documento es obligatorio')
      return
    }
    if (!finalData.fecha_vencimiento) {
      toast.error('La fecha de vencimiento es obligatoria')
      return
    }
    
    if (onSuccess) {
      onSuccess(finalData)
    }
    
    toast.success('✅ Documento guardado correctamente')
    resetForm()
  }

  const resetForm = () => {
    setImage(null)
    setUploadResult(null)
    setExtractedData({})
    setTipoDetectado(null)
    setFormData({
      tipo_documento: '',
      numero: '',
      fecha_emision: '',
      fecha_vencimiento: '',
      observaciones: ''
    })
    setShowForm(false)
    setOcrProgress(0)
    setMode('camera')
  }

  const getTipoLabel = (tipo: string): string => {
    const found = TIPOS_DOCUMENTOS.find(t => t.value === tipo)
    return found?.label || tipo
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardContent className="pt-6">
        {!showForm ? (
          <>
            <div className="flex gap-2 mb-4">
              <Button variant={mode === 'camera' ? 'default' : 'outline'} onClick={() => setMode('camera')} className="flex-1">
                <Camera className="h-4 w-4 mr-2" /> Cámara
              </Button>
              <Button variant={mode === 'upload' ? 'default' : 'outline'} onClick={() => setMode('upload')} className="flex-1">
                <Upload className="h-4 w-4 mr-2" /> Subir Imagen
              </Button>
            </div>

            {mode === 'camera' && !image && (
              <div className="relative">
                <Webcam 
                  ref={webcamRef} 
                  audio={false} 
                  screenshotFormat="image/jpeg" 
                  className="w-full rounded-lg" 
                  videoConstraints={{ facingMode: 'environment' }} 
                />
                <Button onClick={capturePhoto} className="absolute bottom-4 left-1/2 -translate-x-1/2">
                  <Camera className="h-4 w-4 mr-2" /> Capturar
                </Button>
              </div>
            )}

            {mode === 'upload' && !image && (
              <div className="border-2 border-dashed rounded-lg p-8 text-center">
                <Cloud className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                <p className="text-muted-foreground mb-2">Sube la imagen del documento</p>
                <p className="text-xs text-muted-foreground mb-4">Se almacenará en Cloudinary</p>
                <Input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileUpload} className="hidden" />
                <Button onClick={() => fileInputRef.current?.click()}>Seleccionar imagen</Button>
              </div>
            )}

            {processing && (
              <div className="text-center py-8">
                <Loader2 className="h-12 w-12 animate-spin mx-auto text-primary mb-4" />
                <p className="font-medium">Procesando documento...</p>
                <p className="text-sm text-muted-foreground">Subiendo a Cloudinary y aplicando OCR</p>
                {ocrProgress > 0 && (
                  <div className="mt-2 w-full max-w-xs mx-auto bg-gray-200 rounded-full h-2">
                    <div className="bg-primary h-2 rounded-full transition-all duration-300" style={{ width: `${ocrProgress}%` }} />
                  </div>
                )}
              </div>
            )}

            {image && !processing && uploadResult && (
              <div className="relative">
                <img 
                  src={image} 
                  alt="Documento" 
                  className="w-full max-h-64 object-contain rounded-lg border border-gray-200" 
                />
                <div className="absolute top-2 right-2 flex gap-2">
                  <Badge className="bg-blue-100 text-blue-800"><Cloud className="h-3 w-3 mr-1" /> Cloudinary</Badge>
                  <Button variant="destructive" size="sm" onClick={() => { setImage(null); setUploadResult(null); setMode('camera') }}>
                    <X className="h-4 w-4" />
                  </Button>
                </div>
                <div className="absolute bottom-4 left-1/2 -translate-x-1/2">
                  <Button onClick={() => processOCR(image)} variant="secondary">
                    <Scan className="h-4 w-4 mr-2" /> Procesar OCR
                  </Button>
                </div>
              </div>
            )}

            <Button variant="outline" onClick={() => setShowForm(true)} className="w-full mt-4">
              <FileText className="h-4 w-4 mr-2" /> Ingresar datos manualmente
            </Button>
          </>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <FileText className="h-5 w-5" />
                {extractedData.numero ? '✅ Datos extraídos automáticamente' : '📝 Datos del documento'}
              </h3>
              {uploadResult && (
                <Badge className="bg-blue-100 text-blue-800"><Cloud className="h-3 w-3 mr-1" /> Cloudinary</Badge>
              )}
            </div>

            {tipoDetectado && tipoDetectado !== 'desconocido' && (
              <div className="flex items-center gap-2 p-2 bg-green-50 rounded-lg text-sm">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>Tipo detectado: <strong>{getTipoLabel(tipoDetectado)}</strong></span>
              </div>
            )}

            {image && (
              <div className="relative w-full max-w-md mx-auto">
                <img 
                  src={image} 
                  alt="Documento" 
                  className="w-full h-auto max-h-48 object-contain rounded-lg border border-gray-200" 
                />
              </div>
            )}

            <div className="space-y-3">
              <div className="space-y-2">
                <Label>Tipo de Documento *</Label>
                <select
                  className="w-full p-2 border rounded-md"
                  value={formData.tipo_documento}
                  onChange={(e) => setFormData({ ...formData, tipo_documento: e.target.value })}
                >
                  <option value="">Seleccionar tipo</option>
                  {TIPOS_DOCUMENTOS.map(t => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
                {extractedData.tipo_documento && (
                  <p className="text-xs text-green-600">✅ Extraído automáticamente</p>
                )}
              </div>

              <div className="space-y-2">
                <Label>Número *</Label>
                <Input
                  value={formData.numero}
                  onChange={(e) => setFormData({ ...formData, numero: e.target.value })}
                  placeholder={extractedData.numero ? '✅ Extraído automáticamente' : 'Ej: ABC123456'}
                  className={extractedData.numero ? 'border-green-300 bg-green-50' : ''}
                />
                {extractedData.numero && (
                  <p className="text-xs text-green-600">✅ Extraído automáticamente</p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Fecha de Emisión</Label>
                  <Input
                    type="date"
                    value={formData.fecha_emision}
                    onChange={(e) => setFormData({ ...formData, fecha_emision: e.target.value })}
                    className={extractedData.fecha_emision ? 'border-green-300 bg-green-50' : ''}
                  />
                  {extractedData.fecha_emision && (
                    <p className="text-xs text-green-600">✅ Extraído automáticamente</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label>Fecha de Vencimiento *</Label>
                  <Input
                    type="date"
                    value={formData.fecha_vencimiento}
                    onChange={(e) => setFormData({ ...formData, fecha_vencimiento: e.target.value })}
                    className={extractedData.fecha_vencimiento ? 'border-green-300 bg-green-50' : ''}
                  />
                  {extractedData.fecha_vencimiento && (
                    <p className="text-xs text-green-600">✅ Extraído automáticamente</p>
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <Label>Observaciones</Label>
                <Input
                  value={formData.observaciones}
                  onChange={(e) => setFormData({ ...formData, observaciones: e.target.value })}
                  placeholder="Notas adicionales..."
                  className={extractedData.observaciones ? 'border-green-300 bg-green-50' : ''}
                />
                {extractedData.observaciones && (
                  <p className="text-xs text-green-600">✅ Información extraída automáticamente</p>
                )}
              </div>
            </div>

            <div className="flex gap-2">
              <Button onClick={handleSubmit} className="flex-1">
                <Cloud className="h-4 w-4 mr-2" />
                {extractedData.numero ? '✅ Guardar (datos automáticos)' : 'Guardar Documento'}
              </Button>
              <Button variant="outline" onClick={() => { if (image) resetForm() }}>Cancelar</Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}