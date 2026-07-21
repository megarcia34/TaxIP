'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Search, Mail, Send, Inbox, Star, Archive, Trash, 
  Loader2, Plus, RefreshCw, AlertCircle 
} from 'lucide-react'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import { es } from 'date-fns/locale'
import { toast } from 'sonner'

interface Email {
  id: string
  from: string
  to: string
  subject: string
  body: string
  read: boolean
  important: boolean
  archived: boolean
  deleted: boolean
  created_at: string
}

// Datos iniciales mock
const initialMockEmails: Email[] = [
  {
    id: '1',
    from: 'admin@taxip.com',
    to: 'chofer1@taxip.com',
    subject: 'Bienvenido a TaxIP',
    body: 'Bienvenido a la plataforma TaxIP. Esperamos que tengas una excelente experiencia.',
    read: false,
    important: true,
    archived: false,
    deleted: false,
    created_at: new Date().toISOString(),
  },
  {
    id: '2',
    from: 'soporte@taxip.com',
    to: 'admin@taxip.com',
    subject: 'Actualización del sistema',
    body: 'El sistema se actualizará esta noche a las 2:00 AM. Por favor guarda tus cambios.',
    read: true,
    important: false,
    archived: false,
    deleted: false,
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: '3',
    from: 'facturacion@taxip.com',
    to: 'admin@taxip.com',
    subject: 'Factura mensual',
    body: 'Adjuntamos la factura correspondiente al mes de enero. Total: $45,000',
    read: false,
    important: true,
    archived: false,
    deleted: false,
    created_at: new Date(Date.now() - 172800000).toISOString(),
  },
  {
    id: '4',
    from: 'admin@taxip.com',
    to: 'soporte@taxip.com',
    subject: 'Consulta sobre pagos',
    body: 'Buen día, necesito información sobre los pagos del mes pasado.',
    read: true,
    important: false,
    archived: false,
    deleted: false,
    created_at: new Date(Date.now() - 259200000).toISOString(),
  },
]

