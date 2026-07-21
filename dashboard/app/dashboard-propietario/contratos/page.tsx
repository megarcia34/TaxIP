'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { FileText, Users, Car, Calendar, Loader2, Plus, CheckCircle, XCircle } from 'lucide-react'
import { toast } from 'sonner'
import Link from 'next/link'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { apiClient, propietarioAPI } from '@/lib/api'

interface Contrato {
  id: string
  vehiculo_id: string
  patente: string
  marca: string
  modelo: string
  chofer_id: string
  chofer_nombre: string
  chofer_apellido: string
  tipo_contrato: string
  turno_asignado: string
  porcentaje_chofer: number | null
  monto_diario: number | null
  fecha_inicio: string
  fecha_fin: string | null
  activo: boolean
}

interface ChoferDisponible {
  id: string
  email: string
  nombre: string
  apellido: string
  telefono: string
  calificacion_promedio: number
  total_calificaciones: number
}

interface VehiculoSimple {
  id: string
  patente: string
  marca: string
  modelo: string
}

export default function PropietarioContratosPage() {
  const router = useRouter()
  const { user } = useAuth()
  
  // ✅ Estado para propietario_id (leído desde la URL)
  const [propietarioId, setPropietarioId] = useState<string | null>(null)
  
  const [contratos, setContratos] = useState<Contrato[]>([])
  const [loading, setLoading] = useState(true)
  const [filterActivo, setFilterActivo] = useState<boolean | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [vehiculos, setVehiculos] = useState<VehiculoSimple[]>([])
  const [choferes, setChoferes] = useState<ChoferDisponible[]>([])
  const [loadingForm, setLoadingForm] = useState(false)

  const isAdmin = user?.rol === 'admin'

  // ✅ Leer propietario_id de la URL usando window.location
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    setPropietarioId(params.get('propietario_id'))
  }, [])

  const [formData, setFormData] = useState({
    vehiculo_id: '',
    chofer_id: '',
    tipo_contrato: 'PORCENTAJE',
    turno_asignado: 'DIURNO',
    porcentaje_chofer: 50,
    monto_diario: 0,
  })

  // ============================================
  // CARGAR CONTRATOS - USANDO apiClient
  // ============================================
  const cargarContratos = async () => {
    setLoading(true)
    try {
      // El interceptor de apiClient agrega automáticamente:
      // - Authorization: Bearer <token>
      // - X-Propietario-ID: <id> (si es admin)
      const data = await propietarioAPI.getContratos(filterActivo ?? undefined)
      setContratos(data)
    } catch (error: any) {
      console.error('Error al cargar contratos:', error)
      toast.error(error?.response?.data?.detail || 'Error al cargar contratos')
    } finally {
      setLoading(false)
    }
  }

  // ============================================
  // CARGAR VEHÍCULOS Y CHOFERES - USANDO apiClient
  // ============================================
  const cargarVehiculosYChoferes = async () => {
    try {
      // Vehículos
      const dataV = await propietarioAPI.getVehiculos()
      setVehiculos(dataV)

      // Choferes disponibles (por defecto DIURNO)
      const dataC = await propietarioAPI.getChoferesDisponibles('DIURNO')
      setChoferes(dataC)
    } catch (error: any) {
      console.error('Error al cargar vehículos/choferes:', error)
      toast.error('Error al cargar datos del formulario')
    }
  }

  useEffect(() => {
    if (user) {
      cargarContratos()
    }
  }, [user, propietarioId, filterActivo])

  // ============================================
  // CREAR CONTRATO - USANDO apiClient
  // ============================================
  const handleCrearContrato = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoadingForm(true)

    try {
      const payload = {
        vehiculo_id: formData.vehiculo_id,
        chofer_id: formData.chofer_id,
        tipo_contrato: formData.tipo_contrato,
        turno_asignado: formData.turno_asignado,
        porcentaje_chofer: formData.tipo_contrato === 'PORCENTAJE' ? formData.porcentaje_chofer : null,
        monto_diario: formData.tipo_contrato === 'CANON_FIJO' ? formData.monto_diario : null,
      }

      await propietarioAPI.createContrato(payload)

      toast.success('Contrato creado correctamente')
      setShowModal(false)
      cargarContratos()
      setFormData({
        vehiculo_id: '',
        chofer_id: '',
        tipo_contrato: 'PORCENTAJE',
        turno_asignado: 'DIURNO',
        porcentaje_chofer: 50,
        monto_diario: 0,
      })
    } catch (error: any) {
      console.error('Error al crear contrato:', error)
      toast.error(error?.response?.data?.detail || 'Error al crear contrato')
    } finally {
      setLoadingForm(false)
    }
  }

  // ============================================
  // FINALIZAR CONTRATO - USANDO apiClient
  // ============================================
  const finalizarContrato = async (contratoId: string) => {
    try {
      await propietarioAPI.finalizarContrato(contratoId)
      toast.success('Contrato finalizado correctamente')
      cargarContratos()
    } catch (error: any) {
      console.error('Error al finalizar contrato:', error)
      toast.error(error?.response?.data?.detail || 'Error al finalizar contrato')
    }
  }

  const getTipoContratoLabel = (tipo: string) => {
    const tipos: Record<string, string> = {
      AUTO_GESTION: 'Auto-gestión',
      PORCENTAJE: 'A porcentaje',
      CANON_FIJO: 'Canon fijo'
    }
    return tipos[tipo] || tipo
  }

  const getTurnoLabel = (turno: string) => {
    const turnos: Record<string, string> = {
      DIURNO: 'Diurno',
      NOCTURNO: 'Nocturno',
      COMPLETO: 'Completo'
    }
    return turnos[turno] || turno
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Contratos</h1>
          <p className="text-muted-foreground">
            Gestión de contratos de vehículos
          </p>
        </div>
        <Button onClick={() => { setShowModal(true); cargarVehiculosYChoferes() }}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Contrato
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Listado de Contratos</CardTitle>
            <Tabs 
              value={filterActivo === null ? 'todos' : filterActivo ? 'activos' : 'inactivos'}
              onValueChange={(v) => {
                if (v === 'todos') setFilterActivo(null)
                else if (v === 'activos') setFilterActivo(true)
                else setFilterActivo(false)
              }}
            >
              <TabsList>
                <TabsTrigger value="todos">Todos</TabsTrigger>
                <TabsTrigger value="activos">Activos</TabsTrigger>
                <TabsTrigger value="inactivos">Finalizados</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </CardHeader>
        <CardContent>
          {contratos.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
              <p>No hay contratos registrados</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3">Vehículo</th>
                    <th className="text-left py-3">Chofer</th>
                    <th className="text-left py-3">Tipo</th>
                    <th className="text-left py-3">Turno</th>
                    <th className="text-left py-3">Estado</th>
                    <th className="text-left py-3">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {contratos.map((c) => (
                    <tr key={c.id} className="border-b hover:bg-muted/50">
                      <td className="py-3">
                        <div>
                          <span className="font-medium">{c.patente}</span>
                          <span className="text-xs text-muted-foreground ml-2">
                            {c.marca} {c.modelo}
                          </span>
                        </div>
                      </td>
                      <td className="py-3">
                        {c.chofer_nombre} {c.chofer_apellido || ''}
                      </td>
                      <td className="py-3">
                        <Badge variant="outline">{getTipoContratoLabel(c.tipo_contrato)}</Badge>
                      </td>
                      <td className="py-3">{getTurnoLabel(c.turno_asignado)}</td>
                      <td className="py-3">
                        <Badge className={c.activo ? 'bg-green-500' : 'bg-gray-500'}>
                          {c.activo ? 'Activo' : 'Finalizado'}
                        </Badge>
                      </td>
                      <td className="py-3">
                        {c.activo && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => finalizarContrato(c.id)}
                            className="text-red-500 hover:text-red-600"
                          >
                            <XCircle className="h-4 w-4 mr-1" />
                            Finalizar
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal Nuevo Contrato */}
      <Dialog open={showModal} onOpenChange={setShowModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Nuevo Contrato</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCrearContrato}>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Vehículo</Label>
                <Select
                  value={formData.vehiculo_id}
                  onValueChange={(v) => setFormData({ ...formData, vehiculo_id: v })}
                  required
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar vehículo" />
                  </SelectTrigger>
                  <SelectContent>
                    {vehiculos.map((v) => (
                      <SelectItem key={v.id} value={v.id}>
                        {v.patente} - {v.marca} {v.modelo}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Chofer</Label>
                <Select
                  value={formData.chofer_id}
                  onValueChange={(v) => setFormData({ ...formData, chofer_id: v })}
                  required
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar chofer" />
                  </SelectTrigger>
                  <SelectContent>
                    {choferes.map((c) => (
                      <SelectItem key={c.id} value={c.id}>
                        {c.nombre} {c.apellido} ({c.email})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Tipo de Contrato</Label>
                  <Select
                    value={formData.tipo_contrato}
                    onValueChange={(v) => setFormData({ ...formData, tipo_contrato: v })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="AUTO_GESTION">Auto-gestión</SelectItem>
                      <SelectItem value="PORCENTAJE">A porcentaje</SelectItem>
                      <SelectItem value="CANON_FIJO">Canon fijo</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Turno</Label>
                  <Select
                    value={formData.turno_asignado}
                    onValueChange={(v) => setFormData({ ...formData, turno_asignado: v })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="DIURNO">Diurno</SelectItem>
                      <SelectItem value="NOCTURNO">Nocturno</SelectItem>
                      <SelectItem value="COMPLETO">Completo</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {formData.tipo_contrato === 'PORCENTAJE' && (
                <div className="space-y-2">
                  <Label>Porcentaje del Chofer (%)</Label>
                  <Input
                    type="number"
                    min="0"
                    max="100"
                    value={formData.porcentaje_chofer}
                    onChange={(e) => setFormData({ ...formData, porcentaje_chofer: Number(e.target.value) })}
                    required
                  />
                </div>
              )}

              {formData.tipo_contrato === 'CANON_FIJO' && (
                <div className="space-y-2">
                  <Label>Monto Diario ($)</Label>
                  <Input
                    type="number"
                    min="0"
                    value={formData.monto_diario}
                    onChange={(e) => setFormData({ ...formData, monto_diario: Number(e.target.value) })}
                    required
                  />
                </div>
              )}
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowModal(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={loadingForm}>
                {loadingForm && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                Crear Contrato
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}