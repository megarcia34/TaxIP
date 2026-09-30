import { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  Image,
  Alert,
  Keyboard,
} from 'react-native';
import { COLORS } from '@/constants/colors';
import { takePhoto, pickFromGallery } from '@/services/cloudinary.service';
import type { DocumentoConfig } from '@/types/documento.types';

interface DocumentUploadCardProps {
  config: DocumentoConfig;
  onUpload: (uri: string | null, fechaVencimiento?: string) => void;
  disabled?: boolean;
}

export function DocumentUploadCard({
  config,
  onUpload,
  disabled = false,
}: DocumentUploadCardProps) {
  const [fechaVencimiento, setFechaVencimiento] = useState('');
  const [uriLocal, setUriLocal] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Auto-formatear fecha mientras el usuario escribe
  const handleFechaChange = (text: string) => {
    const soloNumeros = text.replace(/\D/g, '');

    let formateado = soloNumeros;
    if (soloNumeros.length >= 5) {
      formateado = `${soloNumeros.slice(0, 2)}/${soloNumeros.slice(
        2,
        4
      )}/${soloNumeros.slice(4, 8)}`;
    } else if (soloNumeros.length >= 3) {
      formateado = `${soloNumeros.slice(0, 2)}/${soloNumeros.slice(2)}`;
    }

    setFechaVencimiento(formateado);

    // Cerrar el teclado cuando la fecha esté completa (DD/MM/AAAA = 10 chars)
    if (formateado.length === 10) {
      Keyboard.dismiss();
    }
  };

  const validarFecha = (fecha: string): boolean => {
    if (!config.requiereVencimiento) return true;
    if (!fecha) return false;

    const regex = /^(\d{2})\/(\d{2})\/(\d{4})$/;
    const match = fecha.match(regex);
    if (!match) return false;

    const dia = parseInt(match[1], 10);
    const mes = parseInt(match[2], 10);
    const anio = parseInt(match[3], 10);

    if (dia < 1 || dia > 31) return false;
    if (mes < 1 || mes > 12) return false;
    if (anio < 2020 || anio > 2100) return false;

    const fechaObj = new Date(anio, mes - 1, dia);
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    if (fechaObj < hoy) return false;

    return true;
  };

  const handleSeleccionar = async (origen: 'camara' | 'galeria') => {
    if (config.requiereVencimiento && !validarFecha(fechaVencimiento)) {
      Alert.alert(
        'Fecha inválida',
        'Ingresá una fecha válida (no puede ser pasada)'
      );
      return;
    }

    setIsLoading(true);
    try {
      const uri =
        origen === 'camara' ? await takePhoto() : await pickFromGallery();

      setUriLocal(uri);

      onUpload(uri, config.requiereVencimiento ? fechaVencimiento : undefined);
    } catch (error: any) {
      Alert.alert('Error', error.message || 'No se pudo obtener la imagen');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEliminar = () => {
    Alert.alert(
      'Eliminar documento',
      '¿Estás seguro que querés eliminar este documento?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Eliminar',
          style: 'destructive',
          onPress: () => {
            setUriLocal(null);
            setFechaVencimiento('');
            onUpload(null);
          },
        },
      ]
    );
  };

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={styles.icono}>{config.icono}</Text>
          <View style={styles.headerText}>
            <Text style={styles.nombre}>
              {config.nombre}
              {config.bloqueante && <Text style={styles.asterisco}> *</Text>}
            </Text>
          </View>
        </View>
        <View style={styles.estadoBadge}>
          {uriLocal && <Text style={styles.estadoCargado}>✓</Text>}
          {!uriLocal && <Text style={styles.estadoPendiente}>○</Text>}
        </View>
      </View>

      {config.requiereVencimiento && (
        <View style={styles.fechaWrapper}>
          <Text style={styles.fechaLabel}>
            Fecha de vencimiento (solo números)
          </Text>
          <TextInput
            style={styles.fechaInput}
            value={fechaVencimiento}
            onChangeText={handleFechaChange}
            placeholder="DD/MM/AAAA"
            placeholderTextColor="rgba(255, 255, 255, 0.3)"
            keyboardType="numeric"
            maxLength={10}
            editable={!disabled && !uriLocal}
          />
        </View>
      )}

      {uriLocal && (
        <View style={styles.previewContainer}>
          <Image
            source={{ uri: uriLocal }}
            style={styles.previewImage}
            resizeMode="cover"
          />
        </View>
      )}

      {!uriLocal ? (
        <View style={styles.botonesRow}>
          <TouchableOpacity
            style={[styles.boton, styles.botonCamara]}
            onPress={() => handleSeleccionar('camara')}
            disabled={disabled || isLoading}
          >
            {isLoading ? (
              <ActivityIndicator size="small" color={COLORS.primary} />
            ) : (
              <Text style={styles.botonText}>📷 Tomar foto</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.boton, styles.botonGaleria]}
            onPress={() => handleSeleccionar('galeria')}
            disabled={disabled || isLoading}
          >
            <Text style={styles.botonText}>📁 Galería</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <TouchableOpacity
          style={[styles.boton, styles.botonEliminar]}
          onPress={handleEliminar}
          disabled={disabled}
        >
          <Text style={styles.botonText}>🗑 Eliminar y volver a subir</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  icono: {
    fontSize: 28,
    marginRight: 12,
  },
  headerText: {
    flex: 1,
  },
  nombre: {
    color: COLORS.textPrimary,
    fontSize: 15,
    fontWeight: '700',
  },
  asterisco: {
    color: COLORS.primary,
  },
  estadoBadge: {
    width: 32,
    height: 32,
    alignItems: 'center',
    justifyContent: 'center',
  },
  estadoCargado: {
    color: COLORS.success,
    fontSize: 22,
    fontWeight: 'bold',
  },
  estadoPendiente: {
    color: 'rgba(255, 255, 255, 0.3)',
    fontSize: 22,
  },
  fechaWrapper: {
    marginBottom: 12,
  },
  fechaLabel: {
    color: COLORS.textPrimary,
    fontSize: 11,
    opacity: 0.7,
    marginBottom: 4,
  },
  fechaInput: {
    color: COLORS.textPrimary,
    fontSize: 16,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.3)',
  },
  previewContainer: {
    marginBottom: 12,
    borderRadius: 8,
    overflow: 'hidden',
  },
  previewImage: {
    width: '100%',
    height: 160,
    backgroundColor: 'rgba(0, 0, 0, 0.2)',
  },
  botonesRow: {
    flexDirection: 'row',
    gap: 8,
  },
  boton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 44,
  },
  botonCamara: {
    backgroundColor: 'rgba(249, 200, 14, 0.2)',
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  botonGaleria: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  botonEliminar: {
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    borderWidth: 1,
    borderColor: COLORS.error,
  },
  botonText: {
    color: COLORS.textPrimary,
    fontSize: 13,
    fontWeight: '600',
  },
});