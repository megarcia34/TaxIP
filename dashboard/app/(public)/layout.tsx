import { Car } from 'lucide-react'
import Link from 'next/link'

export default function PublicLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header público */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <Car className="h-6 w-6 text-primary" />
            <span className="font-bold text-lg">TaxIP</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/qr/registro" className="text-sm text-muted-foreground hover:text-foreground">
              Generar QR para mi negocio
            </Link>
            <Link href="/login" className="text-sm text-muted-foreground hover:text-foreground">
              ¿Eres conductor? Inicia sesión
            </Link>
          </div>
        </div>
      </header>
      
      <main className="flex-1">
        {children}
      </main>
      
      {/* Footer */}
      <footer className="border-t py-6">
        <div className="container text-center text-sm text-muted-foreground">
          <p>TaxIP 2.0 - Tu taxi, al instante</p>
        </div>
      </footer>
    </div>
  )
}