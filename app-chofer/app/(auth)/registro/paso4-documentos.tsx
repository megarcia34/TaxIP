import { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  ScrollView,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { COLORS } from '@/constants/colors';
import { ProgressBar } from '@/components/registro/ProgressBar';
import { RegistroHeader } from '@/components/registro/RegistroHeader';
import { DocumentUploadCard } from '@/components/registro/DocumentUploadCard';
import { DOCUMENTOS } from '@/constants/documentos';
import { registroService } from '@/services/registro.service';

interface DocumentoSubido {
  tipo: string;
  uriLocal: string;
  fechaVencimiento?: string;
}

export default function Paso4DocumentosScreen() {
  const router = useRouter();

  const [documentos, setDocumentos] = useState<Record<string, DocumentoSubido>>(
    {}
  );
  const [isLoading, setIsLoading] = useState(false);

  const handleDocumentoSubido = (
    tipo: string,
    uriLocal: string | null,
    fechaVencimiento?: string
  ) => {
    if (!uriLocal) {
      // El usuario eliminó el documento
      const nuevo = { ...documentos };
      delete nuevo[tipo];
      setDocumentos(nuevo);
      return;
    }

    setDocumentos({
      ...documentos,
      [tipo]: { tipo, uriLocal, fechaVencimiento },
    });
  };

  const totalDocumentos = DOCUMENTOS.length;
  const documentosCargados = Object.keys(documentos).length;
  const todosCargados = documentosCargados === totalDocumentos;
  const faltantes = totalDocumentos - documentosCargados;

  const handleContinue = async () => {
    if (!todosCargados) return;

    setIsLoading(true);
    try {
      // Enviar cada documento al backend
      for (const tipo of Object.keys(documentos)) {
        const doc = documentos[tipo];
        await registroService.subirDocumento(
          doc.uriLocal,
          tipo,
          doc.fechaVencimiento
        );
      }

      // Navegar al Paso 5 (Selfie)
      router.push('/(auth)/registro/paso5-selfie' as any);
    } catch (error: any) {
      const mensaje =
        error?.response?.data?.detail ||
        error?.message ||
        'Error al guardar los documentos';
      Alert.alert('Error', mensaje);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <LinearGradient
      colors={[COLORS.backgroundDark, COLORS.backgroundMedium]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
    >
      <RegistroHeader title="Documentación" />
      <ProgressBar currentStep={4} />

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {/* Título */}
        <Text style={styles.title}>Carga de Documentos</Text>
        <Text style={styles.subtitle}>
          Subí los siguientes documentos para completar tu registro.{'\n'}
          Los marcados con <Text style={styles.asterisco}>*</Text> son
          obligatorios.
        </Text>

        {/* Contador con barra de progreso */}
        <View style={styles.contadorContainer}>
          <View style={styles.contadorHeader}>
            <Text style={styles.contadorText}>Documentos cargados</Text>
            <Text style={styles.contadorNumber}>
              {documentosCargados}/{totalDocumentos}
            </Text>
          </View>
          <View style={styles.progressContainer}>
            <View
              style={[
                styles.progressBar,
                {
                  width: `${(documentosCargados / totalDocumentos) * 100}%`,
                },
              ]}
            />
          </View>
        </View>

        {/* Cards de documentos */}
        {DOCUMENTOS.map((config) => (
          <DocumentUploadCard
            key={config.tipo}
            config={config}
            onUpload={(uri, fecha) =>
              handleDocumentoSubido(config.tipo, uri, fecha)
            }
            disabled={isLoading}
          />
        ))}

        {/* Botón CONTINUAR */}
        <TouchableOpacity
          style={[
            styles.primaryButton,
            (!todosCargados || isLoading) && styles.primaryButtonDisabled,
          ]}
          onPress={handleContinue}
          disabled={!todosCargados || isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color={COLORS.textDark} />
          ) : (
            <Text style={styles.primaryButtonText}>
              {todosCargados
                ? 'CONTINUAR'
                : `FALTAN ${faltantes} DOCUMENTO${faltantes > 1 ? 'S' : ''}`}
            </Text>
          )}
        </TouchableOpacity>

        {/* Nota de ayuda */}
        {!todosCargados && (
          <Text style={styles.helpText}>
            Completá todos los documentos para continuar
          </Text>
        )}
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 48,
  },
  title: {
    color: COLORS.textPrimary,
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    color: COLORS.textPrimary,
    fontSize: 13,
    textAlign: 'center',
    opacity: 0.8,
    marginBottom: 24,
    lineHeight: 18,
  },
  asterisco: {
    color: COLORS.primary,
    fontWeight: 'bold',
  },
  contadorContainer: {
    marginBottom: 24,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  contadorHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  contadorText: {
    color: COLORS.textPrimary,
    fontSize: 14,
    fontWeight: '600',
  },
  contadorNumber: {
    color: COLORS.primary,
    fontSize: 16,
    fontWeight: 'bold',
  },
  progressContainer: {
    height: 6,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressBar: {
    height: 6,
    backgroundColor: COLORS.primary,
    borderRadius: 3,
  },
  primaryButton: {
    backgroundColor: COLORS.primary,
    borderRadius: 8,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
    marginTop: 16,
  },
  primaryButtonDisabled: {
    opacity: 0.4,
  },
  primaryButtonText: {
    color: COLORS.textDark,
    fontSize: 14,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
  helpText: {
    color: COLORS.textPrimary,
    fontSize: 12,
    textAlign: 'center',
    opacity: 0.6,
    marginTop: 12,
    fontStyle: 'italic',
  },
});