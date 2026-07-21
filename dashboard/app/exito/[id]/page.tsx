'use client'

import { useParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Loader2, Download, Printer, Copy, CheckCircle } from 'lucide-react'
import { toast } from 'sonner'

interface ComercioInfo {
  id: string
  nombre: string
  codigo_qr: string
  url_qr: string
  direccion: string
}

export default function ExitoQRPage() {
  const params = useParams()
  const router = useRouter()
  const comercioId = params.id as string
  const [comercio, setComercio] = useState<ComercioInfo | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [qrImage, setQrImage] = useState<string | null>(null)

  useEffect(() => {
    const fetchComercio = async () => {
      try {
        const response = await fetch(`/api/comercio/${comercioId}`)
        const data = await response.json()
        setComercio(data)
        
        // Generar QR en el cliente
        const qr = await generateQR(data.url_qr)
        setQrImage(qr)
      } catch (error) {
        console.error('Error:', error)
        toast.error('Error al cargar los datos')
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchComercio()
  }, [comercioId])

  const generateQR = async (text: string): Promise<string> => {
    // Usar API de QR code
    const url = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(text)}`
    return url
  }

  const downloadQR = () => {
    if (qrImage) {
      const link = document.createElement('a')
      link.href = qrImage
      link.download = `qr_${comercio?.codigo_qr}.png`
      link.click()
      toast.success('QR descargado')
    }
  }

  const copyUrl = () => {
    if (comercio?.url_qr) {
      navigator.clipboard.writeText(comercio.url_qr)
      toast.success('URL copiada al portapapeles')
    }
  }

  const printQR = () => {
    if (qrImage) {
      const printWindow = window.open('', '_blank')
      printWindow?.document.write(`
        <html>
          <head><title>QR - ${comercio?.nombre}</title></head>
          <body style="display:flex; justify-content:center; align-items:center; height:100vh;">
            <div style="text-align:center;">
              <img src="${qrImage}" style="width:300px; height:300px;" />
              <h2>${comercio?.nombre}</h2>
              <p>Escanea para solicitar taxi</p>
            </div>
          </body>
        </html>
      `)
      printWindow?.document.close()
      printWindow?.print()
    }
  }

  if (isLoading) {
    return (
      <div className="container max-w-2xl py-8">
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container max-w-2xl py-8">
      <div className="text-center mb-8">
        <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
        <h1 className="text-2xl font-bold">¡QR generado con éxito!</h1>
        <p className="text-muted-foreground mt-2">
          Tu código QR ya está listo. Descargalo e imprimilo para colocarlo en tu negocio.
        </p>
      </div>

      <Card>
        <CardHeader className="text-center">
          <CardTitle>{comercio?.nombre}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* QR */}
          <div className="flex justify-center">
            {qrImage && (
              <div className="border rounded-lg p-4 bg-white">
                <img src={qrImage} alt="QR Code" className="w-64 h-64" />
              </div>
            )}
          </div>

          {/* URL del QR */}
          <div className="bg-muted p-3 rounded-lg">
            <p className="text-xs text-muted-foreground mb-1">URL del QR:</p>
            <p className="text-sm font-mono break-all">{comercio?.url_qr}</p>
          </div>

          {/* Botones de acción */}
          <div className="flex flex-wrap gap-3 justify-center">
            <Button onClick={downloadQR}>
              <Download className="h-4 w-4 mr-2" />
              Descargar QR
            </Button>
            <Button variant="outline" onClick={copyUrl}>
              <Copy className="h-4 w-4 mr-2" />
              Copiar URL
            </Button>
            <Button variant="outline" onClick={printQR}>
              <Printer className="h-4 w-4 mr-2" />
              Imprimir
            </Button>
          </div>

          {/* Instrucciones */}
          <div className="border-t pt-4">
            <h3 className="font-medium mb-2">¿Cómo usar tu QR?</h3>
            <ol className="text-sm text-muted-foreground space-y-2 list-decimal list-inside">
              <li>Descargá la imagen del código QR</li>
              <li>Imprimilo en el tamaño que prefieras</li>
              <li>Colocalo en mesas, mostrador, vidriera o entrada de tu negocio</li>
              <li>Tus clientes escanean con su celular y solicitan taxi al instante</li>
            </ol>
          </div>

          <Button 
            variant="link" 
            className="w-full"
            onClick={() => router.push('/')}
          >
            Volver al inicio
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}