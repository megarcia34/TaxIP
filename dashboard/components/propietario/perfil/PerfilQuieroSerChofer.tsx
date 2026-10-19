// D:\ataxip\dashboard\components\propietario\perfil\PerfilQuieroSerChofer.tsx
'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Loader2,
  CheckCircle2,
  XCircle,
  Clock,
  AlertCircle,
  FileText,
  Upload,
  RefreshCw,
  Calendar,
} from 'lucide-react';
import {
  useEstadoPostulacion,
  useMisDocumentos,
  useCancelarPostulacion,
  useEnviarARevision,
} from '@/hooks/propietario/usePostulacionChofer';
import type {
  TipoDocumentoChofer,
  EstadoAprobacion,
  DocumentoChofer,
} from '@/lib/api/postulacionChofer';
import {
  TIPOS_DOCUMENTO_REQUERIDOS,
  TIPOS_CON_VENCIMIENTO,
} from '@/lib/api/postulacionChofer';
import ModalSubirDocumentoChofer from './ModalSubirDocumentoChofer';
import { ModalImagen } from '@/components/propietario/ModalImagen';
import { format, differenceInDays, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';

const DOCUMENTOS_INFO: Record<
  TipoDocumentoChofer,
  { label: string; descripcion: string }
> = {
  dni: { label: 'DNI', descripcion: 'Frente y dorso' },
  licencia: { label: 'Licencia de conducir', descripcion: 'Vigente' },
  buena_conducta: {
    label: 'Certificado de buena conducta',
    descripcion: 'Autoridad competente',
  },
  antecedentes: {
    label: 'Certificado de antecedentes',
    descripcion: 'Penales',
  },
  sanidad: { label: 'Certificado de sanidad', descripcion: 'Apto fisico' },
};

function calcularVencimiento(fechaVencimiento: string | null): {
  label: string;
  className: string;
} | null {
  if (!fechaVencimiento) return null;
  try {
    const fecha = parseISO(fechaVencimiento);
    const dias = differenceInDays(fecha, new Date());
    if (dias < 0) {
      return {
        label: `Vencido (${Math.abs(dias)}d)`,
        className: 'bg-red-100 text-red-700 border-red-200',
      };
    }
    if (dias <= 30) {
      return {
        label: `Vence en ${dias}d`,
        className: 'bg-orange-100 text-orange-700 border-orange-200',
      };
    }
    return {
      label: `${dias} dias`,
      className: 'bg-green-100 text-green-700 border-green-200',
    };
  } catch {
    return null;
  }
}

export default function PerfilQuieroSerChofer() {
  const { data: estado, isLoading: loadingEstado } = useEstadoPostulacion();
  const { data: misDocsData, isLoading: loadingDocs } = useMisDocumentos();
  const cancelarMutation = useCancelarPostulacion();
  const enviarMutation = useEnviarARevision();

  const [modalDoc, setModalDoc] = useState<TipoDocumentoChofer | null>(null);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [modalImage, setModalImage] = useState<{
    url: string;
    titulo: string;
  } | null>(null);

  if (loadingEstado || loadingDocs) {
    return (
      <Card>
        <CardContent className="flex justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
        </CardContent>
      </Card>
    );
  }

  const estadoActual: EstadoAprobacion =
    estado?.estado_aprobacion ?? 'pendiente';
  const documentos: DocumentoChofer[] = misDocsData?.documentos ?? [];
  const docsPorTipo = new Map<TipoDocumentoChofer, DocumentoChofer>();
  documentos.forEach((d) => docsPorTipo.set(d.tipo_documento, d));
  const subidos = estado?.documentos_subidos ?? 0;
  const requeridos =
    estado?.documentos_requeridos ?? TIPOS_DOCUMENTO_REQUERIDOS.length;
  const puedeEnviar =
    estado?.puede_manejar === true && estadoActual === 'pendiente';

  // ============================================
  // ESTADO: PENDIENTE
  // ============================================
  if (estadoActual === 'pendiente') {
    return (
      <>
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Cargar documentos
                </CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  {estado?.mensaje ||
                    'Carga los 5 documentos requeridos para enviar a revision.'}
                </p>
              </div>
              <Badge variant="outline" className="text-sm">
                {subidos} / {requeridos}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              {TIPOS_DOCUMENTO_REQUERIDOS.map((tipo) => {
                const info = DOCUMENTOS_INFO[tipo];
                const doc = docsPorTipo.get(tipo);
                const yaSubido = !!doc;
                const vencimiento = doc
                  ? calcularVencimiento(doc.fecha_vencimiento)
                  : null;
                const requiereFecha = TIPOS_CON_VENCIMIENTO.includes(tipo);

                return (
                  <div
                    key={tipo}
                    className={`border rounded-lg p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                      yaSubido ? 'bg-green-50/50 border-green-200' : 'bg-white'
                    }`}
                  >
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      {yaSubido ? (
                        <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                      ) : (
                        <div className="h-5 w-5 rounded-full border-2 border-muted-foreground/30 flex-shrink-0 mt-0.5" />
                      )}

                      {/* MINIATURA (si esta subido) */}
                      {yaSubido && doc?.url && (
                        <button
                          type="button"
                          onClick={() =>
                            setModalImage({
                              url: doc.url!,
                              titulo: info.label,
                            })
                          }
                          className="flex-shrink-0 w-16 h-16 rounded-md overflow-hidden border hover:ring-2 hover:ring-primary transition-all group relative bg-gray-100"
                          title="Click para ampliar"
                        >
                          <img
                            src={doc.url}
                            alt={info.label}
                            className="w-full h-full object-cover"
                          />
                          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors flex items-center justify-center">
                            <span className="text-white text-xs opacity-0 group-hover:opacity-100 transition-opacity font-medium">
                              Ver
                            </span>
                          </div>
                        </button>
                      )}

                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <p className="font-medium text-sm">{info.label}</p>
                          {vencimiento && (
                            <Badge
                              className={`text-xs ${vencimiento.className}`}
                            >
                              {vencimiento.label}
                            </Badge>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {info.descripcion}
                        </p>
                        {yaSubido && doc?.numero && (
                          <p className="text-xs text-muted-foreground mt-1">
                            Nº: {doc.numero}
                          </p>
                        )}
                        {yaSubido && doc?.fecha_vencimiento && (
                          <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            Vence:{' '}
                            {format(
                              parseISO(doc.fecha_vencimiento),
                              'dd/MM/yyyy',
                              { locale: es }
                            )}
                          </p>
                        )}
                        {yaSubido &&
                          requiereFecha &&
                          !doc?.fecha_vencimiento && (
                            <p className="text-xs text-orange-600 mt-1 flex items-center gap-1">
                              <AlertCircle className="h-3 w-3" />
                              Sin fecha de vencimiento. Reemplazar para actualizar.
                            </p>
                          )}
                      </div>
                    </div>
                    <Button
                      variant={yaSubido ? 'outline' : 'default'}
                      size="sm"
                      onClick={() => setModalDoc(tipo)}
                      className="gap-2 flex-shrink-0"
                    >
                      {yaSubido ? (
                        <>
                          <RefreshCw className="h-3.5 w-3.5" />
                          Reemplazar
                        </>
                      ) : (
                        <>
                          <Upload className="h-3.5 w-3.5" />
                          Subir
                        </>
                      )}
                    </Button>
                  </div>
                );
              })}
            </div>

            <div className="border-t pt-4 flex flex-col sm:flex-row justify-between gap-3">
              <Button
                variant="outline"
                onClick={() => setShowCancelConfirm(true)}
                disabled={cancelarMutation.isPending}
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                Cancelar postulacion
              </Button>
              <Button
                onClick={() => enviarMutation.mutate()}
                disabled={!puedeEnviar || enviarMutation.isPending}
                className="gap-2"
              >
                {enviarMutation.isPending && (
                  <Loader2 className="h-4 w-4 animate-spin" />
                )}
                Enviar a revision
              </Button>
            </div>

            {!puedeEnviar && subidos < requeridos && (
              <p className="text-xs text-muted-foreground text-center">
                Faltan {requeridos - subidos} documento(s) para poder enviar a
                revision.
              </p>
            )}
          </CardContent>
        </Card>

        <AlertDialog open={showCancelConfirm} onOpenChange={setShowCancelConfirm}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Cancelar postulacion?</AlertDialogTitle>
              <AlertDialogDescription>
                Se cancelara la postulacion actual y se eliminaran los documentos
                cargados. Podes volver a iniciarla cuando quieras.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Volver</AlertDialogCancel>
              <AlertDialogAction
                onClick={() => cancelarMutation.mutate()}
                className="bg-red-500 hover:bg-red-600"
              >
                Si, cancelar
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        {modalDoc && (
          <ModalSubirDocumentoChofer
            open={!!modalDoc}
            onOpenChange={(open) => !open && setModalDoc(null)}
            tipoDocumento={modalDoc}
          />
        )}

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

  // ============================================
  // ESTADO: EN REVISION
  // ============================================
  if (estadoActual === 'en_revision') {
    return (
      <>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-yellow-600" />
              En revision
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4 text-sm text-yellow-800 flex items-start gap-3">
              <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">Tu postulacion esta siendo revisada</p>
                <p className="mt-1">
                  {estado?.mensaje ||
                    'El municipio revisara tus documentos. Te notificaremos cuando haya novedades.'}
                </p>
              </div>
            </div>

            <div className="space-y-2">
              {TIPOS_DOCUMENTO_REQUERIDOS.map((tipo) => {
                const info = DOCUMENTOS_INFO[tipo];
                const doc = docsPorTipo.get(tipo);
                const vencimiento = doc
                  ? calcularVencimiento(doc.fecha_vencimiento)
                  : null;
                return (
                  <div
                    key={tipo}
                    className="flex items-center gap-3 text-sm border rounded-md p-2"
                  >
                    <CheckCircle2 className="h-4 w-4 text-green-600 flex-shrink-0" />

                    {doc?.url && (
                      <button
                        type="button"
                        onClick={() =>
                          setModalImage({
                            url: doc.url!,
                            titulo: info.label,
                          })
                        }
                        className="flex-shrink-0 w-10 h-10 rounded overflow-hidden border hover:ring-2 hover:ring-primary transition-all bg-gray-100"
                        title="Click para ampliar"
                      >
                        <img
                          src={doc.url}
                          alt={info.label}
                          className="w-full h-full object-cover"
                        />
                      </button>
                    )}

                    <div className="flex-1 min-w-0">
                      <p>{info.label}</p>
                      {doc?.numero && (
                        <p className="text-xs text-muted-foreground">
                          Nº: {doc.numero}
                        </p>
                      )}
                    </div>
                    {vencimiento && (
                      <Badge className={`text-xs ${vencimiento.className}`}>
                        {vencimiento.label}
                      </Badge>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="border-t pt-4 flex justify-end">
              <Button
                variant="outline"
                onClick={() => setShowCancelConfirm(true)}
                disabled={cancelarMutation.isPending}
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                Cancelar postulacion
              </Button>
            </div>
          </CardContent>
        </Card>

        <AlertDialog open={showCancelConfirm} onOpenChange={setShowCancelConfirm}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Cancelar postulacion?</AlertDialogTitle>
              <AlertDialogDescription>
                Se cancelara la postulacion en revision.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Volver</AlertDialogCancel>
              <AlertDialogAction
                onClick={() => cancelarMutation.mutate()}
                className="bg-red-500 hover:bg-red-600"
              >
                Si, cancelar
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

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

  // ============================================
  // ESTADO: APROBADO
  // ============================================
  if (estadoActual === 'aprobado') {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            Aprobado
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-md p-4 text-sm text-green-800 flex items-start gap-3">
            <CheckCircle2 className="h-5 w-5 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium">Ya sos chofer de tu propia flota</p>
              <p className="mt-1">
                {estado?.mensaje ||
                  'Ya podes usar la app chofer con tu cuenta de propietario para iniciar turnos con tus vehiculos.'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // ============================================
  // ESTADO: RECHAZADO
  // ============================================
  if (estadoActual === 'rechazado') {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <XCircle className="h-5 w-5 text-red-600" />
            Postulacion rechazada
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-red-50 border border-red-200 rounded-md p-4 text-sm text-red-800 flex items-start gap-3">
            <XCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium">Tu postulacion fue rechazada</p>
              {estado?.motivo_rechazo ? (
                <p className="mt-1">
                  <span className="font-medium">Motivo:</span>{' '}
                  {estado.motivo_rechazo}
                </p>
              ) : (
                estado?.mensaje && <p className="mt-1">{estado.mensaje}</p>
              )}
            </div>
          </div>
          <div className="flex justify-end">
            <Button
              onClick={() => setShowCancelConfirm(true)}
              disabled={cancelarMutation.isPending}
              className="gap-2"
            >
              {cancelarMutation.isPending && (
                <Loader2 className="h-4 w-4 animate-spin" />
              )}
              Reintentar postulacion
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Fallback desconocido
  return (
    <Card>
      <CardContent className="py-12 text-center text-muted-foreground">
        <AlertCircle className="h-12 w-12 mx-auto mb-3 opacity-50" />
        <p>Estado de postulacion desconocido: {estadoActual}</p>
      </CardContent>
    </Card>
  );
}