import { useState, useEffect, useCallback } from 'react';
import { useFocusEffect, useRouter } from 'expo-router';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { COLORS } from '@/constants/colors';
import { useAuthStore } from '@/stores/auth.store';
import { useTurnoStore } from '@/stores/turno.store';
import { turnoService } from '@/services/turno.service';
import { ScreenHeader } from '@/components/common/ScreenHeader';
import { HeaderTurnos } from '@/components/turno/HeaderTurnos';
import { BotonGrande } from '@/components/turno/BotonGrande';
import { EstadoCuentaCard } from '@/components/turno/EstadoCuentaCard';
import { TurnoActivoCard } from '@/components/turno/TurnoActivoCard';
import { ModalCodigo } from '@/components/turno/ModalCodigo';
import { ModalCheckIn } from '@/components/turno/ModalCheckIn';
import { ModalCheckOut } from '@/components/turno/ModalCheckOut';
import {
  ModalSeleccionVehiculo,
  VehiculoDisponible,
} from '@/components/turno/ModalSeleccionVehiculo';
import type {
  Combustible,
  VehiculoInfo,
  CheckInResponse,
} from '@/types/turno.types';

export default function TurnosScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user } = useAuthStore();
  const {
    turnoActivo,
    estadoLaboral,
    cargarEstado,
    cargarTurnoActivo,
    isLoading: storeLoading,
    error: storeError,
  } = useTurnoStore();

  // ============================================
  // ESTADO LOCAL
  // ============================================
  const [esPropietario, setEsPropietario] = useState(false);
  const [requiereCodigo, setRequiereCodigo] = useState(true);
  const [vehiculosDisponibles, setVehiculosDisponibles] = useState<
    VehiculoDisponible[]
  >([]);

  const [vehiculoSeleccionado, setVehiculoSeleccionado] =
    useState<VehiculoDisponible | null>(null);

  const [vehiculo, setVehiculo] = useState<VehiculoInfo | null>(null);
  const [licencia, setLicencia] = useState<string | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);

  const [modalCodigoVisible, setModalCodigoVisible] = useState(false);
  const [modalSeleccionVisible, setModalSeleccionVisible] = useState(false);
  const [modalCheckInVisible, setModalCheckInVisible] = useState(false);
  const [modalCheckOutVisible, setModalCheckOutVisible] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [isLoadingLocal, setIsLoadingLocal] = useState(false);

  const nombreCorto = user?.nombreCompleto?.split(' ')[0] || 'Chofer';

  // ============================================
  // CARGAR ESTADO CADA VEZ QUE LA PANTALLA RECIBE FOCO
  // ============================================
  useFocusEffect(
    useCallback(() => {
      cargarEstado();
      cargarTurnoActivo();
      detectarModoUsuario();
    }, [])
  );

  // Cuando se carga el turno activo, cargamos los datos del vehículo
  useEffect(() => {
    if (turnoActivo) {
      setVehiculo({
        id: turnoActivo.vehiculoId,
        patente: turnoActivo.patente,
        marca: turnoActivo.marca,
        modelo: turnoActivo.modelo,
        anio: turnoActivo.anio,
      });
    }
  }, [turnoActivo]);

  // ============================================
  // DETECTAR MODO DE USUARIO
  // ============================================
  const detectarModoUsuario = async () => {
    try {
      const data = await turnoService.obtenerModoInicio();
      setEsPropietario(data.esPropietario);
      setRequiereCodigo(data.requiereCodigo);
      setVehiculosDisponibles(data.vehiculosDisponibles || []);
    } catch (err: any) {
      console.warn(
        '[Turnos] modo-inicio falló:',
        err?.response?.data?.detail || err?.message
      );
      // Fallback conservador: asumir chofer normal (requiere código).
      setEsPropietario(false);
      setRequiereCodigo(true);
      setVehiculosDisponibles([]);
    }
  };

  // ============================================
  // BOTÓN PRINCIPAL
  // ============================================
  const handleBotonPress = () => {
    setError(null);

    if (turnoActivo) {
      setModalCheckOutVisible(true);
      return;
    }

    if (requiereCodigo) {
      setModalCodigoVisible(true);
    } else {
      if (vehiculosDisponibles.length === 1) {
        setVehiculoSeleccionado(vehiculosDisponibles[0]);
        setModalCheckInVisible(true);
      } else if (vehiculosDisponibles.length > 1) {
        setModalSeleccionVisible(true);
      } else {
        setError('No tenés vehículos disponibles para trabajar');
      }
    }
  };

  // ============================================
  // SELECCIONAR VEHÍCULO (propietario)
  // ============================================
  const handleSeleccionarVehiculo = (vehiculo: VehiculoDisponible) => {
    setVehiculoSeleccionado(vehiculo);
    setModalSeleccionVisible(false);
    setModalCheckInVisible(true);
  };

  // ============================================
  // VALIDAR CÓDIGO (chofer normal)
  // ============================================
  const handleValidarCodigo = async (codigo: string) => {
    setError(null);
    setIsLoadingLocal(true);
    try {
      const response = await turnoService.validarCodigo(codigo);

      setVehiculo(response.vehiculo);
      setLicencia(response.licencia || null);
      setAuthToken(response.authToken);

      setModalCodigoVisible(false);
      setModalCheckInVisible(true);
    } catch (err: any) {
      const mensaje =
        err?.response?.data?.detail ||
        err?.message ||
        'Código inválido o expirado';
      setError(mensaje);
    } finally {
      setIsLoadingLocal(false);
    }
  };

  // ============================================
  // CHECK-IN
  // ============================================
  const handleCheckIn = async (
    kmInicial: number,
    combustibleInicial: Combustible
  ) => {
    setError(null);
    setIsLoadingLocal(true);
    try {
      let response: CheckInResponse;

      if (requiereCodigo && authToken) {
        response = await turnoService.checkIn(
          authToken,
          kmInicial,
          combustibleInicial
        );
      } else if (vehiculoSeleccionado) {
        response = await turnoService.checkInDirecto(
          vehiculoSeleccionado.id,
          kmInicial,
          combustibleInicial
        );
      } else {
        throw new Error('Falta información para iniciar turno');
      }

      useTurnoStore.getState().setTurnoActivo({
        id: response.turnoId,
        estado: 'ACTIVO',
        inicioTurno: response.inicioTurno,
        vehiculoId: response.vehiculoId,
        patente: response.patente,
        marca: response.marca,
        modelo: response.modelo,
        anio: response.anio,
        estadoLaboral: response.estadoLaboral,
        kmInicial: response.kmInicial,
        combustibleInicial: response.combustibleInicial,
        duracionMinutos: response.duracionMinutos,
        duracionFormateada: response.duracionFormateada,
      });

      setModalCheckInVisible(false);
      setAuthToken(null);
      setVehiculoSeleccionado(null);

      cargarEstado().catch(() => {});
    } catch (err: any) {
      const mensaje =
        err?.response?.data?.detail ||
        err?.message ||
        'Error al iniciar turno';
      setError(mensaje);
    } finally {
      setIsLoadingLocal(false);
    }
  };

  // ============================================
  // CHECK-OUT
  // ============================================
  const handleCheckOut = async (
    kmFinal: number,
    combustibleFinal: Combustible,
    recaudacionTicketera: number
  ) => {
    setError(null);
    setIsLoadingLocal(true);
    try {
      await turnoService.checkOut(
        kmFinal,
        combustibleFinal,
        recaudacionTicketera
      );

      useTurnoStore.getState().setTurnoActivo(null);

      setModalCheckOutVisible(false);
      setVehiculo(null);
      setLicencia(null);

      cargarEstado().catch(() => {});
    } catch (err: any) {
      const mensaje =
        err?.response?.data?.detail ||
        err?.message ||
        'Error al finalizar turno';
      setError(mensaje);
    } finally {
      setIsLoadingLocal(false);
    }
  };

  // ============================================
  // DETERMINAR MODO DEL BOTÓN
  // ============================================
  const getModoBoton = ():
    | 'iniciar_con_codigo'
    | 'iniciar_directo'
    | 'finalizar' => {
    if (turnoActivo) {
      return 'finalizar';
    }
    if (requiereCodigo) {
      return 'iniciar_con_codigo';
    }
    return 'iniciar_directo';
  };

  // ============================================
  // OBTENER PATENTE PARA EL MODAL
  // ============================================
  const getPatenteModal = (): string | undefined => {
    if (vehiculoSeleccionado) {
      return vehiculoSeleccionado.patente;
    }
    if (vehiculo) {
      return vehiculo.patente;
    }
    return undefined;
  };

  // ============================================
  // RENDER
  // ============================================
  const isLoadingAny = storeLoading || isLoadingLocal;

  return (
    <LinearGradient
      colors={[COLORS.backgroundDark, COLORS.backgroundMedium]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
    >
      <ScrollView
        contentContainerStyle={[
          styles.scrollContent,
          { paddingTop: insets.top + 16 },
        ]}
        showsVerticalScrollIndicator={false}
      >
        <ScreenHeader
          titulo="TURNOS"
          textoIzquierda="← HOME"
          onIzquierda={() => router.replace('/(app)/home' as any)}
          conSafeArea={false}
        />

        <HeaderTurnos nombre={nombreCorto} estadoLaboral={estadoLaboral} />

        <BotonGrande
          modo={getModoBoton()}
          onPress={handleBotonPress}
          isLoading={isLoadingAny}
        />

        <EstadoCuentaCard
          vehiculo={
            turnoActivo
              ? {
                  patente: turnoActivo.patente,
                  marca: turnoActivo.marca || '',
                  modelo: turnoActivo.modelo || '',
                  anio: turnoActivo.anio,
                  licencia: 'N/A',
                }
              : vehiculo && licencia
              ? {
                  patente: vehiculo.patente,
                  marca: vehiculo.marca || '',
                  modelo: vehiculo.modelo || '',
                  anio: vehiculo.anio,
                  licencia,
                }
              : vehiculoSeleccionado
              ? {
                  patente: vehiculoSeleccionado.patente,
                  marca: vehiculoSeleccionado.marca || '',
                  modelo: vehiculoSeleccionado.modelo || '',
                  anio: vehiculoSeleccionado.anio,
                  licencia: 'N/A',
                }
              : null
          }
          documentosVigentes={3}
          documentosTotal={3}
        />

        {turnoActivo && <TurnoActivoCard turno={turnoActivo} />}

        {(error || storeError) && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorTexto}>⚠️ {error || storeError}</Text>
          </View>
        )}
      </ScrollView>

      <ModalCodigo
        visible={modalCodigoVisible}
        onClose={() => {
          setModalCodigoVisible(false);
          setError(null);
        }}
        onValidar={handleValidarCodigo}
        isLoading={isLoadingLocal}
        error={error}
      />

      <ModalSeleccionVehiculo
        visible={modalSeleccionVisible}
        onClose={() => {
          setModalSeleccionVisible(false);
          setError(null);
        }}
        vehiculos={vehiculosDisponibles}
        onSeleccionar={handleSeleccionarVehiculo}
        isLoading={isLoadingLocal}
      />

      <ModalCheckIn
        visible={modalCheckInVisible}
        onClose={() => {
          setModalCheckInVisible(false);
          setAuthToken(null);
          setVehiculoSeleccionado(null);
          setError(null);
        }}
        onIniciar={handleCheckIn}
        isLoading={isLoadingLocal}
        error={error}
        patente={getPatenteModal()}
      />

      <ModalCheckOut
        visible={modalCheckOutVisible}
        onClose={() => {
          setModalCheckOutVisible(false);
          setError(null);
        }}
        onFinalizar={handleCheckOut}
        kmInicial={turnoActivo?.kmInicial || 0}
        isLoading={isLoadingLocal}
        error={error}
      />
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  errorContainer: {
    backgroundColor: 'rgba(239, 68, 68, 0.15)',
    borderRadius: 8,
    padding: 12,
    marginTop: 16,
  },
  errorTexto: {
    color: COLORS.error,
    fontSize: 13,
    textAlign: 'center',
  },
});