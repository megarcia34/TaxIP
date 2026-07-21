"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

interface EmailVerificationProps {
  email: string;
  onVerified: () => void;
  onCancel?: () => void;
  onEmailChange?: (email: string) => void;
  strictValidation?: boolean; // Si es true, valida SMTP
}

export function EmailVerification({ 
  email, 
  onVerified, 
  onCancel, 
  onEmailChange,
  strictValidation = true 
}: EmailVerificationProps) {
  const [codigo, setCodigo] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [validating, setValidating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [timer, setTimer] = useState(0);
  const [canResend, setCanResend] = useState(true);
  const [emailTemp, setEmailTemp] = useState(email);
  const [emailValid, setEmailValid] = useState<boolean | null>(null);
  const [validationDetails, setValidationDetails] = useState<any>(null);
  const [codigoEnviado, setCodigoEnviado] = useState(false);

  // ============================================
  // VALIDAR EMAIL (SMTP)
  // ============================================
  const validarEmail = async (): Promise<boolean> => {
    if (!emailTemp || !emailTemp.includes('@')) {
      setError('Ingresa un email válido');
      return false;
    }

    setValidating(true);
    setError(null);
    setEmailValid(null);
    
    try {
      // Validar email con SMTP
      const response = await api.post('/api/verificacion/validar-email', null, {
        params: { 
          email: emailTemp,
          strict: strictValidation
        }
      });
      
      setValidationDetails(response.data);
      
      if (!response.data.valid) {
        let errorMsg = `❌ ${response.data.reason || 'El email no es válido'}`;
        
        // Mostrar sugerencias si hay
        if (response.data.suggestions && response.data.suggestions.length > 0) {
          errorMsg += `\n💡 ¿Quisiste decir: ${response.data.suggestions[0].suggestion}?`;
        }
        
        setError(errorMsg);
        setEmailValid(false);
        return false;
      }
      
      setEmailValid(true);
      return true;
      
    } catch (err: any) {
      console.error('Error validando email:', err);
      const errorMsg = err.response?.data?.detail || 'Error validando email. Intentá nuevamente.';
      setError(errorMsg);
      setEmailValid(false);
      return false;
    } finally {
      setValidating(false);
    }
  };

  // ============================================
  // ENVIAR CÓDIGO DE VERIFICACIÓN
  // ============================================
  const enviarCodigo = async () => {
    // 1. Validar email (SMTP) si es estricto
    if (strictValidation) {
      const isValid = await validarEmail();
      if (!isValid) return;
    } else {
      // Validación básica de formato
      if (!emailTemp || !emailTemp.includes('@')) {
        setError('Ingresa un email válido');
        return;
      }
    }

    // 2. Verificar si el email ya está registrado
    setSending(true);
    setError(null);
    
    try {
      const checkResponse = await api.get('/api/verificacion/check-registro', {
        params: { email: emailTemp }
      });
      
      if (checkResponse.data.registrado) {
        setError('⚠️ Este email ya está registrado en la plataforma. Por favor, inicia sesión.');
        setSending(false);
        return;
      }

      // 3. Enviar código de verificación
      await api.post('/api/verificacion/enviar', null, {
        params: { email: emailTemp }
      });
      
      setCodigoEnviado(true);
      setCanResend(false);
      setTimer(60);
      
      // Iniciar contador
      const interval = setInterval(() => {
        setTimer((t) => {
          if (t <= 1) {
            clearInterval(interval);
            setCanResend(true);
            return 0;
          }
          return t - 1;
        });
      }, 1000);
      
      if (onEmailChange) {
        onEmailChange(emailTemp);
      }
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al enviar el código');
    } finally {
      setSending(false);
    }
  };

  // ============================================
  // VERIFICAR CÓDIGO
  // ============================================
  const verificar = async () => {
    if (!codigo || codigo.length < 6) {
      setError('Ingresa el código de 6 dígitos');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await api.post('/api/verificacion/verificar', null, {
        params: { email: emailTemp, codigo }
      });
      
      setSuccess(true);
      setTimeout(() => {
        onVerified();
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Código inválido');
    } finally {
      setLoading(false);
    }
  };

  // ============================================
  // LIMPIAR ERROR
  // ============================================
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 8000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  // ============================================
  // RENDER - EXITOSO
  // ============================================
  if (success) {
    return (
      <div style={{ textAlign: 'center', padding: '1.5rem 1rem' }}>
        <div style={{ fontSize: '4rem', marginBottom: '0.75rem' }}>✅</div>
        <h3 style={{ fontWeight: 700, color: '#1a1a1a', marginBottom: '0.5rem' }}>
          ¡Email verificado!
        </h3>
        <p style={{ color: '#6B7280', fontSize: '0.875rem' }}>
          {emailTemp} ha sido verificado correctamente.
        </p>
        <p style={{ color: '#9CA3AF', fontSize: '0.75rem', marginTop: '0.5rem' }}>
          Redirigiendo...
        </p>
      </div>
    );
  }

  // ============================================
  // RENDER - PRINCIPAL
  // ============================================
  return (
    <div style={{ padding: '0.5rem 0' }}>
      {/* Título */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#1a1a1a' }}>
          Verificar Email
        </h3>
        <p style={{ fontSize: '0.875rem', color: '#6B7280' }}>
          {strictValidation 
            ? 'Verificaremos que el email sea válido y te enviaremos un código' 
            : 'Te enviaremos un código de verificación al email'}
        </p>
      </div>

      {/* Email input */}
      <div style={{ marginBottom: '1rem' }}>
        <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a1a1a', marginBottom: '0.5rem' }}>
          Email
        </label>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="email"
            className="form-input"
            placeholder="tu@email.com"
            value={emailTemp}
            onChange={(e) => {
              setEmailTemp(e.target.value);
              setEmailValid(null);
              setValidationDetails(null);
              setCodigoEnviado(false);
            }}
            disabled={success || codigoEnviado}
            style={{ flex: 1 }}
          />
          {!codigoEnviado && (
            <button
              onClick={enviarCodigo}
              disabled={sending || validating || !emailTemp}
              style={{
                padding: '0 1.5rem',
                backgroundColor: '#FBBF24',
                color: '#1a1a1a',
                border: 'none',
                borderRadius: '0.75rem',
                fontWeight: 600,
                cursor: sending || validating || !emailTemp ? 'not-allowed' : 'pointer',
                opacity: sending || validating || !emailTemp ? 0.6 : 1,
                whiteSpace: 'nowrap',
              }}
            >
              {sending ? 'Enviando...' : validating ? 'Validando...' : 'Enviar código'}
            </button>
          )}
        </div>
      </div>

      {/* Estado de validación SMTP */}
      {emailValid !== null && (
        <div style={{
          padding: '0.5rem 0.75rem',
          borderRadius: '0.5rem',
          marginBottom: '1rem',
          fontSize: '0.875rem',
          backgroundColor: emailValid ? '#ECFDF5' : '#FEF2F2',
          color: emailValid ? '#065F46' : '#991B1B',
          border: `1px solid ${emailValid ? '#6EE7B7' : '#FCA5A5'}`,
        }}>
          {emailValid ? (
            <span>✅ Email validado correctamente</span>
          ) : (
            <span>❌ {validationDetails?.reason || 'Email inválido'}</span>
          )}
          {validationDetails?.suggestions?.length > 0 && (
            <div style={{ marginTop: '0.25rem', fontSize: '0.75rem' }}>
              💡 Sugerencia: {validationDetails.suggestions[0].suggestion}
            </div>
          )}
        </div>
      )}

      {/* Código de verificación */}
      {codigoEnviado && (
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a1a1a', marginBottom: '0.5rem' }}>
            Código de verificación
          </label>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              className="form-input"
              placeholder="Código de 6 dígitos"
              value={codigo}
              onChange={(e) => setCodigo(e.target.value.replace(/\D/g, '').slice(0, 6))}
              maxLength={6}
              style={{ 
                textAlign: 'center', 
                letterSpacing: '0.5rem', 
                fontSize: '1.25rem',
                flex: 1
              }}
              autoFocus
              disabled={success}
            />
            <button
              onClick={verificar}
              disabled={loading || codigo.length < 6 || success}
              style={{
                padding: '0 1.5rem',
                backgroundColor: '#FBBF24',
                color: '#1a1a1a',
                border: 'none',
                borderRadius: '0.75rem',
                fontWeight: 600,
                cursor: loading || codigo.length < 6 || success ? 'not-allowed' : 'pointer',
                opacity: loading || codigo.length < 6 || success ? 0.6 : 1,
                whiteSpace: 'nowrap',
              }}
            >
              {loading ? 'Verificando...' : 'Verificar'}
            </button>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem' }}>
            <span style={{ fontSize: '0.75rem', color: '#9CA3AF' }}>
              Reenviar código {canResend ? '✅' : `en ${timer}s`}
            </span>
            {canResend && codigoEnviado && (
              <button
                onClick={enviarCodigo}
                disabled={sending}
                style={{
                  fontSize: '0.75rem',
                  color: '#FBBF24',
                  background: 'transparent',
                  border: 'none',
                  cursor: sending ? 'not-allowed' : 'pointer',
                }}
              >
                Reenviar
              </button>
            )}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{
          backgroundColor: '#FEF2F2',
          border: '1px solid #EF4444',
          borderRadius: '0.5rem',
          padding: '0.75rem',
          marginBottom: '1rem',
          color: '#991B1B',
          fontSize: '0.875rem',
          whiteSpace: 'pre-line',
        }}>
          {error}
        </div>
      )}

      {/* Acciones */}
      <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
        {onCancel && !success && (
          <button
            onClick={onCancel}
            style={{
              flex: 1,
              padding: '0.75rem',
              backgroundColor: 'transparent',
              color: '#4B5563',
              border: '2px solid #E5E7EB',
              borderRadius: '0.75rem',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            Cancelar
          </button>
        )}
        
        {codigoEnviado && !success && (
          <div style={{ flex: 1, textAlign: 'center', fontSize: '0.75rem', color: '#9CA3AF' }}>
            {!canResend && `Código válido por ${timer}s`}
          </div>
        )}
      </div>

      {/* Información de seguridad */}
      {strictValidation && emailValid && (
        <div style={{
          marginTop: '1rem',
          padding: '0.75rem',
          backgroundColor: '#F3F4F6',
          borderRadius: '0.5rem',
          fontSize: '0.75rem',
          color: '#6B7280',
        }}>
          <div>🔒 Validación SMTP completada</div>
          <div style={{ marginTop: '0.25rem', fontSize: '0.7rem' }}>
            Dominio: {validationDetails?.domain || 'N/A'} · 
            MX: {validationDetails?.mx_records?.length || 0} registros
          </div>
        </div>
      )}
    </div>
  );
}