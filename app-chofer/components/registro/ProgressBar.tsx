import { View, Text, StyleSheet } from 'react-native';
import { COLORS } from '@/constants/colors';

interface ProgressBarProps {
  currentStep: number; // 1 a 5
}

const STEPS = ['Registro', 'Email', 'Datos', 'Documentos', 'Selfie'];

export function ProgressBar({ currentStep }: ProgressBarProps) {
  return (
    <View style={styles.container}>
      {/* Línea horizontal de fondo */}
      <View style={styles.lineBackground}>
        <View
          style={[
            styles.lineProgress,
            { width: `${((currentStep - 1) / (STEPS.length - 1)) * 100}%` },
          ]}
        />
      </View>

      {/* Círculos y labels */}
      <View style={styles.stepsRow}>
        {STEPS.map((step, index) => {
          const stepNumber = index + 1;
          const isCompleted = stepNumber < currentStep;
          const isCurrent = stepNumber === currentStep;
          const isPending = stepNumber > currentStep;

          return (
            <View key={step} style={styles.stepContainer}>
              <View
                style={[
                  styles.circle,
                  isCompleted && styles.circleCompleted,
                  isCurrent && styles.circleCurrent,
                  isPending && styles.circlePending,
                ]}
              >
                {isCompleted ? (
                  <Text style={styles.checkText}>✓</Text>
                ) : (
                  <Text
                    style={[
                      styles.circleNumber,
                      isCurrent && styles.circleNumberCurrent,
                    ]}
                  >
                    {stepNumber}
                  </Text>
                )}
              </View>
              <Text
                style={[
                  styles.stepLabel,
                  (isCompleted || isCurrent) && styles.stepLabelActive,
                ]}
                numberOfLines={1}
              >
                {step}
              </Text>
            </View>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingVertical: 20,
    position: 'relative',
  },
  lineBackground: {
    position: 'absolute',
    top: 38,
    left: 40,
    right: 40,
    height: 2,
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    zIndex: 0,
  },
  lineProgress: {
    height: 2,
    backgroundColor: COLORS.primary,
  },
  stepsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    zIndex: 1,
  },
  stepContainer: {
    alignItems: 'center',
    flex: 1,
  },
  circle: {
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
    borderWidth: 2,
  },
  circleCompleted: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  circleCurrent: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  circlePending: {
    backgroundColor: 'transparent',
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  circleNumber: {
    color: 'rgba(255, 255, 255, 0.5)',
    fontSize: 14,
    fontWeight: 'bold',
  },
  circleNumberCurrent: {
    color: COLORS.textDark,
  },
  checkText: {
    color: COLORS.textDark,
    fontSize: 16,
    fontWeight: 'bold',
  },
  stepLabel: {
    color: 'rgba(255, 255, 255, 0.5)',
    fontSize: 10,
    textAlign: 'center',
  },
  stepLabelActive: {
    color: COLORS.textPrimary,
    fontWeight: '600',
  },
});