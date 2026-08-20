"""
Validaciones centralizadas para contratos
Incluye validaciones de identidad, capacidades y conflictos horarios
"""

from typing import Optional, List, Dict, Tuple
from uuid import UUID
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# IMPORTAR FUNCIONES COMPARTIDAS DESDE CORE
from app.core.validaciones_compartidas import es_conductor


# ============================================
# 1. VALIDACIÓN DE HORARIOS (reemplaza matriz de turnos)
# ============================================

def calcular_minutos(hora: str) -> int:
    """Convierte HH:MM a minutos desde medianoche"""
    h, m = map(int, hora.split(':'))
    return h * 60 + m


def calcular_duracion_horas(inicio: str, fin: str) -> float:
    """Calcula duración en horas entre dos horarios (soporta cruce de medianoche)"""
    i_h, i_m = map(int, inicio.split(':'))
    f_h, f_m = map(int, fin.split(':'))
    
    inicio_minutos = i_h * 60 + i_m
    fin_minutos = f_h * 60 + f_m
    
    if fin_minutos <= inicio_minutos:
        # Cruza medianoche
        return (24 * 60 - inicio_minutos + fin_minutos) / 60
    else:
        return (fin_minutos - inicio_minutos) / 60


def cruza_medianoche(inicio: str, fin: str) -> bool:
    """Determina si un horario cruza medianoche"""
    return calcular_minutos(fin) <= calcular_minutos(inicio)


def hay_conflicto_horario(
    inicio1: str,
    fin1: str,
    inicio2: str,
    fin2: str
) -> bool:
    """
    Determina si dos horarios se superponen (soporta cruce de medianoche).
    Ambos en formato HH:MM.
    
    Ejemplo:
    06:00-14:00 vs 06:00-14:00 → CONFLICTO
    06:00-14:00 vs 14:00-22:00 → NO CONFLICTO (tope exacto)
    06:00-14:00 vs 13:00-21:00 → CONFLICTO
    22:00-06:00 vs 22:00-06:00 → CONFLICTO
    22:00-06:00 vs 06:00-14:00 → NO CONFLICTO (tope exacto)
    22:00-06:00 vs 23:00-07:00 → CONFLICTO
    """
    i1 = calcular_minutos(inicio1)
    f1 = calcular_minutos(fin1)
    i2 = calcular_minutos(inicio2)
    f2 = calcular_minutos(fin2)
    
    # Caso 1: Ambos cruzan medianoche → siempre se superponen
    if cruza_medianoche(inicio1, fin1) and cruza_medianoche(inicio2, fin2):
        return True
    
    # Caso 2: Turno 1 cruza medianoche, Turno 2 no cruza
    if cruza_medianoche(inicio1, fin1):
        # Turno1 cubre [i1, 1440) ∪ [0, f1]
        # Turno2 no cruza, está en [i2, f2]
        # Hay conflicto si i2 < f1 (está en la parte de la mañana) 
        # O si i2 >= i1 (está en la parte de la noche)
        return i2 < f1 or i2 >= i1
    
    # Caso 3: Turno 2 cruza medianoche, Turno 1 no cruza
    if cruza_medianoche(inicio2, fin2):
        # Turno2 cubre [i2, 1440) ∪ [0, f2]
        # Turno1 no cruza, está en [i1, f1]
        # Hay conflicto si i1 < f2 (está en la parte de la mañana)
        # O si i1 >= i2 (está en la parte de la noche)
        return i1 < f2 or i1 >= i2
    
    # Caso 4: Ninguno cruza medianoche → comparación simple
    return i1 < f2 and i2 < f1


def es_horario_posterior(hora1: str, hora2: str) -> bool:
    """
    Determina si hora1 es posterior a hora2 considerando cruce de medianoche.
    Ejemplo: 08:00 es posterior a 06:00 (True)
             06:00 es posterior a 22:00 (True) - cruza medianoche
             14:00 es posterior a 06:00 (True)
    """
    min1 = calcular_minutos(hora1)
    min2 = calcular_minutos(hora2)
    
    if min1 > min2:
        return True
    if min1 < min2:
        # Podría ser posterior si cruza medianoche
        return (min1 + 24 * 60) - min2 > 0
    return False  # iguales


