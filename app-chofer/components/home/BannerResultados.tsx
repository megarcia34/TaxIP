import { useRef, useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  ScrollView,
  NativeSyntheticEvent,
  NativeScrollEvent,
  Dimensions,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { COLORS } from '@/constants/colors';

export interface BannerInfo {
  titulo: string;
  subtitulo: string;
  color_estado: string;
  tipo_contrato?: string;
  porcentaje_chofer?: number;
  monto_diario?: number;
  tratamiento_gastos?: string;
}

export interface ResultadosResumen {
  fecha: string;
  viajes: number;
  recaudado: number;
  kmRecorridos: number;
  duracionMinutos: number;
  viajeMasCaro: number;
  viajeMasBajo: number;
  promedioViaje: number;
  desglose_por_origen?: Record<string, { viajes: number; recaudado: number }>;
  // Nuevos campos Fase 1
  banner_info: BannerInfo;
  recaudacion_efectivo: number;
  recaudacion_electronico: number;
  gastos_turno: number;
}

interface BannerResultadosProps {
  datos: ResultadosResumen | null;
  isLoading?: boolean;
}

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const BANNER_PADDING = 20;
const CARD_PADDING = 16;
const SLIDE_WIDTH = SCREEN_WIDTH - BANNER_PADDING * 2 - CARD_PADDING * 2;
const AUTO_SCROLL_INTERVAL = 4000; // Un poco mas lento para que se lea bien
const PAUSE_AFTER_TOUCH = 5000;

export function BannerResultados({
  datos,
  isLoading = false,
}: BannerResultadosProps) {
  const navigation = useNavigation<any>();
  const scrollRef = useRef<ScrollView>(null);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isAutoScrollPaused, setIsAutoScrollPaused] = useState(false);
  const pauseTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const formatMoneda = (valor: number | null | undefined) => {
    if (valor === null || valor === undefined) return '$0';
    return `$${valor.toLocaleString('es-AR')}`;
  };

  const formatDuracion = (minutos: number | null | undefined) => {
    if (minutos === null || minutos === undefined) return '00:00';
    const horas = Math.floor(minutos / 60);
    const mins = minutos % 60;
    return `${horas.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
  };

  const getColorByEstado = (estado: string) => {
    switch (estado) {
      case 'naranja': return '#FF9800';
      case 'verde': return '#4CAF50';
      case 'gris': return '#9E9E9E';
      default: return COLORS.primary;
    }
  };

  const handleScrollBeginDrag = () => {
    if (pauseTimeoutRef.current) clearTimeout(pauseTimeoutRef.current);
    setIsAutoScrollPaused(true);
  };

  const handleScrollEndDrag = () => {
    pauseTimeoutRef.current = setTimeout(() => {
      setIsAutoScrollPaused(false);
    }, PAUSE_AFTER_TOUCH);
  };

  const handleScroll = (event: NativeSyntheticEvent<NativeScrollEvent>) => {
    const offsetX = event.nativeEvent.contentOffset.x;
    const slideIndex = Math.round(offsetX / SLIDE_WIDTH);
    setCurrentSlide(slideIndex);
  };

  const totalSlides = 3;

  useEffect(() => {
    if (!datos || datos.viajes === 0) return;
    if (isAutoScrollPaused) return;

    const interval = setInterval(() => {
      const nextSlide = (currentSlide + 1) % totalSlides;
      scrollRef.current?.scrollTo({
        x: nextSlide * SLIDE_WIDTH,
        animated: true,
      });
      setCurrentSlide(nextSlide);
    }, AUTO_SCROLL_INTERVAL);

    return () => clearInterval(interval);
  }, [currentSlide, datos, isAutoScrollPaused]);

  useEffect(() => {
    return () => {
      if (pauseTimeoutRef.current) clearTimeout(pauseTimeoutRef.current);
    };
  }, []);

  if (isLoading) {
    return (
      <View style={styles.card}>
        <View style={styles.headerRow}>
          <Text style={styles.titulo}>RESUMEN DE HOY</Text>
        </View>
        <View style={styles.loadingContent}>
          <ActivityIndicator size="small" color={COLORS.primary} />
          <Text style={styles.loadingText}>Cargando datos...</Text>
        </View>
      </View>
    );
  }

  if (!datos || datos.viajes === 0) {
    return (
      <View style={styles.card}>
        <View style={styles.headerRow}>
          <Text style={styles.titulo}>RESUMEN DE HOY</Text>
        </View>
        <View style={styles.emptyRow}>
          <Text style={styles.emptyIcon}>🌙</Text>
          <Text style={styles.emptyText}>Hoy no trabajaste</Text>
        </View>
      </View>
    );
  }

  // Definicion de los 3 slides dinamicos
  const slides = [
    {
      id: 'objetivo',
      items: [
        {
          icono: '🎯',
          valor: datos.banner_info?.titulo || 'Sin contrato',
          label: datos.banner_info?.subtitulo || 'Contacta a tu propietario',
          color: getColorByEstado(datos.banner_info?.color_estado || 'gris'),
        },
      ],
    },
    {
      id: 'actividad',
      items: [
        { icono: '🛣️', valor: `${datos.kmRecorridos ?? 0} km`, label: 'recorridos' },
        { icono: '⏱️', valor: formatDuracion(datos.duracionMinutos), label: 'hs trabajadas' },
      ],
    },
    {
      id: 'caja',
      items: [
        { icono: '💵', valor: formatMoneda(datos.recaudacion_efectivo), label: 'efectivo' },
        { icono: '💳', valor: formatMoneda(datos.recaudacion_electronico), label: 'electronico' },
      ],
    },
  ];

  return (
    <View style={styles.card}>
      {/* Header */}
      <View style={styles.headerRow}>
        <Text style={styles.titulo}>RESUMEN DE HOY</Text>
        <TouchableOpacity onPress={() => navigation.navigate('Historicos')}>
          <Text style={styles.linkText}>Ver detalle →</Text>
        </TouchableOpacity>
      </View>

      {/* Carrusel */}
      <ScrollView
        ref={scrollRef}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onScroll={handleScroll}
        onScrollBeginDrag={handleScrollBeginDrag}
        onScrollEndDrag={handleScrollEndDrag}
        scrollEventThrottle={16}
        decelerationRate="fast"
        snapToInterval={SLIDE_WIDTH}
        snapToAlignment="start"
        contentContainerStyle={styles.scrollContent}
      >
        {slides.map((slide) => (
          <View key={slide.id} style={styles.slide}>
            <View style={styles.slideInner}>
              {slide.items.map((item, index) => (
                <View key={index} style={styles.item}>
                  <Text style={styles.itemIcon}>{item.icono}</Text>
                  <View style={styles.itemTextContainer}>
                    <Text style={[styles.itemValue, { color: item.color }]}>
                      {item.valor}
                    </Text>
                    <Text style={styles.itemLabel}>{item.label}</Text>
                  </View>
                </View>
              ))}
            </View>
          </View>
        ))}
      </ScrollView>

      {/* Indicadores (dots) */}
      <View style={styles.dotsContainer}>
        {slides.map((_, index) => (
          <View
            key={index}
            style={[styles.dot, currentSlide === index && styles.dotActive]}
          />
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 14,
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    overflow: 'hidden',
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  titulo: {
    color: COLORS.textPrimary,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1.5,
    opacity: 0.7,
  },
  linkText: {
    color: COLORS.primary,
    fontSize: 11,
    fontWeight: '600',
  },
  scrollContent: {
    alignItems: 'center',
  },
  slide: {
    width: SLIDE_WIDTH,
    alignItems: 'center',
    justifyContent: 'center',
  },
  slideInner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    width: '100%',
  },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    justifyContent: 'center',
  },
  itemIcon: {
    fontSize: 22,
    marginRight: 8,
  },
  itemTextContainer: {
    alignItems: 'flex-start',
  },
  itemValue: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  itemLabel: {
    color: COLORS.textPrimary,
    fontSize: 10,
    opacity: 0.6,
    letterSpacing: 0.3,
  },
  divider: {
    width: 1,
    height: 28,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  dotsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 10,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    marginHorizontal: 3,
  },
  dotActive: {
    backgroundColor: COLORS.primary,
    width: 16,
  },
  loadingContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
  },
  loadingText: {
    color: COLORS.textPrimary,
    fontSize: 12,
    opacity: 0.7,
    marginLeft: 8,
  },
  emptyRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
  },
  emptyIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  emptyText: {
    color: COLORS.textPrimary,
    fontSize: 13,
    opacity: 0.7,
  },
});