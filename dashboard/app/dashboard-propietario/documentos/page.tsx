'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api'
import { toast } from 'sonner'
import { 
  FileText, AlertTriangle, Loader2, Plus, Cloud, CheckCircle, XCircle,
  Upload, Trash2, User, Car, Users, Edit, Calendar, Shield, FileCheck, 
  BadgeCheck, Truck, Wrench, Eye, ImageIcon
} from 'lucide-react'
import { CldUploadWidget } from 'next-cloudinary'
import { GaleriaVehiculo } from '@/components/propietario/GaleriaVehiculo'
import { ModalImagen } from '@/components/propietario/ModalImagen'

// ============================================================
// INTERFACES
// ============================================================

interface DocumentoRaw {
  id: string
  tipo_documento: string
  numero: string
  fecha_emision: string | null
  fecha_vencimiento: string | null
  observaciones: string | null
  url_archivo: string | null
  created_at: string
  updated_at: string
}

interface DocumentoNormalized {
  id: string
  tipo_documento: string
  numero: string
  fecha_emision: string | null
  fecha_vencimiento: string | null
  observaciones: string | null
  url_archivo: string | null
  dias_para_vencer: number | null
  estado: 'vigente' | 'proximo' | 'vencido'
}

interface Vehiculo {
  id: string
  patente: string
  marca: string
  modelo: string
}

interface Propietario {
  id: string
  nombre: string
  email: string
  telefono: string
}

interface FotoVehiculo {
  id: string
  url: string
  public_id: string
  descripcion: string | null
  orden: number
  es_principal: boolean
  created_at: string
}

const TIPOS_DOCUMENTOS = [
  { value: 'dni', label: 'DNI', entidad: 'propietario', icon: BadgeCheck },
  { value: 'licencia', label: 'Carnet de Conducir', entidad: 'propietario', icon: FileCheck },
  { value: 'cedula_verde', label: 'Cédula Verde', entidad: 'vehiculo', icon: Truck },
  { value: 'seguro', label: 'Seguro', entidad: 'vehiculo', icon: Shield },
  { value: 'vtv', label: 'VTV', entidad: 'vehiculo', icon: Wrench },
  { value: 'habilitacion', label: 'Habilitación Municipal', entidad: 'vehiculo', icon: FileCheck },
]

const getIconForTipo = (tipo: string) => {
  const found = TIPOS_DOCUMENTOS.find(t => t.value === tipo)
  return found?.icon || FileText
}

// ============================================================
// FUNCIÓN PARA NORMALIZAR DOCUMENTOS
// ============================================================

function normalizarDocumentos(docs: DocumentoRaw[]): DocumentoNormalized[] {
  const hoy = new Date()
  hoy.setHours(0, 0, 0, 0)
  
  return docs.map(doc => {
    let dias_para_vencer: number | null = null
    let estado: 'vigente' | 'proximo' | 'vencido' = 'vigente'
    
    if (doc.fecha_vencimiento) {
      const fechaVen = new Date(doc.fecha_vencimiento)
      fechaVen.setHours(0, 0, 0, 0)
      const diffTime = fechaVen.getTime() - hoy.getTime()
      dias_para_vencer = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (dias_para_vencer < 0) {
        estado = 'vencido'
      } else if (dias_para_vencer <= 30) {
        estado = 'proximo'
      } else {
        estado = 'vigente'
      }
    }
    
    return {
      ...doc,
      dias_para_vencer,
      estado
    }
  })
}

// ============================================================
// COMPONENTE PRINCIPAL
// ============================================================