# ============================================
# 2. VALIDACIÓN DE CAPACIDADES (usuario_rol)
# ============================================

async def agregar_rol_usuario(
    usuario_id: UUID,
    tipo_usuario_id: UUID,
    db: AsyncSession,
    fecha_inicio: Optional[date] = None
) -> None:
    """Agrega un rol adicional a un usuario."""
    if fecha_inicio is None:
        fecha_inicio = date.today()
    
    query_insert = text("""
        INSERT INTO auth.usuario_rol (
            id, usuario_id, tipo_usuario_id, activo, fecha_inicio, created_at, updated_at
        )
        VALUES (
            gen_random_uuid(), :usuario_id, :tipo_usuario_id, true, :fecha_inicio, NOW(), NOW()
        )
        ON CONFLICT (usuario_id, tipo_usuario_id) DO NOTHING
        RETURNING id
    """)
    result = await db.execute(query_insert, {
        "usuario_id": usuario_id,
        "tipo_usuario_id": tipo_usuario_id,
        "fecha_inicio": fecha_inicio
    })
    
    if not result.first():
        query_reactivar = text("""
            UPDATE auth.usuario_rol
            SET activo = true,
                fecha_inicio = :fecha_inicio,
                fecha_fin = NULL,
                updated_at = NOW()
            WHERE usuario_id = :usuario_id
              AND tipo_usuario_id = :tipo_usuario_id
              AND activo = false
            RETURNING id
        """)
        result = await db.execute(query_reactivar, {
            "usuario_id": usuario_id,
            "tipo_usuario_id": tipo_usuario_id,
            "fecha_inicio": fecha_inicio
        })


async def desactivar_rol_usuario(
    usuario_id: UUID,
    tipo_usuario_id: UUID,
    db: AsyncSession
) -> bool:
    """Desactiva un rol adicional de un usuario."""
    query = text("""
        UPDATE auth.usuario_rol
        SET activo = false,
            fecha_fin = CURRENT_DATE,
            updated_at = NOW()
        WHERE usuario_id = :usuario_id
          AND tipo_usuario_id = :tipo_usuario_id
          AND activo = true
        RETURNING id
    """)
    result = await db.execute(query, {
        "usuario_id": usuario_id,
        "tipo_usuario_id": tipo_usuario_id
    })
    return result.first() is not None


# ============================================
# 3. VALIDACIÓN DE PARÁMETROS ALQUILER
# ============================================

DIAS_VALIDOS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
MODALIDADES_VALIDAS = ["DIARIO", "SEMANAL"]
TRATAMIENTOS_VALIDOS = ["POR_DISPONIBILIDAD", "POR_USO_EFECTIVO"]


def validar_parametros_alquiler(
    canon_diario: Optional[float],
    km_incluidos_dia: Optional[float],
    valor_km_excedente: Optional[float],
    modalidad_computo: Optional[str],
    dias_contractuales: Optional[List[str]],
    tratamiento_dia_no_trabajado: Optional[str],
    dia_inicio_semana: Optional[str] = None
) -> None:
    """Valida que todos los parámetros de ALQUILER sean válidos"""
    if canon_diario is None or canon_diario <= 0:
        raise ValueError("canon_diario debe ser mayor a 0")
    
    if km_incluidos_dia is None or km_incluidos_dia <= 0:
        raise ValueError("km_incluidos_dia debe ser mayor a 0")
    
    if valor_km_excedente is None or valor_km_excedente < 0:
        raise ValueError("valor_km_excedente no puede ser negativo")
    
    if modalidad_computo not in MODALIDADES_VALIDAS:
        raise ValueError(f"modalidad_computo debe ser DIARIO o SEMANAL, recibido: {modalidad_computo}")
    
    if modalidad_computo == "SEMANAL":
        if not dia_inicio_semana:
            raise ValueError("dia_inicio_semana es obligatorio para modalidad SEMANAL")
        if dia_inicio_semana not in DIAS_VALIDOS:
            raise ValueError(f"dia_inicio_semana inválido: {dia_inicio_semana}")
    
    if not dias_contractuales or len(dias_contractuales) == 0:
        raise ValueError("dias_contractuales debe tener al menos un día")
    
    if len(set(dias_contractuales)) != len(dias_contractuales):
        raise ValueError("dias_contractuales no puede tener días duplicados")
    
    for dia in dias_contractuales:
        if dia not in DIAS_VALIDOS:
            raise ValueError(f"día inválido: {dia}, debe ser uno de: {', '.join(DIAS_VALIDOS)}")
    
    if tratamiento_dia_no_trabajado not in TRATAMIENTOS_VALIDOS:
        raise ValueError(f"tratamiento_dia_no_trabajado debe ser POR_DISPONIBILIDAD o POR_USO_EFECTIVO")