export default function EmailInboxPage() {
  const [search, setSearch] = useState('')
  const [activeFolder, setActiveFolder] = useState('inbox')
  const queryClient = useQueryClient()

  // Cargar emails (mock por ahora)
  const { data: emails = initialMockEmails, isLoading } = useQuery({
    queryKey: ['emails'],
    queryFn: async () => {
      // Aquí se conectará al backend real después
      return initialMockEmails
    },
  })

  // Marcar como leído
  const markAsReadMutation = useMutation({
    mutationFn: async (id: string) => {
      // Aquí irá la llamada al backend
      return { id }
    },
    onSuccess: (_, id) => {
      queryClient.setQueryData(['emails'], (old: Email[]) => {
        return old.map(email => 
          email.id === id ? { ...email, read: true } : email
        )
      })
    },
  })

  // Marcar como importante
  const toggleImportantMutation = useMutation({
    mutationFn: async (id: string) => {
      return { id }
    },
    onSuccess: (_, id) => {
      queryClient.setQueryData(['emails'], (old: Email[]) => {
        return old.map(email => 
          email.id === id ? { ...email, important: !email.important } : email
        )
      })
      const email = emails.find(e => e.id === id)
      toast.success(email?.important ? 'Eliminado de importantes' : 'Marcado como importante')
    },
  })

  // Archivar
  const archiveMutation = useMutation({
    mutationFn: async (id: string) => {
      return { id }
    },
    onSuccess: (_, id) => {
      queryClient.setQueryData(['emails'], (old: Email[]) => {
        return old.map(email => 
          email.id === id ? { ...email, archived: true, deleted: false } : email
        )
      })
      toast.success('Correo archivado')
    },
  })

  // Mover a papelera
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      return { id }
    },
    onSuccess: (_, id) => {
      queryClient.setQueryData(['emails'], (old: Email[]) => {
        return old.map(email => 
          email.id === id ? { ...email, deleted: true, archived: false } : email
        )
      })
      toast.success('Correo movido a la papelera')
    },
  })

  // Restaurar desde papelera
  const restoreMutation = useMutation({
    mutationFn: async (id: string) => {
      return { id }
    },
    onSuccess: (_, id) => {
      queryClient.setQueryData(['emails'], (old: Email[]) => {
        return old.map(email => 
          email.id === id ? { ...email, deleted: false, archived: false } : email
        )
      })
      toast.success('Correo restaurado')
    },
  })

  // Eliminar permanentemente
  const permanentDeleteMutation = useMutation({
    mutationFn: async (id: string) => {
      return { id }
    },
    onSuccess: (_, id) => {
      queryClient.setQueryData(['emails'], (old: Email[]) => {
        return old.filter(email => email.id !== id)
      })
      toast.success('Correo eliminado permanentemente')
    },
  })

  // Filtrar emails según la carpeta activa
  const getFilteredEmails = () => {
    let filtered = [...emails]

    // Aplicar filtro de carpeta
    switch (activeFolder) {
      case 'inbox':
        filtered = filtered.filter(e => !e.deleted && !e.archived && e.to === 'admin@taxip.com')
        break
      case 'sent':
        filtered = filtered.filter(e => !e.deleted && e.from === 'admin@taxip.com')
        break
      case 'important':
        filtered = filtered.filter(e => !e.deleted && e.important)
        break
      case 'archive':
        filtered = filtered.filter(e => e.archived && !e.deleted)
        break
      case 'trash':
        filtered = filtered.filter(e => e.deleted)
        break
      default:
        filtered = filtered.filter(e => !e.deleted)
    }

    // Aplicar búsqueda
    if (search) {
      filtered = filtered.filter(e =>
        e.subject.toLowerCase().includes(search.toLowerCase()) ||
        e.from.toLowerCase().includes(search.toLowerCase()) ||
        e.to.toLowerCase().includes(search.toLowerCase())
      )
    }

    // Ordenar por fecha (más reciente primero)
    return filtered.sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  }

  const filteredEmails = getFilteredEmails()
  const folderNames = {
    inbox: 'Recibidos',
    sent: 'Enviados',
    important: 'Importantes',
    archive: 'Archivo',
    trash: 'Papelera',
  }

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Email</h1>
        <p className="text-muted-foreground">
          Bandeja de entrada y comunicación interna
        </p>
      </div>

      <div className="flex flex-col gap-6 lg:flex-row">
        {/* Sidebar de carpetas */}
        <div className="w-full lg:w-64 shrink-0 space-y-2">
          <Link href="/email/compose">
            <Button className="w-full">
              <Plus className="h-4 w-4 mr-2" />
              Redactar
            </Button>
          </Link>
          
          <div className="space-y-1">
            {[
              { id: 'inbox', label: 'Recibidos', icon: Inbox, count: emails.filter(e => !e.deleted && !e.archived && e.to === 'admin@taxip.com').length },
              { id: 'sent', label: 'Enviados', icon: Send, count: emails.filter(e => !e.deleted && e.from === 'admin@taxip.com').length },
              { id: 'important', label: 'Importantes', icon: Star, count: emails.filter(e => !e.deleted && e.important).length },
              { id: 'archive', label: 'Archivo', icon: Archive, count: emails.filter(e => e.archived && !e.deleted).length },
              { id: 'trash', label: 'Papelera', icon: Trash, count: emails.filter(e => e.deleted).length },
            ].map((folder) => (
              <Button
                key={folder.id}
                variant={activeFolder === folder.id ? 'secondary' : 'ghost'}
                className="w-full justify-between"
                onClick={() => setActiveFolder(folder.id)}
              >
                <span className="flex items-center">
                  <folder.icon className="h-4 w-4 mr-2" />
                  {folder.label}
                </span>
                {folder.count > 0 && (
                  <Badge variant="secondary" className="ml-auto">
                    {folder.count}
                  </Badge>
                )}
              </Button>
            ))}
          </div>
        </div>

        {/* Lista de emails */}
        <Card className="flex-1">
          <CardHeader>
            <CardTitle className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <span>{folderNames[activeFolder as keyof typeof folderNames]}</span>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por asunto, remitente o destinatario..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-8 w-full sm:w-80"
                />
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {filteredEmails.length === 0 ? (
                <div className="text-center py-12">
                  <Mail className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">
                    No hay correos en {folderNames[activeFolder as keyof typeof folderNames].toLowerCase()}
                  </p>
                </div>
              ) : (
                filteredEmails.map((email) => (
                  <div
                    key={email.id}
                    className={`group relative rounded-lg border p-3 hover:bg-muted/50 transition-colors ${!email.read ? 'bg-muted/30' : ''}`}
                  >
                    <Link href={`/email/view/${email.id}`} className="block">
                      <div className="flex items-start gap-3">
                        <div className="flex items-center gap-2 shrink-0">
                          {email.important && (
                            <Star className="h-4 w-4 fill-yellow-500 text-yellow-500" />
                          )}
                          <Mail className={`h-4 w-4 ${!email.read ? 'text-primary' : 'text-muted-foreground'}`} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex flex-wrap items-center justify-between gap-2">
                            <span className={`font-medium truncate ${!email.read ? 'font-semibold' : ''}`}>
                              {activeFolder === 'sent' ? email.to : email.from}
                            </span>
                            <span className="text-xs text-muted-foreground shrink-0">
                              {formatDistanceToNow(new Date(email.created_at), { addSuffix: true, locale: es })}
                            </span>
                          </div>
                          <p className={`text-sm truncate ${!email.read ? 'font-medium' : 'text-muted-foreground'}`}>
                            {email.subject}
                          </p>
                          <p className="text-xs text-muted-foreground truncate mt-1">
                            {email.body.substring(0, 100)}...
                          </p>
                        </div>
                        <Badge variant={email.read ? 'outline' : 'default'} className="shrink-0">
                          {email.read ? 'Leído' : 'Nuevo'}
                        </Badge>
                      </div>
                    </Link>
                    
                    {/* Acciones rápidas */}
                    <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1 bg-background rounded-md p-1 shadow-sm">
                      {activeFolder !== 'trash' && (
                        <>
                          {!email.read && (
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-7 px-2"
                              onClick={(e) => {
                                e.preventDefault()
                                markAsReadMutation.mutate(email.id)
                              }}
                            >
                              Marcar leído
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-7 px-2"
                            onClick={(e) => {
                              e.preventDefault()
                              toggleImportantMutation.mutate(email.id)
                            }}
                          >
                            {email.important ? 'No importante' : 'Importante'}
                          </Button>
                          {activeFolder !== 'archive' && (
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-7 px-2"
                              onClick={(e) => {
                                e.preventDefault()
                                archiveMutation.mutate(email.id)
                              }}
                            >
                              Archivar
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-7 px-2 text-red-500 hover:text-red-600"
                            onClick={(e) => {
                              e.preventDefault()
                              deleteMutation.mutate(email.id)
                            }}
                          >
                            Eliminar
                          </Button>
                        </>
                      )}
                      {activeFolder === 'trash' && (
                        <>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-7 px-2"
                            onClick={(e) => {
                              e.preventDefault()
                              restoreMutation.mutate(email.id)
                            }}
                          >
                            Restaurar
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-7 px-2 text-red-500 hover:text-red-600"
                            onClick={(e) => {
                              e.preventDefault()
                              permanentDeleteMutation.mutate(email.id)
                            }}
                          >
                            Eliminar permanentemente
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}