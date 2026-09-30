import { useRef, useState } from 'react';
import {
  View,
  TextInput,
  StyleSheet,
  Keyboard,
  NativeSyntheticEvent,
  TextInputKeyPressEventData,
} from 'react-native';
import { COLORS } from '@/constants/colors';

interface OTPInputProps {
  length?: number;
  onComplete?: (code: string) => void;
  onChangeText?: (code: string) => void;
  autoFocus?: boolean;
}

export function OTPInput({
  length = 6,
  onComplete,
  onChangeText,
  autoFocus = false,
}: OTPInputProps) {
  const [code, setCode] = useState<string[]>(Array(length).fill(''));
  const inputs = useRef<Array<TextInput | null>>([]);

  
    const handleChange = (text: string, index: number) => {
    // Solo acepta dígitos
    const digit = text.replace(/[^0-9]/g, '').slice(-1);

    const newCode = [...code];
    newCode[index] = digit;
    setCode(newCode);

    const fullCode = newCode.join('');
    onChangeText?.(fullCode);

    // Auto-avance al siguiente input
    if (digit && index < length - 1) {
      inputs.current[index + 1]?.focus();
    }

    // Si está completo, llamar onComplete y cerrar el teclado
    if (fullCode.length === length && !fullCode.includes('')) {
      onComplete?.(fullCode);

      // Cerrar el teclado automáticamente
      Keyboard.dismiss();
    }
  };




  const handleKeyPress = (
    e: NativeSyntheticEvent<TextInputKeyPressEventData>,
    index: number
  ) => {
    // Auto-retroceso al borrar
    if (e.nativeEvent.key === 'Backspace' && !code[index] && index > 0) {
      inputs.current[index - 1]?.focus();
    }
  };

  return (
    <View style={styles.container}>
      {Array(length)
        .fill(0)
        .map((_, index) => (
          <TextInput
            key={index}
            ref={(ref) => {
              inputs.current[index] = ref;
            }}
            style={[styles.input, code[index] ? styles.inputFilled : null]}
            value={code[index]}
            onChangeText={(text) => handleChange(text, index)}
            onKeyPress={(e) => handleKeyPress(e, index)}
            keyboardType="number-pad"
            maxLength={1}
            autoFocus={autoFocus && index === 0}
            selectTextOnFocus
            accessibilityLabel={`Dígito ${index + 1}`}
          />
        ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    paddingHorizontal: 8,
  },
  input: {
    width: 48,
    height: 56,
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.3)',
    borderRadius: 8,
    textAlign: 'center',
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
  },
  inputFilled: {
    borderColor: COLORS.primary,
    backgroundColor: 'rgba(249, 200, 14, 0.1)',
  },
});