# ============================================
# 4. VALIDACIÓN DE PARÁMETROS AUTO_GESTION
# ============================================

def validar_parametros_autogestion(
    canon_diario: Optional[float],
    km_incluidos_dia: Optional[float],
    valor_km_excedente: Optional[float],
    modalidad_computo: Optional[str],
    tratamiento_dia_no_trabajado: Optional[str],
    porcentaje_chofer: Optional[float]
) -> None:
    """Valida que AUTO_GESTION NO tenga parámetros económicos."""
    if canon_diario is not None:
        raise ValueError("AUTO_GESTION no puede tener canon_diario")
    if km_incluidos_dia is not None:
        raise ValueError("AUTO_GESTION no puede tener km_incluidos_dia")
    if valor_km_excedente is not None:
        raise ValueError("AUTO_GESTION no puede tener valor_km_excedente")
    if modalidad_computo is not None:
        raise ValueError("AUTO_GESTION no puede tener modalidad_computo")
    if tratamiento_dia_no_trabajado is not None:
        raise ValueError("AUTO_GESTION no puede tener tratamiento_dia_no_trabajado")
    if porcentaje_chofer is not None:
        raise ValueError("AUTO_GESTION no puede tener porcentaje_chofer")


# ============================================
# 5. VALIDACIÓN DE DÍAS CONTRACTUALES
# ============================================

def validar_dias_contractuales(
    dias_contractuales: Optional[List[str]],
    tipo_contrato: str
) -> None:
    """Valida los días contractuales para cualquier tipo de contrato."""
    if dias_contractuales:
        if len(set(dias_contractuales)) != len(dias_contractuales):
            raise ValueError("dias_contractuales no puede tener días duplicados")
        for dia in dias_contractuales:
            if dia not in DIAS_VALIDOS:
                raise ValueError(f"día inválido: {dia}")
    
    if tipo_contrato in ["ALQUILER", "AUTO_GESTION"] and not dias_contractuales:
        raise ValueError(f"dias_contractuales es obligatorio para {tipo_contrato}")


# ============================================
# 6. VALIDACIÓN DE PROPIEDAD DEL VEHÍCULO
# ============================================

async def verificar_propiedad_vehiculo(
    vehiculo_id: UUID,
    propietario_id: UUID,
    control_base_id: UUID,
    db: AsyncSession
) -> Tuple[bool, Optional[str]]:
    """Verifica que el vehículo pertenece al propietario y tenant correctos"""
    query = text("""
        SELECT pv.id, v.activo
        FROM fleet.propietario_vehiculo pv
        JOIN fleet.vehiculo v ON v.id = pv.vehiculo_id
        WHERE pv.vehiculo_id = :vehiculo_id
          AND pv.propietario_id = :propietario_id
          AND pv.activo = true
          AND (pv.fecha_fin IS NULL OR pv.fecha_fin > CURRENT_DATE)
          AND v.control_base_id = :control_base_id
          AND v.activo = true
    """)
    result = await db.execute(query, {
        "vehiculo_id": vehiculo_id,
        "propietario_id": propietario_id,
        "control_base_id": control_base_id
    })
    row = result.first()
    
    if not row:
        return False, "El vehículo no pertenece al propietario o no está activo"
    
    return True, None


