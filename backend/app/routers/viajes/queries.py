from sqlalchemy import text

# ============================================
# CONSULTA MEJORADA PARA EL DASHBOARD
# ============================================

GET_VIAJES_DASHBOARD = text("""
    SELECT 
        -- ID del viaje
        vs.id as viaje_id,
        
        -- Estado
        vs.estado,
        
        -- Direcciones
        vs.direccion_origen,
        vs.direccion_destino,
        
        -- Precios
        vs.precio_estimado,
        vs.precio_final,
        
        -- Fechas
        vs.created_at,
        vs.aceptado_en,
        vs.iniciado_en,
        vs.finalizado_en,
        
        -- Distancia y tiempo
        vs.distancia_metros,
        vs.tiempo_estimado_segundos,
        
        -- PASAJERO: nombre + apellido o email
        COALESCE(
            p.nombre || ' ' || p.apellido,
            u.email
        ) as pasajero_nombre,
        
        -- CHOFER: nombre + apellido o "Sin asignar"
        COALESCE(
            p2.nombre || ' ' || p2.apellido,
            u2.email,
            'Sin asignar'
        ) as chofer_nombre,
        
        -- ✅ FECHA formateada (DD/MM/YYYY)
        TO_CHAR(vs.created_at, 'DD/MM/YYYY') as fecha,
        
        -- ✅ HORA formateada (HH24:MI)
        TO_CHAR(vs.created_at, 'HH24:MI') as hora,
        
        -- ✅ PRECIO (estimado o final según estado)
        CASE 
            WHEN vs.estado = 'finalizado' THEN vs.precio_final
            ELSE vs.precio_estimado
        END as precio_mostrado,
        
        -- ✅ EMPRESA (control_base)
        cb.nombre as empresa,
        
        -- ✅ PROPIETARIO del vehículo
        COALESCE(
            p_prop.nombre || ' ' || p_prop.apellido,
            u_prop.email,
            'No asignado'
        ) as propietario_nombre,
        
        -- ✅ DATOS DEL VEHÍCULO
        v.patente,
        v.marca,
        v.modelo,
        
        -- Coordenadas (para mapa)
        ST_X(vs.origen::geometry) as origen_lat,
        ST_Y(vs.origen::geometry) as origen_lng,
        ST_X(vs.destino::geometry) as destino_lat,
        ST_Y(vs.destino::geometry) as destino_lng

    FROM trip.viaje_solicitado vs

    -- Pasajero
    JOIN auth.usuario u ON u.id = vs.pasajero_id
    LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id

    -- Chofer
    LEFT JOIN auth.usuario u2 ON u2.id = vs.chofer_id
    LEFT JOIN auth.perfil_general p2 ON p2.usuario_id = u2.id

    -- ✅ EMPRESA (control_base)
    LEFT JOIN tenant.control_base cb ON cb.id = vs.control_base_id

    -- Vehículo
    LEFT JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id

    -- ✅ PROPIETARIO del vehículo
    LEFT JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true
    LEFT JOIN auth.usuario u_prop ON u_prop.id = pv.propietario_id
    LEFT JOIN auth.perfil_general p_prop ON p_prop.usuario_id = u_prop.id

    WHERE vs.control_base_id = :control_base_id
    ORDER BY vs.created_at DESC
    LIMIT :limit OFFSET :offset
""")


# ============================================
# ESTADÍSTICAS PARA EL DASHBOARD
# ============================================

GET_ESTADISTICAS_DASHBOARD = text("""
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN estado = 'pendiente' THEN 1 END) as pendientes,
        COUNT(CASE WHEN estado = 'aceptado' THEN 1 END) as aceptados,
        COUNT(CASE WHEN estado = 'en_curso' THEN 1 END) as en_curso,
        COUNT(CASE WHEN estado = 'finalizado' THEN 1 END) as finalizados,
        COUNT(CASE WHEN estado = 'cancelado' THEN 1 END) as cancelados,
        COUNT(CASE WHEN created_at::date = CURRENT_DATE THEN 1 END) as hoy,
        COALESCE(SUM(CASE WHEN estado = 'finalizado' AND created_at::date = CURRENT_DATE 
            THEN precio_final ELSE 0 END), 0) as recaudacion_hoy
    FROM trip.viaje_solicitado
    WHERE control_base_id = :control_base_id
""")


