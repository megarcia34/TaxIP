#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SCRIPT: Reemplazar useSearchParams() por window.location
Proyecto: TaxIP 2.0 Dashboard
Objetivo: Eliminar dependencia de useSearchParams() para evitar errores de build
"""

import os
import re
from pathlib import Path

# ============================================
# CONFIGURACIÓN
# ============================================

BASE_DIR = Path(r"D:\ataxip\dashboard")

# Archivos a procesar con sus parámetros
ARCHIVOS = [
    {"ruta": "app/(public)/reservar/page.tsx", "parametros": ["origenId"]},
    {"ruta": "app/dashboard-propietario/page.tsx", "parametros": ["propietario_id"]},
    {"ruta": "app/dashboard-propietario/contratos/page.tsx", "parametros": ["propietario_id"]},
    {"ruta": "app/dashboard-propietario/gastos/page.tsx", "parametros": ["propietario_id"]},
    {"ruta": "app/dashboard-propietario/ingresos/page.tsx", "parametros": ["propietario_id"]},
    {"ruta": "app/dashboard-propietario/mantenimientos/page.tsx", "parametros": ["propietario_id"]},
    {"ruta": "app/dashboard-propietario/rentabilidad/page.tsx", "parametros": ["propietario_id"]},
    {"ruta": "app/dashboard-propietario/reportes/page.tsx", "parametros": ["propietario_id"]},
    {"ruta": "app/dashboard-propietario/vehiculos/page.tsx", "parametros": ["propietario_id"]},
    {"ruta": "app/dashboard-propietario/vehiculos/nuevo/page.tsx", "parametros": ["propietario_id"]},
]

# ============================================
# FUNCIONES
# ============================================

def procesar_archivo(ruta_archivo: Path, parametros: list) -> bool:
    """
    Procesa un archivo reemplazando useSearchParams() por window.location
    Retorna True si se procesó correctamente, False si no se modificó
    """
    
    if not ruta_archivo.exists():
        print(f"⚠️  Archivo no encontrado: {ruta_archivo}")
        return False
    
    print(f"📝 Procesando: {ruta_archivo}")
    
    # Leer contenido
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Verificar si usa useSearchParams
    if 'useSearchParams' not in contenido:
        print(f"   ⏭️  No usa useSearchParams, omitiendo...")
        return False
    
    original = contenido
    modificado = contenido
    
    # --- PASO 1: ELIMINAR import de useSearchParams ---
    # Eliminar import { useSearchParams } from 'next/navigation'
    modificado = re.sub(r'import\s*\{\s*useSearchParams\s*\}\s*from\s*[\'"]next/navigation[\'"]\s*;?\s*\n?', '', modificado)
    
    # Eliminar useSearchParams de imports combinados
    modificado = re.sub(r'import\s*\{\s*([^}]*)\s*useSearchParams\s*,?\s*([^}]*)\s*\}\s*from\s*[\'"]next/navigation[\'"]', 
                        lambda m: f"import {{ {m.group(1).strip()}{', ' if m.group(1).strip() and m.group(2).strip() else ''}{m.group(2).strip()} }} from 'next/navigation'", 
                        modificado)
    
    # Limpiar imports vacíos
    modificado = re.sub(r'import\s*\{\s*\}\s*from\s*[\'"]next/navigation[\'"]\s*;?\s*\n?', '', modificado)
    
    # --- PASO 2: AGREGAR useState y useEffect si no existen ---
    if 'useState' not in modificado and 'useEffect' not in modificado:
        # Buscar import de react existente
        match = re.search(r'import\s*\{([^}]*)\}\s*from\s*[\'"]react[\'"]', modificado)
        if match:
            # Agregar useState y useEffect al import existente
            imports = match.group(1)
            if 'useState' not in imports and 'useEffect' not in imports:
                nuevos_imports = imports.strip()
                if nuevos_imports:
                    nuevos_imports += ', useState, useEffect'
                else:
                    nuevos_imports = 'useState, useEffect'
                modificado = modificado.replace(match.group(0), f"import {{ {nuevos_imports} }} from 'react'")
        else:
            # Agregar nuevo import
            modificado = "import { useState, useEffect } from 'react'\n" + modificado
    
    # --- PASO 3: REEMPLAZAR useSearchParams() por window.location ---
    # Buscar la variable que usa useSearchParams
    match = re.search(r'const\s+(\w+)\s*=\s*useSearchParams\(\)', modificado)
    if match:
        var_name = match.group(1)
        
        # Crear las líneas de reemplazo para cada parámetro
        param_replacements = []
        for param in parametros:
            param_name = param
            setter_name = f"set{param[0].upper()}{param[1:]}"
            param_replacements.append(f"    const [{param_name}, {setter_name}] = useState<string | null>(null)")
        
        # Crear el cuerpo del useEffect
        useEffect_body = "    useEffect(() => {\n"
        useEffect_body += "        const params = new URLSearchParams(window.location.search)\n"
        for param in parametros:
            setter_name = f"set{param[0].upper()}{param[1:]}"
            useEffect_body += f"        {setter_name}(params.get('{param}'))\n"
        useEffect_body += "    }, [])"
        
        # Construir el reemplazo
        replacement = "    // ✅ Reemplazo de useSearchParams() por window.location\n"
        replacement += "\n".join(param_replacements) + "\n\n"
        replacement += useEffect_body
        
        # Reemplazar la declaración de useSearchParams
        pattern = r'const\s+' + var_name + r'\s*=\s*useSearchParams\(\)\s*'
        modificado = re.sub(pattern, replacement, modificado)
        
        # Reemplazar todas las ocurrencias de var_name.get('param') por el estado
        for param in parametros:
            # var_name.get('param') -> param
            pattern_get = re.escape(var_name) + r'\.get\([\'"]' + param + r'[\'"]\)'
            modificado = re.sub(pattern_get, param, modificado)
            
            # var_name.get('param') || '' -> param || ''
            pattern_get_or = re.escape(var_name) + r'\.get\([\'"]' + param + r'[\'"]\)\s*\|\|\s*[\'"]{2}'
            modificado = re.sub(pattern_get_or, f"{param} || ''", modificado)
    
    # --- PASO 4: GUARDAR EL ARCHIVO ---
    if modificado != original:
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(modificado)
        print(f"   ✅ Archivo procesado correctamente")
        return True
    else:
        print(f"   ⏭️  No se realizaron cambios")
        return False


def main():
    """Función principal"""
    print("🚀 Iniciando reemplazo de useSearchParams()...")
    print("=" * 50)
    
    contador = 0
    
    for archivo in ARCHIVOS:
        ruta_completa = BASE_DIR / archivo["ruta"]
        if procesar_archivo(ruta_completa, archivo["parametros"]):
            contador += 1
    
    print("=" * 50)
    print(f"✅ Proceso completado. Archivos procesados: {contador}")
    print("")
    print("📌 Ahora ejecuta: npm run build")


if __name__ == "__main__":
    main()