# ============================================
# 7. VALIDACIÓN DE CHOFER
# ============================================

async def verificar_chofer_valido(
    chofer_id: UUID,
    control_base_id: UUID,
    db: AsyncSession
) -> Tuple[bool, Optional[str]]:
    """Verifica que el chofer existe, es chofer y pertenece al tenant"""
    query = text("""
        SELECT u.id 
        FROM auth.usuario u
        WHERE u.id = :chofer_id 
          AND u.control_base_id = :control_base_id 
          AND u.activo = true
          AND (
              EXISTS (
                  SELECT 1 FROM auth.tipo_usuario tu
                  WHERE tu.id = u.tipo_usuario_id AND tu.nombre = 'chofer'
              )
              OR EXISTS (
                  SELECT 1 FROM auth.usuario_rol ur
                  JOIN auth.tipo_usuario tu ON tu.id = ur.tipo_usuario_id
                  WHERE ur.usuario_id = u.id
                    AND ur.activo = true
                    AND tu.nombre = 'chofer'
                    AND (ur.fecha_fin IS NULL OR ur.fecha_fin > CURRENT_DATE)
              )
          )
    """)
    result = await db.execute(query, {
        "chofer_id": chofer_id,
        "control_base_id": control_base_id
    })
    
    if not result.first():
        return False, "Chofer no encontrado, inactivo o no pertenece al tenant"
    
    return True, None


# ============================================
# 8. VALIDACIÓN DE CONFLICTOS DE CONTRATO (CORREGIDO)
# ============================================

