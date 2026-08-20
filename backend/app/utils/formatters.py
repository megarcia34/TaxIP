# app/utils/formatters.py
"""
Funciones de formateo para números y fechas
"""

def format_number(value: float, decimals: int = 2) -> str:
    """
    Formatea un número con separador de miles (.) y decimales (,)
    Ejemplo: 1234567.89 → "1.234.567,89"
    """
    if value is None:
        return "0,00"
    
    # Formatear con separador de miles y decimales
    if decimals == 0:
        return f"{int(value):,}".replace(",", ".")
    
    parte_entera = int(abs(value))
    parte_decimal = round(abs(value) - parte_entera, decimals)
    
    # Formatear parte entera con separador de miles
    entera_formateada = f"{parte_entera:,}".replace(",", ".")
    
    # Formatear parte decimal con 2 dígitos
    decimal_str = f"{parte_decimal:.{decimals}f}"[2:]
    
    signo = "-" if value < 0 else ""
    return f"{signo}{entera_formateada},{decimal_str}"


def format_currency(value: float) -> str:
    """
    Formatea un número como moneda (ARS)
    Ejemplo: 1234567.89 → "$ 1.234.567,89"
    """
    if value is None:
        return "$ 0,00"
    return f"$ {format_number(value)}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Formatea un número como porcentaje
    Ejemplo: 37.36 → "37,36%"
    """
    if value is None:
        return "0,00%"
    return f"{format_number(value, decimals)}%"