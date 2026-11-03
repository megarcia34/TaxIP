import { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
  RefreshControl,
  Modal,
  TextInput,
  Image,
  Alert,
  KeyboardAvoidingView,
  Platform,
  Keyboard,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useNavigation } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { COLORS } from '@/constants/colors';
import {
  finanzasService,
  gastosService,
  type ResumenFinanzas,
} from '@/services/finanzas.service';

const fmtMoney = (n: number | null | undefined) => {
  if (n === null || n === undefined) return '$0';
  return '$' + n.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 });
};

const fmtDuration = (min: number | null | undefined) => {
  if (min === null || min === undefined) return '0h 0m';
  const h = Math.floor(min / 60);
  const m = min % 60;
  return `${h}h ${m}m`;
};

const ORIGEN_LABELS: Record<string, string> = {
  plataforma: 'App / Landing',
  via_publica: 'Calle',
  qr_comercio: 'QR Comercio',
  corporativo: 'Corporativo',
  despacho_manual: 'Despacho Manual',
  desconocido: 'Sin origen',
};

export default function FinanzasScreen() {
  const navigation = useNavigation<any>();
  const insets = useSafeAreaInsets();
  const [data, setData] = useState<ResumenFinanzas | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Estados para el Modal de Gasto
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [nuevoGasto, setNuevoGasto] = useState({ tipo: 'COMBUSTIBLE', monto: '' });
  const [imagenUri, setImagenUri] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  // Estado para el visor de imagen (Comprobante)
  const [imagenComprobante, setImagenComprobante] = useState<string | null>(null);

  const cargar = async () => {
    try {
      setError(null);
      const res = await finanzasService.obtenerResumen();
      setData(res);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'No se pudo cargar finanzas');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    cargar();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    cargar();
  };

  // --- Logica de la Foto ---
  const seleccionarImagen = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      quality: 0.5,
    });
    if (!result.canceled) {
      setImagenUri(result.assets[0].uri);
    }
  };

  const sacarFoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permiso denegado', 'Necesitamos acceso a la camara');
      return;
    }
    const result = await ImagePicker.launchCameraAsync({ quality: 0.5 });
    if (!result.canceled) {
      setImagenUri(result.assets[0].uri);
    }
  };

  const guardarGasto = async () => {
    Keyboard.dismiss();
    if (!nuevoGasto.monto || isNaN(Number(nuevoGasto.monto))) {
      Alert.alert('Error', 'Ingresa un monto valido');
      return;
    }
    if (!data?.turno?.id) {
      Alert.alert('Error', 'No hay turno activo');
      return;
    }
    setIsSaving(true);
    try {
      await gastosService.registrarGasto(
        data.turno.id,
        nuevoGasto.tipo,
        Number(nuevoGasto.monto),
        imagenUri
      );
      setIsModalVisible(false);
      setNuevoGasto({ tipo: 'COMBUSTIBLE', monto: '' });
      setImagenUri(null);
      cargar();
    } catch (e: any) {
      const msg = e?.response?.data?.detail || 'Error desconocido al guardar';
      Alert.alert('Error del Servidor', typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setIsSaving(false);
    }
  };

  // Helper para color de estado de gasto
  const getEstadoColor = (estado: string | undefined) => {
    if (estado === 'aprobado') return '#4CAF50';
    if (estado === 'rechazado') return '#FF6B6B';
    return '#FFC107';
  };

  if (loading) {
    return (
      <LinearGradient colors={[COLORS.backgroundDark, COLORS.backgroundMedium]} style={styles.center}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={styles.loadingText}>Cargando finanzas...</Text>
      </LinearGradient>
    );
  }

  if (error) {
    return (
      <LinearGradient colors={[COLORS.backgroundDark, COLORS.backgroundMedium]} style={styles.center}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity style={styles.retryBtn} onPress={cargar}>
          <Text style={styles.retryText}>Reintentar</Text>
        </TouchableOpacity>
      </LinearGradient>
    );
  }

  if (!data || !data.turno) {
    return (
      <LinearGradient colors={[COLORS.backgroundDark, COLORS.backgroundMedium]} style={[styles.container, { paddingTop: insets.top }]}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Text style={styles.backText}>Volver</Text>
        </TouchableOpacity>
        <View style={styles.center}>
          <Text style={styles.emptyText}>No hay turnos registrados</Text>
          <Text style={styles.emptySubtext}>Inicia un turno para ver tus finanzas</Text>
        </View>
      </LinearGradient>
    );
  }

  const { turno, resumen, viajes, gastos, ingresos, liquidacion, estimacion_liquidacion } = data;

  return (
    <LinearGradient colors={[COLORS.backgroundDark, COLORS.backgroundMedium]} style={styles.container}>
      <View style={[styles.header, { paddingTop: insets.top + 8 }]}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Text style={styles.backText}>Volver</Text>
        </TouchableOpacity>
        <Text style={styles.title}>FINANZAS</Text>
        <View style={{ width: 60 }} />
      </View>

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.primary} />}
      >
        {/* Card Turno */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>TURNO</Text>
            <View style={[styles.badge, { backgroundColor: turno.estado === 'ACTIVO' ? COLORS.primary : '#555' }]}>
              <Text style={styles.badgeText}>{turno.estado}</Text>
            </View>
          </View>
          <Text style={styles.cardLine}>
            {turno.vehiculo?.patente} - {turno.vehiculo?.marca} {turno.vehiculo?.modelo}
          </Text>
          <Text style={styles.cardLine}>
            {fmtDuration(turno.duracionMinutos)} - {turno.kmRecorridos != null ? `${turno.kmRecorridos.toFixed(1)} km` : '0 km'}
          </Text>
          <Text style={styles.cardMuted}>
            {turno.inicioTurno ? new Date(turno.inicioTurno).toLocaleString('es-AR') : '-'}
            {turno.finTurno ? ` -> ${new Date(turno.finTurno).toLocaleString('es-AR')}` : ''}
          </Text>
        </View>

        {/* BLOQUE 1: LA CAJA (Split Efectivo vs Electronico) */}
                {/* BLOQUE 1: LA CAJA (Split Efectivo vs Electronico) */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>CAJA DEL TURNO</Text>
          <View style={styles.rowBetween}>
            <Text style={styles.label}>Efectivo en tu poder</Text>
            <Text style={styles.valueGreen}>{fmtMoney(resumen.recaudacion_efectivo)}</Text>
          </View>
          <View style={styles.rowBetween}>
            <Text style={styles.label}>Acreditado al Propietario</Text>
            <Text style={styles.value}>{fmtMoney(resumen.recaudacion_electronico)}</Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.rowBetween}>
            <Text style={styles.labelBold}>Recaudación Total</Text>
            <Text style={styles.valueBold}>{fmtMoney(resumen.recaudacionTotal)}</Text>
          </View>
          
          {/* NUEVO: Cálculo de lo que debe entregar */}
          {turno.estado === 'PENDIENTE_CONFIRMACION' && (
             <View style={[styles.rowBetween, { marginTop: 8, paddingTop: 8, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.1)' }]}>
               <Text style={[styles.label, { color: COLORS.primary, fontWeight: 'bold' }]}>
                 Efectivo a entregar (Declarado - Gastos)
               </Text>
               <Text style={styles.valueBold}>
                 {fmtMoney(resumen.recaudacion_efectivo - resumen.gastosTotal)}
               </Text>
             </View>
          )}
        </View>

        {/* BLOQUE 2: LISTA DE VIAJES */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>VIAJES ({viajes.length})</Text>
          {viajes.length === 0 ? (
            <Text style={styles.cardMuted}>Sin viajes</Text>
          ) : (
            viajes.map((v, i) => (
              <View key={i} style={styles.listItem}>
                <View style={{ flex: 1 }}>
                  <Text style={styles.itemTitle}>{v.hora ?? '—'} · {v.origen} → {v.destino}</Text>
                  <Text style={styles.itemSub}>{v.metodoPago}</Text>
                </View>
                <Text style={styles.valueGreen}>{fmtMoney(v.monto)}</Text>
              </View>
            ))
          )}
        </View>

        {/* BLOQUE 3: GASTOS CON SEMAFORO */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>GASTOS ({gastos.length})</Text>
            <TouchableOpacity style={styles.addBtn} onPress={() => setIsModalVisible(true)}>
              <Text style={styles.addBtnText}>+ Agregar</Text>
            </TouchableOpacity>
          </View>
          {gastos.length === 0 ? (
            <Text style={styles.cardMuted}>Sin gastos</Text>
          ) : (
            gastos.map((g, i) => (
              <View key={i} style={styles.listItem}>
                <View style={{ flex: 1 }}>
                  <Text style={styles.itemTitle}>{g.hora ?? '—'} · {g.tipo}</Text>
                  {g.descripcion ? <Text style={styles.itemSub}>{g.descripcion}</Text> : null}
                </View>
                <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                  <Text style={styles.valueRed}>-{fmtMoney(g.monto)}</Text>
                  {g.urlComprobante && (
                    <TouchableOpacity onPress={() => setImagenComprobante(g.urlComprobante!)} style={{ marginLeft: 10 }}>
                      <Text style={{ fontSize: 20 }}>🧾</Text>
                    </TouchableOpacity>
                  )}
                  <View style={[
                    styles.badgeEstado,
                    { backgroundColor: getEstadoColor(g.estado_aprobacion) }
                  ]}>
                    <Text style={styles.badgeText}>{g.estado_aprobacion || 'pendiente'}</Text>
                  </View>
                </View>
              </View>
            ))
          )}
        </View>

        {/* BLOQUE 4: ESTIMACION DE LIQUIDACION EN VIVO */}
        {estimacion_liquidacion && (
          <View style={[styles.card, { borderWidth: 1, borderStyle: 'dashed', borderColor: '#FFC107', opacity: 0.95 }]}>
            <Text style={styles.cardTitle}>⚠️ ESTIMACION (Pendiente de Conciliacion)</Text>
            <Text style={styles.cardMuted}>Monto sujeto a aprobacion final del propietario</Text>
            <View style={styles.divider} />
            <View style={styles.rowBetween}>
              <Text style={styles.label}>Monto bruto</Text>
              <Text style={styles.value}>{fmtMoney(estimacion_liquidacion.monto_bruto)}</Text>
            </View>
            <View style={styles.rowBetween}>
              <Text style={styles.label}>Total gastos</Text>
              <Text style={styles.valueRed}>-{fmtMoney(estimacion_liquidacion.total_gastos)}</Text>
            </View>
            <View style={styles.rowBetween}>
              <Text style={styles.label}>Tu parte (chofer)</Text>
              <Text style={styles.valueGreen}>{fmtMoney(estimacion_liquidacion.comision_chofer)}</Text>
            </View>
            <View style={styles.rowBetween}>
              <Text style={styles.label}>Propietario</Text>
              <Text style={styles.value}>{fmtMoney(estimacion_liquidacion.utilidad_propietario)}</Text>
            </View>
          </View>
        )}

        {/* BLOQUE 5: ESTADO DE CONCILIACION */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>ESTADO DEL TURNO</Text>
          {liquidacion ? (
            <View>
              <View style={styles.rowBetween}>
                <Text style={styles.label}>Liquidacion</Text>
                <View style={[styles.badge, { backgroundColor: '#4CAF50' }]}>
                  <Text style={styles.badgeText}>{liquidacion.estado}</Text>
                </View>
              </View>
              <View style={styles.rowBetween}>
                <Text style={styles.label}>Monto bruto</Text>
                <Text style={styles.value}>{fmtMoney(liquidacion.montoBruto)}</Text>
              </View>
              <View style={styles.rowBetween}>
                <Text style={styles.label}>Comision chofer</Text>
                <Text style={styles.valueGreen}>{fmtMoney(liquidacion.comisionChofer)}</Text>
              </View>
              <View style={styles.rowBetween}>
                <Text style={styles.label}>Utilidad propietario</Text>
                <Text style={styles.value}>{fmtMoney(liquidacion.utilidadPropietario)}</Text>
              </View>
            </View>
          ) : (
            <View style={styles.rowBetween}>
              <Text style={styles.label}>Conciliacion</Text>
              <View style={[styles.badge, { backgroundColor: '#FFC107' }]}>
                <Text style={styles.badgeText}>Pendiente</Text>
              </View>
            </View>
          )}
        </View>

        {/* Desglose por canal */}
        {resumen.desglosePorOrigen && Object.keys(resumen.desglosePorOrigen).length > 0 && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>DESGLOSE POR CANAL</Text>
            {Object.entries(resumen.desglosePorOrigen).map(([origen, data]) => (
              <View key={origen} style={styles.rowBetween}>
                <Text style={styles.label}>{ORIGEN_LABELS[origen] || origen}</Text>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
                  <Text style={styles.itemSub}>{data.viajes} viajes</Text>
                  <Text style={styles.valueGreen}>{fmtMoney(data.recaudado)}</Text>
                </View>
              </View>
            ))}
          </View>
        )}
      </ScrollView>

      {/* MODAL DE CARGA DE GASTO */}
      <Modal visible={isModalVisible} animationType="slide" transparent={true}>
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ flex: 1 }}>
          <View style={styles.modalOverlay}>
            <ScrollView contentContainerStyle={{ flexGrow: 1, justifyContent: 'flex-end' }} keyboardShouldPersistTaps="handled">
              <View style={styles.modalContent}>
                <Text style={styles.modalTitle}>Nuevo Gasto</Text>
                <Text style={styles.label}>Tipo de Gasto</Text>
                <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
                  {['COMBUSTIBLE', 'LUBRICANTE', 'LAVADO', 'REPARACION', 'OTROS'].map((tipo) => (
                    <TouchableOpacity
                      key={tipo}
                      style={[styles.tipoBtn, nuevoGasto.tipo === tipo && styles.tipoBtnActive]}
                      onPress={() => setNuevoGasto({ ...nuevoGasto, tipo })}
                    >
                      <Text style={[styles.tipoBtnText, nuevoGasto.tipo === tipo && styles.tipoBtnTextActive]}>{tipo}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
                <Text style={styles.label}>Monto ($)</Text>
                <TextInput
                  style={styles.input}
                  keyboardType="numeric"
                  value={nuevoGasto.monto}
                  onChangeText={(t) => setNuevoGasto({ ...nuevoGasto, monto: t })}
                  placeholder="0.00"
                  placeholderTextColor="#666"
                  returnKeyType="done"
                  onSubmitEditing={() => Keyboard.dismiss()}
                />
                <Text style={styles.label}>Comprobante</Text>
                <View style={{ flexDirection: 'row', gap: 10, marginBottom: 16 }}>
                  <TouchableOpacity style={styles.photoBtn} onPress={sacarFoto}>
                    <Text style={styles.photoBtnText}>Camara</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={styles.photoBtn} onPress={seleccionarImagen}>
                    <Text style={styles.photoBtnText}>Galeria</Text>
                  </TouchableOpacity>
                </View>
                {imagenUri && <Image source={{ uri: imagenUri }} style={styles.previewImage} />}
                <View style={{ flexDirection: 'row', gap: 10, marginTop: 16 }}>
                  <TouchableOpacity style={[styles.modalBtn, { backgroundColor: '#555' }]} onPress={() => { Keyboard.dismiss(); setIsModalVisible(false); }}>
                    <Text style={styles.modalBtnText}>Cancelar</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={[styles.modalBtn, { backgroundColor: COLORS.primary }]} onPress={guardarGasto} disabled={isSaving}>
                    {isSaving ? <ActivityIndicator color="#fff" /> : <Text style={styles.modalBtnText}>Guardar</Text>}
                  </TouchableOpacity>
                </View>
              </View>
            </ScrollView>
          </View>
        </KeyboardAvoidingView>
      </Modal>

      {/* VISOR DE IMAGEN (COMPROBANTE) */}
      <Modal visible={!!imagenComprobante} transparent={true} animationType="fade">
        <View style={styles.imageViewerOverlay}>
          <TouchableOpacity style={styles.closeButton} onPress={() => setImagenComprobante(null)}>
            <Text style={styles.closeButtonText}>X</Text>
          </TouchableOpacity>
          {imagenComprobante && (
            <Image
              source={{ uri: imagenComprobante }}
              style={styles.fullImage}
              resizeMode="contain"
            />
          )}
        </View>
      </Modal>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 24 },
  loadingText: { color: COLORS.textPrimary, marginTop: 12 },
  errorText: { color: '#FF6B6B', textAlign: 'center', marginBottom: 16 },
  retryBtn: { backgroundColor: COLORS.primary, paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8 },
  retryText: { color: '#fff', fontWeight: 'bold' },
  emptyText: { color: COLORS.textPrimary, fontSize: 18, fontWeight: 'bold' },
  emptySubtext: { color: COLORS.textSecondary, marginTop: 8, textAlign: 'center' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingBottom: 12 },
  backBtn: { paddingVertical: 8, paddingRight: 12 },
  backText: { color: COLORS.primary, fontSize: 16, fontWeight: '600' },
  title: { color: COLORS.textPrimary, fontSize: 18, fontWeight: '900', letterSpacing: 2 },
  scrollContent: { paddingHorizontal: 16, paddingBottom: 32 },
  card: { backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 12, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  cardTitle: { color: COLORS.textPrimary, fontSize: 12, fontWeight: '700', letterSpacing: 1.5, opacity: 0.7, marginBottom: 8 },
  cardLine: { color: COLORS.textPrimary, fontSize: 14, marginBottom: 4 },
  cardMuted: { color: COLORS.textSecondary, fontSize: 12, marginTop: 4 },
  badge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 6 },
  badgeText: { color: '#fff', fontSize: 10, fontWeight: 'bold' },
  badgeEstado: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4, marginLeft: 8 },
  rowBetween: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 4 },
  label: { color: COLORS.textSecondary, fontSize: 14 },
  labelBold: { color: COLORS.textPrimary, fontSize: 14, fontWeight: 'bold' },
  value: { color: COLORS.textPrimary, fontSize: 14, fontWeight: '600' },
  valueGreen: { color: '#4CAF50', fontSize: 14, fontWeight: '600' },
  valueRed: { color: '#FF6B6B', fontSize: 14, fontWeight: '600' },
  valueBold: { color: COLORS.primary, fontSize: 18, fontWeight: '900' },
  divider: { height: 1, backgroundColor: 'rgba(255,255,255,0.1)', marginVertical: 8 },
  listItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.05)' },
  itemTitle: { color: COLORS.textPrimary, fontSize: 13 },
  itemSub: { color: COLORS.textSecondary, fontSize: 11, marginTop: 2 },
  addBtn: { backgroundColor: COLORS.primary, paddingHorizontal: 10, paddingVertical: 4, borderRadius: 6 },
  addBtnText: { color: '#fff', fontSize: 12, fontWeight: 'bold' },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.7)', justifyContent: 'flex-end' },
  modalContent: { backgroundColor: COLORS.backgroundDark, borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 20, paddingBottom: 40 },
  modalTitle: { color: COLORS.textPrimary, fontSize: 20, fontWeight: 'bold', marginBottom: 16 },
  input: { backgroundColor: 'rgba(255,255,255,0.1)', color: COLORS.textPrimary, borderRadius: 8, padding: 12, marginBottom: 16 },
  photoBtn: { flex: 1, backgroundColor: 'rgba(255,255,255,0.1)', padding: 12, borderRadius: 8, alignItems: 'center' },
  photoBtnText: { color: COLORS.textPrimary, fontWeight: '600' },
  previewImage: { width: '100%', height: 150, borderRadius: 8, resizeMode: 'cover', marginBottom: 16 },
  modalBtn: { flex: 1, padding: 14, borderRadius: 8, alignItems: 'center' },
  modalBtnText: { color: '#fff', fontWeight: 'bold' },
  tipoBtn: { paddingHorizontal: 12, paddingVertical: 8, borderRadius: 8, backgroundColor: 'rgba(255,255,255,0.1)', borderWidth: 1, borderColor: 'transparent' },
  tipoBtnActive: { backgroundColor: 'rgba(255, 193, 7, 0.2)', borderColor: COLORS.primary },
  tipoBtnText: { color: COLORS.textSecondary, fontSize: 12, fontWeight: 'bold' },
  tipoBtnTextActive: { color: COLORS.primary },
  imageViewerOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.9)', justifyContent: 'center', alignItems: 'center' },
  closeButton: { position: 'absolute', top: 50, right: 20, zIndex: 10, padding: 10, backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: 20 },
  closeButtonText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  fullImage: { width: '100%', height: '80%' },
});