async def verificar_conflictos_contrato(
    vehiculo_id: UUID,
    chofer_id: UUID,
    hora_inicio: str,
    hora_fin: str,
    control_base_id: UUID,
    db: AsyncSession,
    contrato_excluido_id: Optional[UUID] = None,
    dias_contractuales: Optional[List[str]] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None
) -> Tuple[bool, List[str]]:
    """
    Verifica conflictos de contrato considerando vehículo + horario + días + vigencia
    
    ✅ CORREGIDO: Ahora valida también contratos PROGRAMADO y PENDIENTE_CONFIGURACION
    """
    conflictos = []
    
    if fecha_inicio is None:
        fecha_inicio = date.today()
    
    # ============================================
    # 1. Conflictos de vehículo
    # ============================================
    # ✅ Ahora incluye ACTIVO, PROGRAMADO y PENDIENTE_CONFIGURACION (si tiene horario)
    query_vehiculo = text("""
        SELECT c.id, c.hora_inicio, c.hora_fin, c.dias_contractuales, 
               c.fecha_inicio, c.fecha_fin, c.estado_contrato
        FROM fleet.contrato_vehiculo c
        WHERE c.vehiculo_id = :vehiculo_id
          AND c.control_base_id = :control_base_id
          AND (
              c.estado_contrato = 'ACTIVO'
              OR c.estado_contrato = 'PROGRAMADO'
              OR (c.estado_contrato = 'PENDIENTE_CONFIGURACION' AND c.hora_inicio IS NOT NULL)
          )
    """)
    result = await db.execute(query_vehiculo, {
        "vehiculo_id": vehiculo_id,
        "control_base_id": control_base_id
    })
    
    for row in result:
        contrato_id = row[0]
        hora_inicio_existente = row[1].strftime("%H:%M") if row[1] else None
        hora_fin_existente = row[2].strftime("%H:%M") if row[2] else None
        dias_existentes = row[3] if row[3] else []
        fecha_inicio_existente = row[4].date() if row[4] else None
        fecha_fin_existente = row[5].date() if row[5] else None
        estado_existente = row[6]
        
        # Excluir el contrato que se está configurando
        if contrato_excluido_id and contrato_id == contrato_excluido_id:
            continue
        
        # Verificar superposición de períodos
        if fecha_inicio_existente:
            if fecha_fin_existente:
                if fecha_fin is not None and fecha_fin <= fecha_inicio_existente:
                    continue
                if fecha_inicio >= fecha_fin_existente:
                    continue
            else:
                if fecha_fin is not None and fecha_fin <= fecha_inicio_existente:
                    continue
        
        # Verificar conflicto horario
        if hora_inicio_existente and hora_fin_existente:
            if hay_conflicto_horario(
                hora_inicio, hora_fin,
                hora_inicio_existente, hora_fin_existente
            ):
                if dias_contractuales and dias_existentes:
                    dias_superpuestos = set(dias_contractuales) & set(dias_existentes)
                    if dias_superpuestos:
                        estado_texto = estado_existente if estado_existente != 'ACTIVO' else 'activo'
                        conflictos.append(
                            f"El vehículo ya tiene un contrato {estado_texto.lower()} en horario "
                            f"{hora_inicio_existente}-{hora_fin_existente} "
                            f"para los días {', '.join(dias_superpuestos)}"
                        )
                else:
                    estado_texto = estado_existente if estado_existente != 'ACTIVO' else 'activo'
                    conflictos.append(
                        f"El vehículo ya tiene un contrato {estado_texto.lower()} en horario "
                        f"{hora_inicio_existente}-{hora_fin_existente}"
                    )
    
    # ============================================
    # 2. Conflictos de chofer
    # ============================================
    # ✅ Ahora incluye ACTIVO, PROGRAMADO y PENDIENTE_CONFIGURACION (si tiene horario)
    query_chofer = text("""
        SELECT c.id, c.hora_inicio, c.hora_fin, c.dias_contractuales,
               c.fecha_inicio, c.fecha_fin, c.estado_contrato
        FROM fleet.contrato_vehiculo c
        WHERE c.chofer_id = :chofer_id
          AND c.control_base_id = :control_base_id
          AND (
              c.estado_contrato = 'ACTIVO'
              OR c.estado_contrato = 'PROGRAMADO'
              OR (c.estado_contrato = 'PENDIENTE_CONFIGURACION' AND c.hora_inicio IS NOT NULL)
          )
    """)
    result = await db.execute(query_chofer, {
        "chofer_id": chofer_id,
        "control_base_id": control_base_id
    })
    
    for row in result:
        contrato_id = row[0]
        hora_inicio_existente = row[1].strftime("%H:%M") if row[1] else None
        hora_fin_existente = row[2].strftime("%H:%M") if row[2] else None
        dias_existentes = row[3] if row[3] else []
        fecha_inicio_existente = row[4].date() if row[4] else None
        fecha_fin_existente = row[5].date() if row[5] else None
        estado_existente = row[6]
        
        if contrato_excluido_id and contrato_id == contrato_excluido_id:
            continue
        
        if fecha_inicio_existente:
            if fecha_fin_existente:
                if fecha_fin is not None and fecha_fin <= fecha_inicio_existente:
                    continue
                if fecha_inicio >= fecha_fin_existente:
                    continue
            else:
                if fecha_fin is not None and fecha_fin <= fecha_inicio_existente:
                    continue
        
        if hora_inicio_existente and hora_fin_existente:
            if hay_conflicto_horario(
                hora_inicio, hora_fin,
                hora_inicio_existente, hora_fin_existente
            ):
                if dias_contractuales and dias_existentes:
                    dias_superpuestos = set(dias_contractuales) & set(dias_existentes)
                    if dias_superpuestos:
                        estado_texto = estado_existente if estado_existente != 'ACTIVO' else 'activo'
                        conflictos.append(
                            f"El chofer ya tiene un contrato {estado_texto.lower()} en horario "
                            f"{hora_inicio_existente}-{hora_fin_existente} "
                            f"para los días {', '.join(dias_superpuestos)}"
                        )
                else:
                    estado_texto = estado_existente if estado_existente != 'ACTIVO' else 'activo'
                    conflictos.append(
                        f"El chofer ya tiene un contrato {estado_texto.lower()} en horario "
                        f"{hora_inicio_existente}-{hora_fin_existente}"
                    )
    
    return len(conflictos) > 0, conflictos


# ============================================
# 9. VERIFICAR CONTRATO EXISTE
# ============================================

