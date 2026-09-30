import { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  FlatList,
  ActivityIndicator,
} from 'react-native';
import { COLORS } from '@/constants/colors';

export interface SelectorOption {
  id: string;
  label: string;
  subtitle?: string;
}

interface SelectorProps {
  label: string;
  placeholder: string;
  value: SelectorOption | null;
  options: SelectorOption[];
  onSelect: (option: SelectorOption) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export function Selector({
  label,
  placeholder,
  value,
  options,
  onSelect,
  isLoading = false,
  disabled = false,
}: SelectorProps) {
  const [modalVisible, setModalVisible] = useState(false);

  const handleSelect = (option: SelectorOption) => {
    onSelect(option);
    setModalVisible(false);
  };

  return (
    <View style={styles.wrapper}>
      <Text style={styles.label}>{label}</Text>

      <TouchableOpacity
        style={styles.input}
        onPress={() => setModalVisible(true)}
        disabled={disabled || isLoading}
      >
        <Text style={[styles.inputText, !value && styles.placeholderText]}>
          {value ? value.label : placeholder}
        </Text>
        {isLoading ? (
          <ActivityIndicator size="small" color={COLORS.primary} />
        ) : (
          <Text style={styles.arrow}>▼</Text>
        )}
      </TouchableOpacity>

      <Modal
        visible={modalVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{label}</Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Text style={styles.closeButton}>✕</Text>
              </TouchableOpacity>
            </View>

            <FlatList
              data={options}
              keyExtractor={(item) => item.id}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={styles.option}
                  onPress={() => handleSelect(item)}
                >
                  <Text style={styles.optionLabel}>{item.label}</Text>
                  {item.subtitle && (
                    <Text style={styles.optionSubtitle}>{item.subtitle}</Text>
                  )}
                </TouchableOpacity>
              )}
              ListEmptyComponent={
                <Text style={styles.emptyText}>No hay opciones disponibles</Text>
              }
            />
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    marginBottom: 24,
  },
  label: {
    color: COLORS.textPrimary,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1.5,
    marginBottom: 6,
    opacity: 0.9,
  },
  input: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.35)',
    minHeight: 42,
  },
  inputText: {
    color: COLORS.textPrimary,
    fontSize: 16,
    flex: 1,
  },
  placeholderText: {
    color: 'rgba(255, 255, 255, 0.4)',
  },
  arrow: {
    color: COLORS.textPrimary,
    fontSize: 12,
    opacity: 0.6,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: COLORS.backgroundDark,
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    maxHeight: '70%',
    paddingTop: 16,
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.1)',
  },
  modalTitle: {
    color: COLORS.textPrimary,
    fontSize: 18,
    fontWeight: 'bold',
  },
  closeButton: {
    color: COLORS.textPrimary,
    fontSize: 24,
    padding: 4,
  },
  option: {
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.05)',
  },
  optionLabel: {
    color: COLORS.textPrimary,
    fontSize: 16,
  },
  optionSubtitle: {
    color: COLORS.textSecondary,
    fontSize: 12,
    marginTop: 2,
  },
  emptyText: {
    color: COLORS.textSecondary,
    fontSize: 14,
    textAlign: 'center',
    padding: 32,
  },
});