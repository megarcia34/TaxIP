# ============================================
# SCRIPT: Reemplazar useSearchParams() por window.location
# Proyecto: TaxIP 2.0 Dashboard
# Objetivo: Eliminar dependencia de useSearchParams() para evitar errores de build
# ============================================

Write-Host "🚀 Iniciando reemplazo de useSearchParams()..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Directorio base
$baseDir = "D:\ataxip\dashboard"

# Archivos a procesar (con sus respectivos parámetros)
$archivos = @(
    @{ Ruta = "app/(public)/reservar/page.tsx"; Parametros = @("origenId") },
    @{ Ruta = "app/dashboard-propietario/page.tsx"; Parametros = @("propietario_id") },
    @{ Ruta = "app/dashboard-propietario/contratos/page.tsx"; Parametros = @("propietario_id") },
    @{ Ruta = "app/dashboard-propietario/gastos/page.tsx"; Parametros = @("propietario_id") },
    @{ Ruta = "app/dashboard-propietario/ingresos/page.tsx"; Parametros = @("propietario_id") },
    @{ Ruta = "app/dashboard-propietario/mantenimientos/page.tsx"; Parametros = @("propietario_id") },
    @{ Ruta = "app/dashboard-propietario/rentabilidad/page.tsx"; Parametros = @("propietario_id") },
    @{ Ruta = "app/dashboard-propietario/reportes/page.tsx"; Parametros = @("propietario_id") },
    @{ Ruta = "app/dashboard-propietario/vehiculos/page.tsx"; Parametros = @("propietario_id") },
    @{ Ruta = "app/dashboard-propietario/vehiculos/nuevo/page.tsx"; Parametros = @("propietario_id") }
)

$contador = 0

foreach ($archivo in $archivos) {
    $rutaCompleta = Join-Path $baseDir $archivo.Ruta
    
    # Verificar si el archivo existe
    if (-not (Test-Path $rutaCompleta)) {
        Write-Host "⚠️ Archivo no encontrado: $($archivo.Ruta)" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "📝 Procesando: $($archivo.Ruta)" -ForegroundColor White
    
    # Leer el contenido del archivo
    $contenido = Get-Content $rutaCompleta -Raw -Encoding UTF8
    
    # Verificar si usa useSearchParams
    if ($contenido -notmatch "useSearchParams") {
        Write-Host "   ⏭️ No usa useSearchParams, omitiendo..." -ForegroundColor Gray
        continue
    }
    
    # --- PASO 1: ELIMINAR import de useSearchParams ---
    $contenido = $contenido -replace "import \{ useSearchParams \} from 'next/navigation'\s*", ""
    $contenido = $contenido -replace "import \{ useSearchParams\s*,\s*useRouter \} from 'next/navigation'", "import { useRouter } from 'next/navigation'"
    
    # --- PASO 2: AGREGAR useState y useEffect si no existen ---
    if ($contenido -notmatch "import \{ useState, useEffect \} from 'react'") {
        # Verificar si ya tiene import de react
        if ($contenido -match "import .* from 'react'") {
            # Reemplazar el import de react con useState y useEffect
            $contenido = $contenido -replace "import (.*) from 'react'", "import { useState, useEffect } from 'react'"
        } else {
            # Agregar import después de los imports existentes
            $lineas = $contenido -split "`n"
            $nuevasLineas = @()
            $importsAgregados = $false
            
            foreach ($linea in $lineas) {
                $nuevasLineas += $linea
                if (-not $importsAgregados -and $linea -match "^import ") {
                    # Después del último import, agregar useState/useEffect
                    # Esto se manejará mejor con un enfoque diferente
                }
            }
            # Simplificamos: agregar al inicio
            $contenido = "import { useState, useEffect } from 'react'`n" + $contenido
        }
    }
    
    # --- PASO 3: REEMPLAZAR useSearchParams() por window.location ---
    # Buscar el nombre de la variable que usa useSearchParams
    $match = [regex]::Match($contenido, "const\s+(\w+)\s*=\s*useSearchParams\(\)")
    if ($match.Success) {
        $varName = $match.Groups[1].Value
        
        # Construir las líneas de reemplazo para cada parámetro
        $paramReplacements = @()
        foreach ($param in $archivo.Parametros) {
            $paramReplacements += "const [$param, set$($param.Substring(0,1).ToUpper() + $param.Substring(1))] = useState<string | null>(null)`n"
        }
        
        $useEffectBody = @"
    useEffect(() => {
        const params = new URLSearchParams(window.location.search)
`n"@
        
        foreach ($param in $archivo.Parametros) {
            $setter = "set$($param.Substring(0,1).ToUpper() + $param.Substring(1))"
            $useEffectBody += "        $setter(params.get('$param'))`n"
        }
        
        $useEffectBody += @"
    }, [])
"@
        
        # Reemplazar la declaración de useSearchParams
        $pattern = "const\s+$varName\s*=\s*useSearchParams\(\)\s*"
        $replacement = "    // ✅ Reemplazo de useSearchParams() por window.location`n"
        $replacement += $paramReplacements -join ""
        $replacement += "`n" + $useEffectBody
        
        $contenido = $contenido -replace $pattern, $replacement
        
        # Reemplazar todas las ocurrencias de $varName.get('param') por el estado
        foreach ($param in $archivo.Parametros) {
            $pattern2 = "$varName\.get\(['""]$param['""]\)"
            $replacement2 = $param
            $contenido = $contenido -replace $pattern2, $replacement2
            
            # También reemplazar si se usa con || ''
            $pattern3 = "$varName\.get\(['""]$param['""]\) \|\| ''"
            $replacement3 = "$param || ''"
            $contenido = $contenido -replace $pattern3, $replacement3
        }
    }
    
    # --- PASO 4: Guardar el archivo ---
    $contenido | Set-Content $rutaCompleta -Encoding UTF8
    $contador++
    Write-Host "   ✅ Archivo procesado correctamente" -ForegroundColor Green
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Proceso completado. Archivos procesados: $contador" -ForegroundColor Green
Write-Host ""
Write-Host "📌 Ahora ejecuta: npm run build" -ForegroundColor Yellow