# ============================================
# HISTORIAL DE VIAJES (MEJORADO)
# ============================================

GET_HISTORIAL_VIAJES = text("""
    SELECT 
        vs.id,
        vs.estado,
        vs.direccion_origen,
        vs.direccion_destino,
        vs.precio_estimado,
        vs.precio_final,
        vs.created_at,
        vs.aceptado_en,
        vs.iniciado_en,
        vs.finalizado_en,
        vs.distancia_metros,
        vs.tiempo_estimado_segundos,
        
        -- Pasajero
        COALESCE(p.nombre || ' ' || p.apellido, u.email) as pasajero_nombre,
        
        -- Chofer
        COALESCE(p2.nombre || ' ' || p2.apellido, u2.email, 'Sin asignar') as chofer_nombre,
        
        -- ✅ FECHA formateada (DD/MM/YYYY)
        TO_CHAR(vs.created_at, 'DD/MM/YYYY') as fecha,
        
        -- ✅ HORA formateada (HH24:MI)
        TO_CHAR(vs.created_at, 'HH24:MI') as hora,
        
        -- ✅ PRECIO según estado
        CASE 
            WHEN vs.estado = 'finalizado' THEN vs.precio_final
            ELSE vs.precio_estimado
        END as precio_mostrado,
        
        -- ✅ EMPRESA
        cb.nombre as empresa,
        
        -- ✅ PROPIETARIO
        COALESCE(
            p_prop.nombre || ' ' || p_prop.apellido,
            u_prop.email,
            'No asignado'
        ) as propietario_nombre,
        
        -- Datos del vehículo
        v.patente,
        v.marca,
        v.modelo,
        
        -- Calificación
        c.puntaje as calificacion,
        
        -- Coordenadas
        ST_X(vs.origen::geometry) as origen_lat,
        ST_Y(vs.origen::geometry) as origen_lng,
        ST_X(vs.destino::geometry) as destino_lat,
        ST_Y(vs.destino::geometry) as destino_lng

    FROM trip.viaje_solicitado vs

    -- Pasajero
    JOIN auth.usuario u ON u.id = vs.pasajero_id
    LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id

    -- Chofer
    LEFT JOIN auth.usuario u2 ON u2.id = vs.chofer_id
    LEFT JOIN auth.perfil_general p2 ON p2.usuario_id = u2.id

    -- ✅ EMPRESA
    LEFT JOIN tenant.control_base cb ON cb.id = vs.control_base_id

    -- Vehículo
    LEFT JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id

    -- ✅ PROPIETARIO
    LEFT JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true
    LEFT JOIN auth.usuario u_prop ON u_prop.id = pv.propietario_id
    LEFT JOIN auth.perfil_general p_prop ON p_prop.usuario_id = u_prop.id

    -- Calificación (solo si existe)
    LEFT JOIN trip.calificacion c ON c.viaje_id = vs.id 
        AND c.calificador_id = vs.pasajero_id

    WHERE vs.control_base_id = :control_base_id
    ORDER BY vs.created_at DESC
    LIMIT :limit OFFSET :offset
""")


# ============================================
# VIAJES POR ESTADO (MEJORADO)
# ============================================