async def verificar_contrato_existe(
    contrato_id: UUID,
    propietario_id: UUID,
    db: AsyncSession
) -> Tuple[bool, Optional[str]]:
    """Verifica que el contrato existe y pertenece al propietario"""
    query = text("""
        SELECT id, estado_contrato
        FROM fleet.contrato_vehiculo
        WHERE id = :contrato_id
          AND propietario_id = :propietario_id
    """)
    result = await db.execute(query, {
        "contrato_id": contrato_id,
        "propietario_id": propietario_id
    })
    row = result.first()
    
    if not row:
        return False, "Contrato no encontrado"
    
    return True, row[1]


# ============================================
# 10. PREPARAR PARÁMETROS DE CONTRATO
# ============================================

def preparar_parametros_contrato(
    tipo_contrato: str,
    canon_diario: Optional[float] = None,
    km_incluidos_dia: Optional[float] = None,
    valor_km_excedente: Optional[float] = None,
    modalidad_computo: Optional[str] = None,
    dias_contractuales: Optional[List[str]] = None,
    tratamiento_dia_no_trabajado: Optional[str] = None,
    porcentaje_chofer: Optional[float] = None,
    dia_inicio_semana: Optional[str] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None
) -> dict:
    """Prepara los parámetros del contrato según el tipo"""
    
    # ✅ CORREGIDO: Permite fecha_fin == fecha_inicio (contrato de 1 día)
    if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
        raise ValueError("La fecha de finalización no puede ser anterior a la fecha de inicio")
    
    params = {
        "porcentaje_chofer": None,
        "canon_diario": None,
        "km_incluidos_dia": None,
        "valor_km_excedente": None,
        "modalidad_computo": None,
        "dias_contractuales": None,
        "tratamiento_dia_no_trabajado": None,
        "dia_inicio_semana": None,
    }
    
    if tipo_contrato == "ALQUILER":
        validar_parametros_alquiler(
            canon_diario,
            km_incluidos_dia,
            valor_km_excedente,
            modalidad_computo,
            dias_contractuales,
            tratamiento_dia_no_trabajado,
            dia_inicio_semana
        )
        params["canon_diario"] = canon_diario
        params["km_incluidos_dia"] = km_incluidos_dia
        params["valor_km_excedente"] = valor_km_excedente
        params["modalidad_computo"] = modalidad_computo
        params["dias_contractuales"] = dias_contractuales
        params["tratamiento_dia_no_trabajado"] = tratamiento_dia_no_trabajado
        params["dia_inicio_semana"] = dia_inicio_semana
        
    elif tipo_contrato == "AUTO_GESTION":
        validar_parametros_autogestion(
            canon_diario,
            km_incluidos_dia,
            valor_km_excedente,
            modalidad_computo,
            tratamiento_dia_no_trabajado,
            porcentaje_chofer
        )
        params["dias_contractuales"] = dias_contractuales
        
    elif tipo_contrato == "PORCENTAJE":
        if porcentaje_chofer is None:
            raise ValueError("porcentaje_chofer es obligatorio para PORCENTAJE")
        if porcentaje_chofer < 0 or porcentaje_chofer > 100:
            raise ValueError("porcentaje_chofer debe estar entre 0 y 100")
        params["porcentaje_chofer"] = porcentaje_chofer
        params["dias_contractuales"] = dias_contractuales
    
    return params


# ============================================
# 11. VALIDACIÓN PARA AUTO_GESTION
# ============================================

async def verificar_autogestion(
    propietario_id: UUID,
    chofer_id: UUID,
    db: AsyncSession
) -> Tuple[bool, Optional[str]]:
    """Verifica que un propietario puede operar en AUTO_GESTION."""
    if propietario_id != chofer_id:
        return False, "En AUTO_GESTION, el propietario y el conductor deben ser la misma persona"
    
    tiene_capacidad = await es_conductor(propietario_id, db)
    if not tiene_capacidad:
        return False, "El propietario no está habilitado como conductor (falta capacidad CONDUCTOR)"
    
    return True, None


# ============================================
# 12. FUNCIONES AUXILIARES PARA TURNOS
# ============================================

