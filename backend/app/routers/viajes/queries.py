from sqlalchemy import text

GET_VIAJE_BY_ID = text("""
    SELECT 
        vs.id, vs.estado, vs.direccion_origen, vs.direccion_destino,
        vs.precio_estimado, vs.precio_final, vs.created_at,
        vs.aceptado_en, vs.iniciado_en, vs.finalizado_en,
        vs.distancia_metros, vs.tiempo_estimado_segundos,
        COALESCE(p.nombre || ' ' || p.apellido, u.email) as pasajero_nombre,
        COALESCE(p2.nombre || ' ' || p2.apellido, u2.email) as chofer_nombre,
        ST_X(vs.origen::geometry) as origen_lat,
        ST_Y(vs.origen::geometry) as origen_lng,
        ST_X(vs.destino::geometry) as destino_lat,
        ST_Y(vs.destino::geometry) as destino_lng
    FROM trip.viaje_solicitado vs
    JOIN auth.usuario u ON u.id = vs.pasajero_id
    LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
    LEFT JOIN auth.usuario u2 ON u2.id = vs.chofer_id
    LEFT JOIN auth.perfil_general p2 ON p2.usuario_id = u2.id
    WHERE vs.id = :viaje_id
""")

GET_HISTORIAL_VIAJES = text("""
    SELECT 
        vs.id, vs.estado, vs.direccion_origen, vs.direccion_destino,
        vs.precio_estimado, vs.precio_final, vs.created_at,
        vs.aceptado_en, vs.iniciado_en, vs.finalizado_en,
        vs.distancia_metros, vs.tiempo_estimado_segundos,
        COALESCE(p.nombre || ' ' || p.apellido, u.email) as pasajero_nombre,
        COALESCE(p2.nombre || ' ' || p2.apellido, u2.email) as chofer_nombre,
        ST_X(vs.origen::geometry) as origen_lat,
        ST_Y(vs.origen::geometry) as origen_lng,
        ST_X(vs.destino::geometry) as destino_lat,
        ST_Y(vs.destino::geometry) as destino_lng
    FROM trip.viaje_solicitado vs
    JOIN auth.usuario u ON u.id = vs.pasajero_id
    LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
    LEFT JOIN auth.usuario u2 ON u2.id = vs.chofer_id
    LEFT JOIN auth.perfil_general p2 ON p2.usuario_id = u2.id
    WHERE vs.control_base_id = :control_base_id
    ORDER BY vs.created_at DESC
    LIMIT :limit
""")

GET_VIAJES_POR_ESTADO = text("""
    SELECT 
        vs.id, vs.estado, vs.direccion_origen, vs.direccion_destino,
        vs.precio_estimado, vs.precio_final, vs.created_at,
        vs.aceptado_en, vs.iniciado_en, vs.finalizado_en,
        vs.distancia_metros, vs.tiempo_estimado_segundos,
        COALESCE(p.nombre || ' ' || p.apellido, u.email) as pasajero_nombre,
        COALESCE(p2.nombre || ' ' || p2.apellido, u2.email) as chofer_nombre,
        ST_X(vs.origen::geometry) as origen_lat,
        ST_Y(vs.origen::geometry) as origen_lng,
        ST_X(vs.destino::geometry) as destino_lat,
        ST_Y(vs.destino::geometry) as destino_lng
    FROM trip.viaje_solicitado vs
    JOIN auth.usuario u ON u.id = vs.pasajero_id
    LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
    LEFT JOIN auth.usuario u2 ON u2.id = vs.chofer_id
    LEFT JOIN auth.perfil_general p2 ON p2.usuario_id = u2.id
    WHERE vs.control_base_id = :control_base_id AND vs.estado = :estado
    ORDER BY vs.created_at DESC
    LIMIT :limit
""")

ACTUALIZAR_ESTADO_VIAJE = text("""
    UPDATE trip.viaje_solicitado
    SET estado = :estado, {campo_fecha} = NOW()
    WHERE id = :viaje_id AND control_base_id = :control_base_id
    RETURNING id
""")
# Agregar al final del archivo

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