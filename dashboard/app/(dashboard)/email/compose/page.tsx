'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { ArrowLeft, Send, Save, Loader2, User, Mail, MessageSquare } from 'lucide-react'
import { toast } from 'sonner'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

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
  draft: boolean
  created_at: string
}

// Usuarios disponibles para enviar correos
const availableRecipients = [
  { value: 'chofer1@taxip.com', label: 'Carlos Pérez (Chofer)' },
  { value: 'chofer2@taxip.com', label: 'María González (Chofer)' },
  { value: 'pasajero1@taxip.com', label: 'Juan López (Pasajero)' },
  { value: 'admin@taxip.com', label: 'Administrador' },
  { value: 'soporte@taxip.com', label: 'Soporte Técnico' },
  { value: 'facturacion@taxip.com', label: 'Facturación' },
]

export default function ComposeEmailPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [isSending, setIsSending] = useState(false)
  const [isDraft, setIsDraft] = useState(false)
  const [formData, setFormData] = useState({
    to: '',
    subject: '',
    body: '',
  })

  // Mutación para enviar/guardar correo
  const sendMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      // Crear nuevo email
      const newEmail: Email = {
        id: Date.now().toString(),
        from: 'admin@taxip.com',
        to: data.to,
        subject: data.subject,
        body: data.body,
        read: false,
        important: false,
        archived: false,
        deleted: false,
        draft: isDraft,
        created_at: new Date().toISOString(),
      }
      
      // Simular envío a backend
      await new Promise(resolve => setTimeout(resolve, 500))
      
      return newEmail
    },
    onSuccess: (newEmail) => {
      // Agregar el nuevo email al caché
      queryClient.setQueryData(['emails'], (old: Email[] = []) => {
        return [newEmail, ...old]
      })
      
      if (isDraft) {
        toast.success('Borrador guardado correctamente')
        // Limpiar formulario para nuevo borrador
        setFormData({ to: '', subject: '', body: '' })
        setIsSending(false)
        setIsDraft(false)
      } else {
        toast.success('Correo enviado correctamente')
        router.push('/email')
      }
    },
    onError: () => {
      toast.error('Error al enviar el correo')
      setIsSending(false)
    },
  })

  const handleSend = () => {
    if (!formData.to) {
      toast.error('Ingrese un destinatario')
      return
    }
    if (!formData.subject) {
      toast.error('Ingrese un asunto')
      return
    }
    if (!formData.body) {
      toast.error('Escriba un mensaje')
      return
    }
    
    setIsDraft(false)
    setIsSending(true)
    sendMutation.mutate(formData)
  }

  const handleSaveDraft = () => {
    if (!formData.to && !formData.subject && !formData.body) {
      toast.error('No hay contenido para guardar como borrador')
      return
    }
    
    setIsDraft(true)
    setIsSending(true)
    sendMutation.mutate(formData)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Volver
        </Button>
        <h1 className="text-2xl font-bold tracking-tight">Redactar Correo</h1>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Formulario principal */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Nuevo Mensaje</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="space-y-6">
                {/* Para - Destinatario */}
                <div className="space-y-2">
                  <Label htmlFor="to" className="flex items-center gap-2">
                    <User className="h-4 w-4" />
                    Para <span className="text-red-500">*</span>
                  </Label>
                  <Select 
                    value={formData.to} 
                    onValueChange={(value) => setFormData({ ...formData, to: value })}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Selecciona un destinatario" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableRecipients.map((recipient) => (
                        <SelectItem key={recipient.value} value={recipient.value}>
                          {recipient.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground">
                    También puedes escribir el email manualmente
                  </p>
                  <Input
                    id="to"
                    type="email"
                    placeholder="o escribe un email manualmente..."
                    value={formData.to}
                    onChange={(e) => setFormData({ ...formData, to: e.target.value })}
                    className="mt-2"
                  />
                </div>

                {/* Asunto */}
                <div className="space-y-2">
                  <Label htmlFor="subject" className="flex items-center gap-2">
                    <Mail className="h-4 w-4" />
                    Asunto <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="subject"
                    placeholder="Asunto del mensaje"
                    value={formData.subject}
                    onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                    required
                  />
                </div>

                {/* Cuerpo del mensaje */}
                <div className="space-y-2">
                  <Label htmlFor="body" className="flex items-center gap-2">
                    <MessageSquare className="h-4 w-4" />
                    Mensaje <span className="text-red-500">*</span>
                  </Label>
                  <Textarea
                    id="body"
                    placeholder="Escribe tu mensaje aquí..."
                    rows={12}
                    value={formData.body}
                    onChange={(e) => setFormData({ ...formData, body: e.target.value })}
                    required
                    className="font-mono text-sm"
                  />
                </div>

                {/* Botones de acción */}
                <div className="flex justify-end gap-4 pt-4 border-t">
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={handleSaveDraft}
                    disabled={isSending}
                  >
                    {isSending && isDraft ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Save className="h-4 w-4 mr-2" />
                    )}
                    Guardar Borrador
                  </Button>
                  <Button 
                    type="submit" 
                    disabled={isSending}
                    className="min-w-[100px]"
                  >
                    {isSending && !isDraft ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4 mr-2" />
                    )}
                    Enviar
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Vista previa del mensaje */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Vista Previa</CardTitle>
            </CardHeader>
            <CardContent>
              {formData.body ? (
                <div className="rounded-lg bg-muted/50 p-4">
                  <div className="text-sm text-muted-foreground mb-2">
                    <strong>Para:</strong> {formData.to || '(no especificado)'}
                  </div>
                  <div className="text-sm text-muted-foreground mb-4">
                    <strong>Asunto:</strong> {formData.subject || '(sin asunto)'}
                  </div>
                  <div className="whitespace-pre-wrap text-sm">
                    {formData.body}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <MessageSquare className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p className="text-sm">Escribe tu mensaje para ver la vista previa</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}