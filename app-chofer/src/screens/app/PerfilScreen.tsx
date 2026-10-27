import { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert, Modal, ActivityIndicator, TextInput, KeyboardAvoidingView, Platform } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { LinearGradient } from 'expo-linear-gradient';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { COLORS } from '@/constants/colors';
import { ScreenHeader } from '@/components/common/ScreenHeader';
import { useAuthStore } from '@/stores/auth.store';
import { userService, type UserMeResponse } from '@/services/user.service';
import { choferDocumentosService, type DocumentoChofer } from '@/services/chofer_documentos.service';
import { turnoService } from '@/services/turno.service';
import { authService } from '@/services/auth.service';
import { useTurnoStore } from '@/stores/turno.store'; // <-- IMPORT NECESARIO

const DOCS_REQUERIDOS = [
  { key: 'licencia', label: 'Licencia de Conducir' },
  { key: 'sanidad', label: 'Sanidad' },
  { key: 'buena_conducta', label: 'Buena Conducta' },
  { key: 'antecedentes', label: 'Antecedentes' },
  { key: 'dni', label: 'DNI' },
];

const fmtMoney = (n: number) => '$' + n.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 });

export default function PerfilScreen() {
  const navigation = useNavigation<any>();
  const insets = useSafeAreaInsets();
  // Solo traemos 'user' del store, el logout lo maneja authService
  const { user } = useAuthStore(); 

  const [modalActivo, setModalActivo] = useState<'datos' | 'documentos' | 'reporte' | 'password' | null>(null);

  // DATOS PERSONALES
  const [perfilData, setPerfilData] = useState<UserMeResponse | null>(null);
  const [loadingPerfil, setLoadingPerfil] = useState(false);
  const [errorPerfil, setErrorPerfil] = useState<string | null>(null);

  // DOCUMENTACION
  const [documentos, setDocumentos] = useState<DocumentoChofer[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [docSeleccionado, setDocSeleccionado] = useState<string | null>(null);
  const [imagenUri, setImagenUri] = useState<string | null>(null);
  const [fechaVencimiento, setFechaVencimiento] = useState('');
  const [numeroDoc, setNumeroDoc] = useState('');
  const [isSubiendo, setIsSubiendo] = useState(false);

  // REPORTE ACTIVIDAD
  const [historial, setHistorial] = useState<any[]>([]);
  const [loadingHistorial, setLoadingHistorial] = useState(false);

  // CAMBIAR PASSWORD
  const [passActual, setPassActual] = useState('');
  const [passNueva, setPassNueva] = useState('');
  const [isChangingPass, setIsChangingPass] = useState(false);
  const [showPassActual, setShowPassActual] = useState(false);
  const [showPassNueva, setShowPassNueva] = useState(false);

  useEffect(() => {
    if (modalActivo === 'datos' && !perfilData) cargarPerfil();
    if (modalActivo === 'documentos' && documentos.length === 0) cargarDocumentos();
    if (modalActivo === 'reporte' && historial.length === 0) cargarHistorial();
  }, [modalActivo]);

  const cargarPerfil = async () => {
    setLoadingPerfil(true);
    try { setPerfilData(await userService.obtenerMisDatos()); } catch { setErrorPerfil('Error'); } finally { setLoadingPerfil(false); }
  };

  const cargarDocumentos = async () => {
    setLoadingDocs(true);
    try { setDocumentos(await choferDocumentosService.obtenerMisDocumentos()); } catch { Alert.alert('Error', 'No se pudieron cargar los documentos.'); } finally { setLoadingDocs(false); }
  };

  const cargarHistorial = async () => {
    setLoadingHistorial(true);
    try { setHistorial(await turnoService.obtenerHistorial(30, 0)); } catch { Alert.alert('Error', 'No se pudo cargar el historial.'); } finally { setLoadingHistorial(false); }
  };

  const handleCambiarPassword = async () => {
    if (!passActual || !passNueva) return Alert.alert('Error', 'Completá ambos campos');
    if (passNueva.length < 6) return Alert.alert('Error', 'La nueva contraseña debe tener al menos 6 caracteres');
    
    setIsChangingPass(true);
    try {
      await authService.cambiarPassword(passActual, passNueva);
      Alert.alert('Éxito', 'Contraseña actualizada. Por favor iniciá sesión nuevamente.');
      
      // Limpiamos sesión y redirigimos
      useAuthStore.getState().clearSession();
      navigation.reset({
        index: 0,
        routes: [{ name: 'Login' }],
      });
    } catch (e: any) {
      Alert.alert('Error', e?.response?.data?.detail || 'No se pudo cambiar la contraseña');
    } finally { setIsChangingPass(false); }
  };

    const handleCerrarSesion = () => {
    // 1. Verificar si hay turno activo
    const turnoActivo = useTurnoStore.getState().turnoActivo;
    
    if (turnoActivo) {
      return Alert.alert(
        'Turno Activo', 
        'No podés cerrar sesión mientras tenés un turno en curso. Por favor, finalizá tu turno primero.',
        [{ text: 'Entendido' }]
      );
    }

    // 2. Si no hay turno, preguntar y cerrar
    Alert.alert('Cerrar Sesión', '¿Estás seguro que querés salir?', [
      { text: 'Cancelar', style: 'cancel' }, 
      { 
        text: 'Salir', 
        style: 'destructive', 
        onPress: () => {
          // Limpiamos la sesión del store
          useAuthStore.getState().clearSession();
          // Redirigimos al Login limpiando el historial de navegación
          navigation.reset({
            index: 0,
            routes: [{ name: 'Login' }],
          });
        } 
      }
    ]);
  };

  // --- LOGICA DOCUMENTACION ---
  const iniciarSubida = (tipoDoc: string) => {
    setDocSeleccionado(tipoDoc); setImagenUri(null); setFechaVencimiento(''); setNumeroDoc('');
  };

  const tomarFoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') return Alert.alert('Permiso denegado');
    const result = await ImagePicker.launchCameraAsync({ quality: 0.5 });
    if (!result.canceled) setImagenUri(result.assets[0].uri);
  };

  const elegirFoto = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ['images'], quality: 0.5 });
    if (!result.canceled) setImagenUri(result.assets[0].uri);
  };

  const confirmarSubida = async () => {
    if (!docSeleccionado || !imagenUri) return Alert.alert('Error', 'Seleccioná una imagen');
    if (docSeleccionado !== 'dni' && !fechaVencimiento) return Alert.alert('Error', 'Ingresá fecha (YYYY-MM-DD)');
    
    setIsSubiendo(true);
    try {
      await choferDocumentosService.subirDocumento({ tipo_documento: docSeleccionado, fecha_vencimiento: docSeleccionado !== 'dni' ? fechaVencimiento : undefined, numero: numeroDoc, imagenUri });
      Alert.alert('Éxito', 'Documento subido');
      setDocSeleccionado(null);
      cargarDocumentos();
    } catch (e: any) {
      Alert.alert('Error', e?.response?.data?.detail || 'Error al subir');
    } finally { setIsSubiendo(false); }
  };

  // --- RENDERS ---
  const renderDatosPersonales = () => {
    if (loadingPerfil) return <ActivityIndicator size="large" color={COLORS.primary} style={{ marginTop: 20 }} />;
    if (errorPerfil) return <Text style={{ color: '#FF6B6B', textAlign: 'center', marginTop: 20 }}>{errorPerfil}</Text>;
    if (!perfilData?.perfil) return <Text style={{ color: COLORS.textSecondary, textAlign: 'center', marginTop: 20 }}>Sin datos disponibles</Text>;

    return (
      <View style={styles.dataList}>
        <View style={styles.dataRow}><Text style={styles.dataLabel}>Nombre completo</Text><Text style={styles.dataValue}>{perfilData.perfil.nombre} {perfilData.perfil.apellido}</Text></View>
        <View style={styles.dataRow}><Text style={styles.dataLabel}>Email</Text><Text style={styles.dataValue}>{perfilData.email}</Text></View>
        <View style={styles.dataRow}><Text style={styles.dataLabel}>DNI</Text><Text style={styles.dataValue}>{perfilData.perfil.documento || 'No registrado'}</Text></View>
        <View style={styles.dataRow}><Text style={styles.dataLabel}>Teléfono</Text><Text style={styles.dataValue}>{perfilData.perfil.telefono || 'No registrado'}</Text></View>
        <View style={styles.dataRow}><Text style={styles.dataLabel}>Empresa / Ciudad</Text><Text style={styles.dataValue}>{perfilData.tenant?.nombre || 'No asignada'}</Text></View>
      </View>
    );
  };

  const renderDocumentos = () => {
    if (loadingDocs) return <ActivityIndicator size="large" color={COLORS.primary} style={{ marginTop: 20 }} />;
    return (
      <ScrollView style={{ flex: 1 }}>
        {DOCS_REQUERIDOS.map((req) => {
          const docExistente = documentos.find(d => d.tipo_documento === req.key);
          const estaVencido = docExistente?.fecha_vencimiento ? new Date(docExistente.fecha_vencimiento) < new Date() : false;
          
          if (docSeleccionado === req.key) {
            return (
              <View key={req.key} style={styles.uploadForm}>
                <Text style={styles.uploadTitle}>Subir {req.label}</Text>
                <View style={{ flexDirection: 'row', gap: 10, marginBottom: 12 }}>
                  <TouchableOpacity style={styles.photoBtn} onPress={tomarFoto}><Text style={styles.photoBtnText}>📷 {imagenUri ? 'Retomar' : 'Cámara'}</Text></TouchableOpacity>
                  <TouchableOpacity style={styles.photoBtn} onPress={elegirFoto}><Text style={styles.photoBtnText}>🖼 Galería</Text></TouchableOpacity>
                </View>
                {req.key !== 'dni' && <TextInput style={styles.input} placeholder="Vencimiento (YYYY-MM-DD)" placeholderTextColor="#666" value={fechaVencimiento} onChangeText={setFechaVencimiento} />}
                <TextInput style={styles.input} placeholder="Número (opcional)" placeholderTextColor="#666" value={numeroDoc} onChangeText={setNumeroDoc} />
                <View style={{ flexDirection: 'row', gap: 10 }}>
                  <TouchableOpacity style={[styles.btn, { backgroundColor: '#555' }]} onPress={() => setDocSeleccionado(null)}><Text style={styles.btnText}>Cancelar</Text></TouchableOpacity>
                  <TouchableOpacity style={[styles.btn, { backgroundColor: COLORS.primary }]} onPress={confirmarSubida} disabled={isSubiendo}>{isSubiendo ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Subir</Text>}</TouchableOpacity>
                </View>
              </View>
            );
          }
          return (
            <View key={req.key} style={styles.docRow}>
              <View style={{ flex: 1 }}>
                <Text style={styles.docLabel}>{req.label}</Text>
                <Text style={[styles.docSub, estaVencido && { color: '#FF6B6B' }]}>{docExistente ? `Vence: ${docExistente.fecha_vencimiento || 'N/A'} ${estaVencido ? '(VENCIDO)' : ''}` : 'Pendiente'}</Text>
              </View>
              <TouchableOpacity style={styles.btnRenovar} onPress={() => iniciarSubida(req.key)}><Text style={styles.btnRenovarText}>{docExistente ? 'Renovar' : 'Subir'}</Text></TouchableOpacity>
            </View>
          );
        })}
      </ScrollView>
    );
  };

  const renderReporte = () => {
    if (loadingHistorial) return <ActivityIndicator size="large" color={COLORS.primary} style={{ marginTop: 20 }} />;
    if (historial.length === 0) return <Text style={{ color: COLORS.textSecondary, textAlign: 'center', marginTop: 20 }}>No hay turnos cerrados aún.</Text>;
    
    return (
      <ScrollView style={{ flex: 1 }}>
        {historial.map((turno) => (
          <View key={turno.id} style={styles.reporteCard}>
            <View style={styles.reporteHeader}>
              <Text style={styles.reporteFecha}>{new Date(turno.inicioTurno).toLocaleDateString('es-AR')}</Text>
              <Text style={styles.reporteEstado}>{turno.estado}</Text>
            </View>
            <Text style={styles.reporteVehiculo}>🚕 {turno.patente} ({turno.marca} {turno.modelo})</Text>
            
            <View style={styles.reporteStats}>
              <View style={styles.reporteStatCol}>
                <Text style={styles.reporteStatLabel}>Km Recorridos</Text>
                <Text style={styles.reporteStatVal}>{turno.kmFinal && turno.kmInicial ? (turno.kmFinal - turno.kmInicial).toFixed(1) : '0'} km</Text>
              </View>
              <View style={styles.reporteStatCol}>
                <Text style={styles.reporteStatLabel}>Monto Bruto</Text>
                <Text style={styles.reporteStatVal}>{fmtMoney(turno.montoBruto || 0)}</Text>
              </View>
              <View style={styles.reporteStatCol}>
                <Text style={styles.reporteStatLabel}>Tu Ganancia</Text>
                <Text style={[styles.reporteStatVal, { color: '#4CAF50' }]}>{fmtMoney(turno.totalChofer || 0)}</Text>
              </View>
            </View>
          </View>
        ))}
      </ScrollView>
    );
  };

  const renderPassword = () => (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ flex: 1 }}>
      <ScrollView 
        style={{ flex: 1 }} 
        keyboardShouldPersistTaps="handled"
        contentContainerStyle={{ paddingBottom: 40 }}
      >
        <Text style={styles.label}>Contraseña Actual</Text>
        <View style={styles.passwordContainer}>
          <TextInput 
            style={styles.passwordInput} 
            secureTextEntry={!showPassActual} 
            placeholder="••••••" 
            placeholderTextColor="#666" 
            value={passActual} 
            onChangeText={setPassActual} 
            returnKeyType="next"
          />
          <TouchableOpacity onPress={() => setShowPassActual(!showPassActual)} style={styles.eyeBtn}>
            <Text style={{ fontSize: 18 }}>{showPassActual ? '🙈' : '👁️'}</Text>
          </TouchableOpacity>
        </View>
        
        <Text style={styles.label}>Nueva Contraseña</Text>
        <View style={styles.passwordContainer}>
          <TextInput 
            style={styles.passwordInput} 
            secureTextEntry={!showPassNueva} 
            placeholder="Mínimo 6 caracteres" 
            placeholderTextColor="#666" 
            value={passNueva} 
            onChangeText={setPassNueva} 
            returnKeyType="done"
          />
          <TouchableOpacity onPress={() => setShowPassNueva(!showPassNueva)} style={styles.eyeBtn}>
            <Text style={{ fontSize: 18 }}>{showPassNueva ? '🙈' : '👁️'}</Text>
          </TouchableOpacity>
        </View>
        
        <TouchableOpacity style={[styles.btn, { backgroundColor: COLORS.primary, marginTop: 16 }]} onPress={handleCambiarPassword} disabled={isChangingPass}>
          {isChangingPass ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Cambiar Contraseña</Text>}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );

  return (
    <LinearGradient colors={[COLORS.backgroundDark, COLORS.backgroundMedium]} style={styles.container}>
      <View style={[styles.content, { paddingHorizontal: 20 }]}>
        <ScreenHeader titulo="MI CUENTA" textoIzquierda="← HOME" onIzquierda={() => navigation.navigate('Home')} conSafeArea={false} style={{ paddingTop: insets.top + 12 }} />
        <ScrollView contentContainerStyle={styles.scrollContent}>
          
          <View style={styles.profileHeader}>
            <View style={styles.avatar}><Text style={styles.avatarText}>{user?.nombreCompleto?.charAt(0) || 'C'}</Text></View>
            <Text style={styles.nombre}>{user?.nombreCompleto || 'Chofer'}</Text>
            <Text style={styles.email}>{user?.email || 'email@taxip.com'}</Text>
          </View>

          <Text style={styles.seccionTitulo}>MI INFORMACIÓN</Text>
          <TouchableOpacity style={styles.menuItem} onPress={() => setModalActivo('datos')}><Text style={styles.menuIcon}>👤</Text><Text style={styles.menuText}>Datos Personales</Text><Text style={styles.menuArrow}>›</Text></TouchableOpacity>
          <TouchableOpacity style={styles.menuItem} onPress={() => setModalActivo('documentos')}><Text style={styles.menuIcon}>📄</Text><Text style={styles.menuText}>Documentación</Text><Text style={styles.menuArrow}>›</Text></TouchableOpacity>
          <TouchableOpacity style={styles.menuItem} onPress={() => setModalActivo('reporte')}><Text style={styles.menuIcon}>📊</Text><Text style={styles.menuText}>Reporte de Actividad</Text><Text style={styles.menuArrow}>›</Text></TouchableOpacity>

          <Text style={[styles.seccionTitulo, { marginTop: 24 }]}>SEGURIDAD</Text>
          <TouchableOpacity style={styles.menuItem} onPress={() => setModalActivo('password')}><Text style={styles.menuIcon}>🔒</Text><Text style={styles.menuText}>Cambiar Contraseña</Text><Text style={styles.menuArrow}>›</Text></TouchableOpacity>
          <TouchableOpacity style={[styles.menuItem, styles.menuItemDanger]} onPress={handleCerrarSesion}><Text style={styles.menuIcon}>🚪</Text><Text style={[styles.menuText, { color: '#FF6B6B' }]}>Cerrar Sesión</Text></TouchableOpacity>
        </ScrollView>
      </View>

      <Modal visible={modalActivo !== null} transparent animationType="slide">
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ flex: 1 }}>
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>
                  {modalActivo === 'datos' && 'Datos Personales'}
                  {modalActivo === 'documentos' && 'Documentación'}
                  {modalActivo === 'reporte' && 'Reporte de Actividad'}
                  {modalActivo === 'password' && 'Cambiar Contraseña'}
                </Text>
                <TouchableOpacity style={styles.closeBtn} onPress={() => { setModalActivo(null); setDocSeleccionado(null); }}><Text style={styles.closeText}>✕</Text></TouchableOpacity>
              </View>

              {modalActivo === 'datos' && renderDatosPersonales()}
              {modalActivo === 'documentos' && renderDocumentos()}
              {modalActivo === 'reporte' && renderReporte()}
              {modalActivo === 'password' && renderPassword()}
            </View>
          </View>
        </KeyboardAvoidingView>
      </Modal>

    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 }, content: { flex: 1 }, scrollContent: { paddingBottom: 32 },
  profileHeader: { alignItems: 'center', marginVertical: 24 }, avatar: { width: 80, height: 80, borderRadius: 40, backgroundColor: COLORS.primary, alignItems: 'center', justifyContent: 'center', marginBottom: 12 }, avatarText: { color: '#fff', fontSize: 32, fontWeight: 'bold' },
  nombre: { color: COLORS.textPrimary, fontSize: 20, fontWeight: 'bold' }, email: { color: COLORS.textSecondary, fontSize: 14, marginTop: 4 },
  seccionTitulo: { color: COLORS.textPrimary, fontSize: 12, fontWeight: '700', letterSpacing: 1.5, opacity: 0.6, marginBottom: 8, marginLeft: 8 },
  menuItem: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(255,255,255,0.05)', padding: 16, borderRadius: 12, marginBottom: 8, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  menuIcon: { fontSize: 20, marginRight: 12 }, menuText: { flex: 1, color: COLORS.textPrimary, fontSize: 16, fontWeight: '500' }, menuArrow: { color: COLORS.textSecondary, fontSize: 20 },
  menuItemDanger: { borderColor: 'rgba(255, 107, 107, 0.3)', backgroundColor: 'rgba(255, 107, 107, 0.1)' },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.8)', justifyContent: 'flex-end' }, modalContent: { backgroundColor: COLORS.backgroundDark, borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 24, minHeight: '60%', maxHeight: '90%' },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }, modalTitle: { color: COLORS.textPrimary, fontSize: 20, fontWeight: 'bold' }, closeBtn: { padding: 8 }, closeText: { color: COLORS.textSecondary, fontSize: 18, fontWeight: 'bold' },
  dataList: { gap: 12 }, dataRow: { borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.1)', paddingBottom: 12 }, dataLabel: { color: COLORS.textSecondary, fontSize: 12, marginBottom: 4 }, dataValue: { color: COLORS.textPrimary, fontSize: 16 },
  
  // DOCUMENTACION
  docRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(255,255,255,0.05)', padding: 16, borderRadius: 12, marginBottom: 8, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  docLabel: { color: COLORS.textPrimary, fontSize: 16, fontWeight: 'bold' }, docSub: { color: COLORS.textSecondary, fontSize: 13, marginTop: 4 },
  btnRenovar: { backgroundColor: 'rgba(255,255,255,0.1)', paddingHorizontal: 16, paddingVertical: 8, borderRadius: 8 }, btnRenovarText: { color: COLORS.primary, fontWeight: 'bold', fontSize: 14 },
  uploadForm: { backgroundColor: 'rgba(255,255,255,0.05)', padding: 16, borderRadius: 12, marginBottom: 12, borderWidth: 1, borderColor: COLORS.primary },
  uploadTitle: { color: COLORS.textPrimary, fontSize: 16, fontWeight: 'bold', marginBottom: 12 },
  input: { backgroundColor: 'rgba(255,255,255,0.1)', color: COLORS.textPrimary, borderRadius: 8, padding: 12, marginBottom: 12 },
  photoBtn: { flex: 1, backgroundColor: 'rgba(255,255,255,0.1)', padding: 12, borderRadius: 8, alignItems: 'center' }, photoBtnText: { color: COLORS.textPrimary, fontWeight: '600' },
  btn: { flex: 1, padding: 14, borderRadius: 8, alignItems: 'center' }, btnText: { color: '#fff', fontWeight: 'bold' },
  label: { color: COLORS.textSecondary, fontSize: 14, marginBottom: 4 },

  // REPORTE DE ACTIVIDAD
  reporteCard: { backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 12, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  reporteHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  reporteFecha: { color: COLORS.textPrimary, fontSize: 14, fontWeight: 'bold' },
  reporteEstado: { color: COLORS.textSecondary, fontSize: 12 },
  reporteVehiculo: { color: COLORS.textPrimary, fontSize: 13, marginBottom: 12 },
  reporteStats: { flexDirection: 'row', justifyContent: 'space-between', backgroundColor: 'rgba(0,0,0,0.2)', padding: 10, borderRadius: 8 },
  reporteStatCol: { alignItems: 'center', flex: 1 },
  reporteStatLabel: { color: COLORS.textSecondary, fontSize: 10, marginBottom: 4, textAlign: 'center' },
  reporteStatVal: { color: COLORS.textPrimary, fontSize: 14, fontWeight: 'bold' },

  // CONTRASEÑA (OJITO)
  passwordContainer: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 8, marginBottom: 16, paddingRight: 12 },
  passwordInput: { flex: 1, color: COLORS.textPrimary, padding: 12 },
  eyeBtn: { padding: 4 },
});