GET_VIAJES_POR_ESTADO = text("""
    SELECT 
        vs.id,
        vs.estado,
        vs.direccion_origen,
        vs.direccion_destino,
        vs.precio_estimado,
        vs.precio_final,
        vs.created_at,
        vs.aceptado_en,
        vs.iniciado_en,
        vs.finalizado_en,
        vs.distancia_metros,
        vs.tiempo_estimado_segundos,
        
        -- Pasajero
        COALESCE(p.nombre || ' ' || p.apellido, u.email) as pasajero_nombre,
        
        -- Chofer
        COALESCE(p2.nombre || ' ' || p2.apellido, u2.email, 'Sin asignar') as chofer_nombre,
        
        -- ✅ FECHA formateada
        TO_CHAR(vs.created_at, 'DD/MM/YYYY') as fecha,
        
        -- ✅ HORA formateada
        TO_CHAR(vs.created_at, 'HH24:MI') as hora,
        
        -- ✅ PRECIO según estado
        CASE 
            WHEN vs.estado = 'finalizado' THEN vs.precio_final
            ELSE vs.precio_estimado
        END as precio_mostrado,
        
        -- ✅ EMPRESA
        cb.nombre as empresa,
        
        -- ✅ PROPIETARIO
        COALESCE(
            p_prop.nombre || ' ' || p_prop.apellido,
            u_prop.email,
            'No asignado'
        ) as propietario_nombre,
        
        -- Datos del vehículo
        v.patente,
        v.marca,
        v.modelo,
        
        -- Coordenadas
        ST_X(vs.origen::geometry) as origen_lat,
        ST_Y(vs.origen::geometry) as origen_lng,
        ST_X(vs.destino::geometry) as destino_lat,
        ST_Y(vs.destino::geometry) as destino_lng

    FROM trip.viaje_solicitado vs

    -- Pasajero
    JOIN auth.usuario u ON u.id = vs.pasajero_id
    LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id

    -- Chofer
    LEFT JOIN auth.usuario u2 ON u2.id = vs.chofer_id
    LEFT JOIN auth.perfil_general p2 ON p2.usuario_id = u2.id

    -- ✅ EMPRESA
    LEFT JOIN tenant.control_base cb ON cb.id = vs.control_base_id

    -- Vehículo
    LEFT JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id

    -- ✅ PROPIETARIO
    LEFT JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true
    LEFT JOIN auth.usuario u_prop ON u_prop.id = pv.propietario_id
    LEFT JOIN auth.perfil_general p_prop ON p_prop.usuario_id = u_prop.id

    WHERE vs.control_base_id = :control_base_id 
      AND vs.estado = :estado
    ORDER BY vs.created_at DESC
    LIMIT :limit OFFSET :offset
""")


# ============================================
# VIAJE POR ID (MEJORADO)
# ============================================

GET_VIAJE_BY_ID = text("""
    SELECT 
        vs.id,
        vs.estado,
        vs.direccion_origen,
        vs.direccion_destino,
        vs.precio_estimado,
        vs.precio_final,
        vs.created_at,
        vs.aceptado_en,
        vs.iniciado_en,
        vs.finalizado_en,
        vs.distancia_metros,
        vs.tiempo_estimado_segundos,
        
        -- Pasajero
        COALESCE(p.nombre || ' ' || p.apellido, u.email) as pasajero_nombre,
        
        -- Chofer
        COALESCE(p2.nombre || ' ' || p2.apellido, u2.email, 'Sin asignar') as chofer_nombre,
        
        -- ✅ FECHA formateada
        TO_CHAR(vs.created_at, 'DD/MM/YYYY') as fecha,
        
        -- ✅ HORA formateada
        TO_CHAR(vs.created_at, 'HH24:MI') as hora,
        
        -- ✅ PRECIO según estado
        CASE 
            WHEN vs.estado = 'finalizado' THEN vs.precio_final
            ELSE vs.precio_estimado
        END as precio_mostrado,
        
        -- ✅ EMPRESA
        cb.nombre as empresa,
        
        -- ✅ PROPIETARIO
        COALESCE(
            p_prop.nombre || ' ' || p_prop.apellido,
            u_prop.email,
            'No asignado'
        ) as propietario_nombre,
        
        -- Datos del vehículo
        v.patente,
        v.marca,
        v.modelo,
        
        -- Coordenadas
        ST_X(vs.origen::geometry) as origen_lat,
        ST_Y(vs.origen::geometry) as origen_lng,
        ST_X(vs.destino::geometry) as destino_lat,
        ST_Y(vs.destino::geometry) as destino_lng

    FROM trip.viaje_solicitado vs

    -- Pasajero
    JOIN auth.usuario u ON u.id = vs.pasajero_id
    LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id

    -- Chofer
    LEFT JOIN auth.usuario u2 ON u2.id = vs.chofer_id
    LEFT JOIN auth.perfil_general p2 ON p2.usuario_id = u2.id

    -- ✅ EMPRESA
    LEFT JOIN tenant.control_base cb ON cb.id = vs.control_base_id

    -- Vehículo
    LEFT JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id

    -- ✅ PROPIETARIO
    LEFT JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true
    LEFT JOIN auth.usuario u_prop ON u_prop.id = pv.propietario_id
    LEFT JOIN auth.perfil_general p_prop ON p_prop.usuario_id = u_prop.id

    WHERE vs.id = :viaje_id
""")


