'use client'

import { useEffect, useRef } from 'react'
import { X, Download, ExternalLink } from 'lucide-react'

interface ModalImagenProps {
  url: string
  titulo?: string
  onClose: () => void
}

export function ModalImagen({ url, titulo, onClose }: ModalImagenProps) {
  const modalRef = useRef<HTMLDivElement>(null)

  // Cerrar con ESC
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  // Cerrar al hacer clic fuera del modal
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
      onClose()
    }
  }

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
      onClick={handleBackdropClick}
    >
      <div 
        ref={modalRef}
        className="relative bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
      >
        {/* HEADER */}
        <div className="flex items-center justify-between px-4 py-3 border-b bg-gray-50">
          <h3 className="font-medium text-sm truncate">
            {titulo || 'Imagen del documento'}
          </h3>
          <div className="flex items-center gap-1">
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-1.5 rounded-lg hover:bg-gray-200 transition-colors text-gray-500 hover:text-gray-700"
              title="Abrir en nueva pestaña"
            >
              <ExternalLink className="h-4 w-4" />
            </a>
            <a
              href={url}
              download
              className="p-1.5 rounded-lg hover:bg-gray-200 transition-colors text-gray-500 hover:text-gray-700"
              title="Descargar"
            >
              <Download className="h-4 w-4" />
            </a>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-gray-200 transition-colors text-gray-500 hover:text-gray-700"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* CONTENIDO - IMAGEN */}
        <div className="p-4 flex items-center justify-center bg-gray-100 max-h-[calc(90vh-120px)] overflow-auto">
          <img
            src={url}
            alt={titulo || 'Documento'}
            className="max-w-full max-h-full object-contain rounded-lg shadow-sm"
            style={{ maxHeight: 'calc(90vh - 120px)' }}
          />
        </div>

        {/* FOOTER */}
        <div className="px-4 py-2 border-t bg-gray-50 text-xs text-muted-foreground text-center">
          Haz clic fuera de la imagen para cerrar
        </div>
      </div>
    </div>
  )
}