export default function DocumentosPage() {
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([])
  const [propietario, setPropietario] = useState<Propietario | null>(null)
  const [documentos, setDocumentos] = useState<Record<string, DocumentoNormalized[]>>({})
  const [loading, setLoading] = useState(true)
  const [errorVehiculos, setErrorVehiculos] = useState<string[]>([])
  
  const [showForm, setShowForm] = useState(false)
  const [entidadTipo, setEntidadTipo] = useState<'propietario' | 'vehiculo'>('propietario')
  const [selectedVehiculo, setSelectedVehiculo] = useState('')
  const [formData, setFormData] = useState({
    tipo_documento: '',
    numero: '',
    fecha_emision: '',
    fecha_vencimiento: '',
    observaciones: ''
  })
  const [uploadResult, setUploadResult] = useState<{ url: string; public_id: string } | null>(null)

  const [showEditForm, setShowEditForm] = useState(false)
  const [docEditando, setDocEditando] = useState<DocumentoNormalized | null>(null)
  const [formEdit, setFormEdit] = useState({
    tipo_documento: '',
    numero: '',
    fecha_emision: '',
    fecha_vencimiento: '',
    observaciones: ''
  })
  const [uploadEditResult, setUploadEditResult] = useState<{ url: string; public_id: string } | null>(null)

  const [fotosPorVehiculo, setFotosPorVehiculo] = useState<Record<string, FotoVehiculo[]>>({})
  const [imagenModal, setImagenModal] = useState<{ url: string; titulo: string } | null>(null)

  // ============================================================
  // FUNCIONES DE CARGA
  // ============================================================

  const cargarFotosVehiculo = async (vehiculoId: string) => {
    if (!vehiculoId) return
    try {
      const res = await apiClient.get(`/api/propietario/fotos/vehiculos/${vehiculoId}`)
      setFotosPorVehiculo(prev => ({
        ...prev,
        [vehiculoId]: res.data || []
      }))
    } catch (error) {
      console.error(`Error cargando fotos del vehículo ${vehiculoId}:`, error)
      setFotosPorVehiculo(prev => ({
        ...prev,
        [vehiculoId]: []
      }))
    }
  }

  const cargarDatos = async () => {
    setLoading(true)
    setErrorVehiculos([])
    
    try {
      // 1. Cargar vehículos
      console.log('📋 Cargando vehículos...')
      const vehiculosRes = await apiClient.get('/api/propietario/vehiculos')
      const vehiculosData = vehiculosRes.data || []
      
      const vehiculosMap = new Map<string, Vehiculo>()
      vehiculosData.forEach((v: Vehiculo) => {
        if (!vehiculosMap.has(v.id)) {
          vehiculosMap.set(v.id, v)
        }
      })
      const vehiculosUnicos = Array.from(vehiculosMap.values())
      setVehiculos(vehiculosUnicos)
      console.log(`✅ ${vehiculosUnicos.length} vehículos únicos cargados`)
      
      // 2. Cargar propietario
      console.log('📋 Cargando propietario...')
      let propietarioData = null
      try {
        const propietarioRes = await apiClient.get('/api/propietario/perfil')
        propietarioData = propietarioRes.data
      } catch (e) {
        const session = await fetch('/api/auth/session').then(r => r.json())
        propietarioData = {
          id: session?.user?.id || '',
          nombre: session?.user?.name || 'Propietario',
          email: session?.user?.email || '',
          telefono: ''
        }
      }
      setPropietario(propietarioData)
      console.log('✅ Propietario cargado:', propietarioData?.nombre)
      
      // 3. Cargar documentos de cada vehículo
      const docsMap: Record<string, DocumentoNormalized[]> = {}
      const errores: string[] = []
      
      for (const v of vehiculosUnicos) {
        try {
          console.log(`📋 Cargando documentos de ${v.patente}...`)
          const res = await apiClient.get(`/api/propietario/vehiculos/${v.id}/documentos`)
          const rawDocs = res.data || []
          const docsNormalizados = normalizarDocumentos(rawDocs)
          docsMap[v.id] = docsNormalizados
          console.log(`✅ ${docsNormalizados.length} documentos para ${v.patente}`)
        } catch (e) {
          console.error(`❌ Error cargando documentos de ${v.patente}:`, e)
          docsMap[v.id] = []
          errores.push(v.patente)
        }
      }
      
      // 4. Cargar documentos del propietario
      try {
        console.log('📋 Cargando documentos del propietario...')
        const res = await apiClient.get('/api/propietario/documentos/propietario')
        const rawDocs = res.data || []
        docsMap['propietario'] = normalizarDocumentos(rawDocs)
        console.log(`✅ ${docsMap['propietario'].length} documentos del propietario`)
      } catch (e) {
        console.error('❌ Error cargando documentos del propietario:', e)
        docsMap['propietario'] = []
      }
      
      setDocumentos(docsMap)
      setErrorVehiculos(errores)
      
      // 5. Cargar fotos de TODOS los vehículos
      for (const v of vehiculosUnicos) {
        await cargarFotosVehiculo(v.id)
      }
      
    } catch (error) {
      console.error('❌ Error general cargando datos:', error)
      toast.error('Error al cargar los datos')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    cargarDatos()
  }, [])

  // ============================================================
  // FUNCIONES CRUD
  // ============================================================

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (entidadTipo === 'vehiculo' && !selectedVehiculo) {
      toast.error('Selecciona un vehículo')
      return
    }

    if (!formData.tipo_documento) {
      toast.error('Selecciona un tipo de documento')
      return
    }
    if (!formData.numero) {
      toast.error('Ingresa el número del documento')
      return
    }
    if (!formData.fecha_vencimiento) {
      toast.error('Ingresa la fecha de vencimiento')
      return
    }

    try {
      const payload = {
        tipo_documento: formData.tipo_documento,
        numero: formData.numero,
        fecha_emision: formData.fecha_emision || null,
        fecha_vencimiento: formData.fecha_vencimiento,
        observaciones: formData.observaciones || '',
        url_imagen: uploadResult?.url || null
      }

      const endpoint = entidadTipo === 'propietario'
        ? '/api/propietario/documentos/propietario'
        : `/api/propietario/vehiculos/${selectedVehiculo}/documentos`

      await apiClient.post(endpoint, payload)
      toast.success('✅ Documento subido correctamente')
      resetForm()
      cargarDatos()
    } catch (error: any) {
      console.error('Error:', error)
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail
        if (Array.isArray(detail)) {
          toast.error(detail.map((d: any) => d.msg).join(', '))
        } else {
          toast.error(detail)
        }
      } else {
        toast.error('Error al subir documento')
      }
    }
  }

  const resetForm = () => {
    setShowForm(false)
    setSelectedVehiculo('')
    setEntidadTipo('propietario')
    setFormData({
      tipo_documento: '',
      numero: '',
      fecha_emision: '',
      fecha_vencimiento: '',
      observaciones: ''
    })
    setUploadResult(null)
  }

  const openEditForm = (doc: DocumentoNormalized) => {
    setDocEditando(doc)
    setFormEdit({
      tipo_documento: doc.tipo_documento,
      numero: doc.numero,
      fecha_emision: doc.fecha_emision || '',
      fecha_vencimiento: doc.fecha_vencimiento || '',
      observaciones: doc.observaciones || ''
    })
    setUploadEditResult(doc.url_archivo ? { url: doc.url_archivo, public_id: '' } : null)
    setShowEditForm(true)
  }

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!docEditando) return
    
    try {
      const payload = {
        tipo_documento: formEdit.tipo_documento,
        numero: formEdit.numero,
        fecha_emision: formEdit.fecha_emision || null,
        fecha_vencimiento: formEdit.fecha_vencimiento,
        observaciones: formEdit.observaciones || '',
        url_imagen: uploadEditResult?.url || docEditando.url_archivo || null
      }

      await apiClient.put(`/api/propietario/vehiculos/documentos/${docEditando.id}`, payload)
      toast.success('✅ Documento actualizado correctamente')
      setShowEditForm(false)
      setDocEditando(null)
      cargarDatos()
    } catch (error: any) {
      console.error('Error:', error)
      toast.error('Error al actualizar documento')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('¿Estás seguro de que quieres eliminar este documento?')) return
    
    try {
      await apiClient.delete(`/api/propietario/vehiculos/documentos/${id}`)
      toast.success('✅ Documento eliminado correctamente')
      cargarDatos()
    } catch (error) {
      console.error('Error:', error)
      toast.error('Error al eliminar documento')
    }
  }

  // ============================================================
  // RENDER
  // ============================================================

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  const totalDocumentos = Object.values(documentos).reduce((acc, docs) => acc + docs.length, 0)
  const documentosVencidos = Object.values(documentos).reduce((acc, docs) => {
    return acc + docs.filter(d => d.estado === 'vencido').length
  }, 0)
  const documentosProximos = Object.values(documentos).reduce((acc, docs) => {
    return acc + docs.filter(d => d.estado === 'proximo').length
  }, 0)

  return (
    <div className="space-y-6 pb-8 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 180px)' }}>
      
      {/* ============================================================
      1. HEADER
      ============================================================ */}
      <div className="flex justify-between items-center flex-wrap gap-2">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <FileText className="h-6 w-6 text-primary" />
            Documentos
          </h1>
          <p className="text-muted-foreground">Gestión de documentos de la flota</p>
        </div>
      </div>

      {/* ============================================================
      2. KPIS CENTRADOS
      ============================================================ */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Card>
          <CardContent className="pt-4 text-center">
            <p className="text-xs text-muted-foreground">Vehículos</p>
            <p className="text-xl font-bold">{vehiculos.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <p className="text-xs text-muted-foreground">Documentos</p>
            <p className="text-xl font-bold">{totalDocumentos}</p>
          </CardContent>
        </Card>
        <Card className={documentosProximos > 0 ? 'border-yellow-200 bg-yellow-50/30' : ''}>
          <CardContent className="pt-4 text-center">
            <p className="text-xs text-muted-foreground">Próximos a vencer</p>
            <p className="text-xl font-bold text-yellow-600">{documentosProximos}</p>
          </CardContent>
        </Card>
        <Card className={documentosVencidos > 0 ? 'border-red-200 bg-red-50/30' : ''}>
          <CardContent className="pt-4 text-center">
            <p className="text-xs text-muted-foreground">Vencidos</p>
            <p className="text-xl font-bold text-red-600">{documentosVencidos}</p>
          </CardContent>
        </Card>
      </div>

      {/* ============================================================
      ERRORES POR VEHÍCULO
      ============================================================ */}
      {errorVehiculos.length > 0 && (
        <Card className="border-yellow-200 bg-yellow-50/30">
          <CardContent className="pt-4 text-sm text-yellow-700">
            <AlertTriangle className="h-4 w-4 inline mr-2" />
            No se pudieron cargar documentos de: {errorVehiculos.join(', ')}
          </CardContent>
        </Card>
      )}

      {/* ============================================================
      3. FORMULARIO
      ============================================================ */}
      {showForm && (
        <Card id="documento-form" className="border-primary/20">
          <CardHeader className="py-2">
            <CardTitle className="text-base">📄 Nuevo Documento</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <form onSubmit={handleSubmit} className="space-y-3">
              {/* Tabs: Personales | Vehículo */}
              <div className="space-y-1">
                <Label className="text-sm font-medium">Documento para *</Label>
                <div className="grid grid-cols-2 gap-2 max-w-xs">
                  <Button
                    type="button"
                    variant={entidadTipo === 'propietario' ? 'default' : 'outline'}
                    onClick={() => {
                      setEntidadTipo('propietario')
                      setSelectedVehiculo('')
                    }}
                    className="text-sm h-8"
                    size="sm"
                  >
                    <User className="h-3.5 w-3.5 mr-1" />
                    Personales
                  </Button>
                  <Button
                    type="button"
                    variant={entidadTipo === 'vehiculo' ? 'default' : 'outline'}
                    onClick={() => setEntidadTipo('vehiculo')}
                    className="text-sm h-8"
                    size="sm"
                  >
                    <Car className="h-3.5 w-3.5 mr-1" />
                    Vehículo
                  </Button>
                </div>
              </div>

              {/* Selector de vehículo */}
              {entidadTipo === 'vehiculo' && (
                <div className="space-y-1 max-w-xs">
                  <Label className="text-sm">Vehículo *</Label>
                  <select
                    className="w-full p-1.5 border rounded-md text-sm h-8"
                    value={selectedVehiculo}
                    onChange={(e) => setSelectedVehiculo(e.target.value)}
                    required
                  >
                    <option value="">Seleccionar</option>
                    {vehiculos.map(v => (
                      <option key={v.id} value={v.id}>{v.patente}</option>
                    ))}
                  </select>
                </div>
              )}

              {entidadTipo === 'propietario' && propietario && (
                <div className="p-1.5 bg-muted rounded-lg text-sm flex items-center gap-2 max-w-xs">
                  <Users className="h-3.5 w-3.5 text-muted-foreground" />
                  <span className="font-medium text-sm">{propietario.nombre}</span>
                </div>
              )}

              {/* Tipo y Número */}
              <div className="flex flex-wrap gap-3 items-end">
                <div className="space-y-1">
                  <Label className="text-sm">Tipo *</Label>
                  <select
                    className="w-44 p-1.5 border rounded-md text-sm h-8"
                    value={formData.tipo_documento}
                    onChange={(e) => setFormData({...formData, tipo_documento: e.target.value})}
                    required
                  >
                    <option value="">Seleccionar</option>
                    {TIPOS_DOCUMENTOS.filter(t => t.entidad === entidadTipo).map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1">
                  <Label className="text-sm">Número *</Label>
                  <Input
                    className="text-sm h-8 w-36"
                    value={formData.numero}
                    onChange={(e) => setFormData({...formData, numero: e.target.value})}
                    placeholder="Número"
                    maxLength={15}
                    required
                  />
                </div>
              </div>

              {/* Fechas */}
              <div className="flex flex-wrap gap-3">
                <div className="space-y-1">
                  <Label className="text-sm">Emisión</Label>
                  <Input
                    type="date"
                    className="text-sm h-8 w-36"
                    value={formData.fecha_emision}
                    onChange={(e) => setFormData({...formData, fecha_emision: e.target.value})}
                  />
                </div>
                <div className="space-y-1">
                  <Label className="text-sm">Vencimiento *</Label>
                  <Input
                    type="date"
                    className="text-sm h-8 w-36"
                    value={formData.fecha_vencimiento}
                    onChange={(e) => setFormData({...formData, fecha_vencimiento: e.target.value})}
                    required
                  />
                </div>
              </div>

              <div className="space-y-1">
                <Label className="text-sm">Observaciones</Label>
                <Input
                  className="text-sm h-8 max-w-xs"
                  value={formData.observaciones}
                  onChange={(e) => setFormData({...formData, observaciones: e.target.value})}
                  placeholder="Notas adicionales (opcional)"
                />
              </div>

              {/* Imagen */}
              <div className="space-y-1 max-w-xs">
                <Label className="text-sm">Imagen de respaldo</Label>
                <div className="border-2 border-dashed rounded-lg p-2 text-center">
                  {uploadResult ? (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Cloud className="h-4 w-4 text-blue-500" />
                        <span className="text-xs text-muted-foreground">Imagen subida</span>
                      </div>
                      <div className="flex gap-2">
                        <a 
                          href={uploadResult.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline"
                        >
                          Ver
                        </a>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="h-5 px-1"
                          onClick={() => setUploadResult(null)}
                        >
                          <Trash2 className="h-3 w-3 text-red-500" />
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <CldUploadWidget
                      uploadPreset={process.env.NEXT_PUBLIC_CLOUDINARY_UPLOAD_PRESET || 'documentos_preset'}
                      options={{
                        folder: 'documentos',
                        resourceType: 'image',
                        maxFileSize: 10000000,
                      }}
                      onSuccess={(result) => {
                        const info = result.info as { secure_url: string; public_id: string }
                        if (info && info.secure_url) {
                          setUploadResult({
                            url: info.secure_url,
                            public_id: info.public_id
                          })
                          toast.success('✅ Imagen subida a Cloudinary')
                        }
                      }}
                    >
                      {({ open }) => (
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => open()}
                          className="text-sm h-7 px-3"
                        >
                          <Upload className="h-3 w-3 mr-1" />
                          Subir imagen
                        </Button>
                      )}
                    </CldUploadWidget>
                  )}
                  <p className="text-[10px] text-muted-foreground mt-1">
                    JPG, PNG, PDF (máx. 10MB)
                  </p>
                </div>
              </div>

              <div className="flex gap-2 pt-2 border-t">
                <Button type="submit" className="h-8 px-4 text-sm">
                  <Cloud className="h-3.5 w-3.5 mr-1.5" />
                  Guardar
                </Button>
                <Button type="button" variant="outline" size="sm" className="h-8 px-4 text-sm" onClick={resetForm}>
                  Cancelar
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* ============================================================
      4. EDIT FORM
      ============================================================ */}
      {showEditForm && docEditando && (
        <Card className="border-blue-200 bg-blue-50/30">
          <CardHeader className="py-2">
            <CardTitle className="text-base flex items-center gap-2 text-blue-800">
              <Edit className="h-4 w-4" />
              Editando: {docEditando.tipo_documento}
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <form onSubmit={handleEditSubmit} className="space-y-3">
              <div className="flex flex-wrap gap-3 items-end">
                <div className="space-y-1">
                  <Label className="text-sm">Tipo *</Label>
                  <select
                    className="w-44 p-1.5 border rounded-md text-sm h-8"
                    value={formEdit.tipo_documento}
                    onChange={(e) => setFormEdit({...formEdit, tipo_documento: e.target.value})}
                    required
                  >
                    <option value="">Seleccionar</option>
                    {TIPOS_DOCUMENTOS.filter(t => t.entidad === 'vehiculo').map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1">
                  <Label className="text-sm">Número *</Label>
                  <Input
                    className="text-sm h-8 w-36"
                    value={formEdit.numero}
                    onChange={(e) => setFormEdit({...formEdit, numero: e.target.value})}
                    placeholder="Número"
                    maxLength={15}
                    required
                  />
                </div>
              </div>

              <div className="flex flex-wrap gap-3">
                <div className="space-y-1">
                  <Label className="text-sm">Emisión</Label>
                  <Input
                    type="date"
                    className="text-sm h-8 w-36"
                    value={formEdit.fecha_emision}
                    onChange={(e) => setFormEdit({...formEdit, fecha_emision: e.target.value})}
                  />
                </div>
                <div className="space-y-1">
                  <Label className="text-sm">Vencimiento *</Label>
                  <Input
                    type="date"
                    className="text-sm h-8 w-36"
                    value={formEdit.fecha_vencimiento}
                    onChange={(e) => setFormEdit({...formEdit, fecha_vencimiento: e.target.value})}
                    required
                  />
                </div>
              </div>

              <div className="space-y-1">
                <Label className="text-sm">Observaciones</Label>
                <Input
                  className="text-sm h-8 max-w-xs"
                  value={formEdit.observaciones}
                  onChange={(e) => setFormEdit({...formEdit, observaciones: e.target.value})}
                  placeholder="Notas adicionales"
                />
              </div>

              <div className="space-y-1 max-w-xs">
                <Label className="text-sm">Imagen de respaldo</Label>
                <div className="border-2 border-dashed rounded-lg p-2 text-center">
                  {uploadEditResult ? (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Cloud className="h-4 w-4 text-blue-500" />
                        <span className="text-xs text-muted-foreground">Imagen subida</span>
                      </div>
                      <div className="flex gap-2">
                        <a 
                          href={uploadEditResult.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline"
                        >
                          Ver
                        </a>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="h-5 px-1"
                          onClick={() => setUploadEditResult(null)}
                        >
                          <Trash2 className="h-3 w-3 text-red-500" />
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <CldUploadWidget
                      uploadPreset={process.env.NEXT_PUBLIC_CLOUDINARY_UPLOAD_PRESET || 'documentos_preset'}
                      options={{
                        folder: 'documentos',
                        resourceType: 'image',
                        maxFileSize: 10000000,
                      }}
                      onSuccess={(result) => {
                        const info = result.info as { secure_url: string; public_id: string }
                        if (info && info.secure_url) {
                          setUploadEditResult({
                            url: info.secure_url,
                            public_id: info.public_id
                          })
                          toast.success('✅ Imagen actualizada')
                        }
                      }}
                    >
                      {({ open }) => (
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => open()}
                          className="text-sm h-7 px-3"
                        >
                          <Upload className="h-3 w-3 mr-1" />
                          Cambiar imagen
                        </Button>
                      )}
                    </CldUploadWidget>
                  )}
                  <p className="text-[10px] text-muted-foreground mt-1">
                    JPG, PNG, PDF (máx. 10MB)
                  </p>
                </div>
              </div>

              <div className="flex gap-2">
                <Button type="submit" className="h-8 px-4 text-sm">
                  <Cloud className="h-3.5 w-3.5 mr-1.5" />
                  Actualizar
                </Button>
                <Button type="button" variant="outline" size="sm" className="h-8 px-4 text-sm" onClick={() => { setShowEditForm(false); setDocEditando(null) }}>
                  Cancelar
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* ============================================================
      5. DOCUMENTOS DEL PROPIETARIO (PERSONALES)
      ============================================================ */}
      {propietario && (
        <Card className="overflow-hidden">
          <CardHeader className="py-2.5 bg-muted/20 border-b">
            <div className="flex justify-between items-center">
              <CardTitle className="text-base flex items-center gap-2">
                <User className="h-4 w-4 text-primary" />
                {propietario.nombre}
                <span className="text-xs font-normal text-muted-foreground">
                  {propietario.email}
                </span>
              </CardTitle>
              <Badge variant="outline" className="text-xs">
                {(documentos['propietario'] || []).length} documentos
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="pt-3">
            {(documentos['propietario'] || []).length === 0 ? (
              <div className="text-center py-4 text-muted-foreground text-sm">
                <User className="h-8 w-8 mx-auto mb-2 opacity-30" />
                Sin documentos personales
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {documentos['propietario'].map((doc) => {
                  const Icon = getIconForTipo(doc.tipo_documento)
                  const isVencido = doc.estado === 'vencido'
                  const isProximo = doc.estado === 'proximo'
                  
                  return (
                    <div 
                      key={doc.id} 
                      className={`border rounded-lg p-3 transition-all hover:shadow-md ${
                        isVencido ? 'border-red-200 bg-red-50/30' :
                        isProximo ? 'border-yellow-200 bg-yellow-50/30' :
                        'border-green-200 bg-green-50/30'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex items-center gap-2">
                          <Icon className={`h-4 w-4 ${
                            isVencido ? 'text-red-500' :
                            isProximo ? 'text-yellow-500' :
                            'text-green-500'
                          }`} />
                          <span className="font-medium text-sm">{doc.tipo_documento}</span>
                          <span className="text-xs text-muted-foreground">N°: {doc.numero}</span>
                        </div>
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0"
                            onClick={() => openEditForm(doc)}
                          >
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0 text-red-500 hover:text-red-700"
                            onClick={() => handleDelete(doc.id)}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                      
                      <div className="mt-2 flex items-center gap-2 text-xs">
                        <Calendar className="h-3 w-3 text-muted-foreground" />
                        <span className="text-muted-foreground">Vence:</span>
                        <span className={isVencido ? 'text-red-600 font-medium' : isProximo ? 'text-yellow-600 font-medium' : ''}>
                          {doc.fecha_vencimiento}
                        </span>
                        {doc.dias_para_vencer !== null && (
                          <Badge variant="outline" className={`text-xs ${
                            isVencido ? 'border-red-200 text-red-600' :
                            isProximo ? 'border-yellow-200 text-yellow-600' :
                            'border-green-200 text-green-600'
                          }`}>
                            {isVencido ? `Vencido (${Math.abs(doc.dias_para_vencer)}d)` : `${doc.dias_para_vencer} días`}
                          </Badge>
                        )}
                      </div>
                      
                      {doc.observaciones && (
                        <p className="mt-1 text-xs text-muted-foreground">{doc.observaciones}</p>
                      )}
                      
                      {doc.url_archivo && (
                        <div className="mt-2 flex items-center gap-2">
                          <button
                            onClick={() => setImagenModal({ 
                              url: doc.url_archivo!, 
                              titulo: `${doc.tipo_documento} N° ${doc.numero}` 
                            })}
                            className="inline-flex items-center gap-1 text-xs text-blue-600 hover:underline"
                          >
                            <Eye className="h-3 w-3" />
                            Ver imagen
                          </button>
                          <img 
                            src={doc.url_archivo} 
                            alt={doc.tipo_documento}
                            className="w-12 h-12 object-cover rounded border cursor-pointer hover:opacity-80 transition-opacity"
                            onClick={() => setImagenModal({ 
                              url: doc.url_archivo!, 
                              titulo: `${doc.tipo_documento} N° ${doc.numero}` 
                            })}
                          />
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* ============================================================
      6. DOCUMENTOS POR VEHÍCULO CON CARRUSEL (2 COLUMNAS)
      ============================================================ */}
      {vehiculos.map((vehiculo) => {
        const docs = documentos[vehiculo.id] || []
        const fotosDelVehiculo = fotosPorVehiculo[vehiculo.id] || []
        
        return (
          <Card key={vehiculo.id} className="overflow-hidden">
            {/* HEADER */}
            <CardHeader className="py-2 bg-muted/20 border-b">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <div>
                    <CardTitle className="text-base flex items-center gap-2">
                      <span>{vehiculo.patente}</span>
                      <span className="text-xs font-normal text-muted-foreground">
                        {vehiculo.marca} {vehiculo.modelo}
                      </span>
                    </CardTitle>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs">
                    {docs.length} documentos
                  </Badge>
                  <Badge variant="outline" className="text-xs bg-blue-50 text-blue-700 border-blue-200">
                    <ImageIcon className="h-3 w-3 mr-1" />
                    {fotosDelVehiculo.length} fotos
                  </Badge>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="pt-3">
              {/* ✅ 2 COLUMNAS: DOCUMENTOS | CARRUSEL */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                
                {/* COLUMNA IZQUIERDA: DOCUMENTOS */}
                <div className="space-y-3">
                  {docs.length === 0 ? (
                    <div className="text-center py-4 text-muted-foreground text-sm border rounded-lg">
                      <FileText className="h-8 w-8 mx-auto mb-2 opacity-30" />
                      Sin documentos registrados
                    </div>
                  ) : (
                    docs.map((doc) => {
                      const Icon = getIconForTipo(doc.tipo_documento)
                      const isVencido = doc.estado === 'vencido'
                      const isProximo = doc.estado === 'proximo'
                      
                      return (
                        <div 
                          key={doc.id} 
                          className={`border rounded-lg p-3 transition-all hover:shadow-md ${
                            isVencido ? 'border-red-200 bg-red-50/30' :
                            isProximo ? 'border-yellow-200 bg-yellow-50/30' :
                            'border-green-200 bg-green-50/30'
                          }`}
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex items-center gap-2 min-w-0">
                              <Icon className={`h-4 w-4 flex-shrink-0 ${
                                isVencido ? 'text-red-500' :
                                isProximo ? 'text-yellow-500' :
                                'text-green-500'
                              }`} />
                              <span className="font-medium text-sm truncate">{doc.tipo_documento}</span>
                              <span className="text-xs text-muted-foreground truncate">N°: {doc.numero}</span>
                            </div>
                            <div className="flex gap-1 flex-shrink-0">
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0"
                                onClick={() => openEditForm(doc)}
                              >
                                <Edit className="h-3 w-3" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0 text-red-500 hover:text-red-700"
                                onClick={() => handleDelete(doc.id)}
                              >
                                <Trash2 className="h-3 w-3" />
                              </Button>
                            </div>
                          </div>
                          
                          <div className="mt-1 flex items-center gap-2 text-xs flex-wrap">
                            <Calendar className="h-3 w-3 text-muted-foreground flex-shrink-0" />
                            <span className="text-muted-foreground">Vence:</span>
                            <span className={isVencido ? 'text-red-600 font-medium' : isProximo ? 'text-yellow-600 font-medium' : ''}>
                              {doc.fecha_vencimiento}
                            </span>
                            {doc.dias_para_vencer !== null && (
                              <Badge variant="outline" className={`text-xs ${
                                isVencido ? 'border-red-200 text-red-600' :
                                isProximo ? 'border-yellow-200 text-yellow-600' :
                                'border-green-200 text-green-600'
                              }`}>
                                {isVencido ? `Vencido (${Math.abs(doc.dias_para_vencer)}d)` : `${doc.dias_para_vencer} días`}
                              </Badge>
                            )}
                          </div>
                          
                          {doc.observaciones && (
                            <p className="mt-1 text-xs text-muted-foreground line-clamp-1">{doc.observaciones}</p>
                          )}
                          
                          {doc.url_archivo && (
                            <div className="mt-2 flex items-center gap-2">
                              <button
                                onClick={() => setImagenModal({ 
                                  url: doc.url_archivo!, 
                                  titulo: `${doc.tipo_documento} N° ${doc.numero}` 
                                })}
                                className="inline-flex items-center gap-1 text-xs text-blue-600 hover:underline"
                              >
                                <Eye className="h-3 w-3" />
                                Ver imagen
                              </button>
                              <img 
                                src={doc.url_archivo} 
                                alt={doc.tipo_documento}
                                className="w-10 h-10 object-cover rounded border cursor-pointer hover:opacity-80 transition-opacity flex-shrink-0"
                                onClick={() => setImagenModal({ 
                                  url: doc.url_archivo!, 
                                  titulo: `${doc.tipo_documento} N° ${doc.numero}` 
                                })}
                              />
                            </div>
                          )}
                        </div>
                      )
                    })
                  )}
                </div>
                
                {/* COLUMNA DERECHA: CARRUSEL DE FOTOS */}
                <div>
                  <GaleriaVehiculo 
                    vehiculoId={vehiculo.id} 
                    compact={true}
                    onFotosChange={(fotos) => {
                      setFotosPorVehiculo(prev => ({
                        ...prev,
                        [vehiculo.id]: fotos
                      }))
                    }}
                  />
                </div>
                
              </div>
            </CardContent>
          </Card>
        )
      })}

      <div className="h-4" />

      {/* ============================================================
      BOTÓN FLOTANTE
      ============================================================ */}
      <div className="fixed bottom-8 right-8 z-50">
        <Button
          onClick={() => setShowForm(!showForm)}
          className="h-14 px-6 rounded-full shadow-lg bg-primary hover:bg-primary/90 text-white font-medium flex items-center gap-2 transition-all hover:scale-105 hover:shadow-xl"
        >
          <Plus className="h-5 w-5" />
          Ingresar Documento
        </Button>
      </div>

      {/* ============================================================
      MODAL DE IMAGEN
      ============================================================ */}
      {imagenModal && (
        <ModalImagen
          url={imagenModal.url}
          titulo={imagenModal.titulo}
          onClose={() => setImagenModal(null)}
        />
      )}

    </div>
  )
}