# ============================================
# ACTUALIZAR ESTADO DEL VIAJE
# ============================================

ACTUALIZAR_ESTADO_VIAJE = text("""
    UPDATE trip.viaje_solicitado
    SET estado = :estado, {campo_fecha} = NOW()
    WHERE id = :viaje_id AND control_base_id = :control_base_id
    RETURNING id
""")


# ============================================
# ENCONTRAR CHOFER MÁS CERCANO
# ============================================

ENCONTRAR_CHOFER_MAS_CERCANO = text("""
    SELECT 
        cv.id as chofer_vehiculo_id,
        cv.usuario_id,
        cv.vehiculo_id,
        cv.calificacion_promedio,
        COALESCE(p.nombre || ' ' || p.apellido, u.email) as nombre,
        u.email,
        v.patente,
        v.marca,
        v.modelo,
        ST_Distance(
            cv.ubicacion,
            ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography
        ) as distancia
    FROM fleet.chofer_vehiculo cv
    JOIN auth.usuario u ON u.id = cv.usuario_id
    LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
    LEFT JOIN fleet.vehiculo v ON v.id = cv.vehiculo_id
    WHERE cv.control_base_id = :control_base_id
      AND cv.estado_laboral = 'libre'
      AND cv.activo = true
      AND cv.estado_aprobacion = 'aprobado'
      AND cv.vehiculo_id IS NOT NULL
    ORDER BY distancia ASC
    LIMIT 1
""")


# ============================================
# NUEVA: CONSULTA PARA REPORTES POR ROL
# ============================================

GET_REPORTE_VIAJES = text("""
    SELECT 
        vs.id,
        vs.estado,
        vs.direccion_origen,
        vs.direccion_destino,
        vs.precio_estimado,
        vs.precio_final,
        TO_CHAR(vs.created_at, 'DD/MM/YYYY') as fecha,
        TO_CHAR(vs.created_at, 'HH24:MI') as hora,
        vs.created_at,
        COALESCE(p.nombre || ' ' || p.apellido, u.email) as pasajero_nombre,
        COALESCE(p2.nombre || ' ' || p2.apellido, u2.email, 'Sin asignar') as chofer_nombre,
        cb.nombre as empresa,
        COALESCE(p_prop.nombre || ' ' || p_prop.apellido, u_prop.email, 'No asignado') as propietario_nombre,
        v.patente,
        v.marca,
        v.modelo,
        v.id as vehiculo_id
    FROM trip.viaje_solicitado vs
    JOIN auth.usuario u ON u.id = vs.pasajero_id
    LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
    LEFT JOIN auth.usuario u2 ON u2.id = vs.chofer_id
    LEFT JOIN auth.perfil_general p2 ON p2.usuario_id = u2.id
    LEFT JOIN tenant.control_base cb ON cb.id = vs.control_base_id
    LEFT JOIN fleet.vehiculo v ON v.id = vs.vehiculo_id
    LEFT JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id AND pv.activo = true
    LEFT JOIN auth.usuario u_prop ON u_prop.id = pv.propietario_id
    LEFT JOIN auth.perfil_general p_prop ON p_prop.usuario_id = u_prop.id
    WHERE vs.control_base_id = :control_base_id
    ORDER BY vs.created_at DESC
    LIMIT :limit OFFSET :offset
""")