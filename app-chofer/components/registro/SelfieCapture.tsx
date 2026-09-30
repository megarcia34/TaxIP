import { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Linking,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { COLORS } from '@/constants/colors';

interface SelfieCaptureProps {
  onCapture: (uri: string) => void;
  capturedUri: string | null;
  onRetake: () => void;
}

export function SelfieCapture({
  onCapture,
  capturedUri,
  onRetake,
}: SelfieCaptureProps) {
  const [permission, requestPermission] = useCameraPermissions();
  const [isCapturing, setIsCapturing] = useState(false);
  const cameraRef = useRef<CameraView | null>(null);

  // Preview de la foto capturada
  if (capturedUri) {
    return (
      <View style={styles.previewContainer}>
        <Image
          source={{ uri: capturedUri }}
          style={styles.previewImage}
          resizeMode="cover"
        />
        <TouchableOpacity style={styles.retakeButton} onPress={onRetake}>
          <Text style={styles.retakeText}>🔄 Volver a tomar</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // Cargando permisos
  if (!permission) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  // Permiso denegado
  if (!permission.granted) {
    return (
      <View style={styles.permissionContainer}>
        <Text style={styles.permissionIcon}>📷</Text>
        <Text style={styles.permissionTitle}>Permiso de cámara</Text>
        <Text style={styles.permissionMessage}>
          Necesitamos acceso a tu cámara para tomar la selfie de verificación.
        </Text>

        {permission.canAskAgain ? (
          <TouchableOpacity
            style={styles.permissionButton}
            onPress={requestPermission}
          >
            <Text style={styles.permissionButtonText}>CONCEDER PERMISO</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity
            style={styles.permissionButton}
            onPress={() => Linking.openSettings()}
          >
            <Text style={styles.permissionButtonText}>ABRIR AJUSTES</Text>
          </TouchableOpacity>
        )}
      </View>
    );
  }

  const handleCapture = async () => {
    if (!cameraRef.current || isCapturing) return;

    setIsCapturing(true);
    try {
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.8,
        base64: false,
        skipProcessing: false,
      });

      if (photo?.uri) {
        onCapture(photo.uri);
      }
    } catch (error) {
      console.warn('Error al capturar selfie:', error);
    } finally {
      setIsCapturing(false);
    }
  };

  return (
    <View style={styles.cameraContainer}>
      <CameraView ref={cameraRef} style={styles.camera} facing="front">
        <View style={styles.faceGuide}>
          <View style={styles.faceOval} />
        </View>
      </CameraView>

      <TouchableOpacity
        style={styles.captureButton}
        onPress={handleCapture}
        disabled={isCapturing}
      >
        {isCapturing ? (
          <ActivityIndicator color={COLORS.textDark} />
        ) : (
          <Text style={styles.captureButtonText}>📸 TOMAR SELFIE</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  centerContainer: {
    height: 300,
    alignItems: 'center',
    justifyContent: 'center',
  },
  permissionContainer: {
    padding: 24,
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  permissionIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  permissionTitle: {
    color: COLORS.textPrimary,
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  permissionMessage: {
    color: COLORS.textPrimary,
    fontSize: 14,
    textAlign: 'center',
    opacity: 0.8,
    marginBottom: 24,
    lineHeight: 20,
  },
  permissionButton: {
    backgroundColor: COLORS.primary,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  permissionButtonText: {
    color: COLORS.textDark,
    fontSize: 14,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
  cameraContainer: {
    alignItems: 'center',
  },
  camera: {
    width: 280,
    height: 360,
    borderRadius: 16,
    overflow: 'hidden',
    backgroundColor: '#000',
  },
  faceGuide: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  faceOval: {
    width: 180,
    height: 240,
    borderRadius: 90,
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.5)',
    borderStyle: 'dashed',
  },
  captureButton: {
    marginTop: 20,
    backgroundColor: COLORS.primary,
    paddingHorizontal: 32,
    paddingVertical: 14,
    borderRadius: 8,
    minWidth: 200,
    alignItems: 'center',
  },
  captureButtonText: {
    color: COLORS.textDark,
    fontSize: 15,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
  previewContainer: {
    alignItems: 'center',
  },
  previewImage: {
    width: 280,
    height: 360,
    borderRadius: 16,
    backgroundColor: '#000',
  },
  retakeButton: {
    marginTop: 16,
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderWidth: 1,
    borderColor: COLORS.primary,
    borderRadius: 8,
  },
  retakeText: {
    color: COLORS.primary,
    fontSize: 14,
    fontWeight: '600',
  },
});