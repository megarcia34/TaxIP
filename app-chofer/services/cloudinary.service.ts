/**
 * Servicio para subir imágenes a Cloudinary.
 */
import * as ImagePicker from 'expo-image-picker';
import {
  CLOUDINARY_CLOUD_NAME,
  CLOUDINARY_UPLOAD_PRESET,
} from '@/constants/config';

/**
 * Toma una foto con la cámara.
 */
export async function takePhoto(): Promise<string> {
  const permission = await ImagePicker.requestCameraPermissionsAsync();
  if (!permission.granted) {
    throw new Error('Permiso de cámara denegado');
  }

  const result = await ImagePicker.launchCameraAsync({
    mediaTypes: ['images'],
    allowsEditing: false,
    quality: 0.8,
    base64: false,
  });

  if (result.canceled || !result.assets[0]) {
    throw new Error('Captura cancelada');
  }

  return result.assets[0].uri;
}

/**
 * Selecciona una imagen de la galería.
 */
export async function pickFromGallery(): Promise<string> {
  const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
  if (!permission.granted) {
    throw new Error('Permiso de galería denegado');
  }

  const result = await ImagePicker.launchImageLibraryAsync({
    mediaTypes: ['images'],
    allowsEditing: false,
    quality: 0.8,
    base64: false,
  });

  if (result.canceled || !result.assets[0]) {
    throw new Error('Selección cancelada');
  }

  return result.assets[0].uri;
}

/**
 * Sube una imagen a Cloudinary.
 *
 * En Expo SDK 57, la API de FormData cambió.
 * Ahora se usa fetch(uri).blob() para obtener el archivo como Blob.
 */
export async function uploadToCloudinary(
  uri: string,
  folder: string = 'documentos'
): Promise<string> {
  // Extraer nombre del archivo
  const filename = uri.split('/').pop() || 'file.jpg';

  // Crear FormData con el Blob
  const formData = new FormData();

  // En SDK 57: obtener el archivo como Blob con fetch nativo
  const fileResponse = await fetch(uri);
  const blob = await fileResponse.blob();

  formData.append('file', blob, filename);
  formData.append('upload_preset', CLOUDINARY_UPLOAD_PRESET);
  formData.append('folder', `choferes/${folder}`);

  // Subir a Cloudinary
  const response = await fetch(
    `https://api.cloudinary.com/v1_1/${CLOUDINARY_CLOUD_NAME}/upload`,
    {
      method: 'POST',
      body: formData,
      headers: {
        Accept: 'application/json',
      },
    }
  );

  const data = await response.json();

  if (data.error) {
    throw new Error(data.error.message || 'Error subiendo a Cloudinary');
  }

  return data.secure_url;
}