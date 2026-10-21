// D:\aTaxip\dashboard\components\admin\solicitudes\ModalVerDocumentos.tsx
'use client';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { FileText, AlertCircle } from 'lucide-react';
import { useState } from 'react';
import { ModalImagen } from '@/components/propietario/ModalImagen';
import { getDocumentoUrl } from '@/lib/api/solicitudesTenant';

interface Documento {
  url_archivo: string | null;
  numero: string | null;
  fecha_vencimiento: string | null;
}

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  titulo: string;
  documentos: Record<string, Documento>;
  tiposRequeridos: { tipo: string; label: string }[];
}

export default function ModalVerDocumentos({
  open,
  onOpenChange,
  titulo,
  documentos,
  tiposRequeridos,
}: Props) {
  const [modalImage, setModalImage] = useState<{ url: string; titulo: string } | null>(null);

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              {titulo}
            </DialogTitle>
          </DialogHeader>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            {tiposRequeridos.map(({ tipo, label }) => {
              const doc = documentos[tipo];
              const urlCompleta = doc ? getDocumentoUrl(doc.url_archivo) : null; 
              const presente = !!urlCompleta;

              return (
                <div
                  key={tipo}
                  className={`border rounded-lg p-3 ${
                    presente ? 'bg-green-50/50 border-green-200' : 'bg-red-50 border-red-200'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    {presente ? (
                      <span className="text-green-600">✅</span>
                    ) : (
                      <AlertCircle className="h-4 w-4 text-red-600" />
                    )}
                    <span className="font-medium text-sm">{label}</span>
                    {doc?.fecha_vencimiento && (
                      <Badge variant="outline" className="text-xs ml-auto">
                        Vence: {new Date(doc.fecha_vencimiento).toLocaleDateString('es-AR')}
                      </Badge>
                    )}
                  </div>

                  {doc?.numero && (
                    <p className="text-xs text-muted-foreground mb-2">N°: {doc.numero}</p>
                  )}

                  {presente ? (
                    urlCompleta.toLowerCase().endsWith('.pdf') ? (
                      <a
                        href={urlCompleta}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-center w-full h-32 bg-gray-100 rounded-md border hover:bg-gray-200"
                      >
                        <div className="text-center">
                          <FileText className="h-8 w-8 mx-auto text-red-600" />
                          <p className="text-xs mt-1">Click para abrir PDF</p>
                        </div>
                      </a>
                    ) : (
                      <button
                        type="button"
                        onClick={() =>
                          setModalImage({ url: urlCompleta, titulo: label })
                        }
                        className="w-full h-32 rounded-md overflow-hidden border hover:ring-2 hover:ring-primary transition-all group relative bg-gray-100"
                      >
                        <img
                          src={urlCompleta}
                          alt={label}
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors flex items-center justify-center">
                          <span className="text-white text-sm opacity-0 group-hover:opacity-100 font-medium">
                            Click para ampliar
                          </span>
                        </div>
                      </button>
                    )
                  ) : (
                    <div className="w-full h-32 rounded-md border-2 border-dashed border-red-300 flex items-center justify-center text-sm text-red-600">
                      No cargado
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </DialogContent>
      </Dialog>

      {modalImage && (
        <ModalImagen
          url={modalImage.url}
          titulo={modalImage.titulo}
          onClose={() => setModalImage(null)}
        />
      )}
    </>
  );
}