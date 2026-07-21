'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
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
import { Search, Plus, DollarSign, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { apiClient } from '@/lib/api'

interface Ingreso {
  id: string
  tipo: 'viaje' | 'recaudacion_manual' | 'canon'
  monto: number
  fecha: string
  descripcion: string
  vehiculo_patente: string
  chofer_nombre: string
}

interface VehiculoSimple {
  id: string
  patente: string
  marca: string
  modelo: string
}

interface ContratoSimple {
  id: string
  patente: string
  monto_diario: number
}

export default function PropietarioIngresosPage() {
  const router = useRouter()
  const { user } = useAuth()
  
  // ✅ Estado para propietario_id (leído desde la URL)
  const [propietarioId, setPropietarioId] = useState<string | null>(null)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    setPropietarioId(params.get('propietario_id'))
  }, [])
  
  const [ingresos, setIngresos] = useState<Ingreso[]>([])
  const [vehiculos, setVehiculos] = useState<VehiculoSimple[]>([])
  const [contratos, setContratos] = useState<ContratoSimple[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [showRecaudacionModal, setShowRecaudacionModal] = useState(false)
  const [showCanonModal, setShowCanonModal] = useState(false)
  const [loadingForm, setLoadingForm] = useState(false)

  const isAdmin = user?.rol === 'admin'
  // ✅ Usar el estado 'propietarioId' en lugar de searchParams
  // const propietarioId = searchParams?.get('propietario_id')  // ← ELIMINAR

  const [recaudacionData, setRecaudacionData] = useState({
    vehiculo_id: '',
    monto: 0,
    descripcion: '',
    fecha: new Date().toISOString().split('T')[0],
  })

  const [canonData, setCanonData] = useState({
    contrato_id: '',
    monto: 0,
    fecha_pago: new Date().toISOString().split('T')[0],
  })

  const cargarIngresos = async () => {
    setLoading(true)
    try {
      const res = await apiClient.get('/api/propietario/ingresos')
      setIngresos(res.data)
    } catch (error: any) {
      console.error('Error al cargar ingresos:', error)
      toast.error(error?.response?.data?.detail || 'Error al cargar ingresos')
    } finally {
      setLoading(false)
    }
  }

  const cargarVehiculosYContratos = async () => {
    try {
      const [vehiculosRes, contratosRes] = await Promise.all([
        apiClient.get('/api/propietario/vehiculos'),
        apiClient.get('/api/propietario/contratos?activo=true')
      ])
      setVehiculos(vehiculosRes.data)
      setContratos(contratosRes.data)
    } catch (error: any) {
      console.error('Error al cargar vehículos/contratos:', error)
      toast.error('Error al cargar datos del formulario')
    }
  }

  useEffect(() => {
    if (user) {
      cargarIngresos()
      cargarVehiculosYContratos()
    }
  }, [user, propietarioId])

  const registrarRecaudacion = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoadingForm(true)

    try {
      await apiClient.post('/api/propietario/ingresos/recaudacion-manual', recaudacionData)
      toast.success('Recaudación registrada correctamente')
      setShowRecaudacionModal(false)
      cargarIngresos()
      setRecaudacionData({
        vehiculo_id: '',
        monto: 0,
        descripcion: '',
        fecha: new Date().toISOString().split('T')[0],
      })
    } catch (error: any) {
      console.error('Error al registrar recaudación:', error)
      toast.error(error?.response?.data?.detail || 'Error al registrar recaudación')
    } finally {
      setLoadingForm(false)
    }
  }

  const registrarCanon = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoadingForm(true)

    try {
      await apiClient.post('/api/propietario/ingresos/canon/pagar', canonData)
      toast.success('Pago de canon registrado correctamente')
      setShowCanonModal(false)
      cargarIngresos()
      setCanonData({
        contrato_id: '',
        monto: 0,
        fecha_pago: new Date().toISOString().split('T')[0],
      })
    } catch (error: any) {
      console.error('Error al registrar pago de canon:', error)
      toast.error(error?.response?.data?.detail || 'Error al registrar pago de canon')
    } finally {
      setLoadingForm(false)
    }
  }

  const getTipoLabel = (tipo: string) => {
    const tipos: Record<string, { label: string, variant: 'default' | 'success' | 'warning' }> = {
      viaje: { label: 'Viaje', variant: 'default' },
      recaudacion_manual: { label: 'Recaudación Manual', variant: 'warning' },
      canon: { label: 'Canon', variant: 'success' }
    }
    return tipos[tipo] || { label: tipo, variant: 'default' }
  }

  const filteredIngresos = ingresos.filter(i =>
    i.vehiculo_patente?.toLowerCase().includes(search.toLowerCase()) ||
    i.descripcion?.toLowerCase().includes(search.toLowerCase()) ||
    i.chofer_nombre?.toLowerCase().includes(search.toLowerCase())
  )

  const totalIngresos = filteredIngresos.reduce((sum, i) => sum + i.monto, 0)

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
          <h1 className="text-2xl font-bold">Ingresos</h1>
          <p className="text-muted-foreground">
            Gestión de ingresos de la flota
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => { setShowRecaudacionModal(true); cargarVehiculosYContratos() }}>
            <Plus className="h-4 w-4 mr-2" />
            Recaudación Manual
          </Button>
          <Button onClick={() => { setShowCanonModal(true); cargarVehiculosYContratos() }}>
            <Plus className="h-4 w-4 mr-2" />
            Pago de Canon
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Listado de Ingresos</CardTitle>
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium">
                Total: <span className="text-green-600 font-bold">${totalIngresos.toLocaleString()}</span>
              </span>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por vehículo o descripción..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-8 w-64"
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {filteredIngresos.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <DollarSign className="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
              <p>No hay ingresos registrados</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3">Vehículo</th>
                    <th className="text-left py-3">Tipo</th>
                    <th className="text-left py-3">Monto</th>
                    <th className="text-left py-3">Descripción</th>
                    <th className="text-left py-3">Chofer</th>
                    <th className="text-left py-3">Fecha</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredIngresos.map((i) => {
                    const tipo = getTipoLabel(i.tipo)
                    return (
                      <tr key={i.id} className="border-b hover:bg-muted/50">
                        <td className="py-3 font-medium">{i.vehiculo_patente}</td>
                        <td className="py-3">
                          <Badge variant={tipo.variant as any}>{tipo.label}</Badge>
                        </td>
                        <td className="py-3 font-semibold text-green-600">
                          ${i.monto.toLocaleString()}
                        </td>
                        <td className="py-3 text-muted-foreground">{i.descripcion || '-'}</td>
                        <td className="py-3">{i.chofer_nombre || '-'}</td>
                        <td className="py-3">{new Date(i.fecha).toLocaleDateString()}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={showRecaudacionModal} onOpenChange={setShowRecaudacionModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Registrar Recaudación Manual</DialogTitle>
          </DialogHeader>
          <form onSubmit={registrarRecaudacion}>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Vehículo</Label>
                <Select
                  value={recaudacionData.vehiculo_id}
                  onValueChange={(v) => setRecaudacionData({ ...recaudacionData, vehiculo_id: v })}
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
                <Label>Monto ($)</Label>
                <Input
                  type="number"
                  min="0"
                  step="0.01"
                  value={recaudacionData.monto}
                  onChange={(e) => setRecaudacionData({ ...recaudacionData, monto: Number(e.target.value) })}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label>Descripción</Label>
                <Input
                  value={recaudacionData.descripcion}
                  onChange={(e) => setRecaudacionData({ ...recaudacionData, descripcion: e.target.value })}
                  placeholder="Descripción de la recaudación..."
                />
              </div>

              <div className="space-y-2">
                <Label>Fecha</Label>
                <Input
                  type="date"
                  value={recaudacionData.fecha}
                  onChange={(e) => setRecaudacionData({ ...recaudacionData, fecha: e.target.value })}
                  required
                />
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowRecaudacionModal(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={loadingForm}>
                {loadingForm && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                Registrar
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={showCanonModal} onOpenChange={setShowCanonModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Registrar Pago de Canon</DialogTitle>
          </DialogHeader>
          <form onSubmit={registrarCanon}>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Contrato</Label>
                <Select
                  value={canonData.contrato_id}
                  onValueChange={(v) => {
                    const contrato = contratos.find(c => c.id === v)
                    setCanonData({ 
                      ...canonData, 
                      contrato_id: v,
                      monto: contrato?.monto_diario || 0 
                    })
                  }}
                  required
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar contrato" />
                  </SelectTrigger>
                  <SelectContent>
                    {contratos.map((c) => (
                      <SelectItem key={c.id} value={c.id}>
                        {c.patente} - ${c.monto_diario}/día
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Monto ($)</Label>
                <Input
                  type="number"
                  min="0"
                  step="0.01"
                  value={canonData.monto}
                  onChange={(e) => setCanonData({ ...canonData, monto: Number(e.target.value) })}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label>Fecha de Pago</Label>
                <Input
                  type="date"
                  value={canonData.fecha_pago}
                  onChange={(e) => setCanonData({ ...canonData, fecha_pago: e.target.value })}
                  required
                />
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowCanonModal(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={loadingForm}>
                {loadingForm && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                Registrar
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}