async def obtener_turno_activo_conductor(
    chofer_id: UUID,
    db: AsyncSession
) -> Optional[dict]:
    """Obtiene el turno activo del conductor, si existe."""
    query = text("""
        SELECT 
            t.id, t.vehiculo_id, t.contrato_id, t.control_base_id,
            t.estado, t.inicio_turno, t.km_inicial, t.combustible_inicial,
            t.snapshot_dia_contractual, t.snapshot_hora_inicio, t.snapshot_hora_fin,
            v.patente
        FROM fleet.turno_chofer t
        JOIN fleet.vehiculo v ON v.id = t.vehiculo_id
        WHERE t.chofer_id = :chofer_id AND t.estado = 'ACTIVO'
        ORDER BY t.inicio_turno DESC
        LIMIT 1
    """)
    result = await db.execute(query, {"chofer_id": chofer_id})
    row = result.first()
    if row:
        return {
            "id": row[0],
            "vehiculo_id": row[1],
            "contrato_id": row[2],
            "control_base_id": row[3],
            "estado": row[4],
            "inicio_turno": row[5],
            "km_inicial": float(row[6]) if row[6] else None,
            "combustible_inicial": row[7],
            "snapshot_dia_contractual": row[8],
            "snapshot_hora_inicio": row[9].strftime("%H:%M") if row[9] else None,
            "snapshot_hora_fin": row[10].strftime("%H:%M") if row[10] else None,
            "patente": row[11]
        }
    return None


async def verificar_conflicto_turno(
    chofer_id: UUID,
    vehiculo_id: UUID,
    dia: str,
    hora_inicio: str,
    hora_fin: str,
    db: AsyncSession
) -> tuple[bool, Optional[str]]:
    """Verifica si existe conflicto de turno activo para conductor o vehículo."""
    # Conductor
    q = text("""
        SELECT id FROM fleet.turno_chofer
        WHERE chofer_id = :chofer_id
          AND estado = 'ACTIVO'
          AND snapshot_dia_contractual = :dia
    """)
    res = await db.execute(q, {"chofer_id": chofer_id, "dia": dia})
    for row in res:
        # Verificar conflicto horario
        q_horario = text("""
            SELECT snapshot_hora_inicio, snapshot_hora_fin
            FROM fleet.turno_chofer
            WHERE id = :turno_id
        """)
        res_horario = await db.execute(q_horario, {"turno_id": row[0]})
        horario_row = res_horario.first()
        if horario_row:
            hora_inicio_existente = horario_row[0].strftime("%H:%M") if horario_row[0] else None
            hora_fin_existente = horario_row[1].strftime("%H:%M") if horario_row[1] else None
            if hora_inicio_existente and hora_fin_existente:
                if hay_conflicto_horario(
                    hora_inicio, hora_fin,
                    hora_inicio_existente, hora_fin_existente
                ):
                    return True, f"Conductor ya tiene turno activo para {dia} en horario {hora_inicio_existente}-{hora_fin_existente}"
    
    # Vehículo
    qv = text("""
        SELECT id FROM fleet.turno_chofer
        WHERE vehiculo_id = :vehiculo_id
          AND estado = 'ACTIVO'
          AND snapshot_dia_contractual = :dia
    """)
    resv = await db.execute(qv, {"vehiculo_id": vehiculo_id, "dia": dia})
    for row in resv:
        q_horario = text("""
            SELECT snapshot_hora_inicio, snapshot_hora_fin
            FROM fleet.turno_chofer
            WHERE id = :turno_id
        """)
        res_horario = await db.execute(q_horario, {"turno_id": row[0]})
        horario_row = res_horario.first()
        if horario_row:
            hora_inicio_existente = horario_row[0].strftime("%H:%M") if horario_row[0] else None
            hora_fin_existente = horario_row[1].strftime("%H:%M") if horario_row[1] else None
            if hora_inicio_existente and hora_fin_existente:
                if hay_conflicto_horario(
                    hora_inicio, hora_fin,
                    hora_inicio_existente, hora_fin_existente
                ):
                    return True, f"Vehículo ya tiene turno activo para {dia} en horario {hora_inicio_existente}-{hora_fin_existente}"